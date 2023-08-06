from pathlib import Path


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


def _test_func2(
    x: int,
    y: Path,
    z: int = 54,
    w: list[str] = ("hey", "ho"),
    k: str = "choice1",
    ll: list[int] = None,
    flg: bool = False,
    lb: list[bool] = True,
):
    """This is a test function

    Parameters
    ----------
    x : int
        First arg
    y : Path
        Second arg
    z : int
        Third arg
    w : list[str]
        Fourth arg.
        Multiline documentation
    k : str, choices=("choice1", "choice2")
        Fifth arg
    ll : list[int]
        This is an empty list
    flg : bool
        Set to True to do something
    lb : list[bool]
        A list of boolean values
    Examples
    --------
    >>> test_func()
    """
    print(x, y, z, w, k, ll, flg, lb)