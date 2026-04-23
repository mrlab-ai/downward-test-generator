#! /usr/bin/env python3

import argparse
import json
import subprocess

from pathlib import Path


DIR = Path(__file__).resolve().parent
REPO = DIR.parent
DEFAULT_PROPERTIES = DIR / "data" / "2026-4-22-json-eval" / "properties"

IGNORED_RUN_KEYS = {
    "algorithm",
    "domain",
    "id",
    "memory_limit",
    "problem",
    "run_dir",
    "time_limit",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Lab properties output into lifted-planner test input JSON.",
    )
    parser.add_argument(
        "properties",
        nargs="?",
        default=str(DEFAULT_PROPERTIES),
        help="Path to the Lab properties JSON file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write the converted JSON. Defaults to test_input.json next to the properties file.",
    )
    return parser.parse_args()


def get_git_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "TBD"
    return result.stdout.strip() or "TBD"


def load_runs(properties_path: Path) -> dict:
    with properties_path.open() as properties_file:
        return json.load(properties_file)


def collect_value_keys(runs: dict) -> list:
    value_keys = set()
    for run in runs.values():
        for key in run:
            if key not in IGNORED_RUN_KEYS:
                value_keys.add(key)
    return sorted(value_keys)


def build_output(runs: dict) -> dict:
    if not runs:
        raise ValueError("Properties file does not contain any runs.")

    domains = {run["domain"] for run in runs.values()}
    if len(domains) != 1:
        raise ValueError(f"Expected exactly one domain, found: {sorted(domains)}")

    value_keys = collect_value_keys(runs)
    output = {
        "domain": next(iter(domains)),
        "fd_git_hash": get_git_hash(),
        "values": {},
    }

    sorted_runs = sorted(runs.values(), key=lambda run: run["problem"])
    for value_key in value_keys:
        output["values"][value_key] = [
            {
                "problem": run["problem"],
                "value": run[value_key],
            }
            for run in sorted_runs
            if value_key in run
        ]

    return output


def main() -> int:
    args = parse_args()
    properties_path = Path(args.properties)
    runs = load_runs(properties_path)
    output = build_output(runs)
    output_text = json.dumps(output, indent=4)

    output_path = Path(args.output) if args.output else properties_path.with_name("test_input.json")
    output_path.write_text(output_text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())