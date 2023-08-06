from Trough.Trough_Control import trough_util, message_utils
from threading import Lock
trough_lock = Lock()
TROUGH = None
cmdsend = None
datarcv = None
