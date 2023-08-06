from pathlib import Path
import os


def _test_func(
    outdir: Path,
    pdb: Path,
    simtime: float = 0.5,
    equiltimes: list[float] = None,
    randomize: list[bool] = [True],
    no_prep: bool = False,
    forcefield: str = "CHARMM",
    **kwargs,
):
    """TestFunc

    Test function

    Parameters
    ----------
    outdir : Path
        Output directory
    pdb : Path
        Input file
    simtime : float
        Simulation time
    equiltimes : list[float]
        List of equilibration times
    randomize : list[bool]
        List of booleans
    no_prep : bool
        No preparation
    forcefield : str, choices=("CHARMM", "AMBER")
        The simulation forcefield
    """
    print("Running test function with args:", locals())


def test_app_wrapper():
    from playmolecule.devutils import app_wrapper2

    args = [
        "--outdir",
        "/tmp/",
        "--pdb",
        "/tmp/test.pdb",
        "--simtime",
        "0.3",
        "--equiltimes",
        "0.1 0.2",
        "--randomize",
        "false True",
        "--no-prep",
        "--forcefield",
        "AMBER",
    ]
    app_wrapper2("playmolecule._test_funcs._test_func", " ".join(args))


# def test_app_wrapper_pmws(self):
#     import os

#     args = [
#         "--outdir",
#         "/tmp/",
#         "--pdb",
#         "/tmp/test.pdb",
#         "--simtime",
#         "0.3",
#         "--equiltimes",
#         "0.1 0.2",
#         "--randomize",
#         "false True",
#         "--no-prep",
#         "--forcefield",
#         "AMBER",
#     ]
#     app_wrapper2(
#         "playmolecule.devutils._test_func",
#         token=os.environ["PM_TOKEN"],
#         execid="xx",
#     )


def test_app_argparse_dump():
    from playmolecule.devutils import app_wrapper2
    import tempfile
    import json

    dump_ref = {
        "description": "Test function",
        "params": [
            {
                "mandatory": True,
                "type": "Path",
                "name": "outdir",
                "value": None,
                "tag": "--outdir",
                "description": "Output directory",
                "nargs": None,
                "choices": None,
                "metavar": None,
            },
            {
                "mandatory": True,
                "type": "Path",
                "name": "pdb",
                "value": None,
                "tag": "--pdb",
                "description": "Input file",
                "nargs": None,
                "choices": None,
                "metavar": None,
            },
            {
                "mandatory": False,
                "type": "float",
                "name": "simtime",
                "value": 0.5,
                "tag": "--simtime",
                "description": "Simulation time",
                "nargs": None,
                "choices": None,
                "metavar": None,
            },
            {
                "mandatory": False,
                "type": "float",
                "name": "equiltimes",
                "value": None,
                "tag": "--equiltimes",
                "description": "List of equilibration times",
                "nargs": "+",
                "choices": None,
                "metavar": None,
            },
            {
                "mandatory": False,
                "type": "str_to_bool",
                "name": "randomize",
                "value": [True],
                "tag": "--randomize",
                "description": "List of booleans",
                "nargs": "+",
                "choices": None,
                "metavar": None,
            },
            {
                "mandatory": False,
                "type": "bool",
                "name": "no_prep",
                "value": False,
                "tag": "--no-prep",
                "description": "No preparation",
                "nargs": None,
                "choices": None,
                "metavar": None,
            },
            {
                "mandatory": False,
                "type": "str",
                "name": "forcefield",
                "value": "CHARMM",
                "tag": "--forcefield",
                "description": "The simulation forcefield",
                "nargs": None,
                "choices": ["CHARMM", "AMBER"],
                "metavar": None,
            },
        ],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        argpf = os.path.join(tmpdir, "argp.json")
        app_wrapper2("playmolecule._test_funcs._test_func", dump_argparser=argpf)

        with open(argpf, "r") as f:
            argp = json.load(f)
            assert argp == dump_ref
