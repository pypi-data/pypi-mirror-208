import logging
import sys
import tarfile
from fnmatch import fnmatch
from hashlib import sha256
from io import BytesIO
from os import linesep
from pathlib import Path, PurePosixPath
from typing import Any, Callable, ContextManager, Generator, Iterable, Optional
from urllib.parse import urlparse
from uuid import uuid4

import grpc
from colorama import Fore, Style
from colorama import init as init_colorama
from pathspec import PathSpec
from spm_pb2_grpc import TokenManagerStub

log = logging.getLogger("__name__")


init_colorama()


def red(msg: Any) -> str:
    return f"{Fore.RED}{msg}{Fore.RESET}"


def green(msg: Any) -> str:
    return f"{Fore.GREEN}{msg}{Fore.RESET}"


def cyan(msg: Any) -> str:
    return f"{Fore.CYAN}{msg}{Fore.RESET}"


def yellow(msg: Any) -> str:
    return f"{Fore.YELLOW}{msg}{Fore.RESET}"


def bold(msg: Any) -> str:
    return f"{Style.BRIGHT}{msg}{Style.NORMAL}"


def print_error_and_exit(msg: Any, exit_code: int = 1):
    print(red(msg))
    sys.exit(exit_code)


def print_repository_help_message(path: Path):
    print(
        f" ! {bold('Remember to change directory to the repository:')} {bold(cyan(f'cd {path}'))}"
    )
    print(f" * Connect a remote: {bold(cyan('numerous config --remote <REMOTE URL>'))}")
    print(
        f" * Checkout a scenario: {bold(cyan('numerous checkout --scenario <SCENARIO ID>'))}"
    )
    print(f" * Push changes: {bold(cyan('numerous push -c <COMMENT>'))}")
    print(f" * Build code and update scenario: {bold(cyan('numerous build'))}")


def get_grpc_channel(
    url: str, auth_plugin: Optional[grpc.AuthMetadataPlugin]
) -> grpc.Channel:
    parsed_url = urlparse(url)

    options = (
        ("grpc.keepalive_time_ms", 10000),
        ("grpc.keepalive_timeout_ms", 5000),
        ("grpc.keepalive_permit_without_calls", 1),
        ("grpc.http2_max_pings_without_data", 9999),
    )

    if parsed_url.scheme == "https":
        return grpc.secure_channel(
            f"{parsed_url.hostname}:{parsed_url.port or '443'}",
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(),
                grpc.metadata_call_credentials(auth_plugin),
            )
            if auth_plugin
            else grpc.ssl_channel_credentials(),
            options=options,
        )
    elif parsed_url.hostname == "localhost":
        log.debug("Getting local channel")
        return grpc.secure_channel(
            f"{parsed_url.hostname}:{parsed_url.port or '50056'}",
            credentials=grpc.local_channel_credentials(),
            options=options,
        )
    else:
        return grpc.insecure_channel(
            f"{parsed_url.hostname}:{parsed_url.port or '80'}", options=options
        )


class StubClient:
    def __init__(
        self,
        api_url: str,
        stub: Callable[[grpc.Channel], Any],
        plugin: Optional[grpc.AuthMetadataPlugin] = None,
    ):
        self.channel = get_grpc_channel(api_url, plugin)
        self.stub = stub(self.channel)

    def __enter__(self):
        return self.stub

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.channel.close()


def get_token_manager(api_url: str) -> ContextManager[TokenManagerStub]:
    return StubClient(api_url, TokenManagerStub)


class GzippedTarball:
    def __init__(self, source: Path, paths: Iterable[Path]):
        self.source = source
        self.files = list(path for path in paths if path.is_file())
        self.tar_path = source / f"{uuid4()}.tar.gz"

    def __enter__(self):
        with tarfile.open(str(self.tar_path), mode="w:gz") as tar:
            for file_path in self.files:
                info = tarfile.TarInfo(str(PurePosixPath(Path(file_path.name))))
                info.path = str(file_path.relative_to(self.source))
                info.size = file_path.stat().st_size
                with file_path.open("rb") as file:
                    tar.addfile(info, fileobj=file)
        return self.tar_path

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.tar_path.unlink()


def display_error_and_exit(
    error_header: str, help_lines: list[str], exit_code: int = 1
):
    print(red(error_header))
    print(*help_lines, sep=linesep)
    sys.exit(exit_code)


def extract_gzipped_tarball(file: BytesIO, path: Path) -> None:
    with tarfile.open(fileobj=file, mode="r:gz") as tar:
        tar.extractall(str(path))


def exclude_paths(
    root: Path,
    paths: Iterable[Path],
    exclude_patterns: list[str],
) -> Generator[Path, None, None]:
    spec = PathSpec.from_lines("gitwildmatch", exclude_patterns)
    for path in paths:
        relative_path = path.relative_to(root)
        exclude = spec.match_file(str(relative_path))
        if not exclude:
            yield path


def walk(directory: Path, include_pattern: str | None = None):
    yield from _walk(directory, directory, include_pattern)


def _walk(
    root: Path, directory: Path, include_pattern: str | None = None
) -> Generator[Path, None, None]:
    for path in directory.iterdir():
        relative_path = path.relative_to(root)
        if include_pattern and not fnmatch(str(relative_path), include_pattern):
            continue

        yield path
        if path.is_dir():
            yield from _walk(root, path, include_pattern)


def hash_directory(directory: Path) -> str:
    dirhash = sha256()
    for file_path in (path for path in walk(directory) if path.is_file()):
        dirhash.update(str(file_path.lstat().st_mtime).encode("utf-8"))
    return dirhash.hexdigest()
