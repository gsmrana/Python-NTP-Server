import time
from datetime import datetime
from datetime import timedelta


PRINT_NTP_PACKETS = True
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# configurable options for testing
SEND_FIXED_TIME = None
#SEND_FIXED_TIME = datetime(year=2030, month=1, day=2, hour=3, minute=4, second=5).timestamp()

SEND_DELTA_PLUS_TIME = None
#SEND_DELTA_PLUS_TIME = timedelta(days=365, hours=0, minutes=0, seconds=0).total_seconds()

SEND_DELTA_MINUS_TIME = None
#SEND_DELTA_MINUS_TIME = timedelta(days=365, hours=0, minutes=0, seconds=0).total_seconds()


def get_current_unix_time_seconds():
    """Get the current time in seconds since the Unix epoch."""
    if SEND_FIXED_TIME:
        return SEND_FIXED_TIME
    elif SEND_DELTA_PLUS_TIME:
        return time.time() + SEND_DELTA_PLUS_TIME
    elif SEND_DELTA_MINUS_TIME:
        return time.time() - SEND_DELTA_MINUS_TIME
    
    # default behavior: return current system time
    return time.time()

def get_configuration_type():
    """Get the type of configuration being used."""
    tx_time = datetime.fromtimestamp(get_current_unix_time_seconds()).strftime(DATETIME_FORMAT)
    if SEND_FIXED_TIME:
        return f"Fixed Set Time: {tx_time}"
    elif SEND_DELTA_PLUS_TIME:
        return f"Future Time: {tx_time} (System Time + {timedelta(seconds=SEND_DELTA_PLUS_TIME)})"
    elif SEND_DELTA_MINUS_TIME:
        return f"Past Time: {tx_time} (System Time - {timedelta(seconds=SEND_DELTA_MINUS_TIME)})"
    else:
        return f"System Time: {tx_time} (no adjustments)"
