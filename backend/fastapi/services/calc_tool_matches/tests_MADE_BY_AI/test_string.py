import json
import re

import pytest
from services.calc_tool_matches.string import json_path, string_match

with json_path.open(encoding="utf-8") as file:
    ASCII_ROWS = json.load(file)["ASCII"]

# Powtarzające się symbole w tabeli wskazują pierwszy pasujący wiersz.
ASCII_SYMBOLS = {}
for row in ASCII_ROWS:
    ASCII_SYMBOLS.setdefault(row[4], int(row[0]))


@pytest.mark.parametrize("symbol, expected", ASCII_SYMBOLS.items())
def test_ascii(symbol, expected):
    assert string_match("ascii")(symbol) == expected


@pytest.mark.parametrize("row", ASCII_ROWS, ids=lambda row: row[0])
def test_char(row):
    assert string_match("char")(row[0]) == row[4]


def test_concat():
    function = string_match("concat")
    for i in range(10_000):
        args = (f"Zażółć🙂{i}", "", i, None, True)[: 2 + i % 4]
        expected = "".join(map(str, args))
        assert function(*args) == expected, args


def test_format():
    function = string_match("format")
    for i in range(10_000):
        a, b = f"żółć{i}", f"🙂{i}"
        variants = [
            (f"%2/%1/%2/%3, {a}, {b}", f"{b}/{a}/{b}/%3"),
            (f"%2/%1, {a},{b}", f"{b}/{a}"),
            (f"brak pól {i}, {a}", f"brak pól {i}"),
            (f"%0 %% %1 %01, {a}", f"%0 %% {a} %01"),
            (f"%10-%1-%11, {', '.join([a] * 10)}", f"{a}-{a}-%11"),
        ]
        argument, expected = variants[i % len(variants)]
        assert function(argument) == expected, argument


def test_format_number():
    function = string_match("format_number")
    for i in range(10_000):
        number = (i - 5000) * 123.125
        places = i % 7
        separated, trimmed = bool(i % 2), bool(i % 3)
        expected = format(number, f"{',' if separated else ''}.{places}f").replace(
            ",", " "
        )
        if trimmed and "." in expected:
            expected = expected.rstrip("0").rstrip(".")
        options = {
            "add_space_separator": " TRUE " if separated else False,
            "trim_trailing_zeros": True if trimmed else "false",
        }
        assert function(str(number), str(places), **options) == expected, (
            number,
            places,
            options,
        )


@pytest.mark.parametrize("name", ["left", "right"])
def test_left_right(name):
    function = string_match(name)
    for i in range(10_000):
        text = f"Zażółć🙂{i}" * (1 + i % 4)
        length = i % 81 - 40 if name == "left" else 1 + i % 81
        expected = text[:length] if name == "left" else text[-length:]
        argument = f"{text}, {length}"
        assert function(argument) == expected, argument


@pytest.mark.parametrize(
    "name, operation",
    [
        ("length", len),
        ("lower", str.lower),
        ("upper", str.upper),
        ("title", str.title),
        ("trim", str.strip),
    ],
)
def test_single_value(name, operation):
    function = string_match(name)
    for i in range(10_000):
        values = [f" \tZaŻÓŁĆ straße İΣ🙂 {i}\n", i, -i / 8, [i, None], {"a": i}]
        argument = values[i % len(values)]
        assert function(argument) == operation(str(argument)), argument


@pytest.mark.parametrize("name", ["lpad", "rpad"])
def test_padding(name):
    function = string_match(name)
    for i in range(10_000):
        text = f"a, 🙂{i}" if i % 2 else f"żółć{i}"
        width, pad = i % 61, "0ż🙂 "[i % 4]
        expected = pad * max(0, width - len(text))
        expected = expected + text if name == "lpad" else text + expected
        argument = f"{text}, {width}, {pad}"
        assert function(argument) == expected, argument


def test_ltrim():
    function = string_match("ltrim")
    for i in range(10_000):
        text = f"xyxy \tżółć{i}xy "
        args = (text,) if i % 2 else (text, "xy ")
        expected = text.lstrip() if len(args) == 1 else f"\tżółć{i}xy "
        assert function(*args) == expected, args


