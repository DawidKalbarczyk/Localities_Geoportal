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
        for func in self.expressionFunctions:
            try:
                match func["name"]:
                    # DATE AND TIME FUNCTIONS
                    case "age":
                        def _age(arg):
                            #format age(2026-10-30T13:00:00, 2026-10-29T10:00:00)
                            later_date, earlier_date = map(str.strip, arg.split(","))
                            start = dt.datetime.fromisoformat(earlier_date)
                            end = dt.datetime.fromisoformat(later_date)
                            return end - start
                        self.definedFunctions.update({"age": _age})
                    case "datetime_from_epoch":
                        def _datetime_from_epoch(arg):
                            #format datetime_from_epoch(1700000000)
                            epoch_time = int(arg)
                            return dt.datetime.fromtimestamp(epoch_time).isoformat()
                        self.definedFunctions.update({"datetime_from_epoch": _datetime_from_epoch})
                    case "day":
                        def _day(arg):
                            #format day(2026-10-30)
                            day = int(arg.split("-")[2])
                            return day
                        self.definedFunctions.update({"day": _day})
                    case "day_of_week":
                        def _day_of_week(arg):
                            #format day_of_week(2026-10-30)
                            date = dt.datetime.fromisoformat(arg)
                            return date.weekday()
                        self.definedFunctions.update({"day_of_week": _day_of_week})
                    case "epoch":
                        def _epoch(arg):
                            #format epoch(2026-10-30T13:00:00)
                            to_date = dt.datetime.fromisoformat(arg)
                            return int(to_date.timestamp())
                        self.definedFunctions.update({"epoch": _epoch})
                    case "format_date":
                        def _format_date(arg):
                            #format format_date(2026-10-30, dd.MM.yyyy)
                            # Language support can be added here for month if needed
                            date_str, format_str = map(str.strip, arg.split(","))
                            date_y, date_m, date_d = map(str, date_str.split("-"))
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
                                elif (re.fullmatch("M{1,4}\\.d{1,4}\\.(yy|yyyy)", fmt)):
                                    return ["1", "2", "0"]
                                elif (re.fullmatch("(yy|yyyy)\\.M{1,4}\\.d{1,4}", fmt)):
                                    return ["0", "1", "2"]
                                elif (re.fullmatch("d{1,4}\\.(yy|yyyy)\\.M{1,4}", fmt)):
                                    return ["2", "0", "1"]
                                elif (re.fullmatch("M{1,4}\\.(yy|yyyy)\\.d{1,4}", fmt)):
                                    return ["1", "0", "2"]
                                elif (re.fullmatch("(yy|yyyy)\\.d{1,4}\\.M{1,4}", fmt)):
                                    return ["0", "2", "1"]
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
                        self.definedFunctions.update({"format_date": _format_date})
                    case "format_time":
                        def _format_time(arg):
                            #format format_time(13:05:09, HH:mm:ss)
                            #Function represents time in 12 hour format for h | hh and 24 hour format for H | HH
                            time_str, format_str = map(str.strip, arg.split(","))
                            time = list(map(int, time_str.split(":")))
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
                                elif (re.fullmatch("(h|hh|H|HH)\\:(s|ss)\\:(m|mm)", fmt)):
                                    return ["0", "2", "1"]
                                elif (re.fullmatch("(m|mm)\\:(h|hh|H|HH)\\:(s|ss)", fmt)):
                                    return ["1", "0", "2"]
                                elif (re.fullmatch("(m|mm)\\:(s|ss)\\:(h|hh|H|HH)", fmt)):
                                    return ["1", "2", "0"]
                                elif (re.fullmatch("(s|ss)\\:(h|hh|H|HH)\\:(m|mm)", fmt)):
                                    return ["2", "0", "1"]
                                elif (re.fullmatch("(s|ss)\\:(m|mm)\\:(h|hh|H|HH)", fmt)):
                                    return ["2", "1", "0"]
                                elif (re.fullmatch("(h|hh|H|HH)\\:(m|mm)", fmt)):
                                    return ["0", "1"]
                                elif (re.fullmatch("(h|hh|H|HH)\\:(s|ss)", fmt)):
                                    return ["0", "2"]
                                elif (re.fullmatch("(m|mm)\\:(h|hh|H|HH)", fmt)):
                                    return ["1", "0"]
                                elif (re.fullmatch("(m|mm)\\:(s|ss)", fmt)):
                                    return ["1", "2"]
                                elif (re.fullmatch("(s|ss)\\:(h|hh|H|HH)", fmt)):
                                    return ["2", "0"]
                                elif (re.fullmatch("(s|ss)\\:(m|mm)", fmt)):
                                    return ["2", "1"]
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
                        self.definedFunctions.update({"format_time": _format_time})
                    case "hour":
                        def _hour(arg):
                            #format hour(2026-10-30 13:05:09)
                            if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{1,6})?", arg):
                                return dt.datetime.fromisoformat(arg).hour
                            elif re.fullmatch(r"(?:-?\d+ days?, )?\d{1,2}:\d{2}:\d{2}(?:\.\d{1,6})?", arg):
                                return int(arg.split(", ")[-1].split(":")[0])
                        self.definedFunctions.update({"hour": _hour})
                    case "make_date":
                        def _make_date(arg):
                            #format make_date(2026, 10, 30)
                            year, month, day = map(int, arg.split(","))
                            return f"{year}-{month:02d}-{day:02d}"
                        self.definedFunctions.update({"make_date": _make_date})
                    case "make_datetime":
                        def _make_datetime(arg):
                            #format make_datetime(2026, 10, 30, 13, 5, 9)
                            year, month, day, hour, minute, second = map(int, arg.split(","))
                            return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
                        self.definedFunctions.update({"make_datetime": _make_datetime})
                    case "make_interval":
                        def _make_interval(arg):
                            #format make_interval(days=2, hours=3 etc)
                            params = map(int, arg.split(","))
                            param_keys = ["years", "months", "days", "hours", "minutes", "seconds"]
                            temp_dict = {}
                            for p in params:
                                if "=" not in p:
                                    raise ValueError(f"Invalid parameter format: {p}. Expected format: key=value")
                                if p.strip("=")[0] not in param_keys:
                                    raise ValueError(f"Invalid parameter key: {p.strip('=')[0]}. Expected one of: {param_keys}")
                                for p_key in param_keys:
                                    if p.strip("=")[0] == p.key:
                                        temp_dict[p_key] = p.strip("=")[1]
                       
                            result = []
                            # Stwórz funkcje iteracyjną tutaj
                            for item in temp_dict:
                                match (item, temp_dict[item]):
                                    case ("years", value) if value >= 1:
                                        if value == 1:
                                            result.append(f"{value} year")
                                            break
                                        result.append(f"{value} years")
                                    case ("years", value) if value == 0:
                                        result.append(f"{value} months")

