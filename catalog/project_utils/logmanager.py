import datetime
import os.path
from enum import Enum

LOG_FILE = "events.log"
LOG_FOLDER = "info"

class Function(Enum):
    INDEX = "INDEX"
    SEARCH = "SEARCH"
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    INTEGRITY_CHECK = "INTEGRITY_CHECK"
    SUGGESTED = "SUGGESTED"
    ADMIN = "ADMIN"
    DETAILS = "DETAILS"



class LogLevel(Enum):
    INFO = "INFO",
    ERROR = "ERR ",
    WARNING = "WARN",
    FRAUD = "FRAUD"


def new_event(request, level, action, event=''):
    check_info_folder()
    check_event_log_file()

    with open(f"{LOG_FOLDER}/{LOG_FILE}", "a") as f:
        f.write(f"{get_log_string(request, level, action, event)}\n")


def get_log_string(request, level, action, event=''):
    ip = get_client_ip(request)
    c_time = datetime.datetime.now()
    return f"{level.value[0]} - from {ip} at {c_time}: {action.value} - {event}"


def check_info_folder():
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)


def check_event_log_file():
    if not os.path.exists(f"{LOG_FOLDER}/{LOG_FILE}"):
        open(f"{LOG_FOLDER}/{LOG_FILE}", "w").close()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
