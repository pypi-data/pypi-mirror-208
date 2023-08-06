def isnumber(obj):
    """
    :param obj: object to be tested
    :type obj: any

    :return bool: True is a number.
    :type bool: bool
    """
    if isinstance(obj,(int,float)) and not isinstance(obj,bool):
        return True
    return False

def etol_call(obj, param):
    """
    Wrapping a callable object in this function will cause it to be called until
    it either returns without an error or the maximum recursion depth is reached.
    This should only be used on calls that occasionally return errors because they
    are reading sensors or something like that.

    Parameters
    ----------

    obj: callable

    param: list
        a list containing the parameters in the function call

    Returns
    ------
    result: any
        result of function call

    """
    if callable(obj):
        result = None
        e = None
        try:
            result = obj(*param)
        except Exception as e:
            result = etol_call(obj,param)
        except RecursionError as f:
            raise RecursionError('Recursion error while trying to recover from '+str(e))
        return result
    else:
        raise TypeError(str(obj) + ' must be a callable object.')

def pid_exists(pid):
    """Check whether pid exists in the current process table.
    UNIX only. From this stackoverflow suggestion:
    https://stackoverflow.com/a/6940314
    """
    import os, errno, time
    if pid < 0:
        return False
    if pid == 0:
        # According to "man 2 kill" PID 0 refers to every process
        # in the process group of the calling process.
        # On certain systems 0 is a valid PID but we have no way
        # to know that in a portable fashion.
        raise ValueError('invalid PID 0')
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            # ESRCH == No such process
            return False
        elif err.errno == errno.EPERM:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            # According to "man 2 kill" possible error values are
            # (EINVAL, EPERM, ESRCH)
            raise
    else:
        return True

def is_trough_initialized():
    """Checks for a running Trough process and good connections to it.
    Returns
    -------
    bool
    TRUE if initialized
    """
    from IPython import get_ipython
    from multiprocessing import Process
    from multiprocessing.connection import Connection
    # only load if in IPython to allow building of docs.
    if get_ipython():
        user_ns = get_ipython().user_ns
    else:
        user_ns = []
    trough_running = False
    if "TROUGH" in user_ns:
        # Check that it is a process
        TROUGH = user_ns['TROUGH']
        if isinstance(TROUGH, Process):
            if TROUGH.is_alive():
                cmdsend = user_ns['cmdsend']
                datarcv = user_ns['datarcv']
                if isinstance(cmdsend, Connection) and isinstance(datarcv, Connection):
                    trough_running = True
    return trough_running

def init_trough():
    """
    This initializes the trough control subprocess and creates the pipes to communicate
    with it.
    Returns
    -------
    pipe
    cmdsend: the end of the pipe to sent commands to the trough.

    pipe
    datarcv: the end of the pipe the trough uses to send back data and messages.

    Process
    TROUGH: the process handle for the trough.
    """
    from multiprocessing import Process, Pipe
    from Trough.Trough_Control.message_utils import extract_messages
    import time, os
    from sys import exit

    cmdsend, cmdrcv = Pipe()
    datasend, datarcv = Pipe()
    trough_exists = True
    # Check if another process is monitoring the trough
    pidpath = '/tmp/troughctl.pid'
    if os.path.exists(pidpath):
        file=open(pidpath,'r')
        pid = int(file.readline())
        if pid_exists(pid):
            print("Another process is controlling the Trough.")
            trough_exists = False
    # Check for trough hardware
    if trough_exists:
        try:
            from piplates import DAQC2plate
            del DAQC2plate
        except Exception as e:
            print("An issue was encountered while accessing the DAQC2plate:" +
                  str(e))
            trough_exists = False
    if trough_exists:
        TROUGH = Process(target=troughctl, args=(cmdrcv, datasend))
    else:
        print("Unable to access Trough. Using simulation.")
        from Trough.Trough_Control.simulation import simulated_troughctl
        TROUGH = Process(target=simulated_troughctl, args=(cmdrcv, datasend))
    TROUGH.start()
    time.sleep(0.2)
    waiting = True
    while waiting:
        if datarcv.poll():
            datapkg = datarcv.recv()
            messages = extract_messages(datapkg)
            print(str(messages))
            if "ERROR" in messages:
                exit()
            if "Trough ready" in messages:
                waiting = False
    return cmdsend, datarcv, TROUGH

