import concurrent.futures
import logging
import sys
from abc import ABC, abstractmethod
from ast import literal_eval
from concurrent.futures import Future
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, NamedTuple, Optional, Sequence, Set, Tuple

import click
from pygitguardian import GGClient
from pygitguardian.config import DOCUMENT_SIZE_THRESHOLD_BYTES, MULTI_DOCUMENT_LIMIT
from pygitguardian.iac_models import IaCScanResult
from pygitguardian.models import Detail, ScanResult

from ggshield.core.cache import Cache
from ggshield.core.client import check_client_api_key
from ggshield.core.errors import UnexpectedError
from ggshield.core.filter import (
    leak_dictionary_by_ignore_sha,
    remove_ignored_from_result,
    remove_results_from_ignore_detectors,
)
from ggshield.core.text_utils import STYLE, display_error, format_text, pluralize
from ggshield.core.types import IgnoredMatch
from ggshield.core.utils import Filemode

from .scan_context import ScanContext
from .scannable import DecodeError, Scannable


logger = logging.getLogger(__name__)

# GitGuardian API does not accept paths longer than this
_API_PATH_MAX_LENGTH = 256


class Result(NamedTuple):
    """
    Return model for a scan which zips the information
    between the Scan result and its input file.
    """

    # TODO: Rename `file` to `scannable`?
    file: Scannable  # filename that was scanned
    scan: ScanResult  # Result of content scan

    @property
    def filename(self) -> str:
        return self.file.filename

    @property
    def filemode(self) -> Filemode:
        return self.file.filemode

    @property
    def content(self) -> str:
        return self.file.content

    @property
    def has_policy_breaks(self) -> bool:
        # Needs a `type: ignore` because py-gitguardian type hints are not complete.
        # See https://github.com/GitGuardian/py-gitguardian/issues/49
        return self.scan.has_policy_breaks  # type: ignore


class Error(NamedTuple):
    files: List[Tuple[str, Filemode]]
    description: str  # Description of the error


@dataclass
class Results:
    """
    Return model for a scan with the results and errors of the scan

    Not a NamedTuple like the others because it causes mypy 0.961 to crash on the
    `from_exception()` method (!)

    Similar crash: https://github.com/python/mypy/issues/12629
    """

    results: List[Result] = field(default_factory=list)
    errors: List[Error] = field(default_factory=list)

    @staticmethod
    def from_exception(exc: Exception) -> "Results":
        """Create a Results representing a failure"""
        error = Error(files=[], description=str(exc))
        return Results(results=[], errors=[error])

    def extend(self, others: "Results") -> None:
        self.results.extend(others.results)
        self.errors.extend(others.errors)

    @property
    def has_policy_breaks(self) -> bool:
        return any(x.has_policy_breaks for x in self.results)


