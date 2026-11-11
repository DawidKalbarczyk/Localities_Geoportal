import datetime as dt
import json
import random
from html import escape
from urllib.parse import quote, urlencode

import pytest
from services.service_calc_tool import ExpressionParser

SCENARIOS = [
    "amount_label",
    "length_clamped",
    "code_padding",
    "number_from_text",
    "clean_contact",
    "json_text",
    "map_text_metrics",
    "html_clean_title",
    "rounded_map_value",
    "numeric_json",
    "mapped_scale",
    "seeded_report",
    "dated_label",
    "time_label",
    "date_slug",
    "date_from_numbers",
    "duration_hours_number",
    "appointment_json",
    "date_query",
    "event_summary",
]


FIELD_SCENARIOS = [
    "column_values",
    "column_json",
    "numeric_math",
    "numeric_comparison",
    "text_normalization",
    "dictionary_column",
    "json_columns",
    "date_from_column",
    "date_part",
    "combined_label",
    "json_date_report",
    "independent_columns",
]


def evaluate(expression, table=None, table_keys=None):
    if table is None:
        table = []
    if table_keys is None:
        table_keys = list(table[0]) if table else []
    parser = ExpressionParser(expression, table=table, tableKeys=table_keys)
    parser.find_function_call()
    parser.writeFunctions()
    return parser.parse_expression()


