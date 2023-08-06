from pathlib import Path


def _dict2list(dd):
    ll = []
    for key, val in dd.items():
        ll.append(f"--{key}")
        if type(val) not in (list, tuple):
            if isinstance(val, bool) and val:
                continue
            ll.append(str(val))
        else:
            for vv in val:
                ll.append(str(vv))
    return ll


def _compare_results(test_args, args):
    args = vars(args)
    for key in test_args:
        if key == "y":
            assert args[key] == Path(test_args[key])
        else:
            assert args[key] == test_args[key], f"{args[key]}, {test_args[key]}"


def test_func2argparse():
    from playmolecule._test_funcs import _test_func2
    from playmolecule.func2argparse import func_to_argparser
    import argparse

    parser = func_to_argparser(_test_func2, exit_on_error=False)

    test_args = {
        "x": 5,
        "y": "./func2argparse.py",
        "z": 42,
        "w": ["stefan", "doerr"],
        "k": "choice2",
        "ll": [84, 32],
        "flg": True,
        "lb": [False, True],
    }

    args = parser.parse_args(_dict2list(test_args))
    _compare_results(test_args, args)

    test_args = {
        "x": 5,
        "y": "./func2argparse.py",
    }
    args = parser.parse_args(_dict2list(test_args))
    _compare_results(test_args, args)

    test_args = {
        "x": "ho",  # Wrong, should be integer
        "y": "./func2argparse.py",
    }
    try:
        parser.parse_args(_dict2list(test_args))
    except argparse.ArgumentError:
        pass
    else:
        raise RuntimeError("Did not raise argument error")

    test_args = {
        "x": "7.5",  # Wrong, should be integer
        "y": "./func2argparse.py",
    }
    try:
        parser.parse_args(_dict2list(test_args))
    except argparse.ArgumentError:
        pass
    else:
        raise RuntimeError("Did not raise argument error")
