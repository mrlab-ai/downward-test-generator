#! /usr/bin/env python3

import ast

from lab.parser import Parser

def parse_and_assign_ast_literal(assign_to, content, props):
    props[assign_to] = ast.literal_eval(props[assign_to])

class Sys1Parser(Parser):
    """
    sys_1_heuristic_estimates_initial_state: [1,2,3]
    """
    def __init__(self):
        super().__init__()
        
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
