import argparse
import gzip
import io
import math
import os
from collections import namedtuple
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Sequence
from functools import lru_cache
from itertools import chain
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Literal
from typing import Optional
from typing import Union

import lz4.frame
import numpy as np
import pandas as pd
import polars as pl
import pyzstd
import xz

import artistools as at

roman_numerals = (
    "",
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
)


class CustomArgHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["max_help_position"] = 39
        super().__init__(*args, **kwargs)

    def add_arguments(self, actions: Iterable[argparse.Action]) -> None:
        getinvocation = super()._format_action_invocation

        def my_sort(action: argparse.Action) -> str:
            opstr = getinvocation(action)
            opstr = opstr.upper().replace("-", "z")  # push dash chars below alphabet

            return opstr

        actions = sorted(actions, key=my_sort)
        super().add_arguments(actions)


class AppendPath(argparse.Action):
    def __call__(self, parser, args, values, option_string=None) -> None:  # type: ignore[no-untyped-def] # noqa: ARG002
        # if getattr(args, self.dest) is None:
        #     setattr(args, self.dest, [])
        if isinstance(values, Iterable):
            pathlist = getattr(args, self.dest)
            # not pathlist avoids repeated appending of the same items when called from Python
            # instead of from the command line
            if not pathlist:
                for pathstr in values:
                    # if Path(pathstr) not in pathlist:
                    pathlist.append(Path(pathstr))
        else:
            setattr(args, self.dest, Path(values))


def showtimesteptimes(modelpath: Optional[Path] = None, numberofcolumns: int = 5) -> None:
    """Print a table showing the timesteps and their corresponding times."""
    if modelpath is None:
        modelpath = Path()

    print("Timesteps and midpoint times in days:\n")

    times = get_timestep_times_float(modelpath, loc="mid")
    indexendofcolumnone = math.ceil((len(times) - 1) / numberofcolumns)
    for rownum in range(0, indexendofcolumnone):
        strline = ""
        for colnum in range(numberofcolumns):
            if colnum > 0:
                strline += "\t"
            newindex = rownum + colnum * indexendofcolumnone
            if newindex + 1 < len(times):
                strline += f"{newindex:4d}: {float(times[newindex + 1]):.3f}d"
        print(strline)


@lru_cache(maxsize=8)
def get_composition_data(filename: Union[Path, str]) -> pd.DataFrame:
    """Return a pandas DataFrame containing details of included elements and ions."""
    if os.path.isdir(Path(filename)):
        filename = os.path.join(filename, "compositiondata.txt")

    columns = ("Z,nions,lowermost_ionstage,uppermost_ionstage,nlevelsmax_readin,abundance,mass,startindex").split(",")

    rowdfs = []
    with open(filename) as fcompdata:
        nelements = int(fcompdata.readline())
        fcompdata.readline()  # T_preset
        fcompdata.readline()  # homogeneous_abundances
        startindex = 0
        for _ in range(nelements):
            line = fcompdata.readline()
            linesplit = line.split()
            row_list = [int(x) for x in linesplit[:5]] + [float(x) for x in linesplit[5:]] + [startindex]

            rowdfs.append(pd.DataFrame([row_list], columns=columns))

            startindex += int(rowdfs[-1].iloc[0]["nions"])

    compdf = pd.concat(rowdfs, ignore_index=True)

    return compdf


def get_composition_data_from_outputfile(modelpath: Path) -> pd.DataFrame:
    """Read ion list from output file."""
    atomic_composition = {}

    with open(modelpath / "output_0-0.txt") as foutput:
        Z: Optional[int] = None
        ioncount = 0
        for row in foutput:
            if row.split()[0] == "[input.c]":
                split_row = row.split()
                if split_row[1] == "element":
                    Z = int(split_row[4])
                    ioncount = 0
                elif split_row[1] == "ion":
                    ioncount += 1
                    assert Z is not None
                    atomic_composition[Z] = ioncount

    composition_df = pd.DataFrame([(Z, atomic_composition[Z]) for Z in atomic_composition], columns=["Z", "nions"])
    composition_df["lowermost_ionstage"] = [1] * composition_df.shape[0]
    composition_df["uppermost_ionstage"] = composition_df["nions"]
    return composition_df


def split_dataframe_dirbins(
    res_df: Union[pl.DataFrame, pd.DataFrame], index_of_repeated_value: int = 0, output_polarsdf: bool = False
) -> dict[int, Union[pd.DataFrame, pl.DataFrame]]:
    """Res files repeat output for each angle.
    index_of_repeated_value is the column index to look for repeating eg. time of ts 0.
    In spec_res files it's 1 , but in lc_res file it's 0.
    """
    if isinstance(res_df, pd.DataFrame):
        res_df = pl.from_pandas(res_df)

    indexes_to_split = pl.arg_where(
        res_df[:, index_of_repeated_value] == res_df[0, index_of_repeated_value], eager=True
    )

    res_data: dict[int, pl.DataFrame] = {}
    prev_dfshape = None
    for i, index_value in enumerate(indexes_to_split):
        chunk = (
            res_df[indexes_to_split[i] : indexes_to_split[i + 1], :]
            if index_value != indexes_to_split[-1]
            else res_df[indexes_to_split[i] :, :]
        )

        # the number of timesteps should match for all direction bins
        assert prev_dfshape is None or prev_dfshape == chunk.shape
        prev_dfshape = chunk.shape

        res_data[i] = chunk if output_polarsdf else chunk.to_pandas(use_pyarrow_extension_array=True)

    assert len(res_data) == at.get_viewingdirectionbincount()
    return res_data


