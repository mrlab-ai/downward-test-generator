#! /usr/bin/env python3

import ast

from lab.parser import Parser

def parse_and_assign_ast_literal(assign_to, content, props):
    if assign_to in props:
        props[assign_to] = ast.literal_eval(props[assign_to])

class Sys1Parser(Parser):
    """
    sys_1_heuristic_estimates_initial_state: [1,2,3]
    """
    def __init__(self):
        super().__init__()
        
        # Parse the optional sys_1 heuristic metric
        self.add_pattern(
            "sys_1_heuristic_estimates_initial_state", 
            r"sys_1_heuristic_estimates_initial_state: (\[.*\])", 
            type=str
        )

        self.add_function(
            lambda content, props: parse_and_assign_ast_literal(
                "sys_1_heuristic_estimates_initial_state", content, props
            )
        )
        
        # Always capture run_dir as a fallback so properties file is never empty
        self.add_pattern(
            "captured_run_executed", 
            r".*", 
            type=str
        )
