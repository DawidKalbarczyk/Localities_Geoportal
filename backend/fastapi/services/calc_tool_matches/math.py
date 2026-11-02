import math as m
import random as r


def math_match(func):
    match func:
        case "abs":
            def _abs(arg):
                #format abs(-3.5)
                return abs(float(arg))
                # float - 3.5
            return _abs
        case "acos":
            def _acos(arg):
                #format acos(0.5)
                return m.acos(float(arg))
                # float - 1.0471975511965979
            return _acos
        case "asin":
            def _asin(arg):
                #format asin(0.5)
                return m.asin(float(arg))
                # float - 0.5235987755982989
            return _asin
        case "atan":
            def _atan(arg):
                #format atan(1)
                return m.atan(float(arg))
                # float - 0.7853981633974483
            return _atan
        case "atan2":
            def _atan2(arg):
                #format atan2(1, 2)
                y, x = map(float, arg.split(","))
                return m.atan2(float(y), float(x))
                # float - 0.4636476090008061
            return _atan2
        case "actg":
            def _actg(arg):
                #format actg(1)
                return m.atan(1 / float(arg))
                # float - 0.7853981633974483
            return _actg
        case "actg2":
            def _actg2(arg):
                #format actg2(1, 2)
                y, x = map(float, arg.split(","))
                return m.atan2(1 / float(y), float(x))
                # float - 0.4636476090008061
            return _actg2
        case "ceil":
            def _ceil(arg):
                #format ceil(2.3)
                return m.ceil(float(arg))
                # int - 3
            return _ceil
        case "clamp":
            def _clamp(arg):
                #format clamp(0, 5, 10)
                min_value, value, max_value = map(float, arg.split(","))
                return min(max_value, max(min_value, value))
                # float - 5.0
            return _clamp
        case "sin":
            def _sin(arg):
                #format sin(1.57)
                return m.sin(float(arg))
                # float - 0.9999996829318346
            return _sin
        case "cos":
            def _cos(arg):
                #format cos(1.57)
                return m.cos(float(arg))
                # float - 0.0007963267107332633
            return _cos
        case "tan":
            def _tan(arg):
                #format tan(0.785)
                return m.tan(float(arg))
                # float - 0.9992039901050427
            return _tan
        case "ctg":
            def _ctg(arg):
                #format ctg(0.785)
                return 1 / m.tan(float(arg))
                # float - 1.000796644031489
            return _ctg
        case "degrees":
            def _degrees(arg):
                #format degrees(3.14)
                return (arg * 180) / m.pi
                # float - 179.9087476710785
            return _degrees
        case "radians":
            def _radians(arg):
                #format radians(180)
                return (arg * m.pi) / 180
                # float - 3.141592653589793
            return _radians
        case "exp":
            def _exp(arg):
                #format exp(2)
                return m.exp(float(arg))
                # float - 7.38905609893065
            return _exp
        case "floor":
            def _floor(arg):
                #format floor(2.9)
                return m.floor(float(arg))
                # int - 2
            return _floor
        case "ln":
            def _ln(arg):
                #format ln(2)
                return m.log(float(arg))
                # float - 0.6931471805599453
            return _ln
        case "log":
            def _log(arg):
                #format log(2, 8)
                base, value = map(float, arg.split(","))
                return m.log(value, base)
                # float - 3.0
            return _log
        case "log10":
            def _log10(arg):
                #format log10(100)
                return m.log10(float(arg))
                # float - 2.0
            return _log10
        case "max":
            def _max(arg):
                #format max(1, 2, 3)
                return max(map(float, arg.split(",")))
                # float - 3.0
            return _max
        case "min":
            def _min(arg):
                #format min(1, 2, 3)
                return min(map(float, arg.split(",")))
                # float - 1.0
            return _min
        case "pi":
            def _pi(arg):
                #format pi()
                return m.pi
                # float - 3.141592653589793
            return _pi
        case "pow":
            def _pow(arg):
                #format pow(2, 3)
                base, exponent = map(float, arg.split(","))
                return m.pow(base, exponent)
                # float - 8.0
            return _pow
        case "rand":
            def _rand(arg):
                #format rand(1, 10)
                randomItems = list(map(int, arg.split(",")))
                if len(randomItems) == 2:
                    return r.randint(randomItems[0], randomItems[1])
                    # int - 7
                elif len(randomItems) == 3:
                    return r.Random(randomItems[2]).randint(randomItems[0], randomItems[1])
                    # int - 7
            return _rand
        case "randf":
            def _randf(arg):
                #format randf(0, 1)
                randomItems = list(map(float, arg.split(",")))
                if len(randomItems) == 2:
                    return r.uniform(randomItems[0], randomItems[1])
                    # float - 0.42
                elif len(randomItems) == 3:
                    return r.Random(randomItems[2]).uniform(randomItems[0], randomItems[1])
                    # float - 0.42
            return _randf
        case "round":
            def _round(arg):
                #format round(3.14159, 2)
                value, ndigits = map(float, arg.split(","))
                return round(value, int(ndigits))
                # float - 3.14
            return _round
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
                    # float - 0.0
                if value >= domain_max:
                    return range_max
                    # float - 100.0
                if exponent == 1:
                    ratio = (value - domain_min) / (domain_max - domain_min)
                else:
                    ratio = (
                        (exponent ** (value - domain_min) - 1)
                        / (exponent ** (domain_max - domain_min) - 1)
                        )
                return range_min + ratio * (range_max - range_min)
                # float - 3.0303030303030303
            return _scale_exponential
        case "scale_linear":
            def _scale_linear(arg):
                #format scale_linear(5, 0, 10, 0, 100)
                value, domain_min, domain_max, range_min, range_max = map(float, arg.split(","))
                if domain_min >= domain_max:
                    raise ValueError("domain_max must be greater than domain_min")
                if value <= domain_min:
                    return range_min
                    # float - 0.0
                if value >= domain_max:
                    return range_max
                    # float - 100.0
                ratio = (value - domain_min) / (domain_max - domain_min)
                return range_min + ratio * (range_max - range_min)
                # float - 50.0
            return _scale_linear
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
                    # float - 0.0
                if value >= domain_max:
                    return range_max
                    # float - 100.0
                ratio = ((value - domain_min) / (domain_max - domain_min)) ** exponent
                return range_min + ratio * (range_max - range_min)
                # float - 25.0
            return _scale_polynomial
        case "scale_logarithmic":
            def _scale_logarithmic(arg):
                #format scale_logarithmic(5, 1, 10, 0, 100)
                value, domain_min, domain_max, range_min, range_max = map(float, arg.split(","))
                if domain_min >= domain_max:
                    raise ValueError("domain_min must be less than domain_max")
                if value <= domain_min:
                    return range_min
                    # float - 0.0
                if value >= domain_max:
                    return range_max
                    # float - 100.0
                ratio = (m.log(value) - m.log(domain_min)) / (m.log(domain_max) - m.log(domain_min))
                return range_min + ratio * (range_max - range_min)
                # float - 69.89700043360187
            return _scale_logarithmic
        case "sqrt":
            def _sqrt(arg):
                #format sqrt(9)
                return m.sqrt(float(arg))
                # float - 3.0
            return _sqrt
        case "root":
            def _root(arg):
                #format root(27, 3)
                value, n = map(float, arg.split(","))
                return value ** (1 / n)
                # float | complex - 3.0, (1+2j)
            return _root
        case _:
            return None