def average_direction_bins(
    dirbindataframes: dict[int, pl.DataFrame],
    overangle: Literal["phi", "theta"],
) -> dict[int, pl.DataFrame]:
    """Will average dict of direction-binned polars DataFrames according to the phi or theta angle."""
    dirbincount = at.get_viewingdirectionbincount()
    nphibins = at.get_viewingdirection_phibincount()

    assert overangle in ["phi", "theta"]
    if overangle == "phi":
        start_bin_range = range(0, dirbincount, nphibins)
    elif overangle == "theta":
        ncosthetabins = at.get_viewingdirection_costhetabincount()
        start_bin_range = range(0, nphibins)

    # we will make a copy to ensure that we don't cause side effects from altering the original DataFrames
    # that might be returned again later by an lru_cached function
    dirbindataframesout: dict[int, pd.DataFrame] = {}

    for start_bin in start_bin_range:
        dirbindataframesout[start_bin] = dirbindataframes[start_bin]

        contribbins = (
            range(start_bin + 1, start_bin + nphibins)
            if overangle == "phi"
            else range(start_bin + ncosthetabins, dirbincount, ncosthetabins)
        )

        for dirbin_contrib in contribbins:
            dirbindataframesout[start_bin] += dirbindataframes[dirbin_contrib]

        dirbindataframesout[start_bin] /= 1 + len(contribbins)  # every nth bin is the average of n bins
        print(f"bin number {start_bin} = the average of bins {[start_bin, *list(contribbins)]}")

    return dirbindataframesout


def match_closest_time(reftime: float, searchtimes: list[Any]) -> str:
    """Get time closest to reftime in list of times (searchtimes)."""
    return str(f"{min([float(x) for x in searchtimes], key=lambda x: abs(x - reftime))}")


def get_vpkt_config(modelpath: Union[Path, str]) -> dict[str, Any]:
    filename = Path(modelpath, "vpkt.txt")
    vpkt_config: dict[str, Any] = {}
    with open(filename) as vpkt_txt:
        vpkt_config["nobsdirections"] = int(vpkt_txt.readline())
        vpkt_config["cos_theta"] = [float(x) for x in vpkt_txt.readline().split()]
        vpkt_config["phi"] = [float(x) for x in vpkt_txt.readline().split()]
        nspecflag = int(vpkt_txt.readline())

        if nspecflag == 1:
            vpkt_config["nspectraperobs"] = int(vpkt_txt.readline())
            for _ in range(vpkt_config["nspectraperobs"]):
                vpkt_txt.readline()
        else:
            vpkt_config["nspectraperobs"] = 1

        vpkt_config["time_limits_enabled"], vpkt_config["initial_time"], vpkt_config["final_time"] = (
            int(x) for x in vpkt_txt.readline().split()
        )

    return vpkt_config


@lru_cache(maxsize=8)
def get_grid_mapping(modelpath: Union[Path, str]) -> tuple[dict[int, list[int]], dict[int, int]]:
    """Return dict with the associated propagation cells for each model grid cell and
    a dict with the associated model grid cell of each propagration cell.
    """
    modelpath = Path(modelpath)
    filename = firstexisting("grid.out", tryzipped=True, folder=modelpath) if modelpath.is_dir() else Path(modelpath)

    assoc_cells: dict[int, list[int]] = {}
    mgi_of_propcells: dict[int, int] = {}
    with open(filename) as fgrid:
        for line in fgrid:
            row = line.split()
            propcellid, mgi = int(row[0]), int(row[1])
            if mgi not in assoc_cells:
                assoc_cells[mgi] = []
            assoc_cells[mgi].append(propcellid)
            mgi_of_propcells[propcellid] = mgi

    return assoc_cells, mgi_of_propcells


def get_wid_init_at_tmin(modelpath: Path) -> float:
    # cell width in cm at time tmin
    day_to_sec = 86400
    tmin = get_timestep_times_float(modelpath, loc="start")[0] * day_to_sec
    _, modelmeta = at.get_modeldata(modelpath)

    rmax: float = modelmeta["vmax_cmps"] * tmin

    coordmax0 = rmax
    ncoordgrid0 = 50

    wid_init = 2 * coordmax0 / ncoordgrid0
    return wid_init


def get_wid_init_at_tmodel(
    modelpath: Union[Path, str, None] = None,
    ngridpoints: Optional[int] = None,
    t_model_days: Optional[float] = None,
    xmax: Optional[float] = None,
) -> float:
    if ngridpoints is None or t_model_days is None or xmax is None:
        # Luke: ngridpoint only equals the number of model cells if the model is 3D
        assert modelpath is not None
        dfmodel, modelmeta = at.get_modeldata(modelpath, getheadersonly=True)
        assert modelmeta["dimensions"] == 3
        ngridpoints = len(dfmodel)
        xmax = modelmeta["vmax_cmps"] * modelmeta["t_model_init_days"] * 86400
    ncoordgridx: int = round(ngridpoints ** (1.0 / 3.0))

    assert xmax is not None
    wid_init = 2.0 * xmax / ncoordgridx

    return wid_init


def get_syn_dir(modelpath: Path) -> tuple[float, float, float]:
    if not (modelpath / "syn_dir.txt").is_file():
        print(f"{modelpath / 'syn_dir.txt'} does not exist. using x,y,z = 0,0,1")
        return (0.0, 0.0, 1.0)

    with open(modelpath / "syn_dir.txt") as syn_dir_file:
        x, y, z = (float(i) for i in syn_dir_file.readline().split())
        syn_dir = (x, y, z)

    return syn_dir


def vec_len(vec: Union[Sequence[float], np.ndarray[Any, np.dtype[np.float64]]]) -> float:
    return float(np.sqrt(np.dot(vec, vec)))


