from Trough import Trough_GUI
from Trough.Trough_GUI import *
from IPython import get_ipython
# only load if in IPython so docs can be built.
if get_ipython():
    cmdsend = get_ipython().user_ns["Trough_Control"].cmdsend
    datarcv = get_ipython().user_ns["Trough_Control"].datarcv
    trough_lock = get_ipython().user_ns["Trough_Control"].trough_lock

def Monitor_Setup_Trough(calibrations):
    """
    This produces a user interface in jupyter notebooks using ipywidgets. The
    interface allows monitoring of the trough barrier positions, balance
    signal, and temperature signal. The barrier positions can be
    adjusted using this interface. Calibrations of all the signals are
    performed using this interface.

    Calibrations are stored in the calibration files in the .Trough/calibrations
    directory of the current user. The latest file is used. If none exists
    one is created using default parameters. Users should calibrate all
    signals before using the trough.

    NOTE: some objects used here are global and created by importing from
    status_widgets.py and command_widgets.py.

    Parameters
    ----------
    calibrations: Calibrations
        The object containing the calibrations be used and modified. See
        `Trough_GUI.calibration_utils`.
    """
    from ipywidgets import Layout, HBox, VBox, Accordion, \
        Label, Button,  FloatText
    from ipywidgets import HTML as richLabel
    from IPython.display import display

    # Places to put calibrations data
    open_pos_x = []  # raw value
    open_pos_y = []  # actual (cm separation = [] # raw value
    close_pos_x = []  # raw value
    close_pos_y = []  # actual (cm separation)
    open_speed_x = []  # setting
    open_speed_y = []  # fractional speed/min
    close_speed_x = []  # setting
    close_speed_y = []  # fractional speed/min
    cal_bal_x = []
    cal_bal_y = []
    cal_temp_x = []
    cal_temp_y = []

    # Boilerplate style for long descriptions on ipywidget
    longdesc = {'description_width': 'initial'}

    # Balance Monitoring
    balance_label = Label(value="BALANCE:")
    Balance = HBox(children = [balance_label,VBox(children =[
        mg, surf_press]), VBox(children = [plate_circumference,zero_press])],
                   layout = Layout(border="solid"))
    # Balance Calibration
    def on_calib_bal(change):
        nonlocal cal_bal_x
        nonlocal cal_bal_y
        if Bal_Cal_Butt.description == 'Start Calibration':
            Bal_Cal_Butt.description = 'Keep'
            cal_bal_x = []
            cal_bal_y = []
            return
        if Bal_Cal_Butt.description == 'Keep':
            Bal_Cal_Butt.description = 'Acquiring...'
            trough_lock.acquire()
            cmdsend.send(['Send', ''])
            waiting = True
            while waiting:
                if datarcv.poll():
                    datapkg = datarcv.recv()
                    cal_bal_y.append(Bal_Cal_Mass.value)
                    cal_bal_x.append(datapkg[3][-1])
                    waiting = False
            trough_lock.release()
            Bal_Cal_Butt.description = 'Keep'
        if len(cal_bal_x) == 6:
            # we're done do calibrations
            # fit and save the data
            from pathlib import Path
            import time
            cal_path = Path('~/.Trough/calibrations').expanduser()
            params, stdev = calibrations.poly_fit(cal_bal_x, cal_bal_y, 1, 0.5)
            inv_params, inv_stdev = calibrations.poly_fit(cal_bal_y,
                                                          cal_bal_x, 1, 0.001)
            calibrations.balance = Trough.Trough_GUI.calibration_utils. \
                Calibration(
                'balance', 'mg', time.time(), params, stdev, inv_params,
                inv_stdev, cal_bal_x, cal_bal_y)
            calibrations.write_cal(cal_path, calibrations.balance)

            # Calibrations have been updated so restart the status watcher
            Trough_GUI.run_updater.value = False
            while Trough_GUI.updater_running.value:
                # We wait
                pass
            Trough_GUI.start_status_updater()

            Bal_Cal_Butt.description = 'Start Calibration'
        return

    Bal_Cal_Butt = Button(description = "Start Calibration")
    Bal_Cal_Butt.on_click(on_calib_bal)
    Bal_Cal_Mass = FloatText(description = 'Mass (mg):',
                             value = 100.0,
                             step=0.01,
                             disabled = False,
                             style = longdesc)
    Bal_Cal_Instr = richLabel(value = '<ol><li>Collect 5 calibration masses of'
                                      ' 100 mg or less.</li>'
                                      '<li>Click "Start Calibration".</li> '
                                      '<li>Place the'
                                      ' first mass on the balance and '
                                      'enter its mass.</li>'
                                      '<li>When the raw reading is stable click'
                                      ' "keep".</li>'
                                      '<li>Repeat for each calibration '
                                      'mass, plus no calibration mass.</li></ol>'
                                      'The button will revert to "Start '
                                      'Calibration" when done.')
    Bal_Cal_Box = VBox(children = [Bal_Cal_Instr,HBox(children=[Bal_Raw,
                                                                Bal_Cal_Mass,
                                                                Bal_Cal_Butt])])
    Cal_Bal = Accordion(children = [Bal_Cal_Box])
    Cal_Bal.set_title(0,'Calibrate Balance')
    Cal_Bal.selected_index = None

    # Temperature Calibration
    def on_calib_temp(change):
        nonlocal cal_temp_x
        nonlocal cal_temp_y
        if Temp_Cal_Butt.description == 'Start Calibration':
            Temp_Cal_Butt.description = 'Keep'
            cal_temp_x =[]
            cal_temp_y = []
            return
        if Temp_Cal_Butt.description == 'Keep':
            Temp_Cal_Butt.description = 'Acquiring...'
            trough_lock.acquire()
            cmdsend.send(['Send', ''])
            waiting = True
            while waiting:
                if datarcv.poll():
                    datapkg = datarcv.recv()
                    cal_temp_y.append(Temp_Cal_Val.value)
                    cal_temp_x.append(datapkg[5][-1])
                    waiting = False
            trough_lock.release()
            Temp_Cal_Butt.description = 'Keep'
        if len(cal_temp_x) == 5:
            # we're done do calibrations
            # fit and save the data
            from pathlib import Path
            import time
            cal_path = Path('~/.Trough/calibrations').expanduser()
            params, stdev = calibrations.poly_fit(cal_temp_x, cal_temp_y, 3, 0.1)
            inv_params, inv_stdev = calibrations.poly_fit(cal_temp_y,
                                                          cal_temp_x, 3, 0.001)
            calibrations.temperature = Trough.Trough_GUI.calibration_utils. \
                Calibration(
                'temperature', 'C', time.time(), params, stdev, inv_params,
                inv_stdev, cal_temp_x, cal_temp_y)
            calibrations.write_cal(cal_path, calibrations.temperature)

            # Calibrations have been updated so restart the status watcher
            Trough_GUI.run_updater.value = False
            while Trough_GUI.updater_running.value:
                # We wait
                pass
            Trough_GUI.start_status_updater()

            Temp_Cal_Butt.description = 'Start Calibration'
        return

    # Temperature Monitoring
    temp_label = Label(value = "TEMPERATURE:")
    Temperature = HBox(children=[temp_label,degC],
                   layout = Layout(border="solid"))
    # Temperature Calibration
    Temp_Cal_Val = FloatText(description = "Actual $^o C$", disabled = False,
                             step = 0.01, style = longdesc)
    Temp_Cal_Butt = Button(description = "Start Calibration")
    Temp_Cal_Butt.on_click(on_calib_temp)
    Temp_Cal_Instr = richLabel(value = '<ol><li>Gather 5 liquid temperature '
                                       'references.</li>'
                                       '<li>Click "Start Calibration".</li>'
                                       '<li>Place the temperature probe in '
                                       'the first reference.</li>'
                                       '<li>When the raw reading is stable '
                                       'click "keep".</li>'
                                       '<li>Repeat for each temperature '
                                       'reference.</li></ol>'
                                       'The button will revert to "Start '
                                       'Calibration" when done.')
    Temp_Cal_Box = VBox(children = [Temp_Cal_Instr,HBox(children = [Temp_Raw,
                                                                Temp_Cal_Val,
                                                                Temp_Cal_Butt
                                                                    ])])
    Cal_Temp = Accordion(children = [Temp_Cal_Box])
    Cal_Temp.set_title(0,'Calibrate Temperature')
    Cal_Temp.selected_index = None

    # Barrier Monitoring
    barrier_label = Label(value="BARRIERS:")
    Barrier = HBox(children = [barrier_label,
                               VBox(children=[Bar_Frac,Bar_Sep,Bar_Area]),
                               VBox(children=[moles_molec,
                                              Bar_Area_per_Molec])],
                               layout=Layout(border="solid"))

    Move_Barrier = HBox(children=[VBox(children=[Barr_Direction, Barr_Target]),
                        VBox(children=[Barr_Units, Barr_Speed]),
                                   VBox(children=[Barr_Start,Barr_Stop])])
    # Barrier Calibration
    open_steps = [{"speed":0.1, "target":0.05, "speed_data":True,
                   "position":True},
                   {"speed":0.5, "target":0.10, "speed_data":True,
                    "position":True},
                   {"speed": 0.2, "target": 0.20, "speed_data": True,
                    "position": True},
                   {"speed": 0.9, "target": 0.30, "speed_data": True,
                    "position": True},
                   {"speed": 0.3, "target": 0.40, "speed_data": True,
                    "position": True},
                   {"speed": 0.8, "target": 0.50, "speed_data": True,
                    "position": True},
                   {"speed": 0.4, "target": 0.60, "speed_data": True,
                    "position": True},
                   {"speed": 0.7, "target": 0.70, "speed_data": True,
                    "position": True},
                   {"speed": 0.5, "target": 0.80, "speed_data": True,
                    "position": True},
                   {"speed": 0.6, "target": 0.90, "speed_data": True,
                    "position": True},
                   {"speed": 1.0, "target": 1.0, "speed_data": True,
                    "position": True}
                  ]
    close_steps = [{"speed":0.1, "target":0.95, "speed_data":True,
                    "position":True},
                   {"speed":1.0, "target":0.85, "speed_data":True,
                    "position":True},
                   {"speed": 0.2, "target": 0.75, "speed_data": True,
                    "position": True},
                   {"speed": 0.9, "target": 0.65, "speed_data": True,
                    "position": True},
                   {"speed": 0.3, "target": 0.55, "speed_data": True,
                    "position": True},
                   {"speed": 0.8, "target": 0.45, "speed_data": True,
                    "position": True},
                   {"speed": 0.4, "target": 0.35, "speed_data": True,
                    "position": True},
                   {"speed": 0.7, "target": 0.25, "speed_data": True,
                    "position": True},
                   {"speed": 0.5, "target": 0.15, "speed_data": True,
                    "position": True},
                   {"speed": 0.5, "target": 0.05, "speed_data": True,
                    "position": True},
                   {"speed": 0.6, "target": 0.0, "speed_data": True,
                    "position": True}
                   ]
    calibrating_barr_direction = "close"
    calibrating_barr_step = 0

    def _speed_only(speed, target, steps):
        """Collect data for a speed only step."""
        import time
        nonlocal calibrating_barr_direction
        nonlocal calibrating_barr_step
        timestamp = []
        position = []
        positiondev = []
        trough_lock.acquire()
        cmdsend.send(['Speed', speed])
        cmdsend.send(['MoveTo', target])
        time.sleep(3.0)
        moving = True
        while moving:
            min_next_time = time.time() + 3.0
            cmdsend.send(['Send', ''])
            waiting = True
            while waiting:
                if datarcv.poll():
                    datapkg = datarcv.recv()
                    timestamp += datapkg[0]
                    position += datapkg[1]
                    positiondev += datapkg[2]
                    if len(datapkg[0]) >= 1:
                        status_dict = {'barr_raw': datapkg[1][-1],
                                       'barr_dev': datapkg[2][-1],
                                       'bal_raw': datapkg[3][-1],
                                       'bal_dev': datapkg[4][-1],
                                       'temp_raw': datapkg[5][-1],
                                       'temp_dev': datapkg[6][-1],
                                       'messages': datapkg[7]}

                        if calibrating_barr_direction == "open":
                            Trough_GUI.lastdirection.value = 1
                        else:
                            Trough_GUI.lastdirection.value = -1
                        Trough.Trough_GUI.status_widgets.update_status(status_dict,
                                                                       calibrations,
                                                                       Trough_GUI.lastdirection)
                        if abs(target - position[-1]) < 0.01:
                            moving = False
                        waiting = False
            if time.time() < min_next_time:
                time.sleep(min_next_time - time.time())
        trough_lock.release()
        tempindex_start = 0
        tempindex_end = len(position) - 1
        n_moving_end = 0
        n_moving_start = 0
        while n_moving_end < 3 or n_moving_start < 3:
            # print('tempindex_start: ' + str(tempindex_start) + " tempindex_end: " + str(tempindex_end))
            # print(position[-10:], positiondev[-10:])
            if tempindex_end < 2:
                raise ValueError('Attempting to measure barrier speed, but '
                                 'it was not moving. The speed setting: ' \
                                 + str(steps[calibrating_barr_step][
                                           'speed']))
            if abs(position[tempindex_end] - position[tempindex_end - 1]) > \
                    (positiondev[tempindex_end] ** 2 + \
                     positiondev[tempindex_end - 1] ** 2) ** 0.5:
                if n_moving_end < 3:
                    n_moving_end += 1
            if n_moving_end < 3:
                tempindex_end -= 1
            if abs(position[tempindex_start] - position[tempindex_end + 1]) \
                    > (positiondev[tempindex_start] ** 2 + \
                     positiondev[tempindex_start - 1] ** 2) ** 0.5:
                if n_moving_start < 3:
                    n_moving_start += 1
            if n_moving_start < 3:
                tempindex_start += 1
        if calibrating_barr_direction == 'open':
            open_speed_x.append(speed)
            # Can't calculate speeds until have distance calibration.
            # Save [start_raw, end_raw, delta_time in seconds]
            open_speed_y.append([position[tempindex_start], position[tempindex_end],
                                (timestamp[tempindex_end] - timestamp[tempindex_start])])
        if calibrating_barr_direction == 'close':
            close_speed_x.append(speed)
            # speed fraction per minute
            close_speed_y.append([position[tempindex_start], position[tempindex_end],
                                (timestamp[tempindex_end] - timestamp[tempindex_start])])
        return

    def _get_position():
        """Collect the position data"""
        trough_lock.acquire()
        cmdsend.send(['Send', ''])
        waiting = True
        while waiting:
            if datarcv.poll():
                datapkg = datarcv.recv()
                if calibrating_barr_direction == 'close':
                    close_pos_y.append(Barr_Cal_Val.value)
                    close_pos_x.append(datapkg[1][-1])
                elif calibrating_barr_direction == 'open':
                    open_pos_y.append(Barr_Cal_Val.value)
                    open_pos_x.append(datapkg[1][-1])
                waiting = False
        trough_lock.release()
        return

    def on_calib_barr(change):
        import time
        nonlocal calibrating_barr_direction
        nonlocal calibrating_barr_step
        steps = None
        direction = 0
        just_finished_keep = False
        if Barr_Cal_Butt.description == 'Start Calibration':
            # begin the calibration by opening the trough
            Barr_Cal_Butt.description = 'Moving...'
            Barr_Cal_Butt.disabled = True
            close_pos_x = []
            open_pos_y = []
            close_speed_x = []
            open_speed_x = []
            close_speed_y = []
            open_speed_y = []
            trough_lock.acquire()
            cmdsend.send(['Speed', 1.0])
            cmdsend.send(['Direction', 1.0])
            cmdsend.send(['Start', ''])
            trough_lock.release()
            while float(Barr_Raw.value) < 1.0:
                # We wait
                pass
            # Barr_Cal_Butt.description = 'Keep'
            # Barr_Cal_Butt.disabled = False
            # return
        if calibrating_barr_direction == 'open':
            steps = open_steps
        elif calibrating_barr_direction == 'close':
            steps = close_steps

        if Barr_Cal_Butt.description == 'Keep':
            _get_position()
            calibrating_barr_step += 1

        # Move barriers according to step and collect some data
        if calibrating_barr_step < len(steps):

            # print('Starting step: '+str(calibrating_barr_step) + " of " + str(calibrating_barr_direction))

            if steps[calibrating_barr_step]["position"] and steps[calibrating_barr_step]["speed"]:
                Barr_Cal_Butt.description = "Moving..."
                Barr_Cal_Butt.disabled = True
                _speed_only(steps[calibrating_barr_step]["speed"],
                            steps[calibrating_barr_step]["target"], steps)
                Barr_Cal_Butt.description = "Keep"
                Barr_Cal_Butt.disabled = False
                return
            elif steps[calibrating_barr_step]["position"]:
                # position only
                Barr_Cal_Butt.description = "Moving..."
                Barr_Cal_Butt.disabled = True
                trough_lock.acquire()
                cmdsend.send(['Speed', steps[calibrating_barr_step]["speed"]])
                cmdsend.send(['MoveTo', steps[calibrating_barr_step]["target"]])
                trough_lock.release()
                while abs(float(Barr_Raw.value) - steps[calibrating_barr_step]["target"]) < 0.01:
                    # We wait
                    pass
                Barr_Cal_Butt.description = 'Keep'
                Barr_Cal_Butt.disabled = False
                return
            elif steps[calibrating_barr_step]["speed"]:
                # speed only
                Barr_Cal_Butt.description = "Moving..."
                Barr_Cal_Butt.disabled = True
                _speed_only(steps[calibrating_barr_step]["speed"],
                            steps[calibrating_barr_step]["target"], steps)
                calibrating_barr_step += 1
                on_calib_barr({"clicked":True})

        # Update step information
        if calibrating_barr_step > len(steps)-1:
            # next time we will go the other way
            if calibrating_barr_direction == 'open':
                calibrating_barr_direction = 'done'
            elif calibrating_barr_direction == 'close':
                calibrating_barr_direction = 'open'
                calibrating_barr_step = 0
                Barr_Cal_Butt.description = "Moving..."
                Barr_Cal_Butt.disabled = True
                on_calib_barr({"clicked":True})


        if calibrating_barr_direction == 'done':
            # fitting and save the data
            from pathlib import Path
            cal_path = Path('~/.Trough/calibrations').expanduser()
            # Opening Positions
            params, stdev = calibrations.poly_fit(open_pos_x, open_pos_y, 3, 0.1)
            inv_params, inv_stdev = calibrations.poly_fit(open_pos_y,
                                                          open_pos_x, 3, 0.001)
            calibrations.barriers_open = Trough.Trough_GUI.calibration_utils.\
                Calibration(
                'barriers_open', 'cm', time.time(), params, stdev, inv_params,
                inv_stdev, open_pos_x, open_pos_y, additional_data={
                    "trough width (cm)": float(Trough_Width.value),
                    "skimmer correction (cm^2)": float(Skimer_Correction.value)}
            )
            calibrations.write_cal(cal_path, calibrations.barriers_open)
            # Closing Positions
            params, stdev = calibrations.poly_fit(close_pos_x, close_pos_y, 3, 0.1)
            inv_params, inv_stdev = calibrations.poly_fit(close_pos_y,
                                                          close_pos_x, 3, 0.001)
            calibrations.barriers_close = Trough.Trough_GUI.calibration_utils.\
                Calibration(
                'barriers_close', 'cm', time.time(), params, stdev, inv_params,
                inv_stdev, close_pos_x, close_pos_y, additional_data={
                    "trough width (cm)": float(Trough_Width.value),
                    "skimmer correction (cm^2)": float(Skimer_Correction.value)}
            )
            calibrations.write_cal(cal_path, calibrations.barriers_close)
            # Opening Speeds
            speed_cm_per_min = []
            for k in open_speed_y:
                start = calibrations.barriers_open.cal_apply(k[0],0)[0]
                end = calibrations.barriers_open.cal_apply(k[1],0)[0]
                speed_cm_per_min.append(abs(start - end)*60/k[2])
            params, stdev = calibrations.poly_fit(open_speed_x, speed_cm_per_min, 3, 0.01)
            inv_params, inv_stdev = calibrations.poly_fit(speed_cm_per_min,
                                                          open_speed_x, 3, 0.001)
            calibrations.speed_open = Trough.Trough_GUI.calibration_utils.Calibration(
                'speed_open', 'cm/min', time.time(), params, stdev, inv_params,
                inv_stdev, open_speed_x, speed_cm_per_min)
            calibrations.write_cal(cal_path, calibrations.speed_open)
            # Closing Speeds
            speed_cm_per_min = []
            for k in close_speed_y:
                start = calibrations.barriers_close.cal_apply(k[0],0)[0]
                end = calibrations.barriers_close.cal_apply(k[1],0)[0]
                speed_cm_per_min.append(abs(start - end)*60/k[2])
            params, stdev = calibrations.poly_fit(close_speed_x, speed_cm_per_min,
                                                  3, 0.01)
            inv_params, inv_stdev = calibrations.poly_fit(speed_cm_per_min,
                                                          close_speed_x, 3, 0.001)
            calibrations.speed_close = Trough.Trough_GUI.calibration_utils.Calibration(
                'speed_close', 'cm/min', time.time(), params, stdev, inv_params,
                inv_stdev, close_speed_x, speed_cm_per_min)
            calibrations.write_cal(cal_path, calibrations.speed_close)

            # Calibrations have been updated so restart the status watcher
            Trough_GUI.run_updater.value = False
            while Trough_GUI.updater_running.value:
                # We wait
                pass
            Trough_GUI.start_status_updater()

            Barr_Cal_Butt.description = 'Start Calibration'
            Barr_Cal_Butt.disabled = False
            calibrating_barr_direction = 'close'
            calibrating_barr_step = 0
        return

    Barr_Cal_Val = FloatText(description = "Measured Barrier Separation (cm)",
                            step = 0.01, disabled = False, style = longdesc)
    Trough_Width = FloatText(description="Trough width (cm)",
                                value=calibrations.barriers_open.\
                                additional_data['trough width (cm)'],
                                disabled = False, style = longdesc)
    Skimer_Correction = FloatText(description = "Skimmer Correction ($cm^2$)",
                                value= calibrations.barriers_open.\
                                additional_data['skimmer correction (cm^2)'],
                                disabled=False, style=longdesc)
    Barr_Cal_Butt = Button(description = "Start Calibration")
    Barr_Cal_Butt.on_click(on_calib_barr)
    Barr_Cal_Instr = richLabel(value = '<span style="color:red;">Do Not '
                                       'adjust the trough width or skimmer '
                                       'corrections without accounting for '
                                       'curvature of the surface and the '
                                       'skimmers.</span>'
                                       '<ol><li>Get a ruler with a precision '
                                       'of 0.1 cm or better that is long '
                                       'enough to measure the distance '
                                       'between the barriers when they are '
                                       'fully open.</li>'
                                       '<li>Click on "Start Calibration".</li>'
                                       '<li>When the button converts to '
                                       '"keep" measure the distance between '
                                       'the barriers.</li>'
                                       '<li>Enter the measured value. '
                                       'Make sure the raw value is stable. '
                                       'Then click "keep".</li>'
                                       '<li>Repeat.</li></ol>'
                                       'The button will revert to "Start '
                                       'Calibration" when done.')
    Barr_Adjust_Rarely = VBox(children =[Trough_Width, Skimer_Correction])
    Barr_Adjust_Box = VBox(children = [Barr_Raw, Barr_Cal_Val])
    Barr_Cal_Box = VBox(children = [Barr_Cal_Instr,
                                    HBox(children = [ Barr_Adjust_Rarely,
                                                      Barr_Adjust_Box,
                                                      Barr_Cal_Butt])])

    def on_click_motor_cal(change):
        from time import sleep
        Motor_Cal_Butt.description = "Calibrating..."
        Motor_Cal_Butt.disabled = True
        trough_lock.acquire()
        cmdsend.send(["MotorCal",""])
        trough_lock.release()
        while "Trough ready" not in Status.value:
            sleep(5) # we wait
        Motor_Cal_Butt.description = "Start Motor Calibration"
        Motor_Cal_Butt.disabled = False
        return

    Motor_Cal_Butt = Button(description = "Start Motor Calibration")
    Motor_Cal_Butt.on_click(on_click_motor_cal)
    Barrier_Accord = Accordion(children=[Move_Barrier,Barr_Cal_Box,Motor_Cal_Butt])
    Barrier_Accord.set_title(0, "Manual Barrier Control")
    Barrier_Accord.set_title(1, "Calibrate Barriers")
    Barrier_Accord.set_title(2, "Motor Calibration (automatic after 12 hrs)")
    Barrier_Accord.selected_index = None

    # Monitor, Control and Calibrate widget
    Mon_Ctl_Calib = VBox(children=[Balance, Cal_Bal, Temperature, Cal_Temp,
                                   Barrier, Barrier_Accord, Status])
    display(Mon_Ctl_Calib)
    pass

