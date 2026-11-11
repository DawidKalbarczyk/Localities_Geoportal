import cmath
import math
import random
from types import SimpleNamespace

import pytest
from services.calc_tool_matches import math as module

UNARY = {
    "abs": abs,
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "actg": lambda x: math.atan(1 / x),
    "ceil": math.ceil,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "ctg": lambda x: 1 / math.tan(x),
    "degrees": math.degrees,
    "radians": math.radians,
    "exp": math.exp,
    "floor": math.floor,
    "ln": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
}
NAMES = list(UNARY) + [
    "atan2",
    "actg2",
    "clamp",
    "log",
    "max",
    "min",
    "pi",
    "pow",
    "rand",
    "randf",
    "round",
    "scale_exponential",
    "scale_linear",
    "scale_polynomial",
    "scale_logarithmic",
    "root",
]


@pytest.mark.parametrize("name", UNARY)
def test_unary(name):
    function = module.math_match(name)
    for i in range(10_000):
        value = (i - 5000.5) / 32
        if name in ("acos", "asin"):
            value = -1 + 2 * i / 9999
        elif name in ("ln", "log10"):
            value = (i + 1) / 32
        elif name == "sqrt":
            value = i / 32
        argument = [str(value), f" {value} ", repr(value)][i % 3]
        expected = UNARY[name](value)
        result = function(argument)
        assert type(result) is type(expected), argument
        assert result == pytest.approx(expected, rel=1e-12, abs=1e-12), argument


@pytest.mark.parametrize("name", ["atan2", "actg2"])
def test_two_angles(name):
    function = module.math_match(name)
    for i in range(10_000):
        y, x = (i - 5000.5) / 16, (i % 113 - 56) / 8
        expected = math.atan2(y if name == "atan2" else 1 / y, x)
        argument = f" {y}, {x} "
        result = function(argument)
        assert type(result) is float
        assert result == pytest.approx(expected, rel=1e-12, abs=1e-12), argument


def test_clamp():
    function = module.math_match("clamp")
    for i in range(10_000):
        lower, upper, value = i / 8 - 500, i / 8 - 490, i / 8 - 505 + i % 21
        if i % 7 == 0:
            lower, upper = upper, lower
        expected = sorted([lower, value, upper])[1] if lower <= upper else upper
        argument = f"{lower}, {value}, {upper}"
        assert function(argument) == expected, argument


def test_log():
    function = module.math_match("log")
    for i in range(10_000):
        base = [0.5, 2, 10, math.e][i % 4]
        value = (i + 1) / 16
        argument = f"{base}, {value}"
        assert function(argument) == pytest.approx(
            math.log(value) / math.log(base), rel=1e-12, abs=1e-12
        ), argument


@pytest.mark.parametrize("name, reference", [("max", max), ("min", min)])
def test_extremes(name, reference):
    function = module.math_match(name)
    for i in range(10_000):
        values = [i / 8, -i / 4, 0.0, i + 0.5, -i - 0.5][: 1 + i % 5]
        argument = ", ".join(map(str, values))
        result = function(argument)
        assert type(result) is float
        assert result == reference(values), argument


def test_pi():
    result = module.math_match("pi")("")
    assert type(result) is float
    assert result == math.pi


def test_pow():
    function = module.math_match("pow")
    for i in range(10_000):
        base = (i - 5000) / 64
        exponent = i % 9 - 4 if base else 2
        argument = f"{base}, {exponent}"
        assert function(argument) == pytest.approx(
            base**exponent, rel=1e-12, abs=1e-12
        ), argument