@lru_cache(maxsize=16)
def get_nu_grid(modelpath: Path) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Get an array of frequencies at which the ARTIS spectra are binned by exspec."""
    specfilename = firstexisting(["spec.out", "specpol.out"], folder=modelpath, tryzipped=True)
    specdata = pd.read_csv(specfilename, delim_whitespace=True)
    return specdata.loc[:, "0"].to_numpy()


def get_deposition(modelpath: Union[Path, str] = ".") -> pd.DataFrame:
    if Path(modelpath).is_file():
        depfilepath = modelpath
        modelpath = Path(modelpath).parent
    else:
        depfilepath = Path(modelpath, "deposition.out")

    ts_mids = get_timestep_times_float(modelpath, loc="mid")

    with open(depfilepath) as fdep:
        filepos = fdep.tell()
        line = fdep.readline()
        if line.startswith("#"):
            columns = line.lstrip("#").split()
        else:
            fdep.seek(filepos)  # undo the readline() and go back
            columns = ["tmid_days", "gammadep_Lsun", "positrondep_Lsun", "total_dep_Lsun"]

        depdata = pd.read_csv(fdep, delim_whitespace=True, header=None, names=columns)

    depdata.index.name = "timestep"

    # no timesteps are given in the old format of deposition.out, so ensure that
    # the times in days match up with the times of our assumed timesteps
    for timestep, row in depdata.iterrows():
        assert abs(ts_mids[timestep] / row["tmid_days"] - 1) < 0.01  # deposition times don't match input.txt

    return depdata


@lru_cache(maxsize=16)
def get_timestep_times_float(
    modelpath: Union[Path, str], loc: Literal["mid", "start", "end", "delta"] = "mid"
) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Return a list of the time in days of each timestep."""
    modelpath = Path(modelpath)
    # virtual path to code comparison workshop models
    if not modelpath.exists() and modelpath.parts[0] == "codecomparison":
        import artistools.codecomparison

        return artistools.codecomparison.get_timestep_times_float(modelpath=modelpath, loc=loc)

    modelpath = modelpath if modelpath.is_dir() else modelpath.parent

    # custom timestep file
    tsfilepath = Path(modelpath, "timesteps.out")
    if tsfilepath.exists():
        dftimesteps = pd.read_csv(tsfilepath, delim_whitespace=True, escapechar="#", index_col="timestep")
        if loc == "mid":
            return dftimesteps.tmid_days.to_numpy()
        if loc == "start":
            return dftimesteps.tstart_days.to_numpy()
        if loc == "end":
            return dftimesteps.tstart_days.to_numpy() + dftimesteps.twidth_days.to_numpy()
        if loc == "delta":
            return dftimesteps.twidth_days.to_numpy()

        msg = "loc must be one of 'mid', 'start', 'end', or 'delta'"
        raise ValueError(msg)

    # older versions of Artis always used logarithmic timesteps and didn't produce a timesteps.out file
    inputparams = get_inputparams(modelpath)
    tmin = inputparams["tmin"]
    dlogt = (math.log(inputparams["tmax"]) - math.log(tmin)) / inputparams["ntstep"]
    timesteps = range(inputparams["ntstep"])
    if loc == "mid":
        tmids = np.array([tmin * math.exp((ts + 0.5) * dlogt) for ts in timesteps])
        return tmids
    if loc == "start":
        tstarts = np.array([tmin * math.exp(ts * dlogt) for ts in timesteps])
        return tstarts
    if loc == "end":
        tends = np.array([tmin * math.exp((ts + 1) * dlogt) for ts in timesteps])
        return tends
    if loc == "delta":
        tdeltas = np.array([tmin * (math.exp((ts + 1) * dlogt) - math.exp(ts * dlogt)) for ts in timesteps])
        return tdeltas

    msg = "loc must be one of 'mid', 'start', 'end', or 'delta'"
    raise ValueError(msg)


def get_timestep_of_timedays(modelpath: Path, timedays: Union[str, float]) -> int:
    """Return the timestep containing the given time in days."""
    if isinstance(timedays, str):
        # could be a string like '330d'
        timedays = timedays.rstrip("d")

    timedays_float = float(timedays)

    arr_tstart = get_timestep_times_float(modelpath, loc="start")
    arr_tend = get_timestep_times_float(modelpath, loc="end")
    # to avoid roundoff errors, use the next timestep's tstart at each timestep's tend (t_width is not exact)
    arr_tend[:-1] = arr_tstart[1:]

    for ts, (tstart, tend) in enumerate(zip(arr_tstart, arr_tend)):
        if timedays_float >= tstart and timedays_float < tend:
            return ts

    msg = f"Could not find timestep bracketing time {timedays_float}"
    raise ValueError(msg)


def get_time_range(
    modelpath: Path,
    timestep_range_str: Optional[str] = None,
    timemin: Optional[float] = None,
    timemax: Optional[float] = None,
    timedays_range_str: Union[None, str, float] = None,
) -> tuple[int, int, Optional[float], Optional[float]]:
    """Handle a time range specified in either days or timesteps."""
    # assertions make sure time is specified either by timesteps or times in days, but not both!
    tstarts = get_timestep_times_float(modelpath, loc="start")
    tmids = get_timestep_times_float(modelpath, loc="mid")
    tends = get_timestep_times_float(modelpath, loc="end")

    if timemin and timemin > tends[-1]:
        print(f"{get_model_name(modelpath)}: WARNING timemin {timemin} is after the last timestep at {tends[-1]:.1f}")
        return -1, -1, timemin, timemax
    if timemax and timemax < tstarts[0]:
        print(
            f"{get_model_name(modelpath)}: WARNING timemax {timemax} is before the first timestep at {tstarts[0]:.1f}"
        )
        return -1, -1, timemin, timemax

    if timestep_range_str is not None:
        if "-" in timestep_range_str:
            timestepmin, timestepmax = (int(nts) for nts in timestep_range_str.split("-"))
        else:
            timestepmin = int(timestep_range_str)
            timestepmax = timestepmin
    elif (timemin is not None and timemax is not None) or timedays_range_str is not None:
        # time days range is specified
        timestepmin = None
        timestepmax = None
        if timedays_range_str is not None:
            if isinstance(timedays_range_str, str) and "-" in timedays_range_str:
                timemin, timemax = (float(timedays) for timedays in timedays_range_str.split("-"))
            else:
                timeavg = float(timedays_range_str)
                timestepmin = get_timestep_of_timedays(modelpath, timeavg)
                timestepmax = timestepmin
                timemin = tstarts[timestepmin]
                timemax = tends[timestepmax]
                # timedelta = 10
                # timemin, timemax = timeavg - timedelta, timeavg + timedelta

        assert timemin is not None

        for timestep, tmid in enumerate(tmids):
            if tmid >= float(timemin):
                timestepmin = timestep
                break

        if timestepmin is None:
            print(f"Time min {timemin} is greater than all timesteps ({tstarts[0]} to {tends[-1]})")
            raise ValueError

        if not timemax:
            timemax = tends[-1]
        assert timemax is not None

        for timestep, tmid in enumerate(tmids):
            if tmid <= float(timemax):
                timestepmax = timestep

        if timestepmax < timestepmin:
            msg = "Specified time range does not include any full timesteps."
            raise ValueError(msg)
    else:
        msg = "Either time or timesteps must be specified."
        raise ValueError(msg)

    timesteplast = len(tmids) - 1
    if timestepmax is not None and timestepmax > timesteplast:
        print(f"Warning timestepmax {timestepmax} > timesteplast {timesteplast}")
        timestepmax = timesteplast
    time_days_lower = float(tstarts[timestepmin])
    time_days_upper = float(tends[timestepmax])
    assert timestepmin is not None
    assert timestepmax is not None

    return timestepmin, timestepmax, time_days_lower, time_days_upper