class ScanCollection:
    id: str
    type: str
    results: Optional[Results] = None
    scans: Optional[List["ScanCollection"]] = None
    iac_result: Optional[IaCScanResult] = None
    optional_header: Optional[str] = None  # To be printed in Text Output
    extra_info: Optional[Dict[str, str]] = None  # To be included in JSON Output

    def __init__(
        self,
        id: str,
        type: str,
        results: Optional[Results] = None,
        scans: Optional[List["ScanCollection"]] = None,
        iac_result: Optional[IaCScanResult] = None,
        optional_header: Optional[str] = None,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        self.id = id
        self.type = type
        self.results = results
        self.scans = scans
        self.iac_result = iac_result
        self.optional_header = optional_header
        self.extra_info = extra_info

        (
            self.known_secrets_count,
            self.new_secrets_count,
        ) = self._get_known_new_secrets_count()

    @property
    def has_new_secrets(self) -> bool:
        return self.new_secrets_count > 0

    @property
    def has_secrets(self) -> bool:
        return (self.new_secrets_count + self.known_secrets_count) > 0

    @property
    def scans_with_results(self) -> List["ScanCollection"]:
        if self.scans:
            return [scan for scan in self.scans if scan.results]
        return []

    @property
    def has_iac_result(self) -> bool:
        return bool(self.iac_result and self.iac_result.entities_with_incidents)

    @property
    def has_results(self) -> bool:
        return bool(self.results and self.results.results)

    def _get_known_new_secrets_count(self) -> Tuple[int, int]:
        policy_breaks = []
        for result in self.get_all_results():
            for policy_break in result.scan.policy_breaks:
                policy_breaks.append(policy_break)

        known_secrets_count = 0
        new_secrets_count = 0
        sha_dict = leak_dictionary_by_ignore_sha(policy_breaks)

        for ignore_sha, policy_breaks in sha_dict.items():
            if policy_breaks[0].known_secret:
                known_secrets_count += 1
            else:
                new_secrets_count += 1

        return known_secrets_count, new_secrets_count

    def get_all_results(self) -> Iterable[Result]:
        """Returns an iterable on all results and sub-scan results"""
        if self.results:
            yield from self.results.results
        if self.scans:
            for scan in self.scans:
                if scan.results:
                    yield from scan.results.results


class SecretScannerUI(ABC):
    """
    An abstract class used by SecretScanner to notify callers about progress or events
    during a scan
    """

    @abstractmethod
    def on_scanned(self, scannables: Sequence[Scannable]) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_skipped(self, scannable: Scannable, reason: str) -> None:
        """
        Called when a scannable was skipped, `reason` explains why. If `reason` is empty
        then the user should not be notified of the skipped scannable (this happens for
        example when skipping empty files)
        """
        raise NotImplementedError


class DefaultSecretScannerUI(SecretScannerUI):
    """
    Default implementation of SecretScannerUI. Does not show progress.
    """

    def on_scanned(self, scannables: Sequence[Scannable]) -> None:
        pass

    def on_skipped(self, scannable: Scannable, reason: str) -> None:
        if reason:
            print(f"Skipped {scannable.url}: {reason}", file=sys.stderr)


class SecretScanner:
    """
    A SecretScanner scans a list of File, using multiple threads
    """

    def __init__(
        self,
        client: GGClient,
        cache: Cache,
        scan_context: ScanContext,
        ignored_matches: Optional[Iterable[IgnoredMatch]] = None,
        ignored_detectors: Optional[Set[str]] = None,
        check_api_key: Optional[bool] = True,
    ):
        if check_api_key:
            check_client_api_key(client)

        self.client = client
        self.cache = cache
        self.ignored_matches = ignored_matches or []
        self.ignored_detectors = ignored_detectors
        self.headers = scan_context.get_http_headers()
        self.command_id = scan_context.command_id

    def scan(
        self,
        files: Iterable[Scannable],
        scanner_ui: SecretScannerUI = DefaultSecretScannerUI(),
        scan_threads: int = 4,
    ) -> Results:
        """
        Starts the scan, using at most scan_threads.
        Reports progress through `scanner_ui`.
        Returns a Results instance.
        """
        logger.debug("files=%s command_id=%s", self, self.command_id)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=scan_threads, thread_name_prefix="content_scan"
        ) as executor:
            chunks_for_futures = self._start_scans(
                executor,
                files,
                scanner_ui,
            )

            return self._collect_results(scanner_ui, chunks_for_futures)

    def _scan_chunk(
        self, executor: concurrent.futures.ThreadPoolExecutor, chunk: List[Scannable]
    ) -> Future:
        """
        Sends a chunk of files to scan to the API
        """
        # `documents` is a version of `chunk` suitable for `GGClient.multi_content_scan()`
        documents = [
            {"document": x.content, "filename": x.filename[-_API_PATH_MAX_LENGTH:]}
            for x in chunk
        ]

        return executor.submit(
            self.client.multi_content_scan,
            documents,
            self.headers,
            ignore_known_secrets=True,
        )

    def _start_scans(
        self,
        executor: concurrent.futures.ThreadPoolExecutor,
        scannables: Iterable[Scannable],
        scanner_ui: SecretScannerUI,
    ) -> Dict[Future, List[Scannable]]:
        """
        Start all scans, return a tuple containing:
        - a mapping of future to the list of files it is scanning
        - a list of files which we did not send to scan because we could not decode them
        """
        chunks_for_futures = {}

        chunk: List[Scannable] = []
        for scannable in scannables:
            try:
                if scannable.is_longer_than(DOCUMENT_SIZE_THRESHOLD_BYTES):
                    max_size_mb = DOCUMENT_SIZE_THRESHOLD_BYTES // 1024 // 1024
                    scanner_ui.on_skipped(
                        scannable, f"content is over {max_size_mb} MB"
                    )
                    continue
                content = scannable.content
            except DecodeError:
                scanner_ui.on_skipped(scannable, "can't detect encoding")
                continue

            if content:
                chunk.append(scannable)
                if len(chunk) == MULTI_DOCUMENT_LIMIT:
                    future = self._scan_chunk(executor, chunk)
                    chunks_for_futures[future] = chunk
                    chunk = []
            else:
                scanner_ui.on_skipped(scannable, "")
        if chunk:
            future = self._scan_chunk(executor, chunk)
            chunks_for_futures[future] = chunk
        return chunks_for_futures

    def _collect_results(
        self,
        scanner_ui: SecretScannerUI,
        chunks_for_futures: Dict[Future, List[Scannable]],
    ) -> Results:
        """
        Receive scans as they complete, report progress and collect them and return
        a Results.
        """
        self.cache.purge()

        results = []
        errors = []
        for future in concurrent.futures.as_completed(chunks_for_futures):
            chunk = chunks_for_futures[future]
            scanner_ui.on_scanned(chunk)

            exception = future.exception()
            if exception is None:
                scan = future.result()
            else:
                scan = Detail(detail=str(exception))
                errors.append(
                    Error(
                        files=[(x.filename, x.filemode) for x in chunk],
                        description=scan.detail,
                    )
                )

            if not scan.success:
                handle_scan_chunk_error(scan, chunk)
                continue

            for file, scanned in zip(chunk, scan.scan_results):
                remove_ignored_from_result(scanned, self.ignored_matches)
                remove_results_from_ignore_detectors(scanned, self.ignored_detectors)
                if scanned.has_policy_breaks:
                    for policy_break in scanned.policy_breaks:
                        self.cache.add_found_policy_break(policy_break, file.filename)
                    results.append(
                        Result(
                            file=file,
                            scan=scanned,
                        )
                    )

        self.cache.save()
        return Results(results=results, errors=errors)


