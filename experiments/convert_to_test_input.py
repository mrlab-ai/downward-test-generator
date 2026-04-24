#! /usr/bin/env python3

import argparse
import json
import subprocess

from pathlib import Path

from downward import suites
from tyr_benchmark_config import BENCHMARKS_DIR, SUITE, validate_benchmarks_dir


DIR = Path(__file__).resolve().parent
REPO = DIR.parent
DEFAULT_PROPERTIES = DIR / "data" / "generate_systematic_pdb_test_data-eval" / "properties"

validate_benchmarks_dir()

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


def build_output(runs: dict) -> dict:
    if not runs:
        raise ValueError("Properties file does not contain any runs.")

    # Build task mapping from domain/problem names to file paths
    task_map = {}  # (domain_name, problem_name) -> (domain_file, problem_file)
    domain_files = {}  # domain_name -> domain_file
    
    for task in suites.build_suite(BENCHMARKS_DIR, SUITE):
        domain_files[task.domain] = str(task.domain_file)
        problem_name = Path(task.problem_file).stem + ".pddl"
        task_map[(task.domain, problem_name)] = (str(task.domain_file), str(task.problem_file))

    output = {
        "fd_git_hash": get_git_hash(),
    }

    # Group runs by (domain, problem) to merge sys_1 and sys_2 results
    problem_runs = {}  # (domain, problem) -> {"sys_1": run, "sys_2": run}
    for run in runs.values():
        domain = run["domain"]
        problem = run["problem"]
        algorithm = run["algorithm"]
        key = (domain, problem)
        
        if key not in problem_runs:
            problem_runs[key] = {}
        problem_runs[key][algorithm] = run

    # Group by domain
    domains_dict = {}
    for (domain, problem), algo_runs in problem_runs.items():
        if domain not in domains_dict:
            domains_dict[domain] = []
        domains_dict[domain].append((problem, algo_runs))

    # Build output for each domain
    for domain in sorted(domains_dict.keys()):
        problem_list = sorted(domains_dict[domain], key=lambda x: x[0])
        
        # Get domain file path
        domain_file = domain_files.get(domain)
        if not domain_file:
            raise ValueError(f"Domain '{domain}' not found in task suite")
        
        # Build instances array
        instances = []
        for problem, algo_runs in problem_list:
            key = (domain, problem)
            
            if key not in task_map:
                raise ValueError(f"Task ({domain}, {problem}) not found in task suite")
            
            domain_file_path, problem_file_path = task_map[key]
            
            # Extract heuristic estimates from sys_1 and sys_2 runs
            sys_1_run = algo_runs.get("sys-1")
            sys_2_run = algo_runs.get("sys-2")
            
            instance = {
                "path": problem_file_path,
                "initial_projection_heuristic_estimates_sys_1": sys_1_run.get("sys_1_heuristic_estimates_initial_state") if sys_1_run else None,
                "initial_projection_heuristic_estimates_sys_2": sys_2_run.get("sys_2_heuristic_estimates_initial_state") if sys_2_run else None,
            }
            instances.append(instance)
        
        output[domain] = {
            "domain": domain_file,
            "instances": instances,
        }

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