def get_timestep_time(modelpath: Union[Path, str], timestep: int) -> float:
    """Return the time in days of the midpoint of a timestep number."""
    timearray = get_timestep_times_float(modelpath, loc="mid")
    if timearray is not None:
        return timearray[timestep]

    return -1


def get_escaped_arrivalrange(modelpath: Union[Path, str]) -> tuple[int, Optional[float], Optional[float]]:
    modelpath = Path(modelpath)
    dfmodel, modelmeta = at.inputmodel.get_modeldata(modelpath, printwarningsonly=True, getheadersonly=True)
    vmax = modelmeta["vmax_cmps"]
    cornervmax = math.sqrt(3 * vmax**2)

    # find the earliest possible escape time and add the largest possible travel time

    # for 3D models, the box corners can have non-zero density (allowing packet escape from tmin)
    # for 1D and 2D, the largest escape radius at tmin is the box side radius
    vmax_tmin = cornervmax if at.inputmodel.get_dfmodel_dimensions(dfmodel) == 3 else vmax

    # earliest completely valid time is tmin plus maximum possible travel time from corner to origin
    validrange_start_days = at.get_timestep_times_float(modelpath, loc="start")[0] * (1 + vmax_tmin / 29979245800)

    t_end = at.get_timestep_times_float(modelpath, loc="end")
    # find the last possible escape time and subtract the largest possible travel time (observer time correction)
    try:
        depdata = at.get_deposition(modelpath=modelpath)  # use this file to find the last computed timestep
        nts_last = depdata.ts.max() if "ts" in depdata.columns else len(depdata) - 1
    except FileNotFoundError:
        print("WARNING: No deposition.out file found. Assuming all timesteps have been computed")
        nts_last = len(t_end) - 1

    nts_last_tend = t_end[nts_last]

    # latest possible valid range is the end of the latest computed timestep plus the longest travel time
    validrange_end_days = nts_last_tend * (1 - cornervmax / 29979245800)

    if validrange_start_days > validrange_end_days:
        validrange_start_days, validrange_end_days = None, None

    return nts_last, validrange_start_days, validrange_end_days


@lru_cache(maxsize=8)
def get_model_name(path: Union[Path, str]) -> str:
    """Get the name of an ARTIS model from the path to any file inside it.

    Name will be either from a special plotlabel.txt file if it exists or the enclosing directory name
    """
    path = Path(path)
    if not path.exists() and path.parts[0] == "codecomparison":
        return str(path)

    abspath = path.resolve()

    modelpath = abspath if abspath.is_dir() else abspath.parent

    try:
        plotlabelfile = Path(modelpath, "plotlabel.txt")
        with open(plotlabelfile) as f:
            return f.readline().strip()
    except FileNotFoundError:
        return os.path.basename(modelpath)


def get_z_a_nucname(nucname: str) -> tuple[int, int]:
    """Return atomic number and mass number from a string like 'Pb208' (returns 92, 208)."""
    if nucname.startswith("X_"):
        nucname = nucname[2:]
    z = get_atomic_number(nucname.rstrip("0123456789"))
    assert z > 0
    a = int(nucname.lower().lstrip("abcdefghijklmnopqrstuvwxyz"))
    return z, a


@lru_cache(maxsize=1)
def get_elsymbolslist() -> list[str]:
    elsymbols = [
        "n",
        *list(pd.read_csv(at.get_config()["path_datadir"] / "elements.csv", usecols=["symbol"])["symbol"].to_numpy()),
    ]

    return elsymbols


def get_atomic_number(elsymbol: str) -> int:
    assert elsymbol is not None
    if elsymbol.startswith("X_"):
        elsymbol = elsymbol[2:]

    elsymbol = elsymbol.split("_")[0].split("-")[0].rstrip("0123456789")

    if elsymbol.title() in get_elsymbolslist():
        return get_elsymbolslist().index(elsymbol.title())

    return -1


def decode_roman_numeral(strin: str) -> int:
    if strin.upper() in roman_numerals:
        return roman_numerals.index(strin.upper())
    return -1


def get_elsymbol(atomic_number: int) -> str:
    return get_elsymbolslist()[atomic_number]


@lru_cache(maxsize=16)
def get_ionstring(
    atomic_number: int, ionstage: Union[int, Literal["ALL"], None], spectral: bool = True, nospace: bool = False
) -> str:
    if ionstage == "ALL" or ionstage is None:
        return f"{get_elsymbol(atomic_number)}"

    if spectral:
        return f"{get_elsymbol(atomic_number)}{' ' if not nospace else ''}{roman_numerals[ionstage]}"

    # ion notion e.g. Co+, Fe2+
    if ionstage > 2:
        strcharge = r"$^{" + str(ionstage - 1) + r"{+}}$"
    elif ionstage == 2:
        strcharge = r"$^{+}$"
    else:
        strcharge = ""
    return f"{get_elsymbol(atomic_number)}{strcharge}"


# based on code from https://gist.github.com/kgaughan/2491663/b35e9a117b02a3567c8107940ac9b2023ba34ced
def parse_range(rng: str, dictvars: dict[str, int]) -> Iterable[Any]:
    """Parse a string with an integer range and return a list of numbers, replacing special variables in dictvars."""
    strparts = rng.split("-")

    if len(strparts) not in [1, 2]:
        msg = f"Bad range: '{rng}'"
        raise ValueError(msg)

    parts = [int(i) if i not in dictvars else dictvars[i] for i in strparts]
    start: int = parts[0]
    end: int = start if len(parts) == 1 else parts[1]

    if start > end:
        end, start = start, end

    return range(start, end + 1)


