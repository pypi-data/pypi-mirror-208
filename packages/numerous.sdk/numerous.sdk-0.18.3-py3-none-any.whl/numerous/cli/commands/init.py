import sys
from pathlib import Path
from typing import Optional

from ..repository import NumerousRepository
from ..utils import bold, green, print_repository_help_message, red


def command_init(path: Optional[Path]):
    path = path or Path.cwd()

    if (path / NumerousRepository.FILE_NAME).exists():
        try:
            repo = NumerousRepository(path).load()
            if repo.remote:
                error = f"Folder already a repository for {bold(repo.remote.name)}"
            else:
                error = "Folder already a repository without a configured remote"
            print(red(f"Cannot init: {error}"))
        except Exception:
            print(
                red(
                    "Cannot init: Folder already exists, but repository configuration is invalid"
                )
            )
        finally:
            sys.exit(1)

    path.mkdir(parents=True, exist_ok=True)

    if not (path / ".exclude").exists():
        src = Path(__file__).parent.parent / ".exclude"
        dst = path / ".exclude"
        dst.write_text(src.read_text())

    repo = NumerousRepository(path).save()

    abs_path = Path(path.name).absolute()
    print(green(f"Initialized new repository in {bold(abs_path)}"))
    print_repository_help_message(abs_path)
