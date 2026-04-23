#! /usr/bin/env python3

import ast

from lab.parser import Parser


HEURISTIC_KEYS = [
    "sys_1_heuristic_estimates_initial_state",
    "sys_2_heuristic_estimates_initial_state",
]


def parse_and_assign_ast_literal(assign_to, content, props):
    if assign_to in props:
        props[assign_to] = ast.literal_eval(props[assign_to])


class SystematicPDBParser(Parser):
    """
    sys_1_heuristic_estimates_initial_state: [1,2,3]
    sys_2_heuristic_estimates_initial_state: [1,2,3]
    """
    def __init__(self):
        super().__init__()

        self._add_heuristic_patterns(HEURISTIC_KEYS)
        self._add_heuristic_literal_parsers(HEURISTIC_KEYS)
        
        # Always capture run_dir as a fallback so properties file is never empty
        self.add_pattern(
            "captured_run_executed", 
            r".*", 
            type=str
        )

    def _add_heuristic_patterns(self, keys):
        for key in keys:
            self.add_pattern(
                key,
                rf"{key}: (\[.*\])",
                type=str,
            )

    def _add_heuristic_literal_parsers(self, keys):
        for key in keys:
            self.add_function(
                lambda content, props, key=key: parse_and_assign_ast_literal(
                    key, content, props
                )
            )
