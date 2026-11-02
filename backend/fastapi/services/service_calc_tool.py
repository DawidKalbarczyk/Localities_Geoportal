import re
from tokenize import TokenError

from sympy import parse_expr

from .calc_tool_matches import date_and_time as dtm
from .calc_tool_matches import dictionary as dcm
from .calc_tool_matches import fields_and_values as fvm
from .calc_tool_matches import math as mtm
from .calc_tool_matches import string as stm


class ExpressionParser:
    def __init__(self, expression: str):
        self.expression = expression
        self.expressionFunctions = []
        self.definedFunctions = {}

    def find_function_call(self):
        for match in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", self.expression):
            start = match.end()
            depth = 1

            for i in range(start, len(self.expression)):
                if self.expression[i] == "(":
                    depth += 1
                elif self.expression[i] == ")":
                    depth -= 1

                if depth == 0:
                    self.expressionFunctions.append({
                        "name": match.group(1),
                        "arguments": self.expression[start:i],
                        "expression": self.expression[match.start():i + 1]
                    })
                    break
            else:
                raise ValueError(f"Unmatched parentheses in expression: {self.expression}")

# FUNCTIONS: 
# age, datetime_from_epoch, day, day_of_week, epoch, format_date, hour, make_date, make_datetime, make_interval, 
# make_time, minute, month, now, second, to_date, to_datetime, to_interval, to_time, week, year, abs, acos, asin, 
# atan, atan2, actg, actg2, ceil, clamp, sin, cos, tan, ctg, degrees, exp, floor, ln, log, log10, max, min, pi, pow, 
# radians, rand, randf, round, scale_exponential, scale_linear, scale_polynomial, scale_logarithmic, sqrt, from_json, 
# hstore_to_map, map, map_akeys, map_avals, map_concat, map_delete, map_exist, map_get, map_insert, map_prefix_keys, 
# map_to_hstore, map_to_html_dl, map_to_html_table, to_json, url_encode, ascii, char, concat, format, format_date, 
# format_number, left, length, lower, lpad, ltrim, regexp_match, regexp_replace, regexp_substr, replace, right, rpad, 
# rtrim, strpos, substr, title, to_string, trim, upper, wordwrap

# OPERATORS: AND, BETWEEN, ILIKE, IN, IS, IS NOT, LIKE, NOT, NOT BETWEEN, 
# OR, −, +, ×, ÷, ÷÷, [], %, ^, =, ≠, <, >, ≤, ≥, ||, ∼
    def writeFunctions(self):
        for func in self.expressionFunctions:
            match_functions = [dtm.date_and_time_match, fvm.fields_and_values_match, dcm.dictionary_match, stm.string_match, mtm.math_match]
            for m_func in match_functions:
                try:
                    result = m_func(func["name"])
                    if result is not None:
                        self.definedFunctions.update({func["name"]: result})
                        break
                except (ValueError, OSError, OverflowError) as exc:
                    print(f"Error defining function {func['name']}: {exc}") 
          
    def parse_expression(self):
        try:
            parsed_expr = parse_expr(self.expression)
            return parsed_expr
        except (TokenError, SyntaxError, ValueError, TypeError) as e:
            print(f"Error parsing expression: {e}")
            raise ValueError(f"Error parsing expression: {e}")
