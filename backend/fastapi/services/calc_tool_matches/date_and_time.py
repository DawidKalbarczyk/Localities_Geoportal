import datetime as dt
import math as m
import re


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

def date_and_time_match(func):
    match func:
        case "age":
            # Przykład: age(2026-10-30 13:00:00, 2026-10-29 10:00:00)
            def _age(arg):
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
            return _age
        case "datetime_from_epoch":
            def _datetime_from_epoch(arg):
                #format datetime_from_epoch(1700000000)
                try:
                    epoch_time = int(arg)
                except ValueError:
                    raise ValueError(f"Invalid epoch time: {arg}. Expected a non-negative integer.")
                if not int(arg) >= 0:
                    raise ValueError(f"Invalid epoch time: {arg}. Expected a non-negative integer.")
                try:
                    return dt.datetime.fromtimestamp(epoch_time).isoformat(sep=" ")
                except (OSError, OverflowError, ValueError) as exc:
                    raise ValueError(f"Invalid epoch time: {arg}. Expected a valid epoch time.") from exc
                # str - "2023-11-14 23:13:20"
            return _datetime_from_epoch
        case "day_of_week":
            def _day_of_week(arg):
                #format day_of_week(2026-10-30)
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", arg):
                    raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD")
                
                date = dt.datetime.fromisoformat(arg)
                return (date.weekday() + 1)
                # int - 4
            return _day_of_week
        case "epoch":
            def _epoch(arg):
                #format epoch(2026-10-30 13:00:00)
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", arg):
                    raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD HH:MM:SS")
                to_date = dt.datetime.fromisoformat(arg)
                return int(to_date.timestamp())
                # int - 1793365200
            return _epoch
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
                    fmt = f"{format_x}.{format_y}.{format_z}"
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
                            new_format.append(f"{date_obj[tempIdx]!s}")

                fmt = f"{format_x}. {format_y}. {format_z}"
                final_date = ""
                if ("MMM" in fmt or "MMMM" in fmt):
                    final_date = " ".join(new_format)
                else:
                    final_date = ".".join(new_format)
                return final_date
                # str - "30.10.2026"
            return _format_date
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
            return _format_time
        case "make_date":
            def _make_date(arg):
                #format make_date(2026, 10, 30)
                if not re.fullmatch(r"\d{4},\s*\d{1,2},\s*\d{1,2}", arg):
                    raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY, MM, DD")
                year, month, day = map(int, arg.split(","))
                return dt.date(year, month, day).isoformat()
                # str - "2026-10-30"
            return _make_date
        case "to_date":
            def _to_date(arg):
                _input = arg.split(",")
                if len(_input) not in [1, 2]:
                    raise ValueError(f"Invalid number of arguments: {arg}. Expected 1 or 2 arguments.")
                #QGIS ma z przecinkiem, ale tu robię bez
                if len(_input) == 2 and not re.fullmatch(r"(d{1,4}|dd|ddd|dddd|M{1,4}|MM|MMM|MMMM|yy|yyyy)(\.(d{1,4}|dd|ddd|dddd|M{1,4}|MM|MMM|MMMM|yy|yyyy)){2}", _input[1].strip()):
                                                raise ValueError(f"Invalid format: {_input[1].strip()}. Expected a valid format in the format d.M.yyyy or dd.MM.yyyy or ddd.MMM.yy etc.")
                if not re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}|\d{1,2}-\d{1,2}-\d{4}|\d{4} \w+ \d{1,2}|\d{1,2} \w+ \d{4}", _input[0].strip()):
                    raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD/DD-MM-YYYY or YYYY MMMM DD/DD MMMM YYYY")
                
                if len(_input) == 1:
                    date = _input[0].strip()
                    if "-" in date:
                        date = date.split("-")
                    elif " " in date:
                        date = date.split(" ")
                    try:
                        int(date[1])
                        m = int(date[1])
                    except ValueError:
                        m = str(date[1])
                    if isinstance(m, str):
                        monthList = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                        m = monthList.index(m) + 1
                    if len(date) != 3:
                        raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD/DD-MM-YYYY or YYYY MMMM DD/DD MMMM YYYY")
                    if len(date[0]) == 4:
                        year = int(date[0])
                        day = int(date[2])
                    elif len(date[2]) == 4:
                        year = int(date[2])
                        day = int(date[0])
                    else:
                        raise ValueError(f"Invalid date format: {arg}. Expected a valid date in the format YYYY-MM-DD/DD-MM-YYYY or YYYY MMMM DD/DD MMMM YYYY")
                    return dt.date(year, m, day).isoformat()
                elif len(_input) == 2:
                    date, format_ipt = map(str.strip, arg.split(","))
                    if "-" in date:
                        date = date.split("-")
                    elif " " in date:
                        date = date.split(" ")
                    if len(date[2]) == 4:
                        date = [date[2], date[1], date[0]]
                    try:
                        month = int(date[1])
                    except ValueError:
                        monthList = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                        month = monthList.index(date[1]) + 1
                    date[1] = str(month).zfill(2)
                    date2 = dt.date(int(date[0]), int(date[1]), int(date[2]))  # Validate date
                    format = format_ipt.split(".")
                    new_format = []
                    for idx, fmt in enumerate(format):
                        match fmt:
                            case "d":
                                new_format.append(f"{(date[2]).lstrip('0')}")
                            case 'dd':
                                new_format.append(f"{(date[2]).zfill(2)}")
                            case 'ddd':
                                weekdayList = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                                new_format.append(f"{weekdayList[date2.weekday()]}")
                            case 'dddd':
                                weekdayList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                                new_format.append(f"{weekdayList[date2.weekday()]}")
                            case 'M':
                                new_format.append(f"{(date[1]).lstrip('0')}")
                            case 'MM':
                                new_format.append(f"{(date[1]).zfill(2)}")
                            case 'MMM':
                                monthList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                                new_format.append(f"{monthList[int(date[1]) - 1]}")
                            case 'MMMM':
                                monthList = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                                new_format.append(f"{monthList[int(date[1]) - 1]}")
                            case 'yy':
                                new_format.append(f"{str(date[0])[-2:]}")
                            case 'yyyy':
                                new_format.append(f"{date[0]!s}")
                    if 'MMM' in format or 'MMMM' in format:
                        return " ".join(new_format)
                    else:
                        return "-".join(new_format)
            return _to_date
        case "make_datetime":
            def _make_datetime(arg):
                #format make_datetime(2026, 10, 30, 13, 5, 9)
                if not re.fullmatch(r"\d{4},\s*\d{1,2},\s*\d{1,2},\s*\d{1,2},\s*\d{1,2},\s*\d{1,2}", arg):
                    raise ValueError(f"Invalid datetime format: {arg}. Expected a valid datetime in the format YYYY, MM, DD, HH, MM, SS")
                year, month, day, hour, minute, second = map(int, arg.split(","))
                return dt.datetime(year, month, day, hour, minute, second).isoformat(sep=" ")
                # str - "2026-10-30 13:05:09"
            return _make_datetime
        case "to_datetime":
            def _to_datetime(arg):
                _input = list(map(str.strip, arg.split(",")))
                if len(_input) not in [1, 2] or not _input[0]:
                    raise ValueError(f"Invalid datetime arguments: {arg}. Expected datetime or datetime, format")

                datetime_ipt = _input[0]
                monthList = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                shortMonthList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                format_parts = []

                if len(_input) == 2:
                    format_ipt = _input[1]
                    if not re.fullmatch(r"(?:dddd|ddd|dd|d|MMMM|MMM|MM|M|yyyy|yy|HH|H|hh|h|mm|m|ss|s)(?:[ .:/-]+(?:dddd|ddd|dd|d|MMMM|MMM|MM|M|yyyy|yy|HH|H|hh|h|mm|m|ss|s))*", format_ipt):
                        raise ValueError(f"Invalid datetime format: {format_ipt}")
                    format_parts = re.split(r"[ .:/-]+", format_ipt)
                    format_fields = []
                    for fmt in format_parts:
                        match fmt:
                            case "d" | "dd":
                                format_fields.append("day")
                            case "ddd" | "dddd":
                                format_fields.append("weekday")
                            case "M" | "MM" | "MMM" | "MMMM":
                                format_fields.append("month")
                            case "yy" | "yyyy":
                                format_fields.append("year")
                            case "h" | "hh" | "H" | "HH":
                                format_fields.append("hour")
                            case "m" | "mm":
                                format_fields.append("minute")
                            case "s" | "ss":
                                format_fields.append("second")
                    if len(format_fields) != len(set(format_fields)):
                        raise ValueError(f"Invalid datetime format: {format_ipt}. Expected unique components")
                    if not all(field in format_fields for field in ["year", "month", "day"]):
                        raise ValueError(f"Invalid datetime format: {format_ipt}. Expected year, month and day components")

                # ISO is recognized directly, including the examples with a supplied format.
                iso_input = re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}(?:[ T]\d{1,2}:\d{1,2}(?::\d{1,2}(?:\.\d{1,6})?)?)?", datetime_ipt)
                if len(_input) == 1 or iso_input:
                    datetime_parts = re.sub(r"(?<=\d)T(?=\d)", " ", datetime_ipt).rsplit(" ", 1)
                    hour, minute, second, microsecond = 0, 0, 0, 0
                    if len(datetime_parts) == 2 and ":" in datetime_parts[1]:
                        date_ipt, time_ipt = datetime_parts
                        if not re.fullmatch(r"\d{1,2}:\d{1,2}(?::\d{1,2}(?:\.\d{1,6})?)?", time_ipt):
                            raise ValueError(f"Invalid time format: {time_ipt}. Expected HH:mm or HH:mm:ss")
                        time_parts = time_ipt.split(":")
                        hour, minute = int(time_parts[0]), int(time_parts[1])
                        if len(time_parts) == 3:
                            if "." in time_parts[2]:
                                second_ipt, fraction = time_parts[2].split(".")
                                second = int(second_ipt)
                                microsecond = int(fraction.ljust(6, "0"))
                            else:
                                second = int(time_parts[2])
                    else:
                        date_ipt = datetime_ipt

                    if not re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}|\d{1,2}-\d{1,2}-\d{4}|\d{4} (?:[A-Za-z]+|\d{1,2}) \d{1,2}|\d{1,2} (?:[A-Za-z]+|\d{1,2}) \d{4}", date_ipt):
                        raise ValueError(f"Invalid date format: {date_ipt}. Expected YYYY-MM-DD, DD-MM-YYYY, YYYY MMMM DD or DD MMMM YYYY")
                    if "-" in date_ipt:
                        date_parts = date_ipt.split("-")
                    else:
                        date_parts = date_ipt.split(" ")
                    if len(date_parts) != 3:
                        raise ValueError(f"Invalid date components: {date_ipt}")
                    try:
                        month = int(date_parts[1])
                    except ValueError:
                        month_ipt = date_parts[1].capitalize()
                        if month_ipt in monthList:
                            month = monthList.index(month_ipt) + 1
                        elif month_ipt in shortMonthList:
                            month = shortMonthList.index(month_ipt) + 1
                        else:
                            raise ValueError(f"Invalid month name: {date_parts[1]}")
                    if len(date_parts[0]) == 4:
                        year = int(date_parts[0])
                        day = int(date_parts[2])
                    elif len(date_parts[2]) == 4:
                        year = int(date_parts[2])
                        day = int(date_parts[0])
                    else:
                        raise ValueError(f"Invalid date format: {date_ipt}. Expected a four-digit year")
                    return dt.datetime(year, month, day, hour, minute, second, microsecond)

                # For other layouts, each token identifies its input component.
                if not re.fullmatch(r"[A-Za-z0-9]+(?:[ .:/-][A-Za-z0-9]+)*", datetime_ipt):
                    raise ValueError(f"Invalid datetime components: {datetime_ipt}")
                input_parts = re.split(r"[ .:/-]+", datetime_ipt)
                if len(input_parts) != len(format_parts):
                    raise ValueError(f"Invalid datetime and format lengths: {datetime_ipt}, {_input[1]}. Expected the same number of components")
                year, month, day = None, None, None
                hour, minute, second = 0, 0, 0
                weekday = None
                for value, fmt in zip(input_parts, format_parts):
                    match fmt:
                        case "d" | "dd":
                            pattern = r"\d{2}" if fmt == "dd" else r"\d{1,2}"
                            if not re.fullmatch(pattern, value):
                                raise ValueError(f"Invalid day: {value} for format {fmt}")
                            day = int(value)
                        case "ddd":
                            weekdayList = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                            weekday_ipt = value.capitalize()
                            if weekday_ipt not in weekdayList:
                                raise ValueError(f"Invalid weekday: {value}")
                            weekday = weekdayList.index(weekday_ipt)
                        case "dddd":
                            weekdayList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                            weekday_ipt = value.capitalize()
                            if weekday_ipt not in weekdayList:
                                raise ValueError(f"Invalid weekday: {value}")
                            weekday = weekdayList.index(weekday_ipt)
                        case "M" | "MM":
                            pattern = r"\d{2}" if fmt == "MM" else r"\d{1,2}"
                            if not re.fullmatch(pattern, value):
                                raise ValueError(f"Invalid month: {value} for format {fmt}")
                            month = int(value)
                        case "MMM":
                            month_ipt = value.capitalize()
                            if month_ipt not in shortMonthList:
                                raise ValueError(f"Invalid abbreviated month: {value}")
                            month = shortMonthList.index(month_ipt) + 1
                        case "MMMM":
                            month_ipt = value.capitalize()
                            if month_ipt not in monthList:
                                raise ValueError(f"Invalid month name: {value}")
                            month = monthList.index(month_ipt) + 1
                        case "yy":
                            if not re.fullmatch(r"\d{2}", value):
                                raise ValueError(f"Invalid two-digit year: {value}")
                            year = int(value)
                            year += 2000 if year <= 68 else 1900
                        case "yyyy":
                            if not re.fullmatch(r"\d{4}", value):
                                raise ValueError(f"Invalid four-digit year: {value}")
                            year = int(value)
                        case "h" | "hh" | "H" | "HH":
                            pattern = r"\d{2}" if len(fmt) == 2 else r"\d{1,2}"
                            if not re.fullmatch(pattern, value):
                                raise ValueError(f"Invalid hour: {value} for format {fmt}")
                            hour = int(value)
                        case "m" | "mm":
                            pattern = r"\d{2}" if fmt == "mm" else r"\d{1,2}"
                            if not re.fullmatch(pattern, value):
                                raise ValueError(f"Invalid minute: {value} for format {fmt}")
                            minute = int(value)
                        case "s" | "ss":
                            pattern = r"\d{2}" if fmt == "ss" else r"\d{1,2}"
                            if not re.fullmatch(pattern, value):
                                raise ValueError(f"Invalid second: {value} for format {fmt}")
                            second = int(value)

                result = dt.datetime(year, month, day, hour, minute, second)
                if weekday is not None and result.weekday() != weekday:
                    raise ValueError(f"Invalid weekday for datetime: {datetime_ipt}")
                return result
            return _to_datetime
        case "make_interval":
            def _make_interval(arg):
                #format make_interval(days=2, hours=3 etc)
                params = arg.split(",")
                param_keys = ["years", "months", "weeks","days", "hours", "minutes", "seconds"]
                arguments_dict = {}
                for p in params:
                    if "=" not in p:
                        raise ValueError(f"Invalid parameter format: {p}. Expected format: key=value")
                    p_val = float(p.split("=", 1)[1])

                    if not m.isfinite(p_val) or p_val < 0:
                        raise ValueError(f"Invalid parameter value: {p.split('=')[1]}. Expected a non-negative integer.")
                    
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
            return _make_interval
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
                    p_val = float(p.split(" ")[0])
                    if not m.isfinite(p_val) or p_val < 0:
                        raise ValueError(f"Invalid parameter value: {p_val}")
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
            return _to_interval
        case "year":
            def _year(arg):
                years = match_time_format("year", arg)
                return years
            return _year
        case "month":
            def _month(arg):
                months = match_time_format("month", arg)
                return months
            return _month
        case "week":
            def _week(arg):
                weeks = match_time_format("week", arg)
                return weeks
            return _week
        case "day":
            def _day(arg):
                #format day(2026-10-30)
                days = match_time_format("day", arg)
                # int - 30
                return days
            return _day
        case "hour":
            def _hour(arg):
                #format hour(2026-10-30 13:05:09)
                hours = match_time_format("hour", arg)
                return hours
                # int - 51 for "2.125 days"
            return _hour
        case "minute":
            def _minute(arg):
                minutes = match_time_format("minute", arg)
                return minutes
            return _minute
        case "second":
            def _second(arg):
                seconds = match_time_format("second", arg)
                return seconds
            return _second
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
            return _make_time
        case "to_time":
            def _to_time(arg):
                # minimum HH:MM
                p_time, p_format = map(str.strip, arg.split(","))

                if not re.fullmatch(r"\d{2}:\d{2}(?::\d{2})?", p_time):
                    raise ValueError(f"Invalid time format: {p_time}. Expected a valid time in the format HH:MM or HH:MM:SS")
                if (
                    not re.fullmatch(r"(?:HH|hh|mm|MM|ss|SS):(?:HH|hh|mm|MM|ss|SS)", p_format)
                    and not re.fullmatch(r"(?:HH|hh|mm|MM|ss|SS):(?:HH|hh|mm|MM|ss|SS):(?:HH|hh|mm|MM|ss|SS)", p_format)
                ):
                    raise ValueError(f"Invalid time format: {p_format}. Expected a valid time format in the format HH:MM or HH:MM:SS")

                time, format = p_time.strip().split(":"), p_format.strip().split(":")
                if len(time) != len(format):
                                                raise ValueError(f"Invalid time and format lengths: {p_time}, {p_format}. Expected the same number of components in time and format.")
                for idx, t in enumerate(time):
                    if format[idx] in ["HH", "hh"] and not (0 <= int(t) < 24):
                        raise ValueError(f"Invalid time value: {t}. Expected a valid hour in the range 0-23 for format {format[idx]}")
                    if format[idx] in ["mm", "MM"] and not (0 <= int(t) < 60):
                        raise ValueError(f"Invalid time value: {t}. Expected a valid minute in the range 0-59 for format {format[idx]}")
                    if format[idx] in ["ss", "SS"] and not (0 <= int(t) < 60):
                        raise ValueError(f"Invalid time value: {t}. Expected a valid second in the range 0-59 for format {format[idx]}")
                if len(format) != len(set(format)):
                    raise ValueError(f"Invalid time format: {p_format}. Expected unique components in the format.")
                else:
                    chk_list = format.copy()
                    for idx, fmt in enumerate(chk_list):
                        chk_list[idx] = fmt.upper()
                    if len(chk_list) != len(set(chk_list)):
                        raise ValueError(f"Invalid time format: {p_format}. Expected unique components in the format.")
                    
                
                pairs = {}
                for t, f in zip(time, format):
                    pairs[f] = t
                output_list = []
                for p_format, p_time in pairs.items():
                    output_list.append(f"{p_time.zfill(2)}")
                output_time = ":".join(output_list)
                final_time = dt.datetime
                def transform_format(fmt):
                    match fmt:
                        case "H" | "h" | "HH" | "hh":
                            return "H"
                        case "M" | "m" | "MM" | "mm":
                            return "M"
                        case "S" | "s" | "SS" | "ss":
                            return "S"
                if len(output_list) < 3:
                    final_time = dt.datetime.strptime(output_time, f"%{transform_format(format[0])}:%{transform_format(format[1])}")
                else:
                    final_time = dt.datetime.strptime(output_time, f"%{transform_format(format[0])}:%{transform_format(format[1])}:%{transform_format(format[2])}")
                return final_time.time()
            return _to_time
        case "now":
            def _now(arg):
                if arg == "":
                    return dt.datetime.now().isoformat(sep=" ")
                else:
                    raise ValueError(f"Invalid parameter format: {arg}. Expected no parameters for now()")
            return _now
        case _:
            return None
