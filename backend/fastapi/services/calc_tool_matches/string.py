def string_match(func):
    match func:
        case "test":
            return "test"
        case _:
            return None