def mixed_case(scenario, i):
    date = dt.date(2020, 2, 1) + dt.timedelta(days=i)
    date_expression = f"make_date({date.year}, {date.month}, {date.day})"
    formatted_date = f"{date.day:02}.{date.month:02}.{date.year}"
    city = ["Łódź", "Kraków", "Gdańsk"][i % 3]
    name = f"  aLa_nowak{i}, {city}  " if i % 10 == 0 else f"  aLa_nowak{i}  "
    amount = 125.5 + i * 17.25
    start = dt.datetime(2020, 2, 1, 8)
    hours = i + 1 + (i % 4) / 4
    end = start + dt.timedelta(hours=hours)
    duration = f"hour(age({end.isoformat(sep=' ')!r}, {start.isoformat(sep=' ')!r}))"

    match scenario:
        case "amount_label":
            value = (i - 25) / 8
            return (
                f"concat('Kwota: ', format_number(abs({value}), 2), ' PLN')",
                f"Kwota: {abs(value):.2f} PLN",
            )
        case "length_clamped":
            return (
                f"clamp(3, length(trim({name!r})), 12)",
                float(min(12, max(3, len(name.strip())))),
            )
        case "code_padding":
            return (
                f"lpad(upper(concat('id', floor({i + 0.75}))), 8, '0')",
                f"ID{i}".rjust(8, "0"),
            )
        case "number_from_text":
            return f"round(sqrt(to_string('{(i + 1) ** 2}')), 2)", float(i + 1)
        case "clean_contact":
            return (
                f"replace(upper(trim(map_get(map('name', {name!r}), 'name'))), '_', ' ')",
                name.strip().upper().replace("_", " "),
            )
        case "json_text":
            text = f"O'Reilly, {city} — kontakt {i}"
            payload = json.dumps({"name": text})
            return f"lower(map_get(from_json({payload!r}), 'name'))", text.lower()
        case "map_text_metrics":
            return (
                f"to_json(map('name', title(trim({name!r})), 'length', length(trim({name!r}))))",
                json.dumps({"name": name.strip().title(), "length": len(name.strip())}),
            )
        case "html_clean_title":
            text = f"  <b>jan & ola {i}</b>  "
            return (
                f"map_to_html_dl(map(upper('name'), title(trim({text!r}))))",
                f"<dl><dt>NAME</dt><dd>{escape(text.strip().title())}</dd></dl>",
            )
        case "rounded_map_value":
            return (
                f"format_number(map_get(map('amount', round({amount}, 2)), 'amount'), 2)",
                f"{amount:.2f}",
            )
        case "numeric_json":
            ratio = (i + 1) // 2 if (i + 1) % 2 == 0 else (i + 1) / 2
            return (
                f"to_json(map('square', pow({i - 25}, 2), 'root', sqrt({(i + 1) ** 2}), 'ratio', ({i} + 1) / 2))",
                json.dumps(
                    {
                        "square": float((i - 25) ** 2),
                        "root": float(i + 1),
                        "ratio": ratio,
                    }
                ),
            )
        case "mapped_scale":
            return (
                f"scale_linear(map_get(map('score', {i}), 'score'), 0, 49, 0, 100)",
                i / 49 * 100,
            )
        case "seeded_report":
            return (
                f"to_json(map('id', rand(1, 100, {i}), 'score', round(randf(0, 1, {i}), 3)))",
                json.dumps(
                    {
                        "id": random.Random(i).randint(1, 100),
                        "score": round(random.Random(float(i)).uniform(0, 1), 3),
                    }
                ),
            )
        case "dated_label":
            return (
                f"concat('Termin: ', format_date({date_expression}, 'dd.MM.yyyy'))",
                f"Termin: {formatted_date}",
            )
        case "time_label":
            minutes = i * 29 % 1440
            text = f"{minutes // 60:02}:{minutes % 60:02}"
            return (
                f"concat('Godzina: ', format_time(to_time({text!r}, 'HH:mm'), 'HH:mm:ss'))",
                f"Godzina: {text}:00",
            )
        case "date_slug":
            return (
                f"replace(format_date({date_expression}, 'dd.MM.yyyy'), '.', '-')",
                f"{date.day:02}-{date.month:02}-{date.year}",
            )
        case "date_from_numbers":
            year = 2020 + i % 4
            return (
                f"make_date(floor({year + 0.9}), ceil({date.month - 0.25}), floor({date.day + 0.9}))",
                dt.date(year, date.month, date.day).isoformat(),
            )
        case "duration_hours_number":
            return f"abs(regexp_substr({duration}, '[0-9.]+'))", hours
        case "appointment_json":
            return (
                f"to_json(map('date', {date_expression}, 'weekday', day_of_week({date_expression})))",
                json.dumps({"date": date.isoformat(), "weekday": date.isoweekday()}),
            )
        case "date_query":
            return (
                f"url_encode(map('date', format_date({date_expression}, 'dd.MM.yyyy'), 'city', {city!r}))",
                urlencode(
                    {"date": formatted_date, "city": city}, quote_via=quote, safe="+"
                ),
            )
        case "event_summary":
            return (
                (
                    f"to_json(map('date', {date_expression}, 'label', upper(trim({name!r})), "
                    f"'hours', round(abs(regexp_substr({duration}, '[0-9.]+')), 2)))"
                ),
                json.dumps(
                    {
                        "date": date.isoformat(),
                        "label": name.strip().upper(),
                        "hours": round(hours, 2),
                    }
                ),
            )
        case _:
            raise ValueError(f"Unknown test scenario: {scenario}")


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("i", range(50))
def test_mixed_functions(scenario, i):
    # 20 scenariuszy × 50 wariantów = dokładnie 1000 testów przez parser.
    expression, expected = mixed_case(scenario, i)
    actual = evaluate(expression)
    if isinstance(expected, float):
        assert actual == pytest.approx(expected, rel=1e-12, abs=1e-12), expression
    else:
        assert actual == expected, expression