@pytest.mark.parametrize("name", ["regexp_match", "regexp_replace", "regexp_substr"])
def test_regexp(name):
    function = string_match(name)
    for i in range(10_000):
        text = f"zażółć{i}:abc{i}🙂"
        pattern = [r"\d+", r"abc\d+", "missing", "", r"(żółć)(\d+)", r"\w+$"][i % 6]
        flag = ["", r"\b", ".?"][i % 3]
        combined = f"(?:{flag})(?:{pattern})(?:{flag})"
        if name == "regexp_substr":
            match = re.search(pattern, text)
            args, expected = (text, pattern), match.group(0) if match else ""
        elif name == "regexp_match":
            match = re.search(combined, text)
            args, expected = (text, pattern, flag), match.start() if match else -1
        else:
            replacement = f"wynik{i}" if i % 2 else r"[\g<0>]"
            args = (text, pattern, replacement, flag)
            expected = re.sub(combined, replacement, text)
        assert function(*args) == expected, args


def test_replace():
    function = string_match("replace")
    for i in range(10_000):
        text = f"ab🙂{i}, Łódźab"
        old = ["ab", "🙂", "missing", "", ", "][i % 5]
        new = f"ż{i}, " if i % 2 else ""
        args = (text, old, new)
        assert function(*args) == text.replace(old, new), args


def test_rtrim():
    function = string_match("rtrim")
    for i in range(10_000):
        text = f" żółć{i} \txyxy" if i % 2 else f"żółć{i}\t \n"
        argument = f"{text}, xy" if i % 2 else text
        expected = f" żółć{i} \t" if i % 2 else f"żółć{i}"
        assert function(argument) == expected, argument


def test_strpos():
    function = string_match("strpos")
    for i in range(10_000):
        text = f"żółć{i}🙂żółć"
        substring = ["żółć", str(i), "🙂", "missing"][i % 4]
        argument = f"{text}, {substring}"
        assert function(argument) == text.find(substring), argument


def test_substr():
    function = string_match("substr")
    for i in range(10_000):
        text = f"żółć🙂{i}"
        start, length = i % 41 - 20, i % 31 - 15
        argument = f"{text}, {start}"
        expected = text[start:]
        if i % 2:
            argument += f", {length}"
            expected = text[start : start + length]
        assert function(argument) == expected, argument


def test_to_string():
    function = string_match("to_string")
    for i in range(10_000):
        value = (i - 5000) / 8
        argument = [str(value), f"{value:e}", f"  {value}  "][i % 3]
        assert function(argument) == str(value), argument


def test_worldwrap():
    function = string_match("worldwrap")
    for i in range(10_000):
        text = f"Zażółć gęślą🙂{i}" * (1 + i % 5)
        width = 1 + i % 31
        argument = f"{text}, {width}"
        expected = "\n".join(
            text[start : start + width] for start in range(0, len(text), width)
        )
        assert function(argument) == expected, argument