def parse_range_list(rngs: Union[str, list], dictvars: Optional[dict] = None) -> list[Any]:
    """Parse a string with comma-separated ranges or a list of range strings.

    Return a sorted list of integers in any of the ranges.
    """
    if isinstance(rngs, list):
        rngs = ",".join(rngs)
    elif not hasattr(rngs, "split"):
        return [rngs]

    return sorted(set(chain.from_iterable([parse_range(rng, dictvars or {}) for rng in rngs.split(",")])))


def makelist(x: Union[None, list, Sequence, str, Path]) -> list[Any]:
    """If x is not a list (or is a string), make a list containing x."""
    if x is None:
        return []
    if isinstance(x, (str, Path)):
        return [x]
    return list(x)


def trim_or_pad(requiredlength: int, *listoflistin: list[list[Any]]) -> Iterator[list[Any]]:
    """Make lists equal in length to requiredlength either by padding with None or truncating."""
    for listin in listoflistin:
        listin = makelist(listin)

        listout = [listin[i] if i < len(listin) else None for i in range(requiredlength)]

        assert len(listout) == requiredlength
        yield listout


def flatten_list(listin: list) -> list:
    listout = []
    for elem in listin:
        if isinstance(elem, list):
            listout.extend(elem)
        else:
            listout.append(elem)
    return listout


def zopen(filename: Union[Path, str], mode: str = "rt", encoding: Optional[str] = None) -> Any:
    """Open filename, filename.gz or filename.xz."""
    ext_fopen = [(".lz4", lz4.frame.open), (".zst", pyzstd.open), (".gz", gzip.open), (".xz", xz.open)]

    for ext, fopen in ext_fopen:
        file_ext = str(filename) if str(filename).endswith(ext) else str(filename) + ext
        if Path(file_ext).exists():
            return fopen(file_ext, mode=mode, encoding=encoding)

    # open() can raise file not found if this file doesn't exist
    return open(filename, mode=mode, encoding=encoding)  # noqa: SIM115


def firstexisting(
    filelist: Union[Sequence[Union[str, Path]], str, Path],
    folder: Union[Path, str] = Path("."),
    tryzipped: bool = True,
) -> Path:
    """Return the first existing file in file list. If none exist, raise exception."""
    if isinstance(filelist, (str, Path)):
        filelist = [filelist]

    fullpaths = []
    for filename in filelist:
        fullpaths.append(Path(folder) / filename)

        if tryzipped:
            for ext in [".lz4", ".zst", ".gz", ".xz"]:
                filenameext = str(filename) if str(filename).endswith(ext) else str(filename) + ext
                if filenameext not in filelist:
                    fullpaths.append(Path(folder) / filenameext)

    for fullpath in fullpaths:
        if fullpath.exists():
            return fullpath

    msg = f"None of these files exist in {folder}: {', '.join([str(x) for x in fullpaths])}"
    raise FileNotFoundError(msg)


def anyexist(
    filelist: Sequence[Union[str, Path]],
    folder: Union[Path, str] = Path("."),
    tryzipped: bool = True,
) -> bool:
    """Return true if any files in file list exist."""
    try:
        firstexisting(filelist=filelist, folder=folder, tryzipped=tryzipped)
    except FileNotFoundError:
        return False

    return True


def stripallsuffixes(f: Path) -> Path:
    """Take a file path (e.g. packets00_0000.out.gz) and return the Path with no suffixes (e.g. packets)."""
    f_nosuffixes = Path(f)
    for _ in f.suffixes:
        f_nosuffixes = f_nosuffixes.with_suffix("")  # each call removes only one suffix

    return f_nosuffixes


def readnoncommentline(file: io.TextIOBase) -> str:
    """Read a line from the text file, skipping blank and comment lines that begin with #."""
    line = ""

    while not line.strip() or line.strip().lstrip().startswith("#"):
        line = file.readline()

    return line


@lru_cache(maxsize=24)
def get_file_metadata(filepath: Union[Path, str]) -> dict[str, Any]:
    filepath = Path(filepath)

    def add_derived_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        if "a_v" in metadata and "e_bminusv" in metadata and "r_v" not in metadata:
            metadata["r_v"] = metadata["a_v"] / metadata["e_bminusv"]
        elif "e_bminusv" in metadata and "r_v" in metadata and "a_v" not in metadata:
            metadata["a_v"] = metadata["e_bminusv"] * metadata["r_v"]
        elif "a_v" in metadata and "r_v" in metadata and "e_bminusv" not in metadata:
            metadata["e_bminusv"] = metadata["a_v"] / metadata["r_v"]

        return metadata

    import yaml

    filepath = Path(str(filepath).replace(".xz", "").replace(".gz", "").replace(".lz4", "").replace(".zst", ""))

    # check if the reference file (e.g. spectrum.txt) has an metadata file (spectrum.txt.meta.yml)
    individualmetafile = filepath.with_suffix(filepath.suffix + ".meta.yml")
    if individualmetafile.exists():
        with individualmetafile.open("r") as yamlfile:
            metadata = yaml.load(yamlfile, Loader=yaml.FullLoader)

        return add_derived_metadata(metadata)

    # check if the metadata is in the big combined metadata file (todo: eliminate this file)
    combinedmetafile = Path(filepath.parent.resolve(), "metadata.yml")
    if combinedmetafile.exists():
        with combinedmetafile.open("r") as yamlfile:
            combined_metadata = yaml.load(yamlfile, Loader=yaml.FullLoader)
        metadata = combined_metadata.get(str(filepath), {})

        return add_derived_metadata(metadata)

    return {}


