# human = human-readable, system = system format, month digit = 11
# month name = november, seconds = show seconds, swap 1 = date then time
# swap 2 = month then day

hnnnn12 = '%I:%M %p | %d %B, %Y'        # 12h, human, day then month name                                # 02:34 PM | 15 January, 2023             # 00
hnndn12 = '%I:%M %p | %d/%m/%Y'         # 12h, human, day then month digit                               # 02:34 PM | 15/01/2023                   # 01
hnnns12 = '%I:%M:%S %p | %d %B, %Y'     # 12h, human, day then month name, seconds                       # 02:34:56 PM | 15 January, 2023          # 02
hnnds12 = '%I:%M:%S %p | %d/%m/%Y'      # 12h, human, day then month digit, seconds                      # 02:34:56 PM | 15/01/2023                # 03
snnnn12 = '%I.%M_%p_%d-%B-%Y'           # 12h, system, day then month name                               # 02.34_PM_15-January-2023                # 04
snndn12 = '%I.%M_%p_%d-%m-%Y'           # 12h, system, day then month digit                              # 02.34_PM_15-01-2023                     # 05
snnns12 = '%I.%M.%S_%p_%d-%B-%Y'        # 12h, system, day then month name, seconds                      # 02.34.56_PM_15-January-2023             # 06
snnds12 = '%I.%M.%S_%p_%d-%m-%Y'        # 12h, system, day then month digit, seconds                     # 02.34.56_PM_15-01-2023                  # 07
hsnnn12 = '%d %B, %Y | %I:%M %p'        # 12h, human, day then month name, date then time                # 01 January, 2023 | 02:34 PM             # 08
hsndn12 = '%d/%m/%Y | %I:%M %p'         # 12h, human, day then month digit, date then time               # 01/01/2023 | 02:34 PM                   # 09
hsnns12 = '%d %B, %Y | %I:%M:%S %p'     # 12h, human, day then month name, seconds, date then time       # 15 January, 2023 | 02:34:56 PM          # 10
hsnds12 = '%d/%m/%Y | %I:%M:%S %p'      # 12h, human, day then month digit, seconds, date then time      # 15/01/2023 | 02:34:56 PM                # 11
ssnnn12 = '%d-%B-%Y_%I.%M_%p'           # 12h, system, day then month name, date then time               # 15-January-2023_02.34_PM                # 12
ssndn12 = '%d-%m-%Y_%I.%M_%p'           # 12h, system, day then month digit, date then time              # 15-01-2023_02.34_PM                     # 13
ssnns12 = '%d-%B-%Y_%I.%M.%S_%p'        # 12h, system, day then month name, seconds, date then time      # 15-January-2023_02.34.56_PM             # 14
ssnds12 = '%d-%m-%Y_%I.%M.%S_%p'        # 12h, system, day then month digit, seconds, date then time     # 15-01-2023_02.34.56_PM                  # 15
hnnnn24 = '%H:%M | %d %B, %Y'           # 24h, human, day then month name                                # 14:34 | 15 January, 2023                # 16
hnndn24 = '%H:%M | %d/%m/%Y'            # 24h, human, day then month digit                               # 14:34 | 15/01/2023                      # 17
hnnns24 = '%H:%M:%S | %d %B, %Y'        # 24h, human, day then month name, seconds                       # 14:34:56 | 15 January, 2023             # 18
hnnds24 = '%H:%M:%S | %d/%m/%Y'         # 24h, human, day then month digit, seconds                      # 14:34:56 | 15/01/2023                   # 19
snnnn24 = '%H.%M_%d-%B-%Y'              # 24h, system, day then month name                               # 14.34_15-January-2023                   # 20
snndn24 = '%H.%M_%d-%m-%Y'              # 24h, system, day then month digit                              # 14.34_15-01-2023                        # 21
snnns24 = '%H.%M.%S_%d-%B-%Y'           # 24h, system, day then month name, seconds                      # 14.34.56_15-January-2023                # 22
snnds24 = '%H.%M.%S_%d-%m-%Y'           # 24h, system, day then month digit, seconds                     # 14.34.56_15-01-2023                     # 23
hsnnn24 = '%d %B, %Y | %H:%M'           # 24h, human, day then month name, date then time                # 15 January, 2023 | 14:34                # 24
hsndn24 = '%d/%m/%Y | %H:%M'            # 24h, human, day then month digit, date then time               # 15/01/2023 | 14:34                      # 25
hsnns24 = '%d %B, %Y | %H:%M:%S'        # 24h, human, day then month name, seconds, date then time       # 15 January, 2023 | 14:34:56             # 26
hsnds24 = '%d/%m/%Y | %H:%M:%S'         # 24h, human, day then month digit, seconds, date then time      # 15/01/2023 | 14:34:56                   # 27
ssnnn24 = '%d-%B-%Y_%H.%M'              # 24h, system, day then month name, date then time               # 15-January-2023_14.34                   # 28
ssndn24 = '%d-%m-%Y_%H.%M'              # 24h, system, day then month digit, date then time              # 15-01-2023_14.34                        # 29
ssnns24 = '%d-%B-%Y_%H.%M.%S'           # 24h, system, day then month name, seconds, date then time      # 15-January-2023_14.34.56                # 30
ssnds24 = '%d-%m-%Y_%H.%M.%S'           # 24h, system, day then month digit, seconds, date then time     # 15-01-2023_14.34.56                     # 31
hnsnn12 = '%I:%M %p | %B %d, %Y'        # 12h, human, month name then day                                # 02:34 PM | January 15, 2023             # 32
hnsdn12 = '%I:%M %p | %m/%d/%Y'         # 12h, human, month digit then day                               # 02:34 PM | 01/15/2023                   # 33
hnsns12 = '%I:%M:%S %p | %B %d, %Y'     # 12h, human, month name then day, seconds                       # 02:34:56 PM | January 15, 2023          # 34
hnsds12 = '%I:%M:%S %p | %m/%d/%Y'      # 12h, human, month digit then day, seconds                      # 02:34:56 PM | 01/15/2023                # 35
snsnn12 = '%I.%M_%p_%B-%d-%Y'           # 12h, system, month name then day                               # 02.34_PM_January-15-2023                # 36
snsdn12 = '%I.%M_%p_%m-%d-%Y'           # 12h, system, month digit then day                              # 02.34_PM_01-15-2023                     # 37
snsns12 = '%I.%M.%S_%p_%B-%d-%Y'        # 12h, system, month name then day, seconds                      # 02.34.56_PM_January-15-2023             # 38
snsds12 = '%I.%M.%S_%p_%m-%d-%Y'        # 12h, system, month digit then day, seconds                     # 02.34.56_PM_01-15-2023                  # 39
hssnn12 = '%B %d, %Y | %I:%M %p'        # 12h, human, month name then day, date then time                # January 15, 2023 | 02:34 PM             # 40
hssdn12 = '%m/%d/%Y | %I:%M %p'         # 12h, human, month digit then day, date then time               # 01/15/2023 | 02:34 PM                   # 41
hssns12 = '%B %d, %Y | %I:%M:%S %p'     # 12h, human, month name then day, seconds, date then time       # January 15, 2023 | 02:34:56 PM          # 42
hssds12 = '%m/%d/%Y | %I:%M:%S %p'      # 12h, human, month digit then day, seconds, date then time      # 01/15/2023 | 02:34:56 PM                # 43
sssnn12 = '%B-%d-%Y_%I.%M_%p'           # 12h, system, month name then day, date then time               # January-15-2023_02.34_PM                # 44
sssdn12 = '%m-%d-%Y_%I.%M_%p'           # 12h, system, month digit then day, date then time              # 01-15-2023_02.34_PM                     # 45
sssns12 = '%B-%d-%Y_%I.%M.%S_%p'        # 12h, system, month name then day, seconds, date then time      # January-15-2023_02.34.56_PM             # 46
sssds12 = '%m-%d-%Y_%I.%M.%S_%p'        # 12h, system, month digit then day, seconds, date then time     # 01-15-2023_02.34.56_PM                  # 47
hnsnn24 = '%H:%M | %B %d, %Y'           # 24h, human, month name then day                                # 14:34 | January 15, 2023                # 48
hnsdn24 = '%H:%M | %m/%d/%Y'            # 24h, human, month digit then day                               # 14:34 | 01/15/2023                      # 49
hnsns24 = '%H:%M:%S | %B %d, %Y'        # 24h, human, month name then day, seconds                       # 14:34:56 | January 15, 2023             # 50
hnsds24 = '%H:%M:%S | %m/%d/%Y'         # 24h, human, month digit then day, seconds                      # 14:34:56 | 01/15/2023                   # 51
snsnn24 = '%H.%M_%B-%d-%Y'              # 24h, system, month name then day                               # 14.34_January-15-2023                   # 52
snsdn24 = '%H.%M_%m-%d-%Y'              # 24h, system, month digit then day                              # 14.34_01-15-2023                        # 53
snsns24 = '%H.%M.%S_%B-%d-%Y'           # 24h, system, month name then day, seconds                      # 14.34.56_January-15-2023                # 54
snsds24 = '%H.%M.%S_%m-%d-%Y'           # 24h, system, month digit then day, seconds                     # 14.34.56_01-15-2023                     # 55
hssnn24 = '%B %d, %Y | %H:%M'           # 24h, human, month name then day, date then time                # January 15, 2023 | 14:34                # 56
hssdn24 = '%m/%d/%Y | %H:%M'            # 24h, human, month digit then day, date then time               # 01/15/2023 | 14:34                      # 57
hssns24 = '%B %d, %Y | %H:%M:%S'        # 24h, human, month name then day, seconds, date then time       # January 15, 2023 | 14:34:56             # 58
hssds24 = '%m/%d/%Y | %H:%M:%S'         # 24h, human, month digit then day, seconds, date then time      # 01/15/2023 | 14:34:56                   # 59
sssnn24 = '%B-%d-%Y_%H.%M'              # 24h, system, month name then day, date then time               # January-15-2023_14.34                   # 60
sssdn24 = '%m-%d-%Y_%H.%M'              # 24h, system, month digit then day, date then time              # 01-15-2023_14.34                        # 61
sssns24 = '%B-%d-%Y_%H.%M.%S'           # 24h, system, month name then day, seconds, date then time      # January-15-2023_14.34.56                # 62
sssds24 = '%m-%d-%Y_%H.%M.%S'           # 24h, system, month digit then day, seconds, date then time     # 01-15-2023_14.34.56                     # 63
hnn = '%B %d, %Y'                       # human, month name then day                                     # January 15, 2023                        # 64
hnd = '%m/%d/%Y'                        # human, month digit then day                                    # 01/15/2023                              # 65
snn = '%B-%d-%Y'                        # system, month name then day                                    # January-15-2023                         # 66
snd = '%m-%d-%Y'                        # system, month digit then day                                   # 01-15-2023                              # 67
hsn = '%d %B, %Y'                       # human, day then month name                                     # 15 January, 2023                        # 68
hsd = '%d/%m/%Y'                        # human, day then month digit                                    # 01/15/2023                              # 69
ssn = '%d-%B-%Y'                        # system, day then month name                                    # 15-January-2023                         # 70
ssd = '%d-%m-%Y'                        # system, day then month digit                                   # 01-15-2023                              # 71
hn12 = '%I:%M %p'                       # 12h, human                                                     # 02:34 PM                                # 72
hs12 = '%I:%M:%S %p'                    # 12h, human, seconds                                            # 02:34:56 PM                             # 73
sn12 = '%I.%M_%p'                       # 12h, system                                                    # 02.34_PM                                # 74
ss12 = '%I.%M.%S_%p'                    # 12h, system, seconds                                           # 02.34.56_PM                             # 75
hn24 = '%H:%M'                          # 24h, human                                                     # 14:34                                   # 76
hs24 = '%H:%M:%S'                       # 24h, human, seconds                                            # 14:34:56                                # 77
sn24 = '%H.%M'                          # 24h, system                                                    # 14.34                                   # 78
ss24 = '%H.%M.%S'                       # 24h, system, seconds                                           # 14.34.56                                # 79