@pytest.mark.parametrize("name", ["rand", "randf"])
def test_random(name, monkeypatch):
    # Osobne generatory pozwalają sprawdzić dokładny wynik bez zmiany globalnego RNG.
    generator, reference = random.Random(12345), random.Random(12345)
    monkeypatch.setattr(
        module,
        "r",
        SimpleNamespace(
            Random=random.Random,
            randint=generator.randint,
            uniform=generator.uniform,
        ),
    )
    function = module.math_match(name)
    for i in range(10_000):
        lower, upper = i - 5000, i - 5000 + i % 31
        if name == "randf":
            lower, upper = lower / 8, upper / 8
            if i % 3 == 0:
                lower, upper = upper, lower
        args = [lower, upper]
        oracle = reference
        if i % 2:
            seed = i if name == "rand" else i / 8
            args.append(seed)
            oracle = random.Random(seed)
        expected = (
            oracle.randint(lower, upper)
            if name == "rand"
            else oracle.uniform(lower, upper)
        )
        argument = ", ".join(map(str, args))
        result = function(argument)
        assert type(result) is (int if name == "rand" else float)
        assert min(lower, upper) <= result <= max(lower, upper), argument
        assert result == expected, argument


def test_round():
    function = module.math_match("round")
    for i in range(10_000):
        value, places = (i - 5000) / 8, i % 13 - 6
        # Obecna funkcja obcina niecałkowite ndigits przed wywołaniem round().
        digits = places + (0.5 if places >= 0 else -0.5)
        argument = f"{value}, {digits}"
        assert function(argument) == round(value, places), argument


@pytest.mark.parametrize(
    "name",
    [
        "scale_linear",
        "scale_exponential",
        "scale_polynomial",
        "scale_logarithmic",
    ],
)
def test_scale(name):
    function = module.math_match(name)
    for i in range(10_000):
        lower, upper = 1 + i / 100, 11 + i / 100
        fraction = [-0.5, 0, (i % 1000) / 999, 1, 1.5][i % 5]
        value = lower + fraction * (upper - lower)
        out_lower, out_upper = (-50.0, 150.0) if i % 2 else (150.0, -50.0)
        exponent = [0.5, 1.0, 2.0, 3.0][i % 4]
        args = [value, lower, upper, out_lower, out_upper]
        if name in ("scale_exponential", "scale_polynomial"):
            args.append(exponent)
        if value <= lower:
            expected = out_lower
        elif value >= upper:
            expected = out_upper
        else:
            ratio = (value - lower) / (upper - lower)
            if name == "scale_polynomial":
                ratio **= exponent
            elif name == "scale_exponential" and exponent != 1:
                ratio = math.expm1(math.log(exponent) * (value - lower)) / math.expm1(
                    math.log(exponent) * (upper - lower)
                )
            elif name == "scale_logarithmic":
                ratio = math.log(value / lower) / math.log(upper / lower)
            expected = out_lower + ratio * (out_upper - out_lower)
        argument = ", ".join(map(str, args))
        result = function(argument)
        assert type(result) is float
        assert result == pytest.approx(expected, rel=1e-10, abs=1e-10), argument


def test_root():
    function = module.math_match("root")
    for i in range(10_000):
        value = (i + 1) / 32 * (-1 if i % 2 else 1)
        degree = [2, 3, 4, -2, 0.5][i % 5]
        argument = f"{value}, {degree}"
        expected = (
            value ** (1 / degree)
            if value >= 0
            else cmath.exp(cmath.log(value) / degree)
        )
        result = function(argument)
        assert result == pytest.approx(expected, rel=1e-12, abs=1e-12), argument


@pytest.mark.parametrize(
    "name, argument",
    [
        (name, argument)
        for name in NAMES
        for argument in ("", "not-a-number", "1,,2")
        if not (name == "pi" and argument == "")
    ],
)
def test_invalid_number(name, argument):
    with pytest.raises(ValueError):
        module.math_match(name)(argument)


