# Retrieves the list of processes using the 'wmic' command and return the data as a pandas DataFrame

## pip install getproclist

### Tested against Windows 10 / Python 3.10 / Anaconda

## Python

```python
from getproclist import get_proc_list
df=get_proc_list(interval=0)
print(df)

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
        >>> df = get_proc_list(interval=10) # press ctrl+c
        >>> print(df.head())
               Name  ProcessId  CommandLine  ...
            0  System Idle Process  0           None
            1  System               4           None
            2  smss.exe             248         \SystemRoot\System32\smss.exe
            3  csrss.exe            424         \??\C:\WINDOWS\system32\csrss.exe
            4  wininit.exe          496         \??\C:\WINDOWS\system32\wininit.exe
        ...  
```
