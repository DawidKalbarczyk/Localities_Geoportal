from sympy import parse_expr

import re
import math as m
import random as r
import datetime as dt

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
        def match_time_format(tmp_arg, arg):
            seconds_per_unit = {
                "year": 1 * 365.25 * 24 * 60 * 60,
                "month": 1 * 365.25 * 24 * 60 * 60 / 12,
                "week": 1 * 7 * 24 * 60 * 60,
                "day": 1 * 24 * 60 * 60,
                "hour": 1 * 60 * 60,
                "minute": 1 * 60,
                "second": 1
            } 
            if isinstance(arg, dt.timedelta):
                new_arg = arg.total_seconds()
                result = new_arg / seconds_per_unit[tmp_arg]
                if result.is_integer():
                    result = int(result)
                return f"{result} {tmp_arg}{'' if result == 1 else 's'}"
            if ((re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{1,6})?", arg) and tmp_arg == "week")
            or (re.fullmatch(r"\d{4}-\d{2}-\d{2}", arg) and tmp_arg == "week")):
                date = dt.datetime.fromisoformat(arg)
                week = date.isocalendar().week
                return f"{week} {tmp_arg}{'' if week == 1 else 's'}"
            if ((re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{1,6})?", arg))
            or (re.fullmatch(r"\d{4}-\d{2}-\d{2}", arg) and tmp_arg not in ["hour", "minute", "second"])):
                calc = getattr(dt.datetime.fromisoformat(arg), tmp_arg)
                return f"{calc} {tmp_arg}{'' if calc == 1 else 's'}"
            
            elif (re.fullmatch(r"-?\d+(?:\.\d+)? (?:years?|months?|weeks?|days?|hours?|minutes?|seconds?)", arg)
            or re.fullmatch(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)? (?:years?|months?|weeks?|days?|hours?|minutes?|seconds?)", arg)):
                value, unit = arg.split(" ")
                if (float(value) < 0):
                    raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD HH:MM:SS")    
                
                result = float(value) * float(seconds_per_unit[unit.rstrip("s")])
                result /= float(seconds_per_unit[tmp_arg])
                if result.is_integer():
                    result = int(result)
                return f"{result} {tmp_arg}{'' if result == 1 else 's'}"
            else:
                raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD HH:MM:SS or an interval in the format <value> <unit>")
        for func in self.expressionFunctions:
            try:
                match func["name"]:
                    # DATE AND TIME FUNCTIONS
                    case "age":
                        def _age(arg):
                            #format age(2026-10-30T13:00:00, 2026-10-29T10:00:00)
                            def _age(arg):
    # Przykład: age(2026-10-30T13:00:00, 2026-10-29T10:00:00)
                                later_date, earlier_date = map(str.strip, arg.split(","))
                                pattern = r"\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}(?:\.\d{1,6})?)?"
                                if not all(
                                    re.fullmatch(pattern, value)
                                    for value in (later_date, earlier_date)
                                ):
                                    raise ValueError(
                                        f"Invalid date format: {arg}. "
                                        "Expected YYYY-MM-DD or YYYY-MM-DD HH:MM:SS "
                                        "(space or T separator; optional fractional seconds)."
                                    )

                                start = dt.datetime.fromisoformat(earlier_date)
                                end = dt.datetime.fromisoformat(later_date)

                                if end < start:
                                    raise ValueError(
                                        "The first date must not be earlier than the second date."
                                    )

                                return end - start
                            # datetime.timedelta - datetime.timedelta(days=1, seconds=10800)
                        self.definedFunctions.update({"age": _age})
                    case "datetime_from_epoch":
                        def _datetime_from_epoch(arg):
                            #format datetime_from_epoch(1700000000)
                            epoch_time = 0
                            if arg.isinteger() and int(arg) >= 0:
                                epoch_time = int(arg)
                            else:
                                raise ValueError(f"Invalid epoch time: {arg}. Expected a non-negative integer.")
                            return dt.datetime.fromtimestamp(epoch_time).isoformat(sep=" ")
                            # str - "2023-11-14 23:13:20"
                        self.definedFunctions.update({"datetime_from_epoch": _datetime_from_epoch})
                    case "day_of_week":
                        def _day_of_week(arg):
                            #format day_of_week(2026-10-30)
                            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", arg):
                                raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD")
                            
                            date = dt.datetime.fromisoformat(arg)
                            return (date.weekday() + 1)
                            # int - 4
                        self.definedFunctions.update({"day_of_week": _day_of_week})
                    case "epoch":
                        def _epoch(arg):
                            #format epoch(2026-10-30 13:00:00)
                            if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", arg):
                                raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD HH:MM:SS")
                            to_date = dt.datetime.fromisoformat(arg)
                            return int(to_date.timestamp())
                            # int - 1793365200
                        self.definedFunctions.update({"epoch": _epoch})
                    case "format_date":
                        def _format_date(arg):
                            #format format_date(2026-10-30, dd.MM.yyyy)
                            # Language support can be added here for month if needed
                            date_str, format_str = map(str.strip, arg.split(","))
                            date_y, date_m, date_d = map(str, date_str.split("-"))
                            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
                                raise ValueError(f"Invalid date format: {date_str}. Expected a valid date in the format YYYY-MM-DD")
                            
                            date_obj = [date_y, date_m, date_d]
                            #Checks and reports ValueError if the date is invalid or the format is invalid
                            date = dt.date(int(date_y), int(date_m), int(date_d))
                            #############################
                            format_x, format_y, format_z = map(str.strip, format_str.split("."))

                            proper_format = ["d", "dd", "ddd", "dddd", "M", "MM", "MMM", "MMMM", "yy", "yyyy"]
                            if format_x not in proper_format or format_y not in proper_format or format_z not in proper_format:
                                raise ValueError(f"Invalid format: {format_str}")
                            
                            def getRightFormat():
                                fmt = ".".join([format_x, format_y, format_z])
                                if (re.fullmatch("d{1,4}\\.M{1,4}\\.(yy|yyyy)", fmt)):
                                    return ["2", "1", "0"]
                                    # list[str] - ["2", "1", "0"]
                                elif (re.fullmatch("M{1,4}\\.d{1,4}\\.(yy|yyyy)", fmt)):
                                    return ["1", "2", "0"]
                                    # list[str] - ["1", "2", "0"]
                                elif (re.fullmatch("(yy|yyyy)\\.M{1,4}\\.d{1,4}", fmt)):
                                    return ["0", "1", "2"]
                                    # list[str] - ["0", "1", "2"]
                                elif (re.fullmatch("d{1,4}\\.(yy|yyyy)\\.M{1,4}", fmt)):
                                    return ["2", "0", "1"]
                                    # list[str] - ["2", "0", "1"]
                                elif (re.fullmatch("M{1,4}\\.(yy|yyyy)\\.d{1,4}", fmt)):
                                    return ["1", "0", "2"]
                                    # list[str] - ["1", "0", "2"]
                                elif (re.fullmatch("(yy|yyyy)\\.d{1,4}\\.M{1,4}", fmt)):
                                    return ["0", "2", "1"]
                                    # list[str] - ["0", "2", "1"]
                                else:
                                    raise ValueError(f"Invalid format: {format_str}")
                                
                            
                            new_format = []
                            for tempIdx, fmt in zip(getRightFormat(), [format_x, format_y, format_z]):
                                tempIdx = int(tempIdx)
                                match (fmt):
                                    case 'd':
                                        new_format.append(f"{(date_obj[tempIdx]).lstrip('0')}")
                                    case 'dd':
                                        new_format.append(f"{(date_obj[tempIdx]).zfill(2)}")
                                    case 'ddd':
                                        weekdayList = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                                        date = dt.datetime.fromisoformat("-".join(date_obj))
                                        new_format.append(f"{weekdayList[date.weekday()]}")
                                    case 'dddd':
                                        weekdayList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                                        date = dt.datetime.fromisoformat("-".join(date_obj))
                                        new_format.append(f"{weekdayList[date.weekday()]}")
                                    case 'M':
                                        new_format.append(f"{(date_obj[tempIdx]).lstrip('0')}")
                                    case 'MM':
                                        new_format.append(f"{(date_obj[tempIdx]).zfill(2)}")
                                    case 'MMM':
                                        monthList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                                        new_format.append(f"{monthList[int(date_obj[tempIdx]) - 1]}")
                                    case 'MMMM':
                                        monthList = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                                        new_format.append(f"{monthList[int(date_obj[tempIdx]) - 1]}")
                                    case 'yy':
                                        new_format.append(f"{str(date_obj[tempIdx])[-2:]}")
                                    case 'yyyy':
                                        new_format.append(f"{str(date_obj[tempIdx])}")

                            fmt = ". ".join([format_x, format_y, format_z])
                            final_date = ""
                            if ("MMM" in fmt or "MMMM" in fmt):
                                final_date = " ".join(new_format)
                            else:
                                final_date = ".".join(new_format)
                            return final_date
                            # str - "30.10.2026"
                        self.definedFunctions.update({"format_date": _format_date})
                    case "format_time":
                        def _format_time(arg):
                            #format format_time(13:05:09, HH:mm:ss)
                            #Function represents time in 12 hour format for h | hh and 24 hour format for H | HH
                            time_str, format_str = map(str.strip, arg.split(","))
                            time = list(map(int, time_str.split(":")))
                            if not re.fullmatch(r"\d{1,2}:\d{1,2}:\d{1,2}", time_str):
                                raise ValueError(f"Invalid time format: {time_str}. Expected a valid time in the format HH:MM:SS")
                            
                            if len(time) not in (2, 3):
                                raise ValueError(f"Invalid time: {time_str}")
                            # Validate time and raise ValueError if invalid
                            dt.time(*time)
                            ###############################

                            proper_format = ["h", "hh", "H", "HH", "m", "mm", "s", "ss"]
                            for fmt in format_str.split(":"):
                                if fmt not in proper_format:
                                    raise ValueError(f"Invalid format: {format_str}")
                                
                            def getRightFormat():
                                fmt = format_str
                                if (re.fullmatch("(h|hh|H|HH)\\:(m|mm)\\:(s|ss)", fmt)):
                                    return ["0", "1", "2"]
                                    # list[str] - ["0", "1", "2"]
                                elif (re.fullmatch("(h|hh|H|HH)\\:(s|ss)\\:(m|mm)", fmt)):
                                    return ["0", "2", "1"]
                                    # list[str] - ["0", "2", "1"]
                                elif (re.fullmatch("(m|mm)\\:(h|hh|H|HH)\\:(s|ss)", fmt)):
                                    return ["1", "0", "2"]
                                    # list[str] - ["1", "0", "2"]
                                elif (re.fullmatch("(m|mm)\\:(s|ss)\\:(h|hh|H|HH)", fmt)):
                                    return ["1", "2", "0"]
                                    # list[str] - ["1", "2", "0"]
                                elif (re.fullmatch("(s|ss)\\:(h|hh|H|HH)\\:(m|mm)", fmt)):
                                    return ["2", "0", "1"]
                                    # list[str] - ["2", "0", "1"]
                                elif (re.fullmatch("(s|ss)\\:(m|mm)\\:(h|hh|H|HH)", fmt)):
                                    return ["2", "1", "0"]
                                    # list[str] - ["2", "1", "0"]
                                elif (re.fullmatch("(h|hh|H|HH)\\:(m|mm)", fmt)):
                                    return ["0", "1"]
                                    # list[str] - ["0", "1"]
                                elif (re.fullmatch("(h|hh|H|HH)\\:(s|ss)", fmt)):
                                    return ["0", "2"]
                                    # list[str] - ["0", "2"]
                                elif (re.fullmatch("(m|mm)\\:(h|hh|H|HH)", fmt)):
                                    return ["1", "0"]
                                    # list[str] - ["1", "0"]
                                elif (re.fullmatch("(m|mm)\\:(s|ss)", fmt)):
                                    return ["1", "2"]
                                    # list[str] - ["1", "2"]
                                elif (re.fullmatch("(s|ss)\\:(h|hh|H|HH)", fmt)):
                                    return ["2", "0"]
                                    # list[str] - ["2", "0"]
                                elif (re.fullmatch("(s|ss)\\:(m|mm)", fmt)):
                                    return ["2", "1"]
                                    # list[str] - ["2", "1"]
                                else:
                                    raise ValueError(f"Invalid format: {format_str}")
                                
                            new_format = []
                            for tempIdx, fmt in zip(getRightFormat(), format_str.split(":")):
                                tempIdx = int(tempIdx)
                                match (fmt):
                                    case 'h':
                                        new_format.append(f"{str(time[tempIdx] % 12 or 12).lstrip('0')}")
                                    case 'hh':
                                        new_format.append(f"{str(time[tempIdx] % 12 or 12).zfill(2)}")
                                    case 'H':
                                        new_format.append(f"{str(time[tempIdx]).lstrip('0') if time[tempIdx] != 0 else '0'}")
                                    case 'HH':
                                        new_format.append(f"{str(time[tempIdx]).zfill(2)}")
                                    case 'm':
                                        new_format.append(f"{str(time[tempIdx]).lstrip('0') if int(time[tempIdx]) != 0 else '0'}")
                                    case 'mm':
                                        new_format.append(f"{str(time[tempIdx]).zfill(2)}")
                                    case 's':
                                        new_format.append(f"{str(time[tempIdx]).lstrip('0') if int(time[tempIdx]) != 0 else '0'}")
                                    case 'ss':
                                        new_format.append(f"{str(time[tempIdx]).zfill(2)}")
                            fmt = ":".join(format_str.split(":"))
                            final_time = ""
                            if ("h" in fmt or "hh" in fmt):
                                new_format.append("AM" if time[0] < 12 else "PM")
                                new_format_time = ":".join(new_format[:-1])
                                new_format_display = new_format[-1]
                                final_time = f"{new_format_time} {new_format_display}"
                            else:
                                final_time = ":".join(new_format)
                            return final_time
                            # str - "13:05:09"
                        self.definedFunctions.update({"format_time": _format_time})
                    case "make_date":
                        def _make_date(arg):
                            #format make_date(2026, 10, 30)
                            if not re.fullmatch(r"\d{4},\s*\d{1,2},\s*\d{1,2}", arg):
                                raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY, MM, DD")
                            year, month, day = map(int, arg.split(","))
                            return f"{year}-{month:02d}-{day:02d}"
                            # str - "2026-10-30"
                        self.definedFunctions.update({"make_date": _make_date})
                    case "to_date":
                        def _to_date(arg):
                            pass
                        self.definedFunctions.update({"to_date": _to_date})
                    case "make_datetime":
                        def _make_datetime(arg):
                            #format make_datetime(2026, 10, 30, 13, 5, 9)
                            if not re.fullmatch(r"\d{4},\s*\d{1,2},\s*\d{1,2},\s*\d{1,2},\s*\d{1,2},\s*\d{1,2}", arg):
                                raise ValueError(f"Invalid datetime format: {arg}. Expected a valid datetime in the format YYYY, MM, DD, HH, MM, SS")
                            year, month, day, hour, minute, second = map(int, arg.split(","))
                            return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
                            # str - "2026-10-30 13:05:09"
                        self.definedFunctions.update({"make_datetime": _make_datetime})
                    case "to_datetime":
                        def _to_datetime(arg):
                            pass
                        self.definedFunctions.update({"to_datetime": _to_datetime})
                    case "make_interval":
                        def _make_interval(arg):
                            #format make_interval(days=2, hours=3 etc)
                            params = arg.split(",")
                            param_keys = ["years", "months", "weeks","days", "hours", "minutes", "seconds"]
                            arguments_dict = {}
                            for p in params:
                                if float(p.split("=")[1]) < 0:
                                    raise ValueError(f"Invalid parameter value: {p.split('=')[1]}. Expected a non-negative integer.")
                                if "=" not in p:
                                    raise ValueError(f"Invalid parameter format: {p}. Expected format: key=value")
                                p_key, item_value = p.split("=", 1)
                                p_key = p_key.strip()
                                if p_key not in param_keys:
                                    raise ValueError(f"Invalid parameter key: {p_key}. Expected one of: {param_keys}")
                                arguments_dict[p_key] = float(item_value.strip())
                            result = 0.0
                            biggest_unit = None
                            seconds_per_unit = {
                                "years": 365.25 * 86400,
                                "months": 365.25 * 86400 / 12,
                                "weeks": 7 * 86400,
                                "days": 86400,
                                "hours": 3600,
                                "minutes": 60,
                                "seconds": 1,
                            }
                            for item_key, item_value in arguments_dict.items():
                                if biggest_unit is None or param_keys.index(item_key) < param_keys.index(biggest_unit):
                                    biggest_unit = item_key

                            for item_key, item_value in arguments_dict.items():
                                result += item_value * seconds_per_unit[item_key]
                            for item_key, item_value in arguments_dict.items():
                                if (item_value < 1 and item_key == biggest_unit and 
                                biggest_unit != "seconds" and abs(result) < seconds_per_unit[biggest_unit]):
                                    biggest_unit = param_keys[param_keys.index(biggest_unit) + 1]
                            result /= seconds_per_unit[biggest_unit]
                            if result.is_integer():
                                result = int(result)   
                            return f"{result} {biggest_unit}"
                            # str - "2.125 days", "6.5 months"
                        self.definedFunctions.update({"make_interval": _make_interval})
                    case "to_interval":
                        def _to_interval(arg):
                            #format make_interval(days=2, hours=3 etc)
                            input_params = arg.split(" ")
                            tmp_param = []
                            params = []
                            if not input_params or len(input_params) % 2 != 0:
                                raise ValueError(f"Invalid parameter format: {arg}. Expected format: value unit [value unit ...]")
                            
                            for i_p in input_params:
                                tmp_param.append(i_p)
                                if len(tmp_param) == 2:
                                    params.append(" ".join(tmp_param))
                                    tmp_param = []

                            param_keys = ["years", "months", "weeks","days", "hours", "minutes", "seconds"]
                            arguments_dict = {}
                            for p in params:
                                if float(p.split(" ")[0]) < 0:
                                    raise ValueError(f"Invalid parameter value: {p.split(' ')[0]}. Expected a non-negative integer.")
                                if " " not in p:
                                    raise ValueError(f"Invalid parameter format: {p}. Expected format: key=value")
                                if p.split(" ")[1] not in param_keys:
                                    raise ValueError(f"Invalid parameter key: {p.split(' ')[1]}. Expected one of: {param_keys}")
                                for p_key in param_keys:
                                    if p.split(" ")[1] == p_key:
                                        arguments_dict[p_key] = float(p.split(" ")[0])
                            result = 0.0
                            biggest_unit = None
                            seconds_per_unit = {
                                "years": 365.25 * 86400,
                                "months": 365.25 * 86400 / 12,
                                "weeks": 7 * 86400,
                                "days": 86400,
                                "hours": 3600,
                                "minutes": 60,
                                "seconds": 1,
                            }
                            for item_key, item_value in arguments_dict.items():
                                if biggest_unit is None or param_keys.index(item_key) < param_keys.index(biggest_unit):
                                    biggest_unit = item_key

                            for item_key, item_value in arguments_dict.items():
                                result += item_value * seconds_per_unit[item_key]
                            for item_key, item_value in arguments_dict.items():
                                if (item_value < 1 and item_key == biggest_unit and 
                                biggest_unit != "seconds" and abs(result) < seconds_per_unit[biggest_unit]):
                                    biggest_unit = param_keys[param_keys.index(biggest_unit) + 1]
                            result /= seconds_per_unit[biggest_unit]
                            if result.is_integer():
                                result = int(result)
                            return f"{result} {biggest_unit}"
                            # str - "3.375 days", "15.0 minutes"
                        self.definedFunctions.update({"to_interval": _to_interval})
                    case "year":
                        def _year(arg):
                            years = match_time_format("year", arg)
                            return years
                        self.definedFunctions.update({"year": _year})
                    case "month":
                        def _month(arg):
                            months = match_time_format("month", arg)
                            return months
                        self.definedFunctions.update({"month": _month})
                    case "week":
                        def _week(arg):
                            weeks = match_time_format("week", arg)
                            return weeks
                        self.definedFunctions.update({"week": _week})
                    case "day":
                        def _day(arg):
                            #format day(2026-10-30)
                            days = match_time_format("day", arg)
                            # int - 30
                            return days
                        self.definedFunctions.update({"day": _day})
                    case "hour":
                        def _hour(arg):
                            #format hour(2026-10-30 13:05:09)
                            hours = match_time_format("hour", arg)
                            return hours
                            # int - 51 for "2.125 days"
                        self.definedFunctions.update({"hour": _hour})
                    case "minute":
                        def _minute(arg):
                            minutes = match_time_format("minute", arg)
                            return minutes
                        self.definedFunctions.update({"minute": _minute})
                    case "second":
                        def _second(arg):
                            seconds = match_time_format("second", arg)
                            return seconds
                        self.definedFunctions.update({"second": _second})
                    case "make_time":
                        def _make_time(arg):
                            h, m, tmp_s = map(str.strip, arg.split(","))
                            if not re.fullmatch(r"\d{1,2},\s*\d{1,2},\s*\d{1,2}(?:\.\d+)?", arg):
                                raise ValueError(f"Invalid time format: {arg}. Expected a valid time in the format HH, MM, SS")
                            h, m = int(h), int(m)
                            if "." in str(tmp_s):
                                seconds, fraction = tmp_s.split(".")
                                s = int(seconds)
                                ms = int(fraction[:3].ljust(3, '0'))  # Convert to milliseconds
                            else:
                                s = int(tmp_s)
                                ms = 0
                            if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
                                raise ValueError(f"Invalid time values: {arg}. Expected hours (0-23), minutes (0-59), seconds (0-59)")
                            return dt.time(int(h), int(m), s, ms * 1000).isoformat(timespec="milliseconds")
                        self.definedFunctions.update({"make_time": _make_time})
                    case "to_time":
                        def _to_time(arg):
                            # minimum HH:MM
                            p_time, p_format = map(str.strip, arg.split(","))
                            # add regex
                            if not re.fullmatch(r"\d{1,2}:\d{1,2}(?::\d{1,2})?", p_time):
                                raise ValueError(f"Invalid time format: {p_time}. Expected a valid time in the format HH:MM or HH:MM:SS")
                            if not re.fullmatch(r"(?:H{1,2}|h{1,2}|m{1,2}|M{1,2}|s{1,2}|S{1,2})(?::(?:H{1,2}|h{1,2}|m{1,2}|M{1,2}|s{1,2}|S{1,2})){1,2}", p_format):
                                raise ValueError(f"Invalid time format: {p_format}. Expected a valid time format in the format HH:MM or HH:MM:SS")
                            time, format = p_time.strip().split(":"), p_format.strip().split(":")
                            pairs = {}
                            for t, f in zip(time, format):
                                pairs[f] = t
                            output_list = []
                            for p_format, p_time in pairs.items():
                                output_list.append(f"{p_time.zfill(2)}")
                            output_time = ":".join(output_list)
                            final_time = dt.datetime
                            if len(output_list) < 3:
                                final_time = dt.datetime.strptime(output_time, f"%{format[0]}:%{format[1]}")
                            else:
                                final_time = dt.datetime.strptime(output_time, f"%{format[0]}:%{format[1]}:%{format[2]}")
                            return final_time.time()
                        self.definedFunctions.update({"to_time": _to_time})
                    case "now":
                        def _now(arg):
                            if arg == "":
                                return dt.datetime.now().isoformat(sep=" ")
                            else:
                                raise ValueError(f"Invalid parameter format: {arg}. Expected no parameters for now()")
                        self.definedFunctions.update({"now": _now})
                           
                                    #### make_interval i to_interval mają bazować na prostych obliczeniach
                                    #### po prosut patrzymy czy poniżej czy powyżej 1 i wtedy
                                    # dodajemy do ogólnego wyniku. CZyli po prostu lista z parametrami i argumentami użytkownika
                                    # a potem pętla for z caseami po tym.
                                    #tutaj nie robić tak samo funkcji tylko dwie logiki zaimplementować bo inputy są różne
                                    # make_interval ma (days=2, hours=3) a to_interval ma (2 days 3 hours) itd.
                                    # POTEM hour, minute itd muszą obsługiwać po prostu typ interval czyli np 1.0008 days
                                    # i patrzeć na hierarchie. Czyli gdy jest days(to_interval(3 weeks 1 day)) to wszystko sprowadza do dni poprzez obliczenia i tyle
                                    # interval musi łapać weeks też.

                                    # do 
service


                    # FIELDS AND VALUES FUNCTIONS
                    # DICTIONARY FUNCTIONS
                    # MATH FUNCTIONS
                    case "abs":
                        def _abs(arg):
                            #format abs(-3.5)
                            return abs(float(arg))
                            # float - 3.5
                        self.definedFunctions.update({"abs": _abs})
                    case "acos":
                        def _acos(arg):
                            #format acos(0.5)
                            return m.acos(float(arg))
                            # float - 1.0471975511965979
                        self.definedFunctions.update({"acos": _acos})
                    case "asin":
                        def _asin(arg):
                            #format asin(0.5)
                            return m.asin(float(arg))
                            # float - 0.5235987755982989
                        self.definedFunctions.update({"asin": _asin})
                    case "atan":
                        def _atan(arg):
                            #format atan(1)
                            return m.atan(float(arg))
                            # float - 0.7853981633974483
                        self.definedFunctions.update({"atan": _atan})
                    case "atan2":
                        def _atan2(arg):
                            #format atan2(1, 2)
                            y, x = map(float, arg.split(","))
                            return m.atan2(float(y), float(x))
                            # float - 0.4636476090008061
                        self.definedFunctions.update({"atan2": _atan2})
                    case "actg":
                        def _actg(arg):
                            #format actg(1)
                            return m.atan(1 / float(arg))
                            # float - 0.7853981633974483
                        self.definedFunctions.update({"actg": _actg})
                    case "actg2":
                        def _actg2(arg):
                            #format actg2(1, 2)
                            y, x = map(float, arg.split(","))
                            return m.atan2(1 / float(y), float(x))
                            # float - 0.4636476090008061
                        self.definedFunctions.update({"actg2": _actg2})
                    case "ceil":
                        def _ceil(arg):
                            #format ceil(2.3)
                            return m.ceil(float(arg))
                            # int - 3
                        self.definedFunctions.update({"ceil": _ceil})
                    case "clamp":
                        def _clamp(arg):
                            #format clamp(0, 5, 10)
                            min_value, value, max_value = map(float, arg.split(","))
                            return min(max_value, max(min_value, value))
                            # float - 5.0
                        self.definedFunctions.update({"clamp": _clamp})
                    case "sin":
                        def _sin(arg):
                            #format sin(1.57)
                            return m.sin(float(arg))
                            # float - 0.9999996829318346
                        self.definedFunctions.update({"sin": _sin})
                    case "cos":
                        def _cos(arg):
                            #format cos(1.57)
                            return m.cos(float(arg))
                            # float - 0.0007963267107332633
                        self.definedFunctions.update({"cos": _cos})
                    case "tan":
                        def _tan(arg):
                            #format tan(0.785)
                            return m.tan(float(arg))
                            # float - 0.9992039901050427
                        self.definedFunctions.update({"tan": _tan})
                    case "ctg":
                        def _ctg(arg):
                            #format ctg(0.785)
                            return 1 / m.tan(float(arg))
                            # float - 1.000796644031489
                        self.definedFunctions.update({"ctg": _ctg})
                    case "degrees":
                        def _degrees(arg):
                            #format degrees(3.14)
                            return (arg * 180) / m.pi
                            # float - 179.9087476710785
                        self.definedFunctions.update({"degrees": _degrees})
                    case "radians":
                        def _radians(arg):
                            #format radians(180)
                            return (arg * m.pi) / 180
                            # float - 3.141592653589793
                        self.definedFunctions.update({"radians": _radians})
                    case "exp":
                        def _exp(arg):
                            #format exp(2)
                            return m.exp(float(arg))
                            # float - 7.38905609893065
                        self.definedFunctions.update({"exp": _exp})
                    case "floor":
                        def _floor(arg):
                            #format floor(2.9)
                            return m.floor(float(arg))
                            # int - 2
                        self.definedFunctions.update({"floor": _floor})
                    case "ln":
                        def _ln(arg):
                            #format ln(2)
                            return m.log(float(arg))
                            # float - 0.6931471805599453
                        self.definedFunctions.update({"ln": _ln})
                    case "log":
                        def _log(arg):
                            #format log(2, 8)
                            base, value = map(float, arg.split(","))
                            return m.log(value, base)
                            # float - 3.0
                        self.definedFunctions.update({"log": _log})
                    case "log10":
                        def _log10(arg):
                            #format log10(100)
                            return m.log10(float(arg))
                            # float - 2.0
                        self.definedFunctions.update({"log10": _log10})
                    case "max":
                        def _max(arg):
                            #format max(1, 2, 3)
                            return max(map(float, arg.split(",")))
                            # float - 3.0
                        self.definedFunctions.update({"max": _max})
                    case "min":
                        def _min(arg):
                            #format min(1, 2, 3)
                            return min(map(float, arg.split(",")))
                            # float - 1.0
                        self.definedFunctions.update({"min": _min})
                    case "pi":
                        def _pi(arg):
                            #format pi()
                            return m.pi
                            # float - 3.141592653589793
                        self.definedFunctions.update({"pi": _pi})
                    case "pow":
                        def _pow(arg):
                            #format pow(2, 3)
                            base, exponent = map(float, arg.split(","))
                            return m.pow(base, exponent)
                            # float - 8.0
                        self.definedFunctions.update({"pow": _pow})
                    case "rand":
                        def _rand(arg):
                            #format rand(1, 10)
                            randomItems = list(map(int, arg.split(",")))
                            if len(randomItems) == 2:
                                return r.randint(randomItems[0], randomItems[1])
                                # int - 7
                            elif len(randomItems) == 3:
                                return r.Random(randomItems[2]).randint(randomItems[0], randomItems[1])
                                # int - 7
                        self.definedFunctions.update({"rand": _rand})
                    case "randf":
                        def _randf(arg):
                            #format randf(0, 1)
                            randomItems = list(map(float, arg.split(",")))
                            if len(randomItems) == 2:
                                return r.uniform(randomItems[0], randomItems[1])
                                # float - 0.42
                            elif len(randomItems) == 3:
                                return r.Random(randomItems[2]).uniform(randomItems[0], randomItems[1])
                                # float - 0.42
                        self.definedFunctions.update({"randf": _randf})
                    case "round":
                        def _round(arg):
                            #format round(3.14159, 2)
                            value, ndigits = map(float, arg.split(","))
                            return round(value, int(ndigits))
                            # float - 3.14
                        self.definedFunctions.update({"round": _round})
                    case "scale_exponential":
                        def _scale_exponential(arg):
                            #format scale_exponential(5, 0, 10, 0, 100, 2)
                            value, domain_min, domain_max, range_min, range_max, exponent = map(float, arg.split(","))
                            if domain_min >= domain_max:
                                raise ValueError("domain_min must be less than domain_max")
                            if exponent <= 0:
                                raise ValueError("exponent must be greater than 0")
                            if value <= domain_min:
                                return range_min
                                # float - 0.0
                            if value >= domain_max:
                                return range_max
                                # float - 100.0
                            if exponent == 1:
                                ratio = (value - domain_min) / (domain_max - domain_min)
                            else:
                                ratio = (
                                    (exponent ** (value - domain_min) - 1)
                                    / (exponent ** (domain_max - domain_min) - 1)
                                    )
                            return range_min + ratio * (range_max - range_min)
                            # float - 3.0303030303030303
                        self.definedFunctions.update({"scale_exponential": _scale_exponential})
                    case "scale_linear":
                        def _scale_linear(arg):
                            #format scale_linear(5, 0, 10, 0, 100)
                            value, domain_min, domain_max, range_min, range_max = map(float, arg.split(","))
                            if domain_min >= domain_max:
                                raise ValueError("domain_max must be greater than domain_min")
                            if value <= domain_min:
                                return range_min
                                # float - 0.0
                            if value >= domain_max:
                                return range_max
                                # float - 100.0
                            ratio = (value - domain_min) / (domain_max - domain_min)
                            return range_min + ratio * (range_max - range_min)
                            # float - 50.0
                        self.definedFunctions.update({"scale_linear": _scale_linear})
                    case "scale_polynomial":
                        def _scale_polynomial(arg):
                            #format scale_polynomial(5, 0, 10, 0, 100, 2)
                            value, domain_min, domain_max, range_min, range_max, exponent = map(float, arg.split(","))
                            if domain_min >= domain_max:
                                raise ValueError("domain_min must be less than domain_max")
                            if exponent <= 0:
                                raise ValueError("exponent must be greater than 0")
                            if value <= domain_min:
                                return range_min
                                # float - 0.0
                            if value >= domain_max:
                                return range_max
                                # float - 100.0
                            ratio = ((value - domain_min) / (domain_max - domain_min)) ** exponent
                            return range_min + ratio * (range_max - range_min)
                            # float - 25.0
                        self.definedFunctions.update({"scale_polynomial": _scale_polynomial})
                    case "scale_logarithmic":
                        def _scale_logarithmic(arg):
                            #format scale_logarithmic(5, 1, 10, 0, 100)
                            value, domain_min, domain_max, range_min, range_max = map(float, arg.split(","))
                            if domain_min >= domain_max:
                                raise ValueError("domain_min must be less than domain_max")
                            if value <= domain_min:
                                return range_min
                                # float - 0.0
                            if value >= domain_max:
                                return range_max
                                # float - 100.0
                            ratio = (m.log(value) - m.log(domain_min)) / (m.log(domain_max) - m.log(domain_min))
                            return range_min + ratio * (range_max - range_min)
                            # float - 69.89700043360187
                        self.definedFunctions.update({"scale_logarithmic": _scale_logarithmic})
                    case "sqrt":
                        def _sqrt(arg):
                            #format sqrt(9)
                            return m.sqrt(float(arg))
                            # float - 3.0
                        self.definedFunctions.update({"sqrt": _sqrt})
                    case "root":
                        def _root(arg):
                            #format root(27, 3)
                            value, n = map(float, arg.split(","))
                            return value ** (1 / n)
                            # float | complex - 3.0, (1+2j)
                        self.definedFunctions.update({"root": _root})

                    # STRING FUNCTIONS
            except Exception as e:
                print(f"Error defining function {func['name']}: {e}")
                
    def parse_expression(self):
        try:
            parsed_expr = parse_expr(self.expression)
            return parsed_expr
        except Exception as e:
            return {"error": str(e)}