@pytest.mark.parametrize(
    "name, argument, error",
    [
        ("acos", "1.01", ValueError),
        ("acos", "-1.01", ValueError),
        ("asin", "1.01", ValueError),
        ("asin", "-1.01", ValueError),
        ("sqrt", "-1", ValueError),
        ("ln", "0", ValueError),
        ("ln", "-1", ValueError),
        ("log10", "0", ValueError),
        ("log10", "-1", ValueError),
        ("log", "1, 10", ZeroDivisionError),
        ("log", "0, 10", ValueError),
        ("log", "2, -1", ValueError),
        ("log", "2", ValueError),
        ("actg", "0", ZeroDivisionError),
        ("actg2", "0, 1", ZeroDivisionError),
        ("ctg", "0", ZeroDivisionError),
        ("root", "4, 0", ZeroDivisionError),
        ("root", "0, -2", ZeroDivisionError),
        ("pow", "0, -1", ValueError),
        ("pow", "-1, 0.5", ValueError),
        ("exp", "1000", OverflowError),
        ("pow", "1e308, 2", OverflowError),
        ("ceil", "inf", OverflowError),
        ("floor", "nan", ValueError),
        ("sin", "inf", ValueError),
        ("cos", "inf", ValueError),
        ("tan", "inf", ValueError),
        ("atan2", "1", ValueError),
        ("atan2", "1, 2, 3", ValueError),
        ("clamp", "1, 2", ValueError),
        ("round", "1", ValueError),
        ("rand", "1", ValueError),
        ("rand", "1, 2, 3, 4", ValueError),
        ("rand", "2, 1", ValueError),
        ("rand", "1.5, 2", ValueError),
        ("randf", "1", ValueError),
        ("randf", "1, 2, 3, 4", ValueError),
        ("pi", " ", ValueError),
        ("pi", "0", ValueError),
    ],
)
def test_errors(name, argument, error):
    with pytest.raises(error):
        module.math_match(name)(argument)


@pytest.mark.parametrize(
    "name",
    [
        "scale_linear",
        "scale_exponential",
        "scale_polynomial",
        "scale_logarithmic",
    ],
)
@pytest.mark.parametrize("bounds", [(1, 1), (2, 1)])
def test_scale_invalid_domain(name, bounds):
    argument = f"1.5, {bounds[0]}, {bounds[1]}, 0, 100"
    if name in ("scale_exponential", "scale_polynomial"):
        argument += ", 2"
    with pytest.raises(ValueError, match="domain_"):
        module.math_match(name)(argument)


@pytest.mark.parametrize("name", ["scale_exponential", "scale_polynomial"])
@pytest.mark.parametrize("exponent", [0, -1])
def test_scale_invalid_exponent(name, exponent):
    with pytest.raises(ValueError, match="exponent must be greater than 0"):
        module.math_match(name)(f"5, 0, 10, 0, 100, {exponent}")


@pytest.mark.parametrize(
    "name, argument, expected",
    [
        ("abs", "-0", 0.0),
        ("abs", "-inf", math.inf),
        ("acos", "1", 0.0),
        ("asin", "-1", -math.pi / 2),
        ("atan", "inf", math.pi / 2),
        ("atan2", "0, 0", 0.0),
        ("ceil", "0", 0),
        ("floor", "-0", 0),
        ("sin", "0", 0.0),
        ("cos", "0", 1.0),
        ("tan", "0", 0.0),
        ("degrees", "0", 0.0),
        ("radians", "180", math.pi),
        ("exp", "-inf", 0.0),
        ("ln", "1", 0.0),
        ("log10", "1", 0.0),
        ("log", "0.5, 0.25", 2.0),
        ("sqrt", "0", 0.0),
        ("root", "-8, 3", complex(1, math.sqrt(3))),
        ("root", "-4, 2", 2j),
        ("root", "-8, 1", -8.0),
        ("pow", "0, 0", 1.0),
        ("round", "2.5, 0", 2.0),
        ("round", "3.5, 0", 4.0),
        ("clamp", "10, 5, 0", 0.0),
        ("scale_linear", "5, 0, 10, 3, 3", 3.0),
        ("scale_logarithmic", "0, 0, 10, 0, 100", 0.0),
    ],
)
def test_boundaries(name, argument, expected):
    result = module.math_match(name)(argument)
    assert type(result) is type(expected)
    assert result == pytest.approx(expected, rel=1e-12, abs=1e-12)


@pytest.mark.parametrize("name", ["abs", "sqrt", "sin", "ln", "root"])
def test_nan(name):
    argument = "nan, 2" if name == "root" else "nan"
    assert math.isnan(module.math_match(name)(argument))


@pytest.mark.parametrize("name", ["", "unknown", None])
def test_unknown_function(name):
    assert module.math_match(name) is None
