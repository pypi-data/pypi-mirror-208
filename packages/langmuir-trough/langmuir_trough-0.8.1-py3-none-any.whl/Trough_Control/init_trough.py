from multiprocessing import Process, Pipe
from trough_util import troughctl
from message_utils import extract_messages
import time

cmdsend, cmdrcv = Pipe()
datasend, datarcv = Pipe()
TROUGH = Process(target=troughctl,args=(cmdrcv,datasend))
TROUGH.start()
time.sleep(0.2)
waiting = True
while waiting:
    #print("polling datarcv...")
    if datarcv.poll():
        #print("got something:")
        datapkg =datarcv.recv()
        #print(type(datapkg))
        #print(str(datapkg))
        print(str(extract_messages(datapkg)))
        if "Trough ready" in extract_messages(datapkg):
            waiting = False
    time.sleep(2)