def troughctl(CTLPipe,DATAPipe):
    """
    Will run as separate process taking in commands through a pipe and
    returning data on demand through a second pipe.
    Iteration 1, collects data into a fifo and watches barrier position.
    :param Pipe CTLPipe: pipe commands come in on and messages go out on.
    :param Pipe DATAPipe: pipe data is sent out on
    """
    import time
    from math import trunc
    import numpy as np
    from collections import deque
    from piplates import DAQC2plate as DAQC2
    from sys import exit

    def bundle_to_send(que_lst):
        """

        Parameters
        ----------
        que_lst: list
            list of deques.

        Returns
        -------
        list
            list of lists. One list for each deque.
        """

        pkg_lst = []
        for k in que_lst:
            # print ('que_lst element: '+ str(k))
            tmp_lst = []
            for j in k:
                tmp_lst.append(j)
            pkg_lst.append(tmp_lst)
        return pkg_lst

    def barrier_at_limit_check(openlimit, closelimit):
        """
        Checks if barrier is at or beyond limit and stops barrier if it is moving
        in a direction that would make it worse.
        :param float openlimit: lowest voltage allowed for opening
        :param float closelimit: highest voltage allowed for closing

        Returns
        =======
        True or False. If True also shuts down power to barrier
        """

        direction = 0  # -1 closing, 0 stopped, 1 openning.
        if (etol_call(DAQC2.getDAC,(0, 0)) >= 2.5):
            direction = -1
        else:
            direction = 1
        position = etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1))
        if (position >= closelimit) and (direction == -1):
            DAQC2.clrDOUTbit(0, 0)  # switch off power/stop barriers
            return True
        if (position <= openlimit) and (direction == 1):
            DAQC2.clrDOUTbit(0, 0)  # switch off power/stop barriers
            return True
        return False

    def take_over_barrier_monitoring():
        """
        Call this to run something in a tight loop that needs to take over watching
        the barriers. Check if a trough controller is registered at /tmp/troughctl.pid.
        If one is store it's pid and replace with own. Revert on exit to avoid
        crashing.

        Returns
        -------
        int:
        pid for process that was watching the barriers.
        """
        import os
        pidpath = '/tmp/troughctl.pid'
        ctlpid = None
        if os.path.exists(pidpath):
            file = open(pidpath, 'r')
            ctlpid = int(file.readline())
            file.close()
        pid = os.getpid()
        # print(str(pid))
        file = open(pidpath, 'w')
        file.write(str(pid) + '\n')
        file.close()
        # Do not proceed until this file exists on the file system
        while not os.path.exists(pidpath):
            pass  # just waiting for file system to catch up.
        # Read it to make sure
        file = open(pidpath, 'r')
        checkpid = file.readline()
        file.close()
        if int(checkpid) != pid:
            raise FileNotFoundError('Checkpid = ' + checkpid + ', but should = ' + str(pid))
        return ctlpid

    def return_barrier_monitoring_to_prev_process(ctlpid):
        """

        Parameters
        ----------
        ctlpid : int
        Process id of the process that was watching the barriers before.

        Returns
        -------

        """
        import os
        pidpath = '/tmp/troughctl.pid'
        if ctlpid is not None:
            file = open(pidpath, 'w')
            file.write(str(ctlpid) + '\n')
            file.close()
        elif os.path.exists(pidpath):
            os.remove(pidpath)
        elif os.path.exists(pidpath):  # double check
            os.remove(pidpath)
        pass

    def get_power_supply_volts():
        """
        Returns the negative and positive voltages from the power supply corrected
        for the inline voltage divider allowing measurement up to a bit more
        than +/- 15 V.

        :returns float V_neg: the negative voltage.
        :returns float V_pos: the positive voltage.
        """
        V_neg = 1.3875*etol_call(DAQC2.getADC, (0,6))
        V_pos = 1.3729*etol_call(DAQC2.getADC, (0,7))

        return V_neg, V_pos

    def start_barriers(speed, direction, maxcloseV, mincloseV, maxopenV,
                       minopenV):
        """
        Will start the barriers including giving a little boost if running
        voltage is below the starting voltage.
        """
        DAC_V = calcDAC_V(speed, direction, maxcloseV, mincloseV, maxopenV,
                          minopenV)
        # print("speed:"+str(speed)+", direction:"+str(direction)+", DAC_V:"+str(DAC_V))
        if (DAC_V > startopenV) and (DAC_V < startcloseV) and (direction != 0):
            # need a boost to start moving
            if direction == -1:
                DAQC2.setDAC(0, 0, startcloseV)
            else:
                DAQC2.setDAC(0, 0, startopenV)
            DAQC2.setDOUTbit(0, 0)
            time.sleep(0.25)
        DAQC2.setDAC(0, 0, DAC_V)
        DAQC2.setDOUTbit(0, 0)
        pass

    def write_motorcal(maxclose, minclose, startclose, maxopen, minopen, startopen):
        """Write the motorcal to a file in ~/.Trough/calibrations."""
        from AdvancedHTMLParser import AdvancedTag as Domel
        from datetime import datetime
        from time import time
        from pathlib import Path
        calib_div = Domel('div')
        calib_title = Domel('h3')
        calib_title.setAttribute('id','title')
        calib_title.appendInnerHTML('Calibration of Motor')
        calib_div.appendChild(calib_title)

        time_table = Domel('table')
        time_table.setAttribute('class','time_table')
        time_table.setAttribute('id', 'time_table')
        time_table.setAttribute('border', '1')
        tr = Domel('tr')
        tr.appendInnerHTML('<th>ISO time</th><th>Timestamp</th>')
        time_table.append(tr)
        tr = Domel('tr')
        timestamp = time()
        isotime = (datetime.fromtimestamp(timestamp)).isoformat()
        tr.appendInnerHTML('<td>' + str(isotime) + '</td>'
                           '<td id="timestamp">' + str(timestamp) + '</td>')
        time_table.append(tr)
        calib_div.append(time_table)

        calib_info = Domel('table')
        calib_info.setAttribute('class', 'calib_info')
        calib_info.setAttribute('id', 'calib_info')
        calib_info.setAttribute('border', '1')
        tr = Domel('tr')
        tr.appendInnerHTML('<th>Calibration of</th><th>Max Value</th>'
                           '<th>Min Value</th><th>Start Value</th>')
        calib_info.appendChild(tr)
        tr = Domel('tr')
        tr.appendInnerHTML('<th id = "name"> Opening </th>'
                           '<td id = "maxopen">' + str(maxopen) + '</td>'
                           '<td id = "minopen">' + str(minopen) + '</td>'
                           '<td id = "startopen">' + str(startopen) + '</td>')
        calib_info.appendChild(tr)
        tr = Domel('tr')
        tr.appendInnerHTML('<th id = "name"> Closing </th>'
                           '<td id = "maxclose">' + str(maxclose) + '</td>'
                           '<td id = "minclose">' + str(minclose) + '</td>'
                           '<td id = "startclose">' + str(startclose) + '</td>')
        calib_info.appendChild(tr)
        calib_div.appendChild(calib_info)


        fileext = '.trh.cal.html'
        filename = 'motorcal'+fileext
        dirpath = Path('~/.Trough/calibrations').expanduser()
        fullpath = Path(dirpath, filename)
        svhtml = '<!DOCTYPE html><html><body>' + calib_div.asHTML() + \
                 '</body></html>'
        f = open(fullpath, 'w')
        f.write(svhtml)
        f.close()
        pass

    def read_motorcal():
        """Reads the motor calibration file in ~/.Trough/calibrations
        if it exists and returns the calibration parameters."""
        from AdvancedHTMLParser import AdvancedHTMLParser as Parser
        from pathlib import Path
        from os.path import exists

        maxopen = 0
        minopen = 0
        startopen = 0
        maxclose = 0
        minclose = 0
        startclose = 0
        timestamp = 0

        filepath = Path('~/.Trough/calibrations/motorcal.trh.cal.html').expanduser()
        html = ""
        if exists(filepath):
            f = open(filepath, 'r')
            html = f.read()
            f.close()
            document = Parser()
            document.parseStr(html)
            if document.getElementById('title').text.strip() != 'Calibration of Motor':
                return maxclose, minclose, startclose, maxopen, minopen, startopen, timestamp
            maxclose = float(document.getElementById('maxclose').text)
            minclose = float(document.getElementById('minclose').text)
            startclose = float(document.getElementById('startclose').text)
            maxopen = float(document.getElementById('maxopen').text)
            minopen = float(document.getElementById('minopen').text)
            startopen = float(document.getElementById('startopen').text)
            timestamp = float(document.getElementById('timestamp').text)
        return maxclose, minclose, startclose, maxopen, minopen, startopen, timestamp

    def motorcal(barriermin, barriermax):
        '''
        :param float barriermin: minimum voltage for barrier (do not open more).
        :param float barriermax: maximum voltage for barrier (do not close more).
        :returns float maxclose: DAC setting for maximum close speed.
        :returns float minclose: DAC setting for minimum close speed.
        :returns float startclose: DAC setting providing minimum voltage to start closing.
        :returns float maxopen: DAC setting for maximum close speed.
        :returns float minopen: DAC setting for minimum close speed.
        :returns float startopen: DAC setting providing minimum voltage to start opening.
        '''

        import time
        # Since this runs in a tight loop needs to take over watching barriers.
        # Check if a trough controller is registered at /tmp/troughctl.pid.
        # If one is store it's pid and replace with own. Will revert on exit without
        # crashing.
        ctlpid = take_over_barrier_monitoring()

        # Set base values
        maxclose = 4
        minclose = 2.6
        startclose = 2.6
        maxopen = 0
        minopen = 2.4
        startopen = 2.4
        # Calibrate the barrier. This assumes a DAQC2 pi-plate is the controlling interface.
        # First move to fully open.
        # print('Moving to fully open...')
        position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        if position > barriermin:
            # need to open some
            atlimit = False
            DAQC2.setDAC(0, 0, maxopen)  # set fast open
            DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
            time.sleep(1)
            while not atlimit:
                atlimit = barrier_at_limit_check(barriermin, barriermax)
        # Get rid of any hysteresis in the close direction
        # print('Removing close hysteresis...')
        position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        stoppos = position + 0.05
        if stoppos > barriermax:
            stoppos = barriermax
        DAQC2.setDAC(0, 0, maxclose)  # set fast close
        DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
        time.sleep(1)
        atlimit = False
        while not atlimit:
            atlimit = barrier_at_limit_check(barriermin, stoppos)
        # Find closing stall voltage
        # print('Finding closing stall voltage...')
        oldposition = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        DAQC2.setDAC(0, 0, maxclose)  # set fast close
        DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
        testclose = maxclose
        time.sleep(2)
        atlimit = False
        while not atlimit:
            atlimit = barrier_at_limit_check(barriermin, barriermax)
            position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
            #        if position > 6.5:
            #            print ('old: '+str(oldposition)+' position: '+str(position))
            if (position - oldposition) < 0.01:
                # because there can be noise take a new reading and check again
                position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
                if (position - oldposition) < 0.01:
                    minclose = testclose
                    atlimit = True
                    DAQC2.clrDOUTbit(0, 0)
            oldposition = position
            testclose = testclose - 0.05
            DAQC2.setDAC(0, 0, testclose)
            time.sleep(2)

        # Find minimum closing start voltage
        # print('Finding minimum closing start voltage...')
        oldposition = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        startclose = minclose
        atlimit = False
        while not atlimit:
            atlimit = barrier_at_limit_check(barriermin, barriermax)
            DAQC2.setDAC(0, 0, startclose)
            DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
            time.sleep(2)
            position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
            if (position - oldposition) < 0.01:
                # because there can be noise take a new reading and check again
                position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
                if (position - oldposition) < 0.01:
                    startclose = startclose + 0.05
            else:
                atlimit = True
                DAQC2.clrDOUTbit(0, 0)
                startclose = startclose + 0.05  # To provide a margin.
        # Move to fully closed
        # print('Moving to fully closed...')
        position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        if position < barriermax:
            # need to close some
            atlimit = False
            DAQC2.setDAC(0, 0, maxclose)  # set fast close
            DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
            time.sleep(1)
            while not atlimit:
                atlimit = barrier_at_limit_check(barriermin, barriermax)

        # Get rid of any hysteresis in the open direction
        # print('Removing open hysteresis...')
        position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        stoppos = position - 0.05
        if stoppos < barriermin:
            stoppos = barriermin
        DAQC2.setDAC(0, 0, maxopen)  # set fast close
        DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
        time.sleep(1)
        atlimit = False
        while not atlimit:
            atlimit = barrier_at_limit_check(stoppos, barriermax)

        # Find openning stall voltage
        # print('Finding openning stall voltage...')
        oldposition = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        DAQC2.setDAC(0, 0, maxopen)  # set fast close
        DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
        testopen = maxopen
        time.sleep(2)
        atlimit = False
        while not atlimit:
            atlimit = barrier_at_limit_check(barriermin, barriermax)
            position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
            #        if position > 6.5:
            #            print ('old: '+str(oldposition)+' position: '+str(position))
            if (oldposition - position) < 0.01:
                # because there can be noise take a new reading and check again
                position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
                if (oldposition - position) < 0.01:
                    minopen = testopen
                    atlimit = True
                    DAQC2.clrDOUTbit(0, 0)
            oldposition = position
            testopen = testopen + 0.05
            DAQC2.setDAC(0, 0, testopen)
            time.sleep(2)

        # Find minimum opening start voltage
        # print('Finding minimum openning start voltage...')
        oldposition = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
        startopen = minopen
        atlimit = False
        while not atlimit:
            atlimit = barrier_at_limit_check(barriermin, barriermax)
            DAQC2.setDAC(0, 0, startopen)
            DAQC2.setDOUTbit(0, 0)  # turn on power/start barriers
            time.sleep(2)
            position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
            if (oldposition - position) < 0.01:
                # because there can be noise take a new reading and check again
                position = round(etol_call(DAQC2.getADC,(0, 0)) - etol_call(DAQC2.getADC,(0, 1)), 2)  # not stable past 2 decimals
                if (oldposition - position) < 0.01:
                    startopen = startopen - 0.05
            else:
                atlimit = True
                DAQC2.clrDOUTbit(0, 0)
                startopen = startopen - 0.05  # To provide a margin.

        write_motorcal(maxclose, minclose, startclose, maxopen, minopen, startopen)

        # Return control to previous trough controller
        return_barrier_monitoring_to_prev_process(ctlpid)

        # Return the results
        return (maxclose, minclose, startclose, maxopen, minopen, startopen)

    def calcDAC_V(speed, direction, maxclose, minclose, maxopen, minopen):
        '''
        :param float speed: fraction of maximum speed
        :param int direction: -1 close, 0 don't move, 1 open
        :param float maxclose: DAC V for maximum close speed
        :param float minclose: DAC V for minimum close speed
        :param float maxopen: DAC V for maximum open speed
        :param float minopen: DAC V for minimum open speed

        :return float DAC_V:
        '''
        DAC_V = (minclose+minopen)/2 # default to not moving
        if direction == -1:
            DAC_V = (maxclose-minclose)*speed + minclose
        if direction == 1:
            DAC_V = (maxopen - minopen)*speed + minopen
        return DAC_V

    # Take over the barrier monitoring because we are in a tight loop.
    # Unless some other process tries to access the A-to-D this should
    # make most of the fault tolerance unnecessary.
    ctlpid = take_over_barrier_monitoring()
    # TODO Should this all be wrapped in a try... so that if
    #   anything stops this it gives up barrier monitoring?
    pos_F = deque(maxlen=20)
    pos_F_std = deque(maxlen=20)
    pos_V = deque(maxlen=20)
    pos_V_std = deque(maxlen=20)
    bal_V = deque(maxlen=20)
    bal_std = deque(maxlen=20)
    therm_V = deque(maxlen=20)
    therm_std = deque(maxlen=20)
    time_stamp = deque(maxlen=20)
    cmd_deque = deque()
    messages = deque()
    que_lst = [time_stamp, pos_F, pos_F_std, bal_V, bal_std, therm_V, therm_std, messages]
    que_lst_labels = ["time stamp", "position fraction", "position standard deviation",
                      "balance voltage", "balance standard deviation", "thermistor voltage",
                      "thermistor standard deviation", "messages"]
    timedelta = 0.500  # seconds
    openmin = 0.02 # minimum voltage allowed when opening.
    openlimit = openmin
    closemax = 7.40 # maximum voltage allowed when closing.
    closelimit = closemax
    # Check that power supply is on. If not we cannot do anything.
    PS_minus, PS_plus = get_power_supply_volts()
    if PS_minus > -10 or PS_plus < 10:
        messages.append("ERROR")
        messages.append("Power supply appears to be off (or malfunctioning). Try again...")
        DATAPipe.send(bundle_to_send(que_lst))
        #   make sure no power to barriers
        DAQC2.clrDOUTbit(0, 0)  # switch off power/stop barriers
        # Close connections
        DATAPipe.close()
        CTLPipe.close()
        #   give up process id
        return_barrier_monitoring_to_prev_process(ctlpid)
        run = False
        exit()
    messages.append("Checking Motor Calibration. Please wait...")
    DATAPipe.send(bundle_to_send(que_lst))
    messages.clear()
    maxcloseV, mincloseV, startcloseV, maxopenV, minopenV, startopenV, lasttime = read_motorcal()
    # check that the calibration is 12 hours or less old
    if lasttime < time.time() - 43200:
        maxcloseV, mincloseV, startcloseV, maxopenV, minopenV, startopenV = motorcal(openlimit, closelimit)
    messages.append("Trough ready")
    DATAPipe.send(bundle_to_send(que_lst))
    messages.clear()
    speed = 0 # 0 to 1 fraction of maximum speed.
    direction = 0 # -1 close, 0 don't move, 1 open
    run = True
    # cycles for doing very low speeds by stepping. If cycles_off = 0 then
    # just runs continuously.
    cycles_on = 1
    cycles_off = 0
    cycle_count = 0
    moving_flag = False
    while run:
        poshigh = []
        poslow = []
        balhigh = []
        ballow = []
        thermhigh = []
        thermlow = []

        if cycle_count >= (cycles_on+cycles_off):
            cycle_count = 0
        if cycle_count >= cycles_on:
            DAQC2.clrDOUTbit(0, 0)  # switch off power/stop barriers
        elif moving_flag:
            DAQC2.setDOUTbit(0, 0)  # switch on power/start barriers

        starttime = time.time()
        stopat = starttime + timedelta - 0.200  # leave 200 ms for communications and control
        while (time.time() < stopat):
            tempposlow = None
            tempposhigh= None
            tempballow = None
            tempbalhigh = None
            tempthermlow = None
            tempthermhigh = None
            #itcount +=1
            #print(str(itcount)+",",end = "")
            tempposlow = etol_call(DAQC2.getADC,(0, 1))
            temposhigh = etol_call(DAQC2.getADC,(0, 0))
            tempballow = etol_call(DAQC2.getADC,(0, 3))
            tempbalhigh = etol_call(DAQC2.getADC,(0, 2))
            tempthermlow = etol_call(DAQC2.getADC,(0, 4))
            tempthermhigh = etol_call(DAQC2.getADC,(0, 5))
            datagood = True
            if isnumber(tempposlow):
                poslow.append(tempposlow)
            else:
                datagood = False
            if isnumber(temposhigh):
                poshigh.append(temposhigh)
            else:
                datagood = False
            if isnumber(tempballow):
                ballow.append(tempballow)
            else:
                datagood = False
            if isnumber(tempbalhigh):
                balhigh.append(tempbalhigh)
            else:
                datagood = False
            if isnumber(tempthermlow):
                thermlow.append(tempthermlow)
            else:
                datagood = False
            if isnumber(tempthermhigh):
                thermhigh.append(tempthermhigh)
            else:
                datagood = False
            if not datagood:
                return_barrier_monitoring_to_prev_process(ctlpid)
                raise ValueError('Not getting numeric values from A-to-D!')

        time_stamp.append((starttime + stopat) / 2)
        # position
        #print("poshigh: "+str(poshigh))
        ndata = len(poshigh)
        if ndata >= 1:
            high = np.array(poshigh, dtype=np.float64)
            #print("poslow: "+str(poslow))
            low = np.array(poslow, dtype=np.float64)
            vals = high - low
            avg = (np.sum(vals)) / ndata
            stdev = np.std(vals, ddof=1, dtype=np.float64)
            stdev_avg = stdev / np.sqrt(float(ndata))
            pos_frac = 1.00 - (avg - openmin)/(closemax - openmin)
            pos_frac_std = stdev_avg/(closemax - openmin)
            pos_V.append(avg)
            pos_V_std.append(stdev_avg)
            pos_F.append(pos_frac)
            pos_F_std.append(pos_frac_std)
            # balance
            ndata = len(balhigh)
            high = np.array(balhigh, dtype=np.float64)
            low = np.array(ballow, dtype=np.float64)
            vals = high - low
            avg = (np.sum(vals)) / ndata
            stdev = np.std(vals, ddof=1, dtype=np.float64)
            stdev_avg = stdev / np.sqrt(float(ndata))
            bal_V.append(avg)
            bal_std.append(stdev_avg)
            # thermistor
            ndata = len(thermhigh)
            high = np.array(thermhigh, dtype=np.float64)
            low = np.array(thermlow, dtype=np.float64)
            vals = high - low
            avg = (np.sum(vals)) / ndata
            stdev = np.std(vals, ddof=1, dtype=np.float64)
            stdev_avg = stdev / np.sqrt(float(ndata))
            therm_V.append(avg)
            therm_std.append(stdev_avg)

        # Check barrier positions
        if openlimit < openmin:
            openlimit = openmin
        if closelimit > closemax:
            closelimit = closemax
        barrier_at_limit = barrier_at_limit_check(openlimit,closelimit)
        if barrier_at_limit:
            moving_flag = False
        # TODO: Send warnings and error messages
        # Check command pipe and update command queue
        #print('Checking commands...')
        while CTLPipe.poll():
            cmd_deque.append(CTLPipe.recv())
        # Each command is a python list.
        #    element 1: cmd name (string)
        #    element 2: single command parameter (number or string)
        # Execute commands in queue
        #print('Executing commands...')
        while len(cmd_deque) > 0:
            cmd = cmd_deque.popleft()
            # execute the command
            #print(str(cmd))
            if cmd[0] == 'Stop':
                DAQC2.clrDOUTbit(0, 0)  # switch off power/stop barriers
                moving_flag = False
            elif cmd[0] == 'Send':
                #print('Got a "Send" command.')
                # send current contents of the data deques
                DATAPipe.send(bundle_to_send(que_lst))
                # purge the sent content
                time_stamp.clear()
                pos_V.clear()
                pos_V_std.clear()
                pos_F.clear()
                pos_F_std.clear()
                bal_V.clear()
                bal_std.clear()
                therm_V.clear()
                therm_std.clear()
                messages.clear()
            elif cmd[0] == 'Start':
                # start barriers moving using current direction and speed
                if speed > 1:
                    speed = 1
                if speed < 0:
                    speed = 0
                if (direction != -1) and (direction != 0) and (direction != 1):
                    direction = 0
                closelimit = closemax
                openlimit = openmin
                start_barriers(speed, direction, maxcloseV, mincloseV, maxopenV,
                               minopenV)
                moving_flag = True
            elif cmd[0] == 'Direction':
                # set the direction
                direction = cmd[1]
                if (direction != -1) and (direction != 0) and (direction != 1):
                    direction = 0
            elif cmd[0] == 'Speed':
                # set the speed
                cycles_on = 1
                cycles_off = 0
                requested_speed = cmd[1]
                if requested_speed > 1:
                    requested_speed = 1
                if requested_speed < 0:
                    requested_speed = 0
                if requested_speed < 0.1:
                    # set up cycles to go at lower speeds
                    ncycles = trunc(0.1/requested_speed) + 1
                    if ncycles >= 2:
                        cycles_on = 1
                        cycles_off = ncycles - 1
                        speed = requested_speed*ncycles
                    else:
                        ncycles = trunc(0.1/(0.1-requested_speed))
                        cycles_on = ncycles - 1
                        cycles_off = 1
                        speed = requested_speed*ncycles/cycles_on
                else:
                    speed = requested_speed
                speedstat=str("cycles_on="+str(cycles_on)+", cycles_off="
                              +str(cycles_off)
                              + ", requested speed="+str(requested_speed)+
                                ", speed="+str(speed))
                messages.append(speedstat)
                pass
            elif cmd[0] == 'MoveTo':
                # Move to fraction of open 0 .. 1.
                # set the stop position
                to_pos = (1.0-float(cmd[1]))*closemax + float(cmd[1])*openmin
                # adjust direction if necessary
                # get current position
                position = etol_call(DAQC2.getADC,(0, 0)) - \
                           etol_call(DAQC2.getADC,(0, 1))
                if position > to_pos:
                    direction = 1
                    openlimit = to_pos
                else:
                    direction = -1
                    closelimit = to_pos
                # start the barriers
                start_barriers(speed, direction, maxcloseV, mincloseV, maxopenV,
                               minopenV)
                moving_flag = True
                pass
            elif cmd[0] == 'MotorCal':
                # calibrate the voltages for starting motor and speeds
                messages.append("Checking Motor Calibration. Please wait...")
                DATAPipe.send(bundle_to_send(que_lst))
                messages.clear()
                maxcloseV, mincloseV, startcloseV, maxopenV, minopenV, startopenV = motorcal(
                    openlimit, closelimit)
                messages.append("Trough ready")
                DATAPipe.send(bundle_to_send(que_lst))
                messages.clear()
                pass
            elif cmd[0] == 'ConstPi':
                # maintain a constant pressure
                # not yet implemented
                messages.append('Constant pressure mode not yet implemented.')
                DATAPipe.send(bundle_to_send(que_lst))
                messages.clear()
                pass
            elif cmd[0] == 'DataLabels':
                # send data labels as a message
                messages.append(que_lst_labels)
                # send current contents of the data deques
                DATAPipe.send(bundle_to_send(que_lst))
                # purge the sent content
                time_stamp.clear()
                pos_V.clear()
                pos_V_std.clear()
                bal_V.clear()
                bal_std.clear()
                therm_V.clear()
                therm_std.clear()
                messages.clear()
            elif cmd[0] == 'ShutDown':
                # shutdown trough
                #   make sure no power to barriers
                DAQC2.clrDOUTbit(0, 0)  # switch off power/stop barriers
                # Close connections
                DATAPipe.close()
                CTLPipe.close()
                #   give up process id
                return_barrier_monitoring_to_prev_process(ctlpid)
                run = False
                exit()
        cycle_count += 1
        # Delay if have not used up all 200 ms
        used = time.time() - starttime
        if used < 0.495:
            time.sleep(0.495 - used)

        # shutdown automatically if no communication from controller?