def mixed_field_case(scenario, i):
    date = dt.date(2020, 2, 1) + dt.timedelta(days=i)
    next_date = date + dt.timedelta(days=1)
    names = [f"  Działka {i} (A), Łódź  ", f"  O'Reilly {i}  "]
    areas = [1200.5 + i * 17.25, 850.25 + i * 9.5]
    dates = [date.isoformat(), next_date.isoformat()]
    table = [
        {"NAZWA": name, "powierzchnia": area, "data": value}
        for name, area, value in zip(names, areas, dates)
    ]

    match scenario:
        case "column_values":
            expression, expected = "NAZWA()", names
        case "column_json":
            expression, expected = "to_json(NAZWA())", json.dumps(names)
        case "numeric_math":
            expression = "round(powierzchnia()[0] / 10000, 4)"
            expected = round(areas[0] / 10000, 4)
        case "numeric_comparison":
            expression = "max(powierzchnia()[0], powierzchnia()[1])"
            expected = max(areas)
        case "text_normalization":
            expression = "upper(trim(NAZWA()[1]))"
            expected = names[1].strip().upper()
        case "dictionary_column":
            expression = "map_get(map('names', NAZWA()), 'names')"
            expected = names
        case "json_columns":
            expression = "to_json(map('names', NAZWA(), 'areas', powierzchnia()))"
            expected = json.dumps({"names": names, "areas": areas})
        case "date_from_column":
            expression = "format_date(data()[0], 'dd.MM.yyyy')"
            expected = date.strftime("%d.%m.%Y")
        case "date_part":
            expression = "day_of_week(data()[1])"
            expected = next_date.isoweekday()
        case "combined_label":
            expression = (
                "concat(upper(trim(NAZWA()[0])), ': ', "
                "format_number(powierzchnia()[0], 2))"
            )
            expected = f"{names[0].strip().upper()}: {areas[0]:.2f}"
        case "json_date_report":
            expression = (
                "to_json(map('name', upper(trim(NAZWA()[0])), "
                "'hectares', round(powierzchnia()[0] / 10000, 4), "
                "'date', format_date(data()[0], 'dd.MM.yyyy')))"
            )
            expected = json.dumps(
                {
                    "name": names[0].strip().upper(),
                    "hectares": round(areas[0] / 10000, 4),
                    "date": date.strftime("%d.%m.%Y"),
                }
            )
        case "independent_columns":
            expression = "[NAZWA(), powierzchnia(), data()]"
            expected = [names, areas, dates]
        case _:
            raise ValueError(f"Unknown field test scenario: {scenario}")

    return expression, table, expected


@pytest.mark.parametrize("scenario", FIELD_SCENARIOS)
@pytest.mark.parametrize("i", range(50))
def test_mixed_fields_and_values(scenario, i):
    # 600 przypadków, w tym połączenie wszystkich pięciu grup funkcji.
    expression, table, expected = mixed_field_case(scenario, i)
    actual = evaluate(expression, table)
    if isinstance(expected, float):
        assert actual == pytest.approx(expected, rel=1e-12, abs=1e-12), expression
    else:
        assert actual == expected, expression


@pytest.mark.parametrize(
    "table, expected",
    [
        ([], []),
        ([{"WARTOSC": None}, {}, {"WARTOSC": "A"}], [None, None, "A"]),
        ([{"WARTOSC": 0}, {"WARTOSC": False}, {"WARTOSC": ""}], [0, False, ""]),
        (
            [{"WARTOSC": {"nested": [1, 2]}}, {"WARTOSC": [True, None]}],
            [{"nested": [1, 2]}, [True, None]],
        ),
    ],
    ids=["empty-table", "missing-and-null", "falsy-values", "nested-values"],
)
def test_fields_and_values_boundaries(table, expected):
    actual = evaluate("WARTOSC()", table, table_keys=["WARTOSC"])
    assert json.dumps(actual) == json.dumps(expected)


@pytest.mark.parametrize("name", ["year", "lower", "map", "pow"])
def test_field_name_takes_precedence_over_builtin_function(name):
    assert evaluate(f"{name}()", [{name: "column value"}]) == ["column value"]


@pytest.mark.parametrize("expression", ["NAZWA(1)", "NAZWA('argument')"])
def test_column_function_rejects_arguments(expression):
    with pytest.raises(ValueError):
        evaluate(expression, [{"NAZWA": "A"}])


def test_unselected_column_is_not_registered():
    with pytest.raises(ValueError, match="Unknown function: hidden"):
        evaluate(
            "hidden()",
            [{"NAZWA": "A", "hidden": 123}],
            table_keys=["NAZWA"],
        )