def handle_scan_chunk_error(detail: Detail, chunk: List[Scannable]) -> None:
    # Use %s for status_code because it can be None. Logger is OK with an int being
    # passed for a %s placeholder.
    logger.error("status_code=%s detail=%s", detail.status_code, detail.detail)
    if detail.status_code == 401:
        raise click.UsageError(detail.detail)
    if detail.status_code is None:
        raise UnexpectedError(f"Error scanning: {detail.detail}")

    details = None

    display_error("\nError scanning. Results may be incomplete.")
    try:
        # try to load as list of dicts to get per file details
        details = literal_eval(detail.detail)
    except Exception:
        pass

    if isinstance(details, list) and details:
        # if the details had per file details
        display_error(
            f"Add the following {pluralize('file', len(details))}"
            " to your paths-ignore:"
        )
        for i, inner_detail in enumerate(details):
            if inner_detail:
                click.echo(
                    f"- {format_text(chunk[i].filename, STYLE['filename'])}:"
                    f" {str(inner_detail)}",
                    err=True,
                )
        return
    else:
        # if the details had a request error
        filenames = ", ".join([file.filename for file in chunk])
        display_error(
            "The following chunk is affected:\n"
            f"{format_text(filenames, STYLE['filename'])}"
        )

        display_error(str(detail))
