from logging import Logger
from pathlib import Path
from typing import Any

from ..repository import NumerousRepository
from ..utils import bold, cyan, yellow


def command_config(log: Logger, path: Path, ns: Any):
    path = Path.cwd() if path is None else path
    repo = NumerousRepository(path).load()

    name = path.name if repo.remote is None else repo.remote.name

    if all(var is None for var in [ns.remote, ns.organization, ns.user, ns.snapshot]):
        print(cyan(f"Current configuration for {bold(name)}"))
        print(f"remote:       {bold(repo.remote or '')}")
        print(f"organization: {bold(repo.organization or '')}")
        print(f"user:         {bold(repo.user or '')}")
        print(f"snapshot:     {bold(repo.snapshot or '')}")
        print(f"scenario:     {bold(repo.scenario or '')}")
    else:
        print(cyan(f"Set configuration for {bold(name)}"))
        if ns.remote:
            print(f"remote       = {bold(ns.remote)}")
            repo.remote = ns.remote
        if ns.organization:
            print(f"organization = {bold(ns.organization)}")
            repo.organization = ns.organization
        if ns.user:
            print(f"user         = {bold(ns.user)}")
            repo.user = ns.user
        if ns.snapshot:
            print(f"snapshot     = {bold(ns.snapshot)}")
            repo.snapshot = ns.snapshot
        if ns.scenario:
            print(f"scenario     = {bold(ns.scenario)}")
            repo.scenario = ns.scenario
        if input(yellow("Save changes? (y/n) ")).strip().lower() == "y":  # nosec
            repo.save()
