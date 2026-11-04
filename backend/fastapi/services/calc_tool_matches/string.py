import json
import re
from pathlib import Path

json_path = Path(__file__).resolve().parents[2] / "json" / "ASCII.json"

def string_match(func):
    match func:
        case "ascii":
            def _ascii(*args):
                if len(args) != 1:
                    raise ValueError("ascii requires exactly one argument")

                argument = str(args[0])
                with json_path.open("r", encoding="utf-8") as f:
                    rows = json.load(f).get("ASCII", [])

                for row in rows:
                    if row[4] == argument:
                        return int(row[0])

                raise ValueError(f"Invalid ASCII symbol: {argument!r}")
            return _ascii
        case "char":
            def _char(arg):
                try:
                    arg = int(arg)
                except ValueError:
                    raise ValueError("char function requires a valid integer argument")
                ascii_values = []
                with json_path.open("r", encoding="utf-8") as f:
                    ascii_dict = json.load(f)
                rows = ascii_dict.get("ASCII", [])
                for row in rows:
                    ascii_values.append(int(row[0]))
                if arg not in ascii_values:
                    raise ValueError(f"Invalid character: {arg}. Must be one of {ascii_values}")
                for row in rows:
                    if int(row[0]) == arg:
                        return row[4]
            return _char
        case "concat":
            def _concat(*args):
                if len(args) < 2:
                    raise ValueError("concat function requires at least two valid arguments")
                return "".join(str(arg) for arg in args)
            return _concat
        case "format":
            def _format(arg):
                ipt = arg.split(", ", 1)
                if len(ipt) != 2:
                    raise ValueError("format function requires a template and at least one inserted value")
                argument, inserted = ipt
                values = inserted.split(", ")
                indexes = [int(index) for index in re.findall(r"%([1-9]\d*)", argument)]
                if len(values) == 1 and max(indexes, default=0) > 1:
                    values = inserted.split(",")
                if any(value == "" for value in values):
                    raise ValueError("format function requires non-empty inserted values")

                def insert(match):
                    index = int(match[1]) - 1
                    return values[index] if index < len(values) else match[0]

                return re.sub(r"%([1-9]\d*)", insert, argument)
            return _format
        case "format_number":
            def _format_number(*args, **kwargs):
                if len(args) != 2:
                    raise ValueError("format_number requires a number and decimal places")

                options = {
                    "add_space_separator": False,
                    "trim_trailing_zeros": False,
                }

                for name, value in kwargs.items():
                    value = str(value).strip().lower()
                    if name not in options or value not in ("true", "false"):
                        raise ValueError("Invalid format_number option")
                    options[name] = value == "true"

                try:
                    argument = float(str(args[0]))
                    places = int(str(args[1]))
                except (ValueError, TypeError) as exc:
                    raise ValueError("format_number requires a number and integer decimal places") from exc
                
                if places < 0:
                    raise ValueError("Decimal places must be non-negative")
                if options["add_space_separator"]:
                    result = f"{argument:,.{places}f}".replace(",", " ")
                else:
                    result = f"{argument:.{places}f}"

                if options["trim_trailing_zeros"] and "." in result:
                    result = result.rstrip("0").rstrip(".")
                return result
            return _format_number
        case "left":
            def _left(arg):
                ipt = list(map(str, arg.split(", ")))
                if len(ipt) != 2:
                    raise ValueError("left function requires exactly two arguments: the string and the length")
                argument, length = ipt[0], ipt[1]
                if argument == "" or length == "":
                    raise ValueError("left function requires both an argument and a length")
                try:
                    length = int(length)
                except ValueError:
                    raise ValueError("left function requires a valid integer for length")
                return argument[:length]
            return _left
        case "length":
            def _length(*args):
                if len(args) != 1:
                    raise ValueError("length requires exactly one argument")
                return len(str(args[0]))
            return _length
        case "lower":
            def _lower(*args):
                if len(args) != 1:
                    raise ValueError("lower requires exactly one argument")
                return str(args[0]).lower()
            return _lower
        case "lpad":
            def _lpad(arg):
                ipt = list(map(str, arg.rsplit(", ", 2)))
                if len(ipt) != 3:
                    raise ValueError("lpad function requires exactly three arguments: the string, the width, and the padding string")
                argument, width, pad_string = ipt
                try:
                    width = int(width)
                    if width < 0:
                        raise ValueError("lpad function requires a non-negative integer for width")
                except ValueError:
                    raise ValueError("lpad function requires a valid integer for width")
                return argument.rjust(width, pad_string)
            return _lpad
        case "ltrim":
            def _ltrim(*args):
                if not 1 <= len(args) <= 2:
                    raise ValueError("ltrim requires one or two arguments")
                argument = str(args[0])
                chars = str(args[1]) if len(args) == 2 else None
                return argument.lstrip(chars)
            return _ltrim
        case "regexp_match":
            def _regexp_match(*args):
                if len(args) != 3:
                    raise ValueError("regexp_match requires exactly three arguments")
                
                argument, pattern, flag = map(str, args)
                try:
                    match = re.search(rf"(?:{flag})(?:{pattern})(?:{flag})", argument)
                except re.error as exc:
                    raise ValueError(f"Invalid regular expression: {exc}") from exc
                
                return match.start() if match else -1
            return _regexp_match

        case "regexp_replace":
            def _regexp_replace(*args):
                if len(args) != 4:
                    raise ValueError("regexp_replace requires exactly four arguments")
                argument, pattern, replacement, flag = map(str, args)
                try:
                    return re.sub(rf"(?:{flag})(?:{pattern})(?:{flag})", replacement, argument)
                except (re.error, IndexError) as exc:
                    raise ValueError(f"Invalid regular expression or replacement: {exc}") from exc
            return _regexp_replace

        case "regexp_substr":
            def _regexp_substr(*args):
                if len(args) != 2:
                    raise ValueError("regexp_substr requires exactly two arguments")
                argument, pattern = map(str, args)
                try:
                    match = re.search(pattern, argument)
                except re.error as exc:
                    raise ValueError(f"Invalid regular expression: {exc}") from exc
                return match.group(0) if match else ""
            return _regexp_substr
        case "replace":
            def _replace(*args):
                if len(args) != 3:
                    raise ValueError("replace function requires exactly three arguments: the string, the old substring, and the new substring")
                argument, old, new = map(str, args)
                return argument.replace(old, new)
            return _replace
        case "right":
            def _right(arg):
                ipt = list(map(str, arg.split(", ")))
                if len(ipt) != 2:
                    raise ValueError("right function requires exactly two arguments: the string and the length")
                argument, length = ipt[0], ipt[1]
                if argument == "" or length == "":
                    raise ValueError("right function requires both an argument and a length")
                try:
                    length = int(length)
                except ValueError:
                    raise ValueError("right function requires a valid integer for length")
                if length >= 1:
                    return argument[-length:]
                else:
                    raise ValueError("right function requires a positive integer for length")
            return _right
        case "rpad":
            def _rpad(arg):
                ipt = list(map(str, arg.rsplit(", ", 2)))
                if len(ipt) != 3:
                    raise ValueError("rpad function requires exactly three arguments: the string, the width, and the padding string")
                argument, width, pad_string = ipt
                try:
                    width = int(width)
                    if width < 0:
                        raise ValueError("rpad function requires a non-negative integer for width")
                except ValueError:
                    raise ValueError("rpad function requires a valid integer for width")
                return argument.ljust(width, pad_string)
            return _rpad
        case "rtrim":
            def _rtrim(arg):
                ipt = arg.split(", ")
                if arg == "":
                    raise ValueError("Input for rtrim cannot be an empty string")
                if not 1 <= len(ipt) <= 2:
                    raise ValueError("rtrim function requires one or two arguments: the string to trim and optionally the characters to trim")
                chars = ipt[1] if len(ipt) == 2 else None
                return ipt[0].rstrip(chars)
            return _rtrim
        case "strpos":
            def _strpos(arg):
                ipt = list(map(str, arg.split(", ")))
                if len(ipt) != 2:
                    raise ValueError("strpos function requires exactly two arguments: the string and the substring")
                argument, substring = ipt[0], ipt[1]
                if argument == "" or substring == "":
                    raise ValueError("strpos function requires both an argument and a substring")
                return argument.find(substring)
            return _strpos
        case "substr":
            def _substr(arg):
                ipt = list(map(str, arg.split(", ")))
                if not (2 <= len(ipt) <= 3):
                    raise ValueError("substr function requires 2 or 3 arguments: the string, the start position, and optionally the length")
                argument, start, length = None, None, None
                if len(ipt) == 2:
                    argument, start = ipt[0], ipt[1]
                if len(ipt) == 3:
                    argument, start, length = ipt[0], ipt[1], ipt[2]
                try:
                    start = int(start)
                    length = int(length) if len(ipt) == 3 else None
                except ValueError:
                    raise ValueError("substr function requires valid integers for start and length")
                if length is not None:
                    return argument[start:start + length]
                else:
                    return argument[start:]
            return _substr
        case "title":
            def _title(*args):
                if len(args) != 1:
                    raise ValueError("title requires exactly one argument")
                return str(args[0]).title()
            return _title
        case "to_string":
            def _to_string(arg):
                ipt = arg.split(", ")
                if len(ipt) != 1:
                    raise ValueError("to_string function requires exactly one argument: the value to convert to string")
                try:
                    argument = float(ipt[0])
                except ValueError:
                    raise ValueError("to_string function requires a valid numeric argument")
                return str(argument)
            return _to_string
        case "trim":
            def _trim(*args):
                if len(args) != 1:
                    raise ValueError("trim requires exactly one argument")
                return str(args[0]).strip()
            return _trim
        case "upper":
            def _upper(*args):
                if len(args) != 1:
                    raise ValueError("upper requires exactly one argument")
                return str(args[0]).upper()
            return _upper
        case "worldwrap":
            def _worldwrap(arg):
                ipt = arg.split(", ")
                if len(ipt) != 2:
                    raise ValueError("worldwrap function requires exactly two arguments: the string and the width")
                argument, max_char = ipt
                try:
                    max_char = int(max_char)
                    if max_char <= 0:
                        raise ValueError("worldwrap function requires a positive integer for width")
                except ValueError:
                    raise ValueError("worldwrap function requires a valid integer for width")
                lines = []
                word_len = len(argument)
                iterates, remaining_chars = divmod(word_len, max_char)
                for it in range(iterates):
                    lines.append(argument[it * max_char:(it + 1) * max_char])
                if remaining_chars:
                    lines.append(argument[iterates * max_char:])
                return "\n".join(lines)
            return _worldwrap
        case _:
            return None
