def simulated_troughctl(CTLPipe, DATAPipe):
    """
    Will run as separate process taking in commands through a pipe and
    returning data on demand through a second pipe.

    Parameters
    ----------
    CTLPipe: Pipe
        commands come in on and messages go out on.

    DATAPipe: Pipe
        data is sent out on
    """
    import time
    import numpy as np
    from random import random, normalvariate
    from math import sin, pi
    from collections import deque
    from sys import exit

    def bundle_to_send(que_lst):
        """

        Parameters
        ----------
        que_lst: list
            list of deques.

        Returns
        -------
        list: list
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

    pos_F = deque(maxlen=20)
    pos_F_std = deque(maxlen=20)
    bal_V = deque(maxlen=20)
    bal_std = deque(maxlen=20)
    therm_V = deque(maxlen=20)
    therm_std = deque(maxlen=20)
    time_stamp = deque(maxlen=20)
    cmd_deque = deque()
    messages = deque()
    que_lst = [time_stamp, pos_F, pos_F_std, bal_V, bal_std, therm_V, therm_std,
               messages]
    que_lst_labels = ["time stamp", "position fraction",
                      "position standard deviation", "balance voltage",
                      "balance standard deviation", "thermistor voltage",
                      "thermistor standard deviation", "messages"]
    timedelta = 0.500  # seconds
    messages.append("Trough ready")
    DATAPipe.send(bundle_to_send(que_lst))
    messages.clear()
    speed = 0  # 0 to 1 fraction of maximum speed.
    direction = 0  # -1 close, 0 don't move, 1 open
    chosen_direction = 0
    run = True
    barrier_start_time = 0
    cycle_seconds = 600
    noise_frac = 0.1
    pos_init = random()
    temp_init = 3.30 + random()*0.05
    bal_init = (random()-0.5)
    to_pos = 0.5
    while run:
        pos = []
        bal = []
        therm = []
        starttime = time.time()
        # leave 200 ms for communications and control
        stopat = starttime + timedelta - 0.200
        while (time.time() < stopat):
            now = time.time()
            # Not using normalvariate to avoid occasional large excursions
            # causing the data collection to think the barrier has reached its
            # target.
            temp_pos = pos_init + (random()-0.5)*(pos_init*noise_frac) \
                      + direction * speed / 78 * (now-barrier_start_time)
            pos.append(temp_pos)
            temp_bal = normalvariate(bal_init, bal_init*noise_frac) \
                       + direction * 0.01 * (now-barrier_start_time)
            bal.append(temp_bal)

            elapsed = now % cycle_seconds
            temp_therm = normalvariate(temp_init, temp_init*noise_frac) \
                        + sin(elapsed*pi*2/cycle_seconds) * 0.05
            therm.append(temp_therm)
            # Check barrier positions
            if direction < 0 and (pos[-1] <= to_pos or pos[-1] <= 0):
                pos_init = pos[-1]
                bal_init = bal[-1]
                speed = 0
                direction = 0
                # messages.append("Reached closing stop at " + str(pos[-1]))
                # messages.append("barrier_start_time "+str(barrier_start_time))
                # messages.append("now " + str(now))
            if direction > 0 and (pos[-1] >= to_pos or pos[-1] >= 1):
                pos_init = pos[-1]
                bal_init = bal[-1]
                speed = 0
                direction = 0
                # messages.append("Reached opening stop at " + str(pos[-1]))
                # messages.append("barrier_start_time "+str(barrier_start_time))
                # messages.append("now " + str(now))
        time_stamp.append((starttime + stopat) / 2)
        # position
        # print("poshigh: "+str(poshigh))
        ndata = len(pos)
        if ndata >= 1:
            vals = np.array(pos, dtype=np.float64)
            avg = (np.sum(vals)) / ndata
            stdev = np.std(vals, ddof=1, dtype=np.float64)
            stdev_avg = stdev / np.sqrt(float(ndata))
            pos_F.append(avg)
            pos_F_std.append(stdev_avg)
            # balance
            ndata = len(bal)
            vals = np.array(bal, dtype=np.float64)
            avg = (np.sum(vals)) / ndata
            stdev = np.std(vals, ddof=1, dtype=np.float64)
            stdev_avg = stdev / np.sqrt(float(ndata))
            bal_V.append(avg)
            bal_std.append(stdev_avg)
            # thermistor
            ndata = len(therm)
            vals = np.array(therm, dtype=np.float64)
            avg = (np.sum(vals)) / ndata
            stdev = np.std(vals, ddof=1, dtype=np.float64)
            stdev_avg = stdev / np.sqrt(float(ndata))
            therm_V.append(avg)
            therm_std.append(stdev_avg)

        # Communicattion
        while CTLPipe.poll():
            try:
                rcvd = CTLPipe.recv()
            except EOFError:
                break
            cmd_deque.append(rcvd)
        # Each command is a python list.
        #    element 1: cmd name (string)
        #    element 2: single command parameter (number or string)
        # Execute commands in queue
        # print('Executing commands...')
        while len(cmd_deque) > 0:
            cmd = cmd_deque.popleft()
            # execute the command
            # print(str(cmd))
            if cmd[0] == 'Stop':
                pos_init = pos_F[-1]
                bal_init = bal[-1]
                speed = 0
                direction = 0
            elif cmd[0] == 'Send':
                # print('Got a "Send" command.')
                # send current contents of the data deques
                DATAPipe.send(bundle_to_send(que_lst))
                # purge the sent content
                time_stamp.clear()
                pos_F.clear()
                pos_F_std.clear()
                bal_V.clear()
                bal_std.clear()
                therm_V.clear()
                therm_std.clear()
                messages.clear()
            elif cmd[0] == 'Start':
                # start barriers moving using current direction and speed
                barrier_start_time = time.time()
                if speed > 1:
                    speed = 1
                if speed < 0:
                    speed = 0
                if chosen_direction >= 0:
                    to_pos = 1
                if chosen_direction == -1:
                    to_pos = 0
                if (chosen_direction != -1) and (chosen_direction != 0) \
                        and (chosen_direction != 1):
                    direction = 0
                else:
                    direction = chosen_direction
                # messages.append("start speed = " + str(speed))
                # messages.append("start direction = " + str(direction))
            elif cmd[0] == 'Direction':
                # set the direction
                chosen_direction = int(cmd[1])
                if (chosen_direction != -1) and (chosen_direction != 0) and \
                        (chosen_direction != 1):
                    chosen_direction = 0
                # messages.append("direction => "+ str(chosen_direction))
            elif cmd[0] == 'Speed':
                # set the speed
                speed = float(cmd[1])
                if speed > 1:
                    speed = 1
                if speed < 0:
                    speed = 0
                # messages.append("speed => " + str(speed))
                pass
            elif cmd[0] == 'MoveTo':
                # Move to fraction of open 0 .. 1.
                # set the stop position
                to_pos = float(cmd[1])
                # adjust direction if necessary
                # get current position
                barrier_start_time = time.time()
                position = pos[-1]
                if position < to_pos:
                    direction = 1
                else:
                    direction = -1
                # messages.append("barrier_start_time => " + str(
                # barrier_start_time))
                # messages.append("moveto speed => " + str(speed))
                # messages.append("moveto position => " + str(to_pos))
                # messages.append("moveto direction => " + str(direction))
                pass
            elif cmd[0] == 'MotorCal':
                # calibrate the voltages for starting motor and speeds
                messages.append("Motor Calibration not implemented in"
                                "simulation.")
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
                pos_F.clear()
                pos_F_std.clear()
                bal_V.clear()
                bal_std.clear()
                therm_V.clear()
                therm_std.clear()
                messages.clear()
            elif cmd[0] == 'ShutDown':
                run = False
                exit()
        # Delay if have not used up all 200 ms
        used = time.time() - starttime
        if used < 0.495:
            time.sleep(0.495 - used)
