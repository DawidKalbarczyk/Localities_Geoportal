import datetime as dt
import itertools
import os
import time
from types import SimpleNamespace

import pytest
from services.calc_tool_matches import date_and_time as module

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
SECONDS = {
    "year": 31557600.0,
    "month": 2629800.0,
    "week": 604800.0,
    "day": 86400.0,
    "hour": 3600.0,
    "minute": 60.0,
    "second": 1.0,
}
UNITS = list(SECONDS)
DATE_ORDERS = list(itertools.permutations(range(3)))


@pytest.fixture(autouse=True)
def utc_timezone(monkeypatch):
    """Epoch ma używać jednej strefy niezależnie od ustawień komputera."""
    if not hasattr(time, "tzset"):
        yield
        return
    previous = os.environ.get("TZ")
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    yield
    if previous is None:
        monkeypatch.delenv("TZ")
    else:
        monkeypatch.setenv("TZ", previous)
    time.tzset()


def sample_datetime(i):
    # 10 000 różnych dat, w tym przełomy lat i dni przestępne.
    return dt.datetime(1999, 1, 1) + dt.timedelta(
        days=i,
        seconds=i * 31 % 86400,
        microseconds=i * 997 % 1_000_000,
    )


def date_tokens(value):
    return {
        "d": str(value.day),
        "dd": f"{value.day:02}",
        "ddd": WEEKDAYS[value.weekday()][:3],
        "dddd": WEEKDAYS[value.weekday()],
        "M": str(value.month),
        "MM": f"{value.month:02}",
        "MMM": MONTHS[value.month - 1][:3],
        "MMMM": MONTHS[value.month - 1],
        "yy": f"{value.year % 100:02}",
        "yyyy": f"{value.year:04}",
    }


