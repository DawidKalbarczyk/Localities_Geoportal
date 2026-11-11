import copy
import json
from html import escape
from urllib.parse import quote, urlencode

import pytest
from services.calc_tool_matches.dictionary import dictionary_match
from sympy import Float, Integer, Rational, Symbol, false, true


def sample_map(i):
    return {f"klucz<&{i}>": f"Zażółć '🙂' <b>{i}</b>", "number": i - 5000}


def test_from_json():
    function = dictionary_match("from_json")
    for i in range(10_000):
        expected = sample_map(i) | {"nested": [i, None, True, {"fraction": i / 8}]}
        argument = json.dumps(expected, ensure_ascii=bool(i % 2))
        assert function(argument) == expected, argument


def test_map():
    function = dictionary_match("map")
    for i in range(10_000):
        key, value = f"klucz{i}", [i, None, True]
        args = (key, value, "number", -i)
        expected = {key: value, "number": -i}
        if i % 2:
            args += (key, i)
            expected[key] = i
        assert function(*args) == expected, args


@pytest.mark.parametrize("name", ["map_akeys", "map_avals"])
def test_keys_values(name):
    function = dictionary_match(name)
    for i in range(10_000):
        source = sample_map(i)
        expected = (
            [f"klucz<&{i}>", "number"]
            if name == "map_akeys"
            else [f"Zażółć '🙂' <b>{i}</b>", i - 5000]
        )
        assert function(source) == expected, source


def test_map_concat():
    function = dictionary_match("map_concat")
    for i in range(10_000):
        source = sample_map(i)
        args = (source, {"number": i, "extra": None}, {})
        expected = {
            f"klucz<&{i}>": f"Zażółć '🙂' <b>{i}</b>",
            "number": i,
            "extra": None,
        }
        result = function(*args)
        assert result == expected, args
        assert source == sample_map(i), args
        assert result is not source


def test_map_delete():
    function = dictionary_match("map_delete")
    for i in range(10_000):
        source = sample_map(i)
        key = f"klucz<&{i}>" if i % 2 else "number"
        expected = (
            {"number": i - 5000}
            if i % 2
            else {f"klucz<&{i}>": f"Zażółć '🙂' <b>{i}</b>"}
        )
        result = function(source, key)
        assert result == expected, (source, key)
        assert source == sample_map(i), (source, key)
        assert result is not source


def test_map_get():
    function = dictionary_match("map_get")
    for i in range(10_000):
        source = sample_map(i)
        key = f"klucz<&{i}>" if i % 2 else "number"
        expected = f"Zażółć '🙂' <b>{i}</b>" if i % 2 else i - 5000
        result = function(source, key)
        assert type(result) is type(expected)
        assert result == expected, (source, key)


def test_map_exist():
    function = dictionary_match("map_exist")
    for i in range(10_000):
        source = {f"key{i}": f"value{i}"}
        key = f"key{i}" if i % 2 else f"value{i}"
        result = function(source, key)
        assert type(result) is bool
        assert result is bool(i % 2), (source, key)


def test_map_insert():
    function = dictionary_match("map_insert")
    for i in range(10_000):
        source = sample_map(i)
        key = "number" if i % 2 else f"new{i}"
        value = [i, None, {"flag": True}]
        expected = source | {key: value}
        result = function(source, key, value)
        assert result == expected, (source, key, value)
        assert source == sample_map(i), (source, key, value)
        assert result is not source


def test_map_prefix_keys():
    function = dictionary_match("map_prefix_keys")
    for i in range(10_000):
        source = sample_map(i)
        prefix = f"prefix{i}, "
        expected = {
            f"{prefix}klucz<&{i}>": f"Zażółć '🙂' <b>{i}</b>",
            f"{prefix}number": i - 5000,
        }
        result = function(source, prefix)
        assert result == expected, (source, prefix)
        assert source == sample_map(i), (source, prefix)
        assert result is not source