translations = {
    "microsecond": "%f",

    "second": "%S",
    "sec": "%S",
    "s": "%S",

    "minute": "%M",
    "min": "%M",
    "m": "%M",

    "12h": "%I",
    "24h": "%H",
    "AM/PM": "%p",

    "short weekday": "%a",
    "long weekday": "%A",
    "numeric weekday": "%w",

    "day": "%d",
    "day of year": "%j",

    "Sunday weeks": "%U",
    "Monday weeks": "%W",

    "short month": "%b",
    "long month": "%B",
    "numeric month": "%m",

    "date": "%x",
    "time": "%X",
    "date time": "%c",

    "ISO 8601 year": "%G",
    "ISO 8601 weekday": "%u",
    "ISO 8601 weeknumber": "%V",

    "decade": "%y",
    "century": "%C",
    "year": "%Y",

    "UTC offset": "%z",
    "timezone": "%Z"
}

import datetime
import pytz
from typing import Optional, Union

formats = ['hnnnn12', 'hnndn12', 'hnnns12', 'hnnds12', 'snnnn12', 'snndn12', 'snnns12', 'snnds12', 'hsnnn12', 'hsndn12', 'hsnns12', 'hsnds12', 'ssnnn12', 'ssndn12', 'ssnns12', 'ssnds12', 'hnnnn24', 'hnndn24', 'hnnns24', 'hnnds24', 'snnnn24', 'snndn24', 'snnns24', 'snnds24', 'hsnnn24', 'hsndn24', 'hsnns24', 'hsnds24', 'ssnnn24', 'ssndn24', 'ssnns24', 'ssnds24', 'hnsnn12', 'hnsdn12', 'hnsns12', 'hnsds12', 'snsnn12', 'snsdn12', 'snsns12', 'snsds12', 'hssnn12', 'hssdn12', 'hssns12', 'hssds12', 'sssnn12', 'sssdn12', 'sssns12', 'sssds12', 'hnsnn24', 'hnsdn24', 'hnsns24', 'hnsds24', 'snsnn24', 'snsdn24', 'snsns24', 'snsds24', 'hssnn24', 'hssdn24', 'hssns24', 'hssds24', 'sssnn24', 'sssdn24', 'sssns24', 'sssds24', 'hnn', 'hnd', 'snn', 'snd', 'hsn', 'hsd', 'ssn', 'ssd', 'hn12', 'hs12', 'sn12', 'ss12', 'hn24', 'hs24', 'sn24', 'ss24']
def get_datetime(fmt: Optional[Union[str, int]] = 13, tz: Optional[str] = None, dt: Optional[datetime.datetime] = None) -> str:
    """
    Get the datetime in the specified format and timezone.

    Args:
        fmt (Union[str, int], optional): The desired datetime strftime format ID. Defaults to 13 (ssndn12: 01-15-2023_02.34_PM).
        tz (str, optional): The desired timezone for datetime timezone. Does not affect output if custom_datetime is not None. If value is None, defaults to UTC.
        dt (datetime.datetime, optional): Override for custom datetime. Defaults to datetime.datetime.now(timezone).

    Returns:
        str: Formatted datetime string.
    """
    tz = pytz.timezone(tz) if tz else pytz.UTC
    dt = dt if dt else datetime.datetime.now(tz)
    if isinstance(fmt, int):
        if (fmt >= 0) and (fmt <= len(formats)): fmt = eval(formats[fmt])
        else: raise ValueError(f'fmt must be between 0 and {len(formats)} inclusive.')
    if not isinstance(fmt, str): raise TypeError(f'fmt must be type str, not {type(fmt)}')
    return str(dt.strftime(fmt))

def valid_timezones(): return pytz.all_timezones
def get_format(format: int): return eval(formats[format])
def create_format(format: str = None): return format % translations if format else translations

print(get_datetime(tz='US/Eastern'))