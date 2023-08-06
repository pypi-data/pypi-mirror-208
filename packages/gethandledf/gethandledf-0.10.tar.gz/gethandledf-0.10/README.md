# Retrieves the list of handles using the 'handle.exe' command and return the data as a pandas DataFrame.

## pip install gethandledf

### Tested against Windows 10 / Python 3.10 / Anaconda

## Python

```python
from gethandledf import get_handle_list, get_handle_list_interval
df = get_handle_list(partial_process_string="explorer.exe")
df2 = get_handle_list_interval(interval=1, partial_process_string="") # press ctrl+c when you are done


get_handle_list_interval(interval: int = 5, partial_process_string: str = "")->pd.DataFrame:
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
		

get_handle_list(partial_process_string: str = "") -> pd.DataFrame:
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
		
```
