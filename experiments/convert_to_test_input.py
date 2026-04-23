#! /usr/bin/env python3

import argparse
import json
import re
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
    "unexplained_errors",
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

    value_keys = collect_value_keys(runs)
    output = {
        "fd_git_hash": get_git_hash(),
        "domains": {},
    }

    # Group runs by domain
    domains_dict = {}
    for run in runs.values():
        domain = run["domain"]
        if domain not in domains_dict:
            domains_dict[domain] = []
        domains_dict[domain].append(run)

    # Build output for each domain
    for domain in sorted(domains_dict.keys()):
        domain_runs = sorted(domains_dict[domain], key=lambda run: run["problem"])
        domain_output = {"values": {}}
        
        for value_key in value_keys:
            domain_output["values"][value_key] = {
                run["problem"]: run.get(value_key, None)
                for run in domain_runs
            }
        
        output["domains"][domain] = domain_output

    return output


def main() -> int:
    args = parse_args()
    properties_path = Path(args.properties)
    runs = load_runs(properties_path)
    output = build_output(runs)
    output_text = json.dumps(output, indent=4)
    output_text = re.sub(r"\[(?:\n\s+\d+,?)+\n\s*\]", lambda match: "[" + ", ".join(re.findall(r"\d+", match.group(0))) + "]", output_text)

    output_path = Path(args.output) if args.output else properties_path.with_name("test_input.json")
    output_path.write_text(output_text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())