service


                    # FIELDS AND VALUES FUNCTIONS
                    # DICTIONARY FUNCTIONS
                    # MATH FUNCTIONS
                    case "abs":
                        def _abs(arg):
                            #format abs(-3.5)
                            return abs(float(arg))
                        self.definedFunctions.update({"abs": _abs})
                    case "acos":
                        def _acos(arg):
                            #format acos(0.5)
                            return m.acos(float(arg))
                        self.definedFunctions.update({"acos": _acos})
                    case "asin":
                        def _asin(arg):
                            #format asin(0.5)
                            return m.asin(float(arg))
                        self.definedFunctions.update({"asin": _asin})
                    case "atan":
                        def _atan(arg):
                            #format atan(1)
                            return m.atan(float(arg))
                        self.definedFunctions.update({"atan": _atan})
                    case "atan2":
                        def _atan2(arg):
                            #format atan2(1, 2)
                            y, x = map(float, arg.split(","))
                            return m.atan2(float(y), float(x))
                        self.definedFunctions.update({"atan2": _atan2})
                    case "actg":
                        def _actg(arg):
                            #format actg(1)
                            return m.atan(1 / float(arg))
                        self.definedFunctions.update({"actg": _actg})
                    case "actg2":
                        def _actg2(arg):
                            #format actg2(1, 2)
                            y, x = map(float, arg.split(","))
                            return m.atan2(1 / float(y), float(x))
                        self.definedFunctions.update({"actg2": _actg2})
                    case "ceil":
                        def _ceil(arg):
                            #format ceil(2.3)
                            return m.ceil(float(arg))
                        self.definedFunctions.update({"ceil": _ceil})
                    case "clamp":
                        def _clamp(arg):
                            #format clamp(0, 5, 10)
                            min_value, value, max_value = map(float, arg.split(","))
                            return min(max_value, max(min_value, value))
                        self.definedFunctions.update({"clamp": _clamp})
                    case "sin":
                        def _sin(arg):
                            #format sin(1.57)
                            return m.sin(float(arg))
                        self.definedFunctions.update({"sin": _sin})
                    case "cos":
                        def _cos(arg):
                            #format cos(1.57)
                            return m.cos(float(arg))
                        self.definedFunctions.update({"cos": _cos})
                    case "tan":
                        def _tan(arg):
                            #format tan(0.785)
                            return m.tan(float(arg))
                        self.definedFunctions.update({"tan": _tan})
                    case "ctg":
                        def _ctg(arg):
                            #format ctg(0.785)
                            return 1 / m.tan(float(arg))
                        self.definedFunctions.update({"ctg": _ctg})
                    case "degrees":
                        def _degrees(arg):
                            #format degrees(3.14)
                            return (arg * 180) / m.pi
                        self.definedFunctions.update({"degrees": _degrees})
                    case "radians":
                        def _radians(arg):
                            #format radians(180)
                            return (arg * m.pi) / 180
                        self.definedFunctions.update({"radians": _radians})
                    case "exp":
                        def _exp(arg):
                            #format exp(2)
                            return m.exp(float(arg))
                        self.definedFunctions.update({"exp": _exp})
                    case "floor":
                        def _floor(arg):
                            #format floor(2.9)
                            return m.floor(float(arg))
                        self.definedFunctions.update({"floor": _floor})
                    case "ln":
                        def _ln(arg):
                            #format ln(2)
                            return m.log(float(arg))
                        self.definedFunctions.update({"ln": _ln})
                    case "log":
                        def _log(arg):
                            #format log(2, 8)
                            base, value = map(float, arg.split(","))
                            return m.log(value, base)
                        self.definedFunctions.update({"log": _log})
                    case "log10":
                        def _log10(arg):
                            #format log10(100)
                            return m.log10(float(arg))
                        self.definedFunctions.update({"log10": _log10})
                    case "max":
                        def _max(arg):
                            #format max(1, 2, 3)
                            return max(map(float, arg.split(",")))
                        self.definedFunctions.update({"max": _max})
                    case "min":
                        def _min(arg):
                            #format min(1, 2, 3)
                            return min(map(float, arg.split(",")))
                        self.definedFunctions.update({"min": _min})
                    case "pi":
                        def _pi(arg):
                            #format pi()
                            return m.pi
                        self.definedFunctions.update({"pi": _pi})
                    case "pow":
                        def _pow(arg):
                            #format pow(2, 3)
                            base, exponent = map(float, arg.split(","))
                            return m.pow(base, exponent)
                        self.definedFunctions.update({"pow": _pow})
                    case "rand":
                        def _rand(arg):
                            #format rand(1, 10)
                            randomItems = list(map(int, arg.split(",")))
                            if len(randomItems) == 2:
                                return r.randint(randomItems[0], randomItems[1])
                            elif len(randomItems) == 3:
                                return r.Random(randomItems[2]).randint(randomItems[0], randomItems[1])
                        self.definedFunctions.update({"rand": _rand})
                    case "randf":
                        def _randf(arg):
                            #format randf(0, 1)
                            randomItems = list(map(float, arg.split(",")))
                            if len(randomItems) == 2:
                                return r.uniform(randomItems[0], randomItems[1])
                            elif len(randomItems) == 3:
                                return r.Random(randomItems[2]).uniform(randomItems[0], randomItems[1])
                        self.definedFunctions.update({"randf": _randf})
                    case "round":
                        def _round(arg):
                            #format round(3.14159, 2)
                            value, ndigits = map(float, arg.split(","))
                            return round(value, int(ndigits))
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
                            if value >= domain_max:
                                return range_max
                            if exponent == 1:
                                ratio = (value - domain_min) / (domain_max - domain_min)
                            else:
                                ratio = (
                                    (exponent ** (value - domain_min) - 1)
                                    / (exponent ** (domain_max - domain_min) - 1)
                                    )
                            return range_min + ratio * (range_max - range_min)
                        self.definedFunctions.update({"scale_exponential": _scale_exponential})
                    case "scale_linear":
                        def _scale_linear(arg):
                            #format scale_linear(5, 0, 10, 0, 100)
                            value, domain_min, domain_max, range_min, range_max = map(float, arg.split(","))
                            if domain_min >= domain_max:
                                raise ValueError("domain_max must be greater than domain_min")
                            if value <= domain_min:
                                return range_min
                            if value >= domain_max:
                                return range_max
                            ratio = (value - domain_min) / (domain_max - domain_min)
                            return range_min + ratio * (range_max - range_min)
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
                            if value >= domain_max:
                                return range_max
                            ratio = ((value - domain_min) / (domain_max - domain_min)) ** exponent
                            return range_min + ratio * (range_max - range_min)
                        self.definedFunctions.update({"scale_polynomial": _scale_polynomial})
                    case "scale_logarithmic":
                        def _scale_logarithmic(arg):
                            #format scale_logarithmic(5, 1, 10, 0, 100)
                            value, domain_min, domain_max, range_min, range_max = map(float, arg.split(","))
                            if domain_min >= domain_max:
                                raise ValueError("domain_min must be less than domain_max")
                            if value <= domain_min:
                                return range_min
                            if value >= domain_max:
                                return range_max
                            ratio = (m.log(value) - m.log(domain_min)) / (m.log(domain_max) - m.log(domain_min))
                            return range_min + ratio * (range_max - range_min)
                        self.definedFunctions.update({"scale_logarithmic": _scale_logarithmic})
                    case "sqrt":
                        def _sqrt(arg):
                            #format sqrt(9)
                            return m.sqrt(float(arg))
                        self.definedFunctions.update({"sqrt": _sqrt})
                    case "root":
                        def _root(arg):
                            #format root(27, 3)
                            value, n = map(float, arg.split(","))
                            return value ** (1 / n)
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
