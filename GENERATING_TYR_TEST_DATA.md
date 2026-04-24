# Generating Tyr Test Data

This fork is used to generate benchmark-derived test input for the lifted planning system Tyr:
https://github.com/drexlerd/tyr

## Prerequisites

- Built Fast Downward binaries in this repository (for example under builds/release/bin)
- A local checkout of Tyr
- Python environment with the experiment dependencies

Set TYR_ROOT to your local Tyr checkout:

```bash
export TYR_ROOT=~/research/Tyr-lifted-pdb
```

The experiment script reads benchmarks from:

- $TYR_ROOT/data

## Workflow

### 1. Generate experiment output (properties)

Run the experiment script from the repository root:

```bash
python experiments/generate_systematic_pdb_test_data.py build start parse fetch
```

This creates experiment outputs under experiments/data/... including a properties file in the corresponding *-eval directory.

### 2. Convert properties into Tyr test input JSON

Convert the generated properties file into test_input.json:

```bash
python experiments/convert_to_test_input.py \
  experiments/data/2026-4-22-json-eval/properties \
  -o experiments/data/2026-4-22-json-eval/test_input.json
```

The resulting JSON is intended to be consumed as test input for Tyr.

## Notes

- The experiment script uses the TYR_ROOT environment variable, defaulting to ~/research/Tyr-lifted-pdb when unset.
- The converter preserves fd_git_hash and writes per-problem values for:
  - initial_projection_heuristic_estimates_sys_1
  - initial_projection_heuristic_estimates_sys_2