@pytest.mark.parametrize("name", ["map_to_html_dl", "map_to_html_table"])
def test_map_to_html(name):
    function = dictionary_match(name)
    for i in range(10_000):
        source = sample_map(i)
        key, value = escape(f"klucz<&{i}>"), escape(f"Zażółć '🙂' <b>{i}</b>")
        if name == "map_to_html_dl":
            expected = f"<dl><dt>{key}</dt><dd>{value}</dd><dt>number</dt><dd>{i - 5000}</dd></dl>"
        else:
            expected = (
                f"<table><thead><tr><th>{key}</th><th>number</th></tr></thead>"
                f"<tbody><tr><td>{value}</td><td>{i - 5000}</td></tr></tbody></table>"
            )
        assert function(source) == expected, source


def test_to_json():
    function = dictionary_match("to_json")
    for i in range(10_000):
        source = {
            "values": [
                Integer(i),
                Float(str(i / 8)),
                Rational(i, 2),
                true if i % 2 else false,
                None,
            ],
            "nested": {Integer(i): (Integer(-i), true, false)},
            "text": f"Zażółć🙂{i}",
        }
        expected = {
            "values": [i, i / 8, i / 2 if i % 2 else i // 2, bool(i % 2), None],
            "nested": {str(i): [-i, True, False]},
            "text": f"Zażółć🙂{i}",
        }
        result = function(source)
        assert result == json.dumps(expected), source
        decoded = json.loads(result)
        assert type(decoded["values"][0]) is int
        assert type(decoded["values"][1]) is float
        assert type(decoded["values"][3]) is bool


def test_url_encode():
    function = dictionary_match("url_encode")
    for i in range(10_000):
        source = {f"a&+b{i}": f"Zażółć 🙂 {i} + &=", "number": i}
        expected = urlencode(source, quote_via=quote, safe="+")
        assert function(source) == expected, source


@pytest.mark.parametrize(
    "argument, expected",
    [
        ('"Zażółć🙂"', "Zażółć🙂"),
        ('""', ""),
        ("null", None),
        ("true", True),
        ("false", False),
        ("123", 123),
        ("-1.5", -1.5),
        ("[]", []),
        ("{}", {}),
        (" [1, null, false] ", [1, None, False]),
    ],
)
def test_from_json_value_types(argument, expected):
    result = dictionary_match("from_json")(argument)
    assert type(result) is type(expected)
    assert result == expected


@pytest.mark.parametrize(
    "name, args, expected",
    [
        ("map_akeys", ({},), []),
        ("map_avals", ({},), []),
        ("map_concat", (), {}),
        ("map_concat", ({},), {}),
        ("map_concat", ({"a": 1}, {"a": None}), {"a": None}),
        ("map_get", ({"a": None}, "a"), None),
        ("map_exist", ({}, "missing"), False),
        ("map_exist", ({"a": "abc"}, "ab"), False),
        ("map_insert", ({}, "a", None), {"a": None}),
        ("map_prefix_keys", ({"a": 1}, ""), {"a": 1}),
        ("map_to_html_dl", ({},), "<dl></dl>"),
        (
            "map_to_html_dl",
            ({"<key>": "<b>Jan & Ola</b>"},),
            "<dl><dt>&lt;key&gt;</dt><dd>&lt;b&gt;Jan &amp; Ola&lt;/b&gt;</dd></dl>",
        ),
        (
            "map_to_html_table",
            ({},),
            "<table><thead><tr></tr></thead><tbody><tr></tr></tbody></table>",
        ),
        (
            "map_to_html_table",
            ({"a": 1},),
            "<table><thead><tr><th>a</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table>",
        ),
        ("to_json", ({},), "{}"),
        ("to_json", ([],), "[]"),
        ("to_json", ((Integer(1), false),), "[1, false]"),
        ("to_json", (true,), "true"),
        ("to_json", (false,), "false"),
        ("url_encode", ({},), ""),
        (
            "url_encode",
            ({"imie": "Jan Kowalski", "wiek": 25},),
            "imie=Jan%20Kowalski&wiek=25",
        ),
        (
            "url_encode",
            ({"a&+b": "a and plus b", "a=b": "a equals b"},),
            "a%26+b=a%20and%20plus%20b&a%3Db=a%20equals%20b",
        ),
    ],
)
def test_boundaries(name, args, expected):
    result = dictionary_match(name)(*args)
    assert type(result) is type(expected)
    assert result == expected


@pytest.mark.parametrize(
    "name, args, error",
    [
        ("from_json", (None,), ValueError),
        ("from_json", ("",), ValueError),
        ("from_json", ("{",), ValueError),
        ("from_json", ('{"a":}',), ValueError),
        ("from_json", ("true false",), ValueError),
        ("from_json", ({},), TypeError),
        ("map", (), ValueError),
        ("map", ("a",), ValueError),
        ("map", ("a", 1, "b"), ValueError),
        ("map", (None, 1), ValueError),
        ("map", ("", 1), ValueError),
        ("map", ([], 1), TypeError),
        ("map_delete", ({"a": 1}, "missing"), ValueError),
        ("map_get", ({"a": 1}, "missing"), ValueError),
        ("map_get", ({"a": 1}, []), TypeError),
        ("map_exist", ({"a": 1}, None), ValueError),
        ("map_exist", ({"a": 1}, ""), ValueError),
        ("map_insert", ({}, None, 1), ValueError),
        ("map_insert", ({}, "", 1), ValueError),
        ("map_insert", ({}, [], 1), TypeError),
        ("to_json", (None,), ValueError),
        ("to_json", ("",), ValueError),
        ("to_json", ({"a": {1, 2}},), ValueError),
        ("to_json", ({"a": complex(1, 2)},), ValueError),
        ("to_json", ({"a": Symbol("x")},), ValueError),
        ("to_json", ({(1, 2): "value"},), ValueError),
    ],
)
def test_invalid_arguments(name, args, error):
    with pytest.raises(error):
        dictionary_match(name)(*args)


@pytest.mark.parametrize(
    "name, error",
    [
        ("map_akeys", ValueError),
        ("map_avals", ValueError),
        ("map_concat", ValueError),
        ("map_to_html_dl", ValueError),
        ("map_to_html_table", ValueError),
        ("map_delete", TypeError),
        ("map_get", TypeError),
        ("map_exist", TypeError),
        ("map_insert", TypeError),
        ("map_prefix_keys", TypeError),
        ("url_encode", TypeError),
    ],
)
@pytest.mark.parametrize("source", [None, "{}", [], 1])
def test_invalid_map_type(name, error, source):
    args = (source,)
    if name in ("map_delete", "map_get", "map_exist", "map_prefix_keys"):
        args += ("a",)
    elif name == "map_insert":
        args += ("a", 1)
    with pytest.raises(error):
        dictionary_match(name)(*args)


def test_url_encode_error_message():
    with pytest.raises(TypeError, match="must be a dictionary"):
        dictionary_match("url_encode")("text")


@pytest.mark.parametrize(
    "name", ["map_concat", "map_delete", "map_insert", "map_prefix_keys", "to_json"]
)
def test_does_not_mutate_nested_input(name):
    source = {"a": {"list": [Integer(1), true, None]}, "b": Integer(2)}
    original = copy.deepcopy(source)
    args = {
        "map_concat": (source, {"a": "new"}),
        "map_delete": (source, "a"),
        "map_insert": (source, "a", "new"),
        "map_prefix_keys": (source, "x_"),
        "to_json": (source,),
    }[name]
    dictionary_match(name)(*args)
    assert source == original
    assert source["a"]["list"][1] is true
    assert type(source["a"]["list"][0]) is type(Integer(1))


@pytest.mark.parametrize("name", ["", "unknown", None])
def test_unknown_function(name):
    assert dictionary_match(name) is None
