import datetime as dt
import re
from tokenize import TokenError

from sympy.parsing.sympy_parser import convert_xor, parse_expr, standard_transformations

from .calc_tool_matches import date_and_time as dtm
from .calc_tool_matches import dictionary as dcm
from .calc_tool_matches import fields_and_values as fvm
from .calc_tool_matches import math as mtm
from .calc_tool_matches import string as stm


def _single_argument(function):
    def execute(*args, **kwargs):
        if (len(args) == 1 and not kwargs and isinstance(args[0], dt.timedelta)):
            return function(args[0])

        arguments = [str(value) for value in args]
        arguments.extend(f"{name}={value}" for name, value in kwargs.items())
        argument = ", ".join(arguments)
        return function(argument)

    return execute


class ExpressionParser:
    def __init__(self, expression: str):
        self.expression = expression
        self.expressionFunctions = []
        self.definedFunctions = {}

    def find_function_call(self):
        masked = re.sub(
            r"""('''|\"\"\"|'|")(?:\\.|(?!\1)[^\\])*\1""",
            lambda match: " " * len(match.group(0)),
            self.expression,
            flags=re.DOTALL,
        )

        for match in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", masked):
            start = match.end()
            depth = 1

            for i in range(start, len(masked)):
                if masked[i] == "(":
                    depth += 1
                elif masked[i] == ")":
                    depth -= 1

                if depth == 0:
                    self.expressionFunctions.append({
                        "name": match.group(1),
                        "arguments": self.expression[start:i],
                        "expression": self.expression[match.start():i + 1],
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
        local_dictionary = {}
        direct_functions = {
            "ascii",
            "concat",
            "regexp_match",
            "regexp_replace",
            "regexp_substr",
            "format_number",
            "length",
            "lower",
            "title",
            "upper",
            "ltrim",
            "trim",
            "map",
            "map_concat",
            "map_insert",
            "map_prefix_keys",
            "map_get",
            "map_delete",
            "map_exist",
            "map_akeys",
            "map_avals",
            "map_to_html_dl",
            "map_to_html_table",
            "to_json",
            "url_encode",
        }

        for func in self.expressionFunctions:
            name = func["name"]
            if name not in self.definedFunctions:
                raise ValueError(f"Unknown function: {name}")
    
        for name, function in self.definedFunctions.items():
            if name in direct_functions:
                local_dictionary[name] = function
            else:
                local_dictionary[name] = _single_argument(function)
        string_pattern = r"""('''|\"\"\"|'|")(?:\\.|(?!\1)[^\\])*\1"""

        expression = re.sub(
            rf"{string_pattern}|#[^\n]*|\s+",
            lambda match: match.group(0) if match.group(1) else " ",
            self.expression,
            flags=re.DOTALL,
        )
        try:
            parsed_expr = parse_expr(
                expression, 
                transformations=standard_transformations + (convert_xor,), #needs , after convert_xor
                local_dict=local_dictionary)
            return parsed_expr
        except (TokenError, SyntaxError, ValueError, TypeError) as e:
            print(f"Error parsing expression: {e}")
            raise ValueError(f"Error parsing expression: {e}")
