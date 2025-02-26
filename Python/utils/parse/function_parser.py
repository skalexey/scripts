# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring, W0123:eval-used

import re
import inspect
import ast


class FunctionSignature:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return f"{self.name}({', '.join(self.args)})"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def parse(cls, string):
        match = re.match(r"(?P<name>[\w\d_]+)\((?P<args>.*)\)", string)
        if not match:
            raise ValueError(f"Function '{string}' is not in the correct format")
        return cls(**match.groupdict())


class BoundFunction:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.func(*self.args, **self.kwargs)

    def __repr__(self):
        args_str = ", ".join(map(str, self.args))
        kwargs_str = ", ".join([f"{k}={v}" for k, v in self.kwargs.items()])

        if kwargs_str:
            return f"{self.func.__name__}({args_str}, {kwargs_str})"
        return f"{self.func.__name__}({args_str})"


def parse_args(args_string):  # pylint: disable=too-many-branches
    """
    Parses a string of arguments into positional and keyword arguments,
    validating for mismatches and incorrect ordering.
    If an argument is a variable, it will traverse the call stack (locals and globals)
    to try to find its value before falling back to eval().
    Supports nested quotes.
    """
    if not args_string.strip():
        return [], {}  # No arguments

    # Replace escaped characters
    args_string = args_string.replace(r'\\"', '"').replace(r"\\'", "'")

    # Handle nested quotes by using regex to split arguments safely
    pattern = re.compile(r'(?:(?<=,)|^)([^,]*?(?:".*?"|\'.*?\')?[^,]*)(?=,|$)')
    parts = [m.group(1).strip() for m in pattern.finditer(args_string)]

    pos_args = []
    kw_args = {}
    keyword_started = False  # Tracks whether we have encountered a keyword argument

    for part in parts:
        if "=" in part and not (part.startswith('"') and part.endswith('"') or part.startswith("'") and part.endswith("'")):
            # Keyword argument detected (but not inside quotes)
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Check if a positional argument appeared after a keyword argument
            keyword_started = True  # Switch to keyword-only mode
            if key in kw_args:
                raise ValueError(f"Duplicate keyword argument: '{key}'")
            kw_args[key] = ast.literal_eval(value)
        else:
            # Positional argument
            if keyword_started:
                raise ValueError("Positional arguments cannot appear after keyword arguments")

            # Try to evaluate the part as a variable name or value
            try:
                # Check if it's a valid literal
                pos_args.append(ast.literal_eval(part))
            except ValueError:
                # If not a literal, try looking up as a variable name in the stack frames
                found_value = None
                for frame in inspect.stack():
                    # Skip the current frame and try looking up the variable in each preceding frame
                    try:
                        # Check if the variable is in locals of the frame
                        if part in frame.frame.f_locals:
                            found_value = frame.frame.f_locals[part]
                            break
                        # Check if the variable is in globals of the frame
                        if part in frame.frame.f_globals:
                            found_value = frame.frame.f_globals[part]
                            break
                    except KeyError:
                        continue

                if found_value is not None:
                    pos_args.append(found_value)
                else:
                    # If the variable is not found in any frame, evaluate it
                    try:
                        pos_args.append(eval(part))
                    except (NameError, SyntaxError) as exc:
                        raise ValueError(f"Cannot resolve argument '{part}' as a variable or expression") from exc

    return pos_args, kw_args


def load_function(string, variables):
    signature = FunctionSignature.parse(string)
    function = variables.get(signature.name)
    if not function:
        raise ValueError(f"Function '{signature.name}' not found in the given variables set")
    sig = inspect.signature(function)
    args, kwargs = parse_args(signature.args)
    bound_args = sig.bind(*args, **kwargs)
    bound_function = BoundFunction(function, *bound_args.args, **bound_args.kwargs)
    return bound_function