def get_filterfunc(
    args: argparse.Namespace, mode: str = "interp"
) -> Optional[Callable[[Union[list[float], np.ndarray]], np.ndarray]]:
    """Use command line arguments to determine the appropriate filter function."""
    filterfunc: Optional[Callable[[Union[list[float], np.ndarray]], np.ndarray]] = None
    dictargs = vars(args)

    if dictargs.get("filtermovingavg", False):

        def movavgfilterfunc(ylist: Union[list[float], np.ndarray]) -> np.ndarray:
            n = args.filtermovingavg
            arr_padded = np.pad(ylist, (n // 2, n - 1 - n // 2), mode="edge")
            return np.convolve(arr_padded, np.ones((n,)) / n, mode="valid")

        assert filterfunc is None
        filterfunc = movavgfilterfunc

    if dictargs.get("filtersavgol", False):
        import scipy.signal

        window_length, poly_order = (int(x) for x in args.filtersavgol)

        def savgolfilterfunc(ylist: Union[list[float], np.ndarray]) -> np.ndarray:
            return scipy.signal.savgol_filter(ylist, window_length, poly_order, mode=mode)

        assert filterfunc is None
        filterfunc = savgolfilterfunc

        print("Applying Savitzky-Golay filter")

    return filterfunc


def join_pdf_files(pdf_list: list[str], modelpath_list: list[Path]) -> None:
    from PyPDF2 import PdfFileMerger

    merger = PdfFileMerger()

    for pdf, modelpath in zip(pdf_list, modelpath_list):
        fullpath = firstexisting([pdf], folder=modelpath)
        merger.append(open(fullpath, "rb"))  # noqa: SIM115
        fullpath.unlink()

    resultfilename = f'{pdf_list[0].split(".")[0]}-{pdf_list[-1].split(".")[0]}'
    with open(f"{resultfilename}.pdf", "wb") as resultfile:
        merger.write(resultfile)

    print(f"Files merged and saved to {resultfilename}.pdf")


@lru_cache(maxsize=2)
def get_bflist(modelpath: Union[Path, str]) -> dict[int, tuple[int, int, int, int]]:
    compositiondata = get_composition_data(modelpath)
    bflist = {}
    bflistpath = firstexisting(["bflist.out", "bflist.dat"], folder=modelpath, tryzipped=True)
    with zopen(bflistpath) as filein:
        bflistcount = int(filein.readline())

        for _ in range(bflistcount):
            rowints = [int(x) for x in filein.readline().split()]
            i, elementindex, ionindex, level = rowints[:4]
            upperionlevel = rowints[4] if len(rowints) > 4 else -1
            atomic_number = compositiondata.Z[elementindex]
            ion_stage = ionindex + compositiondata.lowermost_ionstage[elementindex]
            bflist[i] = (atomic_number, ion_stage, level, upperionlevel)

    return bflist


linetuple = namedtuple("linetuple", "lambda_angstroms atomic_number ionstage upperlevelindex lowerlevelindex")


def read_linestatfile(
    filepath: Union[Path, str]
) -> tuple[int, list[float], list[int], list[int], list[int], list[int]]:
    """Load linestat.out containing transitions wavelength, element, ion, upper and lower levels."""
    print(f"Loading {filepath}")

    data = np.loadtxt(zopen(filepath))
    lambda_angstroms = data[0] * 1e8
    nlines = len(lambda_angstroms)

    atomic_numbers = data[1].astype(int)
    assert len(atomic_numbers) == nlines

    ion_stages = data[2].astype(int)
    assert len(ion_stages) == nlines

    # the file adds one to the levelindex, i.e. lowest level is 1
    upper_levels = data[3].astype(int)
    assert len(upper_levels) == nlines

    lower_levels = data[4].astype(int)
    assert len(lower_levels) == nlines

    return nlines, lambda_angstroms, atomic_numbers, ion_stages, upper_levels, lower_levels


def get_linelist_pldf(modelpath: Union[Path, str]) -> pl.LazyFrame:
    textfile = at.firstexisting("linestat.out", folder=modelpath)
    parquetfile = Path(modelpath, "linelist.out.parquet")
    if not parquetfile.is_file() or parquetfile.stat().st_mtime < textfile.stat().st_mtime:
        _, lambda_angstroms, atomic_numbers, ion_stages, upper_levels, lower_levels = read_linestatfile(textfile)

        pldf = (
            pl.DataFrame(
                {
                    "lambda_angstroms": lambda_angstroms,
                    "atomic_number": atomic_numbers,
                    "ion_stage": ion_stages,
                    "upper_level": upper_levels,
                    "lower_level": lower_levels,
                },
            )
            # .with_columns(pl.col(pl.Int64).cast(pl.Int32))
            .with_row_count(name="lineindex")
        )
        pldf.write_parquet(parquetfile, compression="zstd")
        print(f"Saved {parquetfile}")
    else:
        print(f"Reading {parquetfile}")

    return pl.scan_parquet(parquetfile)


def get_linelist_dict(modelpath: Union[Path, str]) -> dict[int, linetuple]:
    nlines, lambda_angstroms, atomic_numbers, ion_stages, upper_levels, lower_levels = read_linestatfile(
        Path(modelpath, "linestat.out")
    )
    linelistdict = {
        index: linetuple(lambda_a, Z, ionstage, upper, lower)
        for index, lambda_a, Z, ionstage, upper, lower in zip(
            range(nlines), lambda_angstroms, atomic_numbers, ion_stages, upper_levels, lower_levels
        )
    }
    return linelistdict


@lru_cache(maxsize=8)
def get_linelist_dataframe(
    modelpath: Union[Path, str],
) -> pd.DataFrame:
    nlines, lambda_angstroms, atomic_numbers, ion_stages, upper_levels, lower_levels = read_linestatfile(
        Path(modelpath, "linestat.out")
    )

    dflinelist = pd.DataFrame(
        {
            "lambda_angstroms": lambda_angstroms,
            "atomic_number": atomic_numbers,
            "ionstage": ion_stages,
            "upperlevelindex": upper_levels,
            "lowerlevelindex": lower_levels,
        },
        dtype={
            "lambda_angstroms": float,
            "atomic_number": int,
            "ionstage": int,
            "upperlevelindex": int,
            "lowerlevelindex": int,
        },
    )
    dflinelist.index.name = "linelistindex"

    return dflinelist


@lru_cache(maxsize=8)
def get_npts_model(modelpath: Path) -> int:
    """Return the number of cell in the model.txt."""
    modelfilepath = (
        Path(modelpath)
        if Path(modelpath).is_file()
        else at.firstexisting("model.txt", folder=modelpath, tryzipped=True)
    )
    with zopen(modelfilepath) as modelfile:
        npts_model = int(readnoncommentline(modelfile))
    return npts_model


@lru_cache(maxsize=8)
def get_nprocs(modelpath: Path) -> int:
    """Return the number of MPI processes specified in input.txt."""
    return int(Path(modelpath, "input.txt").read_text().split("\n")[21].split("#")[0])


@lru_cache(maxsize=8)
def get_inputparams(modelpath: Path) -> dict[str, Any]:
    """Return parameters specified in input.txt."""
    from astropy import constants as const
    from astropy import units as u

    params: dict[str, Any] = {}
    with Path(modelpath, "input.txt").open("r") as inputfile:
        params["pre_zseed"] = int(readnoncommentline(inputfile).split("#")[0])

        # number of time steps
        params["ntstep"] = int(readnoncommentline(inputfile).split("#")[0])

        # number of start and end time step
        params["itstep"], params["ftstep"] = (int(x) for x in readnoncommentline(inputfile).split("#")[0].split())

        params["tmin"], params["tmax"] = (float(x) for x in readnoncommentline(inputfile).split("#")[0].split())

        params["nusyn_min"], params["nusyn_max"] = (
            (float(x) * u.MeV / const.h).to("Hz") for x in readnoncommentline(inputfile).split("#")[0].split()
        )

        # number of times for synthesis
        params["nsyn_time"] = int(readnoncommentline(inputfile).split("#")[0])

        # start and end times for synthesis
        params["nsyn_time_start"], params["nsyn_time_end"] = (
            float(x) for x in readnoncommentline(inputfile).split("#")[0].split()
        )

        params["n_dimensions"] = int(readnoncommentline(inputfile).split("#")[0])

        # there are more parameters in the file that are not read yet...

    return params


@lru_cache(maxsize=16)
def get_runfolder_timesteps(folderpath: Union[Path, str]) -> tuple[int, ...]:
    """Get the set of timesteps covered by the output files in an ARTIS run folder."""
    folder_timesteps = set()
    try:
        with zopen(Path(folderpath, "estimators_0000.out")) as estfile:
            restart_timestep = -1
            for line in estfile:
                if line.startswith("timestep "):
                    timestep = int(line.split()[1])

                    if restart_timestep < 0 and timestep != 0 and 0 not in folder_timesteps:
                        # the first timestep of a restarted run is duplicate and should be ignored
                        restart_timestep = timestep

                    if timestep != restart_timestep:
                        folder_timesteps.add(timestep)

    except FileNotFoundError:
        pass

    return tuple(folder_timesteps)


def get_runfolders(
    modelpath: Union[Path, str], timestep: Optional[int] = None, timesteps: Optional[Sequence[int]] = None
) -> Sequence[Path]:
    """Get a list of folders containing ARTIS output files from a modelpath, optionally with a timestep restriction.

    The folder list may include non-ARTIS folders if a timestep is not specified.
    """
    folderlist_all = (*sorted([child for child in Path(modelpath).iterdir() if child.is_dir()]), Path(modelpath))
    folder_list_matching = []
    if (timestep is not None and timestep > -1) or (timesteps is not None and len(timesteps) > 0):
        for folderpath in folderlist_all:
            folder_timesteps = get_runfolder_timesteps(folderpath)
            if timesteps is None and timestep is not None and timestep in folder_timesteps:
                return (folderpath,)
            if timesteps is not None and any(ts in folder_timesteps for ts in timesteps):
                folder_list_matching.append(folderpath)

        return tuple(folder_list_matching)

    return [folderpath for folderpath in folderlist_all if get_runfolder_timesteps(folderpath)]


def get_mpiranklist(
    modelpath: Union[Path, str],
    modelgridindex: Optional[Union[Iterable[int], int]] = None,
    only_ranks_withgridcells: bool = False,
) -> Sequence[int]:
    """Get a list of rank ids.

    - modelpath:
        pathlib.Path() to ARTIS model folder
    - modelgridindex:
        give a cell number to only return the rank number that updates this cell (and outputs its estimators)
    - only_ranks_withgridcells:
        set True to skip ranks that only update packets (i.e. that don't update any grid cells/output estimators).
    """
    if modelgridindex is None or modelgridindex == []:
        if only_ranks_withgridcells:
            return range(min(get_nprocs(modelpath), get_npts_model(modelpath)))
        return range(get_nprocs(modelpath))

    if isinstance(modelgridindex, Iterable):
        mpiranklist = set()
        for mgi in modelgridindex:
            if mgi < 0:
                if only_ranks_withgridcells:
                    return range(min(get_nprocs(modelpath), get_npts_model(modelpath)))
                return range(get_nprocs(modelpath))

            mpiranklist.add(get_mpirankofcell(mgi, modelpath=modelpath))

        return sorted(mpiranklist)

    # in case modelgridindex is a single number rather than an iterable
    if modelgridindex < 0:
        return range(min(get_nprocs(modelpath), get_npts_model(modelpath)))

    return [get_mpirankofcell(modelgridindex, modelpath=modelpath)]


def get_cellsofmpirank(mpirank: int, modelpath: Union[Path, str]) -> Iterable[int]:
    """Return an iterable of the cell numbers processed by a given MPI rank."""
    npts_model = get_npts_model(modelpath)
    nprocs = get_nprocs(modelpath)

    assert mpirank < nprocs

    nblock = npts_model // nprocs
    n_leftover = npts_model % nprocs

    if mpirank < n_leftover:
        ndo = nblock + 1
        nstart = mpirank * (nblock + 1)
    else:
        ndo = nblock
        nstart = n_leftover + mpirank * nblock

    return list(range(nstart, nstart + ndo))


@lru_cache(maxsize=16)
def get_dfrankassignments(modelpath: Union[Path, str]) -> Optional[pd.DataFrame]:
    filerankassignments = Path(modelpath, "modelgridrankassignments.out")
    if filerankassignments.is_file():
        df = pd.read_csv(filerankassignments, delim_whitespace=True)
        df = df.rename(columns={df.columns[0]: df.columns[0].lstrip("#")})
        return df
    return None


def get_mpirankofcell(modelgridindex: int, modelpath: Union[Path, str]) -> int:
    """Return the rank number of the MPI process responsible for handling a specified cell's updating and output."""
    modelpath = Path(modelpath)
    npts_model = get_npts_model(modelpath)
    assert modelgridindex < npts_model

    dfrankassignments = get_dfrankassignments(modelpath)
    if dfrankassignments is not None:
        dfselected = dfrankassignments.query(
            "ndo > 0 and nstart <= @modelgridindex and (nstart + ndo - 1) >= @modelgridindex"
        )
        assert len(dfselected) == 1
        return int(dfselected.iloc[0]["rank"])

    nprocs = get_nprocs(modelpath)

    if nprocs > npts_model:
        mpirank = modelgridindex
    else:
        nblock = npts_model // nprocs
        n_leftover = npts_model % nprocs

        mpirank = (
            modelgridindex // (nblock + 1)
            if modelgridindex <= n_leftover * (nblock + 1)
            else n_leftover + (modelgridindex - n_leftover * (nblock + 1)) // nblock
        )

    assert modelgridindex in get_cellsofmpirank(mpirank, modelpath)

    return mpirank


def get_viewingdirectionbincount() -> int:
    return get_viewingdirection_phibincount() * get_viewingdirection_costhetabincount()


def get_viewingdirection_phibincount() -> int:
    return 10


def get_viewingdirection_costhetabincount() -> int:
    return 10


def get_phi_bins() -> tuple[np.ndarray, np.ndarray, list[str]]:
    nphibins = at.get_viewingdirection_phibincount()
    # pi/2 must be an exact boundary because of the change in behaviour there
    assert nphibins % 2 == 0

    # for historical reasons, phi bins ordered by ascending phi are
    # [0, 1, 2, 3, 4, 9, 8, 7, 6, 5] for nphibins == 10

    # convert phibin number to what the number would be if things were sane
    phisteps = list(range(nphibins // 2)) + list(reversed(range(nphibins // 2, nphibins)))

    phi_lower = np.array([step * 2 * math.pi / nphibins for step in phisteps])
    phi_upper = np.array([(step + 1) * 2 * math.pi / nphibins for step in phisteps])

    binlabels = []
    for phibin, step in enumerate(phisteps):
        str_phi_lower = f"{step}π/{nphibins // 2}" if step > 0 else "0"
        lower_compare = "≤" if phibin < (nphibins // 2) else "<"
        str_phi_upper = f"{step+1}π/{nphibins // 2}" if step < nphibins - 1 else "2π"
        upper_compare = "≤" if phibin > (nphibins // 2) else "<"
        binlabels.append(f"{str_phi_lower} {lower_compare} ϕ {upper_compare} {str_phi_upper}")

    return phi_lower, phi_upper, binlabels


def get_costheta_bins() -> tuple[np.ndarray, np.ndarray, list[str]]:
    ncosthetabins = at.get_viewingdirection_costhetabincount()
    costhetabins_lower = np.arange(-1.0, 1.0, 2.0 / ncosthetabins)
    costhetabins_upper = costhetabins_lower + 2.0 / ncosthetabins
    binlabels = [f"{lower:.1f} ≤ cos θ < {upper:.1f}" for lower, upper in zip(costhetabins_lower, costhetabins_upper)]
    return costhetabins_lower, costhetabins_upper, binlabels


def get_costhetabin_phibin_labels() -> tuple[list[str], list[str]]:
    _, _, costhetabinlabels = get_costheta_bins()
    _, _, phibinlabels = get_phi_bins()
    return costhetabinlabels, phibinlabels


def get_vspec_dir_labels(modelpath: Union[str, Path], viewinganglelabelunits: str = "rad") -> dict[int, str]:
    vpkt_config = at.get_vpkt_config(modelpath)
    dirlabels = {}
    for dirindex in range(vpkt_config["nobsdirections"]):
        phi_angle = round(vpkt_config["phi"][dirindex])
        if viewinganglelabelunits == "deg":
            theta_angle = round(math.degrees(math.acos(vpkt_config["cos_theta"][dirindex])))
            dirlabels[dirindex] = rf"v$\theta$ = {theta_angle}$^\circ$, $\phi$ = {phi_angle}$^\circ$"
        elif viewinganglelabelunits == "rad":
            dirlabels[dirindex] = rf"cos $\theta$ = {vpkt_config['cos_theta'][dirindex]}, $\phi$ = {phi_angle}$^\circ$"
    return dirlabels


def get_dirbin_labels(
    dirbins: Union[np.ndarray[Any, np.dtype[Any]], Sequence[int]],
    modelpath: Union[Path, str, None] = None,
    average_over_phi: bool = False,
    average_over_theta: bool = False,
) -> dict[int, str]:
    if modelpath:
        modelpath = Path(modelpath)
        MABINS = at.get_viewingdirectionbincount()
        if len(list(Path(modelpath).glob("*_res_00.out*"))) > 0:  # if the first direction bin file exists
            assert len(list(Path(modelpath).glob(f"*_res_{MABINS-1:02d}.out*"))) > 0  # check last bin exists
            assert len(list(Path(modelpath).glob(f"*_res_{MABINS:02d}.out*"))) == 0  # check one beyond does not exist

    _, _, costhetabinlabels = get_costheta_bins()
    _, _, phibinlabels = get_phi_bins()

    nphibins = at.get_viewingdirection_phibincount()

    angle_definitions: dict[int, str] = {}
    for dirbin in dirbins:
        if dirbin == -1:
            angle_definitions[dirbin] = ""
            continue

        costheta_index = dirbin // nphibins
        phi_index = dirbin % nphibins

        if average_over_phi:
            angle_definitions[dirbin] = f"{costhetabinlabels[costheta_index]}"
            assert phi_index == 0
            assert not average_over_theta
        elif average_over_theta:
            angle_definitions[dirbin] = f"{phibinlabels[phi_index]}"
            assert costheta_index == 0
        else:
            angle_definitions[dirbin] = f"{costhetabinlabels[costheta_index]}, {phibinlabels[phi_index]}"

    return angle_definitions
