import json
from html import escape
from urllib.parse import quote, urlencode

from sympy import Float, Integer, Rational, false, true


def dictionary_match(func):
    match func:
        case "from_json":
            def _from_json(arg):
                if arg is None or arg == "":
                    raise ValueError("Input for from_json cannot be None or empty string")
                try:
                    return json.loads(arg)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON input: {e}")
            return _from_json
        case "map":
            def _map(*args):
                if len(args) < 2:
                    raise ValueError("map function requires at least two arguments")
                if len(args) % 2 != 0:
                    raise ValueError("map function requires an even number of arguments")
                for idx, arg in enumerate(args):
                    if idx % 2 == 0 and (arg is None or arg == ""):
                        raise ValueError("Keys in map function cannot be None or empty string")
                return dict(zip(args[::2], args[1::2]))
            return _map
        case "map_akeys":
            def _map_akeys(arg: dict):
                if arg is None or not isinstance(arg, dict):
                    raise ValueError("Input for map_akeys must be a dictionary and cannot be None")
                return list(arg.keys())
            return _map_akeys
        case "map_avals":
            def _map_avals(arg: dict):
                if arg is None or not isinstance(arg, dict):
                    raise ValueError("Input for map_avals must be a dictionary and cannot be None")
                return list(arg.values())
            return _map_avals
        case "map_concat":
            def _map_concat(*args):
                final_dict = {}
                for arg in args:
                    if arg is None or not isinstance(arg, dict):
                        raise ValueError("All arguments for map_concat must be dictionaries and cannot be None")
                    final_dict.update(arg)
                return final_dict
            return _map_concat
        case "map_delete":
            def _map_delete(map, key):
                if not isinstance(map, dict):
                    raise TypeError("First argument for map_delete must be a dictionary")
                if key not in map:
                    raise ValueError("Key not found in dictionary for map_delete")
                result = map.copy()
                del result[key]
                return result
            return _map_delete
        case "map_exist":
            def _map_exist(map, key):
                if not isinstance(map, dict):
                    raise TypeError("First argument for map_exist must be a dictionary")
                if key is None or key == "":
                    raise ValueError("Key for map_exist cannot be None or empty string")
                return key in map
            return _map_exist
        case "map_get":
            def _map_get(map, key):
                if not isinstance(map, dict):
                    raise TypeError("First argument for map_get must be a dictionary")
                if key not in map:
                    raise ValueError("Key not found in dictionary for map_get")
                return map[key]
                
            return _map_get
        case "map_insert":
            def _map_insert(map, key, value):
                if not isinstance(map, dict):
                    raise TypeError("First argument for map_insert must be a dictionary")
                if key is None or key == "":
                    raise ValueError("Key for map_insert cannot be None or empty string")
                result = map.copy()
                result[key] = value
                return result
            return _map_insert
        case "map_prefix_keys":
            def _map_prefix_keys(map, prefix):
                if not isinstance(map, dict):
                    raise TypeError("First argument for map_prefix_keys must be a dictionary")
                return {f"{prefix}{key}": value for key, value in map.items()}
            return _map_prefix_keys
        case "map_to_html_dl":
            def _map_to_html_dl(arg: dict):
                if arg is None or not isinstance(arg, dict):
                    raise ValueError("Input for map_to_html_dl must be a dictionary and cannot be None")
                html = "<dl>"
                for key, value in arg.items():
                    html += f"<dt>{escape(str(key))}</dt><dd>{escape(str(value))}</dd>"
                html += "</dl>"
                return html
            return _map_to_html_dl
        case "map_to_html_table":
            def _map_to_html_table(arg: dict):
                if arg is None or not isinstance(arg, dict):
                    raise ValueError("Input for map_to_html_table must be a dictionary and cannot be None")
                html = "<table><thead><tr>"
                for key, value in arg.items():
                    html += f"<th>{escape(str(key))}</th>"
                html += "</tr></thead><tbody><tr>"
                for key, value in arg.items():
                    html += f"<td>{escape(str(value))}</td>"
                html += "</tr></tbody></table>"
                return html
            return _map_to_html_table
        case "to_json":
            def _to_json(arg):
                def convert_to_python(val):
                    if val is true or val is false:
                        return bool(val)
                    if isinstance(val, Integer):
                        return int(val)
                    if isinstance(val, (Rational, Float)):
                        return float(val)
                    if isinstance(val, dict):
                        return {convert_to_python(k): convert_to_python(v) for k, v in val.items()}
                    if isinstance(val, (list, tuple)):
                        return [convert_to_python(v) for v in val]
                    return val
                if arg is None or arg == "":
                    raise ValueError("Input for to_json cannot be None or empty string")
                try:
                    return json.dumps(convert_to_python(arg))
                except (TypeError, OverflowError) as e:
                    raise ValueError(f"Invalid input for JSON serialization: {e}")
            return _to_json
        case "url_encode":
            def _url_encode(arg: dict):
                if not isinstance(arg, dict):
                    raise TypeError("Input for url_encode must be a dictionary")
                return urlencode(arg, quote_via=quote, safe='+')
            return _url_encode
        case _:
            return None