@pytest.mark.parametrize(
    "name, args, error",
    [
        ("ascii", (), ValueError),
        ("ascii", ("a", "b"), ValueError),
        ("ascii", ("🙂",), ValueError),
        ("char", ("-1",), ValueError),
        ("char", ("256",), ValueError),
        ("char", ("1.5",), ValueError),
        ("char", (None,), TypeError),
        ("concat", (), ValueError),
        ("concat", ("one",), ValueError),
        ("format", ("%1",), ValueError),
        ("format", ("%1, ",), ValueError),
        ("format", ("%1, a, ",), ValueError),
        ("format_number", ("1",), ValueError),
        ("format_number", ("x", "2"), ValueError),
        ("format_number", ("1", "1.5"), ValueError),
        ("format_number", ("1", "-1"), ValueError),
        ("left", ("abc",), ValueError),
        ("left", ("abc, x",), ValueError),
        ("left", (", 1",), ValueError),
        ("left", ("abc, ",), ValueError),
        ("lpad", ("a, 2",), ValueError),
        ("lpad", ("a, -1, x",), ValueError),
        ("lpad", ("a, x, _",), ValueError),
        ("lpad", ("a, 5, xy",), TypeError),
        ("ltrim", (), ValueError),
        ("ltrim", ("a", "b", "c"), ValueError),
        ("regexp_match", ("a", "a"), ValueError),
        ("regexp_match", ("a", "[", ""), ValueError),
        ("regexp_match", ("a", "a", "(?i)"), ValueError),
        ("regexp_replace", ("a", "a", "b"), ValueError),
        ("regexp_replace", ("a", "[", "b", ""), ValueError),
        ("regexp_replace", ("a", "a", r"\2", ""), ValueError),
        ("regexp_substr", ("a",), ValueError),
        ("regexp_substr", ("a", "["), ValueError),
        ("replace", (), ValueError),
        ("replace", ("a, b",), ValueError),
        ("replace", ("a", "b"), ValueError),
        ("replace", ("a", "b", "c", "d"), ValueError),
        ("right", ("a",), ValueError),
        ("right", ("a, 0",), ValueError),
        ("right", ("a, -1",), ValueError),
        ("right", ("a, x",), ValueError),
        ("right", (", 1",), ValueError),
        ("rpad", ("a, 2",), ValueError),
        ("rpad", ("a, -1, x",), ValueError),
        ("rpad", ("a, x, _",), ValueError),
        ("rpad", ("a, 5, ",), TypeError),
        ("rtrim", ("",), ValueError),
        ("rtrim", ("a, b, c",), ValueError),
        ("strpos", ("a",), ValueError),
        ("strpos", ("a, ",), ValueError),
        ("strpos", (", a",), ValueError),
        ("substr", ("a",), ValueError),
        ("substr", ("a, x",), ValueError),
        ("substr", ("a, 0, x",), ValueError),
        ("substr", ("a, 0, 1, 2",), ValueError),
        ("to_string", ("a",), ValueError),
        ("to_string", ("1, 2",), ValueError),
        ("worldwrap", ("a",), ValueError),
        ("worldwrap", ("a, 0",), ValueError),
        ("worldwrap", ("a, -1",), ValueError),
        ("worldwrap", ("a, x",), ValueError),
    ],
)
def test_invalid_arguments(name, args, error):
    with pytest.raises(error):
        string_match(name)(*args)


@pytest.mark.parametrize("name", ["length", "lower", "upper", "title", "trim"])
@pytest.mark.parametrize("args", [(), ("a", "b")])
def test_single_value_invalid_count(name, args):
    with pytest.raises(ValueError, match="exactly one argument"):
        string_match(name)(*args)


@pytest.mark.parametrize(
    "options",
    [
        {"unknown": True},
        {"add_space_separator": "yes"},
        {"trim_trailing_zeros": 1},
        {"add_space_separator": None},
    ],
)
def test_format_number_invalid_options(options):
    with pytest.raises(ValueError, match="Invalid format_number option"):
        string_match("format_number")("1", "2", **options)


@pytest.mark.parametrize(
    "name, args, expected",
    [
        ("length", ("",), 0),
        ("lower", (None,), "none"),
        ("upper", ("straße",), "STRASSE"),
        ("title", ("",), ""),
        ("trim", ("\u2003\t\n",), ""),
        ("replace", ("ALA_NOWAK, ŁÓDŹ", "_", " "), "ALA NOWAK, ŁÓDŹ"),
        ("replace", ("a, b, c", ", ", " / "), "a / b / c"),
        ("replace", ("", "", "x"), "x"),
        ("replace", (123, 2, 0), "103"),
        ("left", ("abc, 0",), ""),
        ("ltrim", ("xxabc", ""), "xxabc"),
        ("rtrim", ("abc, ",), "abc"),
        ("lpad", (", 0, _",), ""),
        ("rpad", (", 0, _",), ""),
        ("substr", ("abc, -2, 1",), "b"),
        ("worldwrap", (", 1",), ""),
        ("substr", (", 0",), ""),
        ("substr", (", -1, 2",), ""),
        ("char", (65.9,), "A"),
        ("char", (" +065 ",), "A"),
        ("ascii", (7,), 55),
        ("ascii", ("",), 127),
        ("to_string", ("-0",), "-0.0"),
        ("format_number", ("2.5", 0), "2"),
        ("format_number", ("3.5", 0), "4"),
        ("format_number", ("inf", 2), "inf"),
        ("format_number", ("nan", 2), "nan"),
        ("to_string", ("nan",), "nan"),
        ("to_string", ("-inf",), "-inf"),
    ],
)
def test_boundaries(name, args, expected):
    result = string_match(name)(*args)
    assert type(result) is type(expected)
    assert result == expected


@pytest.mark.parametrize("name", ["", "unknown", "wordwrap", None])
def test_unknown_function(name):
    assert string_match(name) is None
