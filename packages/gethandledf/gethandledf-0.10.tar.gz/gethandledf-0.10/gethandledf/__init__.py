import subprocess
import pandas as pd
from kthread_sleep import sleep
from subprocesskiller import kill_subprocs
from io import StringIO
import numpy as np
from getfilenuitkapython import get_filepath

handle = get_filepath("handle.exe")


def get_handle_list(partial_process_string: str = "") -> pd.DataFrame:
    r"""
    Retrieve the list of handles using the 'handle.exe' command and return the data as a pandas DataFrame.

    Args:
        partial_process_string (str): A partial process string to filter the handles by a specific process.
            Defaults to an empty string, which retrieves handles for all processes.

    Returns:
        pd.DataFrame: A DataFrame containing information about the handles.

    Raises:
        None

    Example:
        >>> df = get_handle_list(partial_process_string="explorer.exe")
        >>> print(df.head())
              Process  PID               User   Handle Type ShareFlags  \
        0  System         4  NT AUTHORITY\SYSTEM  0x3f4    Key
        1  System         4  NT AUTHORITY\SYSTEM  0x6cc    Key
        2  System         4  NT AUTHORITY\SYSTEM  0x78c    Key
        3  System         4  NT AUTHORITY\SYSTEM  0x790    Key
        4  System         4  NT AUTHORITY\SYSTEM  0x7a8    Key

                          Name            AccessMask
        0  \REGISTRY\MACHINE\BCD       0x20019
        1  \REGISTRY\MACHINE\BCD       0x20019
        2  \REGISTRY\MACHINE\BCD       0x20019
        3  \REGISTRY\MACHINE\BCD       0x20019
        4  \REGISTRY\MACHINE\BCD       0x20019
        ...
    """
    if partial_process_string:
        cm = [
            handle,
            "-accepteula",
            "-a",
            "-g",
            "-v",
            "-nobanner",
            "-p",
            str(partial_process_string),
        ]
    else:
        cm = [handle,"-accepteula", "-a", "-g", "-v", "-nobanner"]
    p = subprocess.run(cm, capture_output=True)
    csv_data = p.stdout.decode("utf-8", "ignore")
    csv_io = StringIO(csv_data)
    df = pd.read_csv(csv_io, encoding_errors="ignore", on_bad_lines="skip")

    df.columns = [
        "Process",
        "PID",
        "User",
        "Handle",
        "Type",
        "ShareFlags",
        "Name",
        "AccessMask",
    ]
    alldtypes = [
        ("Process", "category"),
        ("PID", np.uint16),
        ("User", "category"),
        ("Handle", "category"),
        ("Type", "category"),
        ("ShareFlags", "category"),
        ("Name", "category"),
        ("AccessMask", "category"),
    ]
    for key, cat in alldtypes:
        try:
            if key == "ShareFlags":
                df[key] = df[key].fillna("")
            df[key] = df[key].astype(cat)
        except Exception:
            pass

    return df


def get_handle_list_interval(interval:int=5, partial_process_string:str="")->pd.DataFrame:
    r"""
    Continuously retrieve the list of handles at a specified interval using the 'handle.exe' command
    and return the data as a concatenated pandas DataFrame. Press ctrl+c when you want the capturing to stop

    Args:
        interval (int): The interval in seconds at which to retrieve the handle list. Defaults to 5.
        partial_process_string (str): A partial process string to filter the handles by a specific process.
            Defaults to an empty string, which retrieves handles for all processes.

    Returns:
        pd.DataFrame: A DataFrame containing information about the handles.

    Raises:
        None

    Example:
        >>> df = get_handle_list_interval(interval=1, partial_process_string="")
        >>> print(df.head())
              Process  PID               User   Handle Type ShareFlags  \
        0  System         4  NT AUTHORITY\SYSTEM  0x3f4    Key
        1  System         4  NT AUTHORITY\SYSTEM  0x6cc    Key
        2  System         4  NT AUTHORITY\SYSTEM  0x78c    Key
        3  System         4  NT AUTHORITY\SYSTEM  0x790    Key
        4  System         4  NT AUTHORITY\SYSTEM  0x7a8    Key

                          Name            AccessMask  scan_id
        0  \REGISTRY\MACHINE\BCD       0x20019           0
        1  \REGISTRY\MACHINE\BCD       0x20019           0
        2  \REGISTRY\MACHINE\BCD       0x20019           0
        3  \REGISTRY\MACHINE\BCD       0x20019           0
        4  \REGISTRY\MACHINE\BCD       0x20019           0
        ...
    """
    alldfs = []
    scanid = 0
    try:
        while True:
            try:
                alldfs.append(
                    get_handle_list(
                        partial_process_string=partial_process_string
                    ).assign(scan_id=scanid)
                )
                scanid += 1

            except KeyboardInterrupt:
                print("Killing handle...")

                kill_subprocs(dontkill=(("Caption", "conhost.exe"),))
                print("Creating data frame...")
                sleep(2)
                break
            except Exception:
                pass
            sleep(interval)
    except KeyboardInterrupt:
        print("Killing handle...")

        kill_subprocs(dontkill=(("Caption", "conhost.exe"),))
        print("Creating data frame...")
        sleep(2)
    return pd.concat(alldfs, ignore_index=True)


# examples
# df = get_handle_list(partial_process_string="explorer.exe")
# df2 = get_handle_list_interval(interval=1, partial_process_string="")
