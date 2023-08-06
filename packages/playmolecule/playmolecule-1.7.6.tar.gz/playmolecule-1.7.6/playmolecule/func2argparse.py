from pathlib import Path
import unittest
import argparse


class LoadFromFile(argparse.Action):
    def __init__(self, unmatched_args="error", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if unmatched_args not in ("error", "warning"):
            raise RuntimeError("unmatched_args can only be set to error or warning")
        self.unmatched_args = unmatched_args

    def _error_unfound(self, key, namespace):
        if key not in namespace:
            if self.unmatched_args == "error":
                raise ValueError(f"Unknown argument in config file: {key}")
            elif self.unmatched_args == "warning":
                print(f"WARNING: Unknown argument in config file: {key}")

    # parser.add_argument('--file', type=open, action=LoadFromFile)
    def __call__(self, parser, namespace, values, option_string=None):
        import yaml
        import json

        if values.name.endswith("yaml") or values.name.endswith("yml"):
            with values as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            for key in config.keys():
                self._error_unfound(key, namespace)
            namespace.__dict__.update(config)
        elif values.name.endswith("json"):
            with values as f:
                config = json.load(f)

            if "execid" in config and "params" in config:
                # Special case for PlayMolecule
                config = config["params"]
                for prm in config:
                    key = prm["name"]
                    self._error_unfound(key, namespace)
                    namespace.__dict__[key] = prm["value"]
            else:
                # General use case similar to yaml above
                for key in config.keys():
                    self._error_unfound(key, namespace)
                namespace.__dict__.update(config)
        else:
            raise ValueError("Configuration file must end with yaml or yml")


def _parse_docs(doc):
    import re
    from ast import literal_eval

    reg1 = re.compile(r"^(\S+)\s*:")
    reg2 = re.compile(r"choices=([\(\[].*[\)\]])")

    lines = doc.splitlines()
    name = lines[0].strip().split()[0]

    description = []
    for line in lines[1:]:
        if line.strip().startswith("Parameters"):
            break
        if len(line.strip()):
            description.append(line.strip())
    description = " ".join(description)

    argdocs = {}
    currvar = None
    paramsection = False
    for i in range(len(lines)):
        line = lines[i].strip()
        if paramsection:
            if reg1.match(line):
                currvar = reg1.findall(line)[0]
                argdocs[currvar] = {"doc": "", "choices": None}
                choices = reg2.findall(line)
                if len(choices):
                    argdocs[currvar]["choices"] = literal_eval(choices[0])
            elif currvar is not None:
                # Everything after the initial variable line counts as help
                argdocs[currvar]["doc"] += line + " "
        if line.startswith("Parameters"):
            paramsection = True
        if paramsection and line == "":
            paramsection = False

    return argdocs, description, name


def _get_name_abbreviations(sig):
    abbrevs = {"help": "h"}

    def get_abbr(name):
        pieces = name.split("_")
        for i in range(len(pieces)):
            yield "".join([p[0] for p in pieces[: i + 1]])
        # Last attempt
        name = name.replace("_", "")
        for i in range(1, len(name) + 1):
            yield name[:i]

    for argname in sig.parameters:
        if argname[0] == "_":
            continue  # Don't add underscore arguments to argparser
        for abb in get_abbr(argname):
            if abb not in abbrevs.values():
                abbrevs[argname] = abb
                break
    return abbrevs


def func_to_argparser(
    func, exit_on_error=True, allow_conf_yaml=False, unmatched_args="error"
):
    import inspect
    from typing import get_origin, get_args

    sig = inspect.signature(func)
    doc = func.__doc__
    if doc is None:
        raise RuntimeError("Could not find documentation in the function...")

    argdocs, description, name = _parse_docs(doc)

    try:
        parser = argparse.ArgumentParser(
            name,
            description=description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            exit_on_error=exit_on_error,
        )
    except:
        parser = argparse.ArgumentParser(
            name,
            description=description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    if allow_conf_yaml:
        parser.add_argument(
            "--conf",
            help="Configuration YAML file to set all parameters",
            type=open,
            action=lambda *x, **y: LoadFromFile(*x, **y, unmatched_args=unmatched_args),
        )

    # Calculate abbreviations
    abbrevs = _get_name_abbreviations(sig)

    for argname in sig.parameters:
        if argname[0] == "_" or argname in ("args", "kwargs"):
            continue  # Don't add underscore arguments to argparser or args, kwargs
        params = sig.parameters[argname]

        if argname not in argdocs:
            raise RuntimeError(
                f"Could not find help for argument {argname} in the docstring of the function. Please document it."
            )

        argtype = params.annotation
        nargs = None
        # This is needed for compound types like: list[str]
        if get_origin(params.annotation) is not None:
            origtype = get_origin(params.annotation)
            argtype = get_args(params.annotation)[0]
            if origtype in (list, tuple):
                nargs = "+"

        default = None
        if params.default != inspect._empty:
            default = params.default
            # Don't allow empty list defaults., convert to None
            if type(default) in (list, tuple) and len(default) == 0:
                raise RuntimeError(
                    f"Please don't use empty tuples/lists as default arguments (e.g. {argname}=()). Use =None instead"
                )

        if type(argtype) == tuple:
            raise RuntimeError(
                f"Failed to get type annotation for argument '{argname}'"
            )

        if argtype == bool:
            if nargs is None:
                if default:
                    raise RuntimeError(
                        "func2argparse does not allow boolean flags with default value True"
                    )
                parser.add_argument(
                    f"--{argname.replace('_', '-')}",
                    f"-{abbrevs[argname]}",
                    help=argdocs[argname]["doc"].strip(),
                    action="store_true",
                )
            else:
                parser.add_argument(
                    f"--{argname.replace('_', '-')}",
                    f"-{abbrevs[argname]}",
                    help=argdocs[argname]["doc"].strip(),
                    default=default,
                    type=str_to_bool,
                    required=params.default == inspect._empty,
                    nargs=nargs,
                )
        else:
            help = argdocs[argname]["doc"].strip()
            choices = argdocs[argname]["choices"]
            parser.add_argument(
                f"--{argname.replace('_', '-')}",
                f"-{abbrevs[argname]}",
                help=help,
                default=default,
                type=argtype,
                choices=choices,
                required=params.default == inspect._empty,
                nargs=nargs,
            )

    return parser


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() == "false":
        return False
    if value.lower() == "true":
        return True
    raise RuntimeError(f"Invalid boolean value {value}")
