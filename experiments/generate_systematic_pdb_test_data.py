#! /usr/bin/env python3

import platform
import re
import os
import sys

from pathlib import Path

from downward import suites
from downward.reports.absolute import AbsoluteReport
from lab.environments import TetralithEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute, geometric_mean
from systematic_pdb_parser import SystematicPDBParser


# Create custom report class with suitable info and error attributes.
class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]

DIR = Path(__file__).resolve().parent
REPO = DIR.parent
TYR_ROOT = Path(os.environ.get("TYR_ROOT", "~/research/Tyr-lifted-pdb")).expanduser()
BENCHMARKS_DIR = TYR_ROOT / "data"

if not BENCHMARKS_DIR.is_dir():
    raise FileNotFoundError(
        f"Could not find benchmark directory at {BENCHMARKS_DIR}. "
        "Set TYR_ROOT to your local Tyr repository path."
    )

NODE = platform.node()
REMOTE = re.match(r"tetralith\d+.nsc.liu.se|n\d+", NODE)
if REMOTE:
    ENV = TetralithEnvironment(
        setup=TetralithEnvironment.DEFAULT_SETUP,
        memory_per_cpu="8G",
        extra_options="#SBATCH --account=naiss2024-5-421")

    TIME_LIMIT = 5 * 60  # 5 minutes
else:
    ENV = LocalEnvironment(processes=12)
    TIME_LIMIT = 10

SUITE = sorted(
    path.name for path in BENCHMARKS_DIR.iterdir()
    if path.is_dir() and not path.name.startswith(".")
)
ATTRIBUTES = [
    "run_dir",
    "sys_1_heuristic_estimates_initial_state",
    "sys_2_heuristic_estimates_initial_state",
]

MEMORY_LIMIT = 8000

# Create a new experiment.
exp = Experiment(environment=ENV)
# Add parser for systematic PDB heuristic-estimate output lines.
exp.add_parser(SystematicPDBParser())


exp.add_resource("fast_downward_py", str(REPO / "fast-downward.py"))
exp.add_resource("driver", str(REPO / "driver"))
exp.add_resource("translator", str(REPO / "builds" / "release" / "bin" / "translate"), str(Path("builds") / "release" / "bin" / "translate"))
exp.add_resource("downward", str(REPO / "builds" / "release" / "bin" / "downward"), str(Path("builds") / "release" / "bin" / "downward"))

CONFIGS = {
    "sys-1": [
        "--translate-options", "--invariant-generation-max-time=0", "--search-options", "--search", "astar(cpdbs(systematic(1)), bound=1)",
    ],
    "sys-2": [
        "--translate-options", "--invariant-generation-max-time=0", "--search-options", "--search", "astar(cpdbs(systematic(2)), bound=1)",
    ],
}

for task in suites.build_suite(BENCHMARKS_DIR, SUITE):
    for config_name, CFG in CONFIGS.items():
        run = exp.add_run()
        run.add_resource("domain", task.domain_file, symlink=True)
        run.add_resource("problem", task.problem_file, symlink=True)
        # 'ff' binary has to be on the PATH.
        # We could also use exp.add_resource().
        run.add_command(
            "planner",
            [sys.executable, "{fast_downward_py}", task.domain_file, task.problem_file] + CFG,
            time_limit=TIME_LIMIT,
            memory_limit=MEMORY_LIMIT,
        )
        # AbsoluteReport needs the following properties:
        # 'domain', 'problem', 'algorithm', 'coverage'.
        run.set_property("domain", task.domain)
        run.set_property("problem", task.problem)
        run.set_property("algorithm", config_name)
        # BaseReport needs the following properties:
        # 'time_limit', 'memory_limit'.
        run.set_property("time_limit", TIME_LIMIT)
        run.set_property("memory_limit", MEMORY_LIMIT)
        # Every run has to have a unique id in the form of a list.
        # The algorithm name is only really needed when there are
        # multiple algorithms.
        run.set_property("id", [config_name, task.domain, task.problem])

# Add step that writes experiment files to disk.
exp.add_step("build", exp.build)

# Add step that executes all runs.
exp.add_step("start", exp.start_runs)

exp.add_step("parse", exp.parse)

# Add step that collects properties from run directories and
# writes them to *-eval/properties.
exp.add_fetcher(name="fetch")

# Make a report.
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="report.html")

# Parse the commandline and run the specified steps.
exp.run_steps()