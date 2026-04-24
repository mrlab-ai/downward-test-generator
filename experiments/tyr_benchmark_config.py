#! /usr/bin/env python3

import os

from pathlib import Path


TYR_ROOT = Path(os.environ.get("TYR_ROOT", "~/research/Tyr-lifted-pdb")).expanduser()
BENCHMARKS_DIR = TYR_ROOT / "data"


def validate_benchmarks_dir() -> None:
    if not BENCHMARKS_DIR.is_dir():
        raise FileNotFoundError(
            f"Could not find benchmark directory at {BENCHMARKS_DIR}. "
            "Set TYR_ROOT to your local Tyr repository path."
        )


def get_suite() -> list:
    validate_benchmarks_dir()
    return sorted(
        path.name for path in BENCHMARKS_DIR.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


SUITE = get_suite()