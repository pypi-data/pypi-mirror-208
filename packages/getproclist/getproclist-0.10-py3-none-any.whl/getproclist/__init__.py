import subprocess
import pandas as pd
from flatten_everything import flatten_everything
from time import sleep
from subprocesskiller import kill_subprocs
from a_pandas_ex_less_memory_more_speed import pd_add_less_memory_more_speed
from math import ceil

pd_add_less_memory_more_speed()


def get_proc_list(interval: int = 5) -> pd.DataFrame:
    r"""
    Retrieve the list of processes using the 'wmic' command and return the data as a pandas DataFrame.

    Args:
        interval (int): The interval in seconds at which to retrieve the process list. Defaults to 5.
            It has to be stopped by pressing ctrl+c
            If interval is less than or equal to 0, the process list is captured only once.

    Returns:
        pd.DataFrame: A DataFrame containing information about the processes.

    Raises:
        None

    Example:
        >>> df = get_proc_list(interval=10)
        >>> print(df.head())
               Name  ProcessId  CommandLine  ...
            0  System Idle Process  0           None
            1  System               4           None
            2  smss.exe             248         \SystemRoot\System32\smss.exe
            3  csrss.exe            424         \??\C:\WINDOWS\system32\csrss.exe
            4  wininit.exe          496         \??\C:\WINDOWS\system32\wininit.exe
        ...
    """
    if interval > 0:
        p = subprocess.Popen(
            ["wmic", "process", "list", "FULL", f"/EVERY:{ceil(interval)}"],
            stdout=subprocess.PIPE,
        )
    else:
        p = subprocess.Popen(
            ["wmic", "process", "list", "FULL"],
            stdout=subprocess.PIPE,
        )
    alllists = [[]]
    try:
        for ini, line in enumerate(iter(p.stdout.readline, b"")):
            try:
                line2 = line.decode("utf-8")
                if line2 == "\r\r\n":
                    alllists.append([])
                alllists[-1].append(line2)
            except KeyboardInterrupt:
                print("Killing wmic...")
                kill_subprocs(dontkill=(("Caption", "conhost.exe"),))
                sleep(2)
                break

    except KeyboardInterrupt:
        print("Killing wmic...")

        kill_subprocs(dontkill=(("Caption", "conhost.exe"),))
        print("Creating data frame...")
        sleep(2)

    while True:
        try:
            firstf = [
                [g for y in flatten_everything(x) if (g := y.strip())]
                for x in alllists
            ]
            if firstf:
                break
        except KeyboardInterrupt:
            pass
    firstf = [f for f in firstf if f]
    df2 = pd.concat(
        [
            pd.DataFrame.from_records([y.split("=", maxsplit=1) for y in z if "=" in y])
            .set_index(0)
            .T.assign(procid=ini)
            for ini, z in enumerate(firstf)
        ],
        ignore_index=True,
    )
    df = df2.ds_reduce_memory_size_carefully(verbose=False)
    return df