def date_format(i):
    parts = [
        ["d", "dd", "ddd", "dddd"][(i // 6) % 4],
        ["M", "MM", "MMM", "MMMM"][(i // 24) % 4],
        ["yy", "yyyy"][(i // 96) % 2],
    ]
    return [parts[index] for index in DATE_ORDERS[i % 6]]


def quantity(value, unit):
    value = int(value) if float(value).is_integer() else value
    return f"{value} {unit}"


def test_age():
    function = module.date_and_time_match("age")
    for i in range(10_000):
        start = sample_datetime(i)
        difference = dt.timedelta(days=i % 367, seconds=i * 17, microseconds=i)
        end = start + difference
        if i % 3 == 0:
            start, end = (
                start.replace(hour=0, minute=0, second=0, microsecond=0),
                end.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                ),
            )
            argument = f"{end.date()}, {start.date()}"
        else:
            argument = f" {end.isoformat(sep=' ')}, {start.isoformat(sep=' ')} "
        result = function(argument)
        assert type(result) is dt.timedelta
        assert result == end - start, argument


def test_datetime_from_epoch():
    function = module.date_and_time_match("datetime_from_epoch")
    for i in range(10_000):
        seconds = i * 7919
        argument = [str(seconds), f" +{seconds:012} "][i % 2]
        expected = dt.datetime(*time.localtime(seconds)[:6]).isoformat(sep=" ")
        assert function(argument) == expected, argument


def test_day_of_week():
    function = module.date_and_time_match("day_of_week")
    for i in range(10_000):
        value = sample_datetime(i).date()
        argument = value.isoformat()
        result = function(argument)
        assert type(result) is int
        assert result == value.isoweekday(), argument


def test_epoch():
    function = module.date_and_time_match("epoch")
    for i in range(10_000):
        value = sample_datetime(i).replace(microsecond=0)
        argument = value.isoformat(sep=" ")
        expected = int(time.mktime(value.timetuple()))
        result = function(argument)
        assert type(result) is int
        assert result == expected, argument


def test_format_date():
    function = module.date_and_time_match("format_date")
    for i in range(10_000):
        value = sample_datetime(i).date()
        parts, tokens = date_format(i), date_tokens(value)
        separator = " " if any(part in ("MMM", "MMMM") for part in parts) else "."
        expected = separator.join(tokens[part] for part in parts)
        argument = f"{value.isoformat()}, {'.'.join(parts)}"
        assert function(argument) == expected, argument


TIME_FORMATS = sorted(
    {
        parts
        for hour, minute, second in itertools.product(
            ["h", "hh", "H", "HH"], ["m", "mm"], ["s", "ss"]
        )
        for length in (2, 3)
        for parts in itertools.permutations((hour, minute, second), length)
    }
)


def test_format_time():
    function = module.date_and_time_match("format_time")
    for i in range(10_000):
        value = sample_datetime(i)
        parts = TIME_FORMATS[i % len(TIME_FORMATS)]
        values = {
            "H": value.hour,
            "h": value.hour % 12 or 12,
            "m": value.minute,
            "s": value.second,
        }
        expected = ":".join(str(values[part[0]]).zfill(len(part)) for part in parts)
        if any(part in ("h", "hh") for part in parts):
            expected += " AM" if value.hour < 12 else " PM"
        argument = f"{value.hour}:{value.minute}:{value.second}, {':'.join(parts)}"
        assert function(argument) == expected, argument


def test_make_date():
    function = module.date_and_time_match("make_date")
    for i in range(10_000):
        value = sample_datetime(i).date()
        argument = f"{value.year:04}, {value.month}, {value.day}"
        assert function(argument) == value.isoformat(), argument


def test_to_date():
    function = module.date_and_time_match("to_date")
    for i in range(10_000):
        value = sample_datetime(i).date()
        inputs = [
            value.isoformat(),
            f"{value.day}-{value.month}-{value.year:04}",
            f"{value.year:04} {MONTHS[value.month - 1]} {value.day}",
            f"{value.day} {MONTHS[value.month - 1]} {value.year:04}",
        ]
        argument, expected = inputs[i % 4], value.isoformat()
        if i % 3:
            parts, tokens = date_format(i), date_tokens(value)
            separator = " " if any(part in ("MMM", "MMMM") for part in parts) else "-"
            expected = separator.join(tokens[part] for part in parts)
            argument += f", {'.'.join(parts)}"
        assert function(argument) == expected, argument


def test_make_datetime():
    function = module.date_and_time_match("make_datetime")
    for i in range(10_000):
        value = sample_datetime(i).replace(microsecond=0)
        argument = f"{value.year:04}, {value.month}, {value.day}, {value.hour}, {value.minute}, {value.second}"
        assert function(argument) == value.isoformat(sep=" "), argument


def test_to_datetime():
    function = module.date_and_time_match("to_datetime")
    for i in range(10_000):
        value = sample_datetime(i)
        mode = i % 6
        if mode == 0:
            argument = value.isoformat(sep="T" if i % 2 else " ")
        elif mode == 1:
            argument = value.date().isoformat()
            value = value.replace(hour=0, minute=0, second=0, microsecond=0)
        elif mode == 2:
            argument = (
                f"{value.day}-{value.month}-{value.year:04} {value.hour}:{value.minute}"
            )
            value = value.replace(second=0, microsecond=0)
        elif mode == 3:
            month = MONTHS[value.month - 1]
            month = month[:3].lower() if i % 4 else month
            argument = f"{value.day} {month} {value.year:04} {value.hour}:{value.minute}:{value.second}"
            value = value.replace(microsecond=0)
        elif mode == 4:
            month_token = ["M", "MM", "MMM", "MMMM"][(i // 6) % 4]
            parts = ["dd", month_token, "yy" if i % 4 else "yyyy", "H", "mm", "ss"]
            shift = (i // 24) % len(parts)
            parts = parts[shift:] + parts[:shift]
            if i % 5 == 0:
                parts.insert(0, "dddd" if i % 2 else "ddd")
            tokens = date_tokens(value) | {
                "H": str(value.hour),
                "mm": f"{value.minute:02}",
                "ss": f"{value.second:02}",
            }
            separator = ["/", "-", ".", " ", ":"][(i // 6) % 5]
            text = separator.join(tokens[part] for part in parts)
            argument = f"{text}, {separator.join(parts)}"
            value = value.replace(microsecond=0)
        else:
            # Obecna implementacja rozpoznaje ISO także przy podaniu innego układu.
            argument = f"{value.isoformat(sep=' ')}, dd.MM.yyyy"
        result = function(argument)
        assert type(result) is dt.datetime
        assert result == value, argument


@pytest.mark.parametrize("name", ["make_interval", "to_interval"])
def test_intervals(name):
    function = module.date_and_time_match(name)
    for i in range(10_000):
        first = i % 7
        pairs = [(UNITS[first], i / 8)]
        if first < 6:
            pairs = [
                (UNITS[first], [0.0, 0.5, 1.0, i / 8][i % 4]),
                (UNITS[first + 1], (i + 1) / 16),
            ]
        if i % 2:
            pairs.reverse()
        total = sum(value * SECONDS[unit] for unit, value in pairs)
        output_index = first
        # Zmiana jednostki jest oceniana kolejno w porządku podanych parametrów.
        for unit, value in pairs:
            if (
                UNITS[output_index] == unit
                and value < 1
                and output_index < 6
                and total < SECONDS[unit]
            ):
                output_index += 1
        expected = quantity(
            total / SECONDS[UNITS[output_index]], UNITS[output_index] + "s"
        )
        if name == "make_interval":
            argument = ", ".join(f"{unit}s={value}" for unit, value in pairs)
            if i % 5 == 0:
                argument = f"{pairs[0][0]}s=999, " + argument
        else:
            argument = " ".join(f"{value} {unit}s" for unit, value in pairs)
            if i % 5 == 0:
                argument = f"999 {pairs[0][0]}s " + argument
        assert function(argument) == expected, argument


@pytest.mark.parametrize("unit", UNITS)
def test_date_parts(unit):
    function = module.date_and_time_match(unit)
    for i in range(10_000):
        value = sample_datetime(i)
        mode = i % 4
        if mode == 0 or (mode == 1 and unit in ("year", "month", "week", "day")):
            argument = (
                value.isoformat(sep=" ") if mode == 0 else value.date().isoformat()
            )
            number = (
                value.isocalendar().week if unit == "week" else getattr(value, unit)
            )
        elif mode == 3:
            argument = dt.timedelta(days=i - 5000, seconds=i * 7, microseconds=i)
            number = argument.total_seconds() / SECONDS[unit]
        else:
            source_unit = UNITS[(i // 4) % 7]
            amount = i / 8
            suffix = "s" if (i // 4) % 2 else ""
            amount_text = f"{amount:e}" if i % 5 == 0 else str(amount)
            argument = f"{amount_text} {source_unit}{suffix}"
            number = amount * SECONDS[source_unit] / SECONDS[unit]
        expected = quantity(number, unit + ("" if number == 1 else "s"))
        assert function(argument) == expected, (unit, argument)


def test_make_time():
    function = module.date_and_time_match("make_time")
    for i in range(10_000):
        value = sample_datetime(i).time().replace(microsecond=0)
        seconds = str(value.second)
        if i % 2:
            fraction = f"{i * 7919:09}"
            seconds += "." + fraction
            value = value.replace(microsecond=int(fraction[:3]) * 1000)
        argument = f"{value.hour}, {value.minute}, {seconds}"
        assert function(argument) == value.isoformat(timespec="milliseconds"), argument


def test_to_time():
    function = module.date_and_time_match("to_time")
    orders = list(itertools.permutations(("HH", "mm", "ss")))
    for i in range(10_000):
        if i < 1440:
            value = dt.time(i // 60, i % 60)
            argument = f"{value.hour:02}:{value.minute:02}, HH:mm"
        else:
            value = sample_datetime(i).time().replace(microsecond=0)
            parts = orders[i % 6]
            tokens = {
                "HH": f"{value.hour:02}",
                "mm": f"{value.minute:02}",
                "ss": f"{value.second:02}",
            }
            text = ":".join(tokens[part] for part in parts)
            format_text = ":".join(parts)
            if i % 2:
                format_text = (
                    format_text.replace("HH", "hh")
                    .replace("mm", "MM")
                    .replace("ss", "SS")
                )
            argument = f"{text}, {format_text}"
        result = function(argument)
        assert type(result) is dt.time
        assert result == value, argument


def test_now(monkeypatch):
    class Clock:
        current = None

        @classmethod
        def now(cls):
            return cls.current

    monkeypatch.setattr(module, "dt", SimpleNamespace(datetime=Clock))
    function = module.date_and_time_match("now")
    for i in range(10_000):
        Clock.current = sample_datetime(i)
        assert function("") == Clock.current.isoformat(sep=" "), Clock.current


NAMES = [
    "age",
    "datetime_from_epoch",
    "day_of_week",
    "epoch",
    "format_date",
    "format_time",
    "make_date",
    "to_date",
    "make_datetime",
    "to_datetime",
    "make_interval",
    "to_interval",
    *UNITS,
    "make_time",
    "to_time",
    "now",
]


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("argument", ["garbage", "1, 2, 3, 4, 5, 6, 7, 8"])
def test_invalid_input(name, argument):
    with pytest.raises(ValueError):
        module.date_and_time_match(name)(argument)


@pytest.mark.parametrize(
    "name, argument",
    [
        ("age", "2026-01-01, 2026-01-02"),
        ("age", "2026-01-01T00:00:00, 2026-01-01"),
        ("age", "2026-02-30, 2026-01-01"),
        ("datetime_from_epoch", "-1"),
        ("datetime_from_epoch", "1.5"),
        ("datetime_from_epoch", "999999999999999999999999999999"),
        ("day_of_week", "2026-02-29"),
        ("day_of_week", "2026-1-1"),
        ("epoch", "2026-01-01"),
        ("epoch", "2026-01-01 24:00:00"),
        ("format_date", "2026-01-01, dd.MM"),
        ("format_date", "2026-1-01, dd.MM.yyyy"),
        ("format_date", "2026-01-01, xx.MM.yyyy"),
        ("format_date", "2026-01-01, dd.dd.yyyy"),
        ("format_date", "2026-02-30, dd.MM.yyyy"),
        ("format_time", "24:00:00, HH:mm:ss"),
        ("format_time", "12:00, HH:mm"),
        ("format_time", "12:00:00, HH:HH"),
        ("format_time", "12:00:00, xx:mm:ss"),
        ("make_date", "1900, 2, 29"),
        ("make_date", "0000, 1, 1"),
        ("make_date", "2026, 13, 1"),
        ("make_date", "2026, 1, 0"),
        ("to_date", "2026-01-01, wrong"),
        ("to_date", "2026-01-01, dd.MM.yyyy, x"),
        ("to_date", "1 Unknown 2026"),
        ("to_date", "2026-02-29"),
        ("make_datetime", "2026, 1, 1, 24, 0, 0"),
        ("make_datetime", "2026, 1, 1, 0, 60, 0"),
        ("make_datetime", "2026, 1, 1, 0, 0, 60"),
        ("to_datetime", ""),
        ("to_datetime", "2026-01-01, HH:mm"),
        ("to_datetime", "2026-01-01, yyyy-MM-dd-dd"),
        ("to_datetime", "2026-01-01, yyyy-MM-dd, x"),
        ("to_datetime", "2026-01-01 00:00:00.1234567"),
        ("to_datetime", "2026-01-01, xyz"),
        ("to_datetime", "2026-13-01"),
        ("to_datetime", "2026-01-01 24:00:00"),
        ("to_datetime", "01 Foo 2026, dd MMM yyyy"),
        ("to_datetime", "01 January 2026, dd MMM yyyy"),
        ("to_datetime", "Friday 01 January 2026, dddd dd MMMM yyyy"),
        ("to_datetime", "01 Jan 2026 12, dd MMM yyyy"),
        ("to_datetime", "1 Foo 2026"),
        ("to_datetime", "01@Jan@2026, dd.MMM.yyyy"),
        ("to_datetime", "1 Jan 2026, dd MMM yyyy"),
        ("to_datetime", "Bogus 01 Jan 2026, ddd dd MMM yyyy"),
        ("to_datetime", "Bogus 01 Jan 2026, dddd dd MMM yyyy"),
        ("to_datetime", "01 1 2026, dd MM yyyy"),
        ("to_datetime", "01 Foo 2026, dd MMMM yyyy"),
        ("to_datetime", "01 Jan 2026, dd MMM yy"),
        ("to_datetime", "01 Jan 26, dd MMM yyyy"),
        ("to_datetime", "01 Jan 2026 1, dd MMM yyyy HH"),
        ("to_datetime", "01 Jan 2026 1, dd MMM yyyy mm"),
        ("to_datetime", "01 Jan 2026 1, dd MMM yyyy ss"),
        ("make_interval", "days=-1"),
        ("make_interval", "days=nan"),
        ("make_interval", "days=inf"),
        ("make_interval", "day=1"),
        ("make_interval", "days="),
        ("make_interval", "days=1=2"),
        ("to_interval", "-1 days"),
        ("to_interval", "nan days"),
        ("to_interval", "inf days"),
        ("to_interval", "1 day"),
        ("to_interval", "1 days 2"),
        ("to_interval", "1  days"),
        ("make_time", "24, 0, 0"),
        ("make_time", "0, 60, 0"),
        ("make_time", "0, 0, 60"),
        ("make_time", "-1, 0, 0"),
        ("to_time", "24:00, HH:mm"),
        ("to_time", "00:60, HH:mm"),
        ("to_time", "00:60, HH:ss"),
        ("to_time", "12:00, HH:hh"),
        ("to_time", "12:00, HH:HH"),
        ("to_time", "12:00, mm:MM"),
        ("to_time", "12:00, HH:mm:ss"),
        ("to_time", "12:00:00, HH:mm"),
        ("to_time", "1:00, HH:mm"),
        ("to_time", "12:00, H:m"),
        ("to_time", "12:00, wrong"),
        ("now", " "),
        ("now", "0"),
    ],
)
def test_errors(name, argument):
    with pytest.raises(ValueError):
        module.date_and_time_match(name)(argument)


@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize(
    "argument", ["-1 days", "1 fortnight", "2026-02-30", "", "nan seconds"]
)
def test_date_parts_invalid_input(unit, argument):
    with pytest.raises(ValueError):
        module.date_and_time_match(unit)(argument)


@pytest.mark.parametrize("unit", ["hour", "minute", "second"])
def test_date_without_time(unit):
    with pytest.raises(ValueError):
        module.date_and_time_match(unit)("2026-01-01")


@pytest.mark.parametrize("unit", UNITS)
def test_exact_timedelta_unit(unit):
    argument = dt.timedelta(seconds=SECONDS[unit])
    assert module.date_and_time_match(unit)(argument) == f"1 {unit}"


@pytest.mark.parametrize(
    "name, argument, expected",
    [
        ("age", "2000-02-29, 2000-02-29", dt.timedelta(0)),
        ("make_date", "2000, 2, 29", "2000-02-29"),
        ("make_date", "0001, 1, 1", "0001-01-01"),
        ("make_date", "9999, 12, 31", "9999-12-31"),
        ("make_datetime", "0001, 1, 1, 0, 0, 0", "0001-01-01 00:00:00"),
        ("make_datetime", "9999, 12, 31, 23, 59, 59", "9999-12-31 23:59:59"),
        ("make_time", "0, 0, 0", "00:00:00.000"),
        ("make_time", "23, 59, 59.999999", "23:59:59.999"),
        ("make_time", "1, 2, 3.1", "01:02:03.100"),
        ("make_time", "1, 2, 3.12", "01:02:03.120"),
        ("to_time", "59:23, ss:HH", dt.time(23, 0, 59)),
        ("to_time", "59:58, mm:ss", dt.time(0, 59, 58)),
        ("to_time", "23:59, hh:MM", dt.time(23, 59)),
        ("to_time", "59:23, MM:hh", dt.time(23, 59)),
        ("to_time", "58:59, SS:MM", dt.time(0, 59, 58)),
        ("format_time", "0:0:0, h:mm:ss", "12:00:00 AM"),
        ("format_time", "12:0:0, hh:mm:ss", "12:00:00 PM"),
        ("format_time", "0:0:0, H:m:s", "0:0:0"),
        ("format_date", "0001-01-01, yyyy.MM.dd", "0001.01.01"),
        ("to_date", "2026-01-01, dd.dd.yyyy", "01-01-2026"),
        (
            "to_datetime",
            "29 February 2000 23:59:59",
            dt.datetime(2000, 2, 29, 23, 59, 59),
        ),
        ("to_datetime", "1.1.68, d.M.yy", dt.datetime(2068, 1, 1)),
        ("to_datetime", "1.1.69, d.M.yy", dt.datetime(1969, 1, 1)),
        ("to_datetime", "2026-1-1T1:2:3.1", dt.datetime(2026, 1, 1, 1, 2, 3, 100000)),
        ("week", "2021-01-01", "53 weeks"),
        ("week", "2021-01-04", "1 week"),
        ("day", "1 day", "1 day"),
        ("hour", "0 seconds", "0 hours"),
        ("make_interval", "days=0", "0 hours"),
        ("make_interval", "seconds=0", "0 seconds"),
        ("make_interval", "days=1, days=2", "2 days"),
        ("to_interval", "1 days 2 days", "2 days"),
        ("to_interval", "0 days", "0 hours"),
    ],
)
def test_boundaries(name, argument, expected):
    result = module.date_and_time_match(name)(argument)
    assert type(result) is type(expected)
    assert result == expected


@pytest.mark.skipif(
    not hasattr(time, "tzset"), reason="System nie udostępnia time.tzset"
)
@pytest.mark.parametrize("zone", ["UTC", "Europe/Warsaw"])
def test_epoch_timezone(zone, monkeypatch):
    monkeypatch.setenv("TZ", zone)
    time.tzset()
    # W Warszawie te chwile leżą po obu stronach zmian czasu w marcu i październiku.
    for value in [
        dt.datetime(2026, 3, 29, 0, 30, tzinfo=dt.UTC),
        dt.datetime(2026, 3, 29, 1, 30, tzinfo=dt.UTC),
        dt.datetime(2026, 10, 25, 0, 30, tzinfo=dt.UTC),
        dt.datetime(2026, 10, 25, 2, 30, tzinfo=dt.UTC),
    ]:
        seconds = int(value.timestamp())
        expected = value.astimezone().replace(tzinfo=None).isoformat(sep=" ")
        assert (
            module.date_and_time_match("datetime_from_epoch")(str(seconds)) == expected
        )
        assert module.date_and_time_match("epoch")(expected) == seconds


@pytest.mark.parametrize("name", ["", "unknown", None])
def test_unknown_function(name):
    assert module.date_and_time_match(name) is None
