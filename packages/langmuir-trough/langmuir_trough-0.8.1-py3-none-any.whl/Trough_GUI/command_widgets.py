from ipywidgets import Dropdown, Button, RadioButtons, BoundedFloatText

# Boilerplate style for long descriptions on ipywidget
longdesc = {'description_width': 'initial'}

# Barriers
# Manual Barrier Control
Barr_Target_Frac = 1.0
speed = 1.0

def _moveto_direction():
    """Returns the appropriate value for direction based on current
    position and position specified by user in the moveto box."""
    from IPython import get_ipython
    import numpy as np
    calibrations = get_ipython().user_ns["Trough_GUI"].calibrations
    current_position = float(get_ipython().user_ns["Trough_GUI"].status_widgets.Bar_Sep.value)
    desired_position = float(Barr_Target.value)
    width = float(calibrations.barriers_open.additional_data["trough width (cm)"])
    skimmer_correction = float(calibrations.barriers_open.additional_data["skimmer correction (cm^2)"])
    moles_molec = float(get_ipython().user_ns["Trough_GUI"].status_widgets.moles_molec.value)
    if Barr_Units.value == 'cm':
        return int(np.sign(desired_position - current_position))
    elif Barr_Units.value == 'cm^2':
        return int(np.sign((desired_position -skimmer_correction)/width - current_position))
    elif Barr_Units.value == 'Angstrom^2/molec':
        desired_position =  desired_position/1e16*moles_molec*6.02214076e23
        return int(np.sign((desired_position -skimmer_correction)/width - current_position))

def _set_min_max(obj, min, max):
    """This sets the min and max trait of the widget, while accounting for the
    current min:max settings to avoid an error of max < min or min > max."""
    if obj.min > max:
        obj.min = min
        obj.max = max
    else:
        obj.max = max
        obj.min = min
    pass

def on_change_Barr_Units(change):
    from IPython import get_ipython
    calibrations = get_ipython().user_ns["Trough_GUI"].calibrations
    width = float(calibrations.barriers_open.additional_data["trough width (cm)"])
    skimmer_correction = float(calibrations.barriers_open.additional_data["skimmer correction (cm^2)"])
    moles_molec = float(get_ipython().user_ns["Trough_GUI"].status_widgets.moles_molec.value)
    if change['new'] == 'cm':
        _set_min_max(Barr_Target, round(calibrations.barriers_close.cal_apply(0.0,0.0)[0], 2),
                     round(calibrations.barriers_open.cal_apply(1.0, 0.0)[0],2))
        if Barr_Direction.value == "Open":
            Barr_Target.value = calibrations.barriers_open.cal_apply(Barr_Target_Frac, 0.0)[0]
            tempspeed = calibrations.speed_open.cal_apply(speed,0.0)[0]
            max = calibrations.speed_open.cal_apply(1.0, 0.0)[0]
            min = calibrations.speed_open.cal_apply(0.0, 0.0)[0]
            _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
            Barr_Speed.value = tempspeed
        elif Barr_Direction.value == "Close":
            Barr_Target.value = calibrations.barriers_close.cal_apply(Barr_Target_Frac, 0.0)[0]
            tempspeed = calibrations.speed_close.cal_apply(speed,0.0)[0]
            max = calibrations.speed_close.cal_apply(1.0, 0.0)[0]
            min = calibrations.speed_close.cal_apply(0.0, 0.0)[0]
            _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
            Barr_Speed.value = tempspeed
        else: # MoveTo case
            if _moveto_direction() == -1:
                Barr_Target.value = calibrations.barriers_open.cal_apply(Barr_Target_Frac, 0.0)[0]
                tempspeed = calibrations.speed_close.cal_apply(speed, 0.0)[0]
                max = calibrations.speed_close.cal_apply(1.0, 0.0)[0]
                min = calibrations.speed_close.cal_apply(0.0, 0.0)[0]
                _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
                Barr_Speed.value = tempspeed
            elif _moveto_direction() == 1:
                Barr_Target.value = calibrations.barriers_open.cal_apply(Barr_Target_Frac, 0.0)[0]
                tempspeed = calibrations.speed_open.cal_apply(speed, 0.0)[0]
                max = calibrations.speed_open.cal_apply(1.0, 0.0)[0]
                min = calibrations.speed_open.cal_apply(0.0, 0.0)[0]
                _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
                Barr_Speed.value = tempspeed
            pass
    if change['new'] == 'cm^2':
        max = calibrations.barriers_open.cal_apply(1.0, 0.0)[0]*float(width) +\
                          float(skimmer_correction)
        min = calibrations.barriers_close.cal_apply(0.0,0.0)[0]*float(width) +\
                          float(skimmer_correction)
        _set_min_max(Barr_Target, round(min, 2), round(max, 2))
        if Barr_Direction.value == "Open":
            temptarg = calibrations.barriers_open.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                       float(width) + float(skimmer_correction)
            Barr_Target.value = temptarg
            tempspeed = calibrations.speed_open.cal_apply(speed,0.0)[0]*float(width) + \
                            float(skimmer_correction)
            max = calibrations.speed_open.cal_apply(1.0, 0.0)[0] * \
                  float(width) + \
                  float(skimmer_correction)
            min = calibrations.speed_open.cal_apply(0.0, 0.0)[0] * \
                  float(width) + \
                  float(skimmer_correction)
            _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
            Barr_Speed.value = tempspeed
        elif Barr_Direction.value == "Close":
            temptarg = calibrations.barriers_close.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                       float(width) + float(skimmer_correction)
            Barr_Target.value = temptarg
            tempspeed = calibrations.speed_close.cal_apply(speed,0.0)[0]*float(width) + \
                            float(skimmer_correction)
            max = calibrations.speed_close.cal_apply(1.0, 0.0)[0] * \
                  float(width) + \
                  float(skimmer_correction)
            min = calibrations.speed_close.cal_apply(0.0, 0.0)[0] * \
                  float(width) + \
                  float(skimmer_correction)
            _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
            Barr_Speed.value = tempspeed
        else: # MoveTo case
            if _moveto_direction() == -1:
                temptarg = calibrations.barriers_close.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                           float(width) + float(skimmer_correction)
                Barr_Target.value = temptarg
                tempspeed = calibrations.speed_close.cal_apply(speed, 0.0)[0] * float(width) + \
                            float(skimmer_correction)
                max = calibrations.speed_close.cal_apply(1.0, 0.0)[0] * \
                      float(width) + \
                      float(skimmer_correction)
                min = calibrations.speed_close.cal_apply(0.0, 0.0)[0] * \
                      float(width) + \
                      float(skimmer_correction)
                _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
                Barr_Speed.value = tempspeed
            elif _moveto_direction() == 1:
                temptarg = calibrations.barriers_open.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                           float(width) + float(skimmer_correction)
                Barr_Target.value = temptarg
                tempspeed = calibrations.speed_open.cal_apply(speed, 0.0)[0] * float(width) + \
                            float(skimmer_correction)
                max = calibrations.speed_open.cal_apply(1.0, 0.0)[0] * \
                      float(width) + \
                      float(skimmer_correction)
                min = calibrations.speed_open.cal_apply(0.0, 0.0)[0] * \
                      float(width) + \
                      float(skimmer_correction)
                _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
                Barr_Speed.value = tempspeed
            pass
    if change['new'] == 'Angstrom^2/molec':
        max = (calibrations.barriers_open.cal_apply(1.0,0.0)[0]*\
                            width + skimmer_correction)*\
                            1e16/moles_molec/6.02214076e23
        min = (calibrations.barriers_close.cal_apply(0.0,0.0)[0]*\
                            width +skimmer_correction)*\
                            1e16/moles_molec/6.02214076e23
        _set_min_max(Barr_Target, min, max)
        if Barr_Direction.value == "Open":
            temptarg = (calibrations.barriers_open.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                        width + skimmer_correction) * \
                       1e16 / moles_molec / 6.02214076e23
            Barr_Target.value = temptarg
            tempspeed = (calibrations.speed_open.cal_apply(speed,0.0)[0]*width + \
                            skimmer_correction)*\
                            1e16/moles_molec/6.02214076e23
            max = (calibrations.speed_open.cal_apply(1.0, 0.0)[0] * \
                  width + skimmer_correction) * \
                  1e16 / moles_molec / 6.02214076e23
            min = (calibrations.speed_open.cal_apply(0.0, 0.0)[0] * \
                  width + skimmer_correction) * \
                  1e16 / moles_molec / 6.02214076e23
            _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
            Barr_Speed.value = tempspeed
        elif Barr_Direction.value == "Close":
            temptarg = (calibrations.barriers_close.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                        width + skimmer_correction) * \
                       1e16 / moles_molec / 6.02214076e23
            Barr_Target.value = temptarg
            tempspeed = (calibrations.speed_close.cal_apply(speed,0.0)[0]*width + \
                            skimmer_correction)*\
                            1e16/moles_molec/6.02214076e23
            max = (calibrations.speed_close.cal_apply(1.0, 0.0)[0] * \
                  width + skimmer_correction) * \
                  1e16 / moles_molec / 6.02214076e23
            min = (calibrations.speed_close.cal_apply(0.0, 0.0)[0] * \
                  width + skimmer_correction) * \
                  1e16 / moles_molec / 6.02214076e23
            _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
            Barr_Speed.value = tempspeed
        else: # MoveTo case
            if _moveto_direction() == -1:
                temptarg = (calibrations.barriers_close.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                            width + skimmer_correction) * \
                           1e16 / moles_molec / 6.02214076e23
                Barr_Target.value = temptarg
                tempspeed = calibrations.speed_close.cal_apply(speed, 0.0)[0] * float(width) + \
                            float(skimmer_correction) * \
                            1e16 / moles_molec / 6.02214076e23
                max = calibrations.speed_close.cal_apply(1.0, 0.0)[0] * \
                      float(width) + \
                      float(skimmer_correction) * \
                      1e16 / moles_molec / 6.02214076e23
                min = calibrations.speed_close.cal_apply(0.0, 0.0)[0] * \
                      float(width) + \
                      float(skimmer_correction) * \
                      1e16 / moles_molec / 6.02214076e23
                _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
                Barr_Speed.value = tempspeed
            elif _moveto_direction() == 1:
                temptarg = (calibrations.barriers_open.cal_apply(Barr_Target_Frac, 0.0)[0] * \
                            width + skimmer_correction) * \
                           1e16 / moles_molec / 6.02214076e23
                Barr_Target.value = temptarg
                tempspeed = (calibrations.speed_open.cal_apply(speed, 0.0)[0] * width + \
                            skimmer_correction) * \
                            1e16 / moles_molec / 6.02214076e23
                max = (calibrations.speed_open.cal_apply(1.0, 0.0)[0] * \
                      width + skimmer_correction) * \
                      1e16 / moles_molec / 6.02214076e23
                min = (calibrations.speed_open.cal_apply(0.0, 0.0)[0] * \
                      width + skimmer_correction) * \
                      1e16 / moles_molec / 6.02214076e23
                _set_min_max(Barr_Speed, round(min, 2), round(max, 2))
                Barr_Speed.value = tempspeed
            pass
    pass

Barr_Units = Dropdown(description="Units",
                      options=["cm", "cm^2", "Angstrom^2/molec"])

Barr_Units.observe(on_change_Barr_Units, names='value')

def on_change_Barr_Direction(changed):
    if Barr_Direction.value == 'Move To':
        Barr_Target.disabled = False
    else:
        Barr_Target.disabled = True
    on_change_Barr_Units({'new':Barr_Units.value})
    pass

Barr_Direction = RadioButtons(options=["Open", "Close", "Move To"])
Barr_Direction.observe(on_change_Barr_Direction, names='value')

def on_Barr_Target_change(change):
    """Updates the speed settings since open and close are different."""
    direction = _moveto_direction()
    on_change_Barr_Units({'new': Barr_Units.value})
    pass

Barr_Target = BoundedFloatText(value=10.0, min=0.0, max=12.6,
                               step=0.01, disabled=True)
Barr_Speed = BoundedFloatText(description="Speed (/min)", value=5.0, min = 0.0,
                       max = 10.0, step = 0.01, disabled=False)
def on_click_Start(change):
    from IPython import get_ipython
    cmdsend = get_ipython().user_ns["Trough_Control"].cmdsend
    calibrations = get_ipython().user_ns["Trough_GUI"].calibrations
    width = float(calibrations.barriers_open.additional_data["trough width (cm)"])
    skimmer_correction = float(calibrations.barriers_open.additional_data["skimmer correction (cm^2)"])
    moles_molec = float(get_ipython().user_ns["Trough_GUI"].status_widgets.moles_molec.value)
    trough_lock = get_ipython().user_ns["Trough_Control"].trough_lock
    lastdirection = get_ipython().user_ns["Trough_GUI"].lastdirection
    global speed
    if Barr_Units.value == 'cm':
        tempspeed = float(Barr_Speed.value)
        Barr_Target_Frac = calibrations.barriers_open.cal_inv(Barr_Target.value, 0)[0]
    elif Barr_Units.value == 'cm^2':
        tempspeed = (Barr_Speed.value - skimmer_correction)/width
        temptarg = (Barr_Target.value - skimmer_correction)/width
        Barr_Target_Frac = calibrations.barriers_open.cal_inv(temptarg, 0)[0]
    elif Barr_Units.value == 'Angstrom^2/molec':
        tempspeed = (Barr_Speed.value - skimmer_correction)/width/1e16*moles_molec*6.02214076e23
        temptarg = Barr_Target.value/1e16*moles_molec*6.02214076e23
        temptarg = (temptarg - skimmer_correction)/width
        Barr_Target_Frac = calibrations.barriers_open.cal_inv(temptarg, 0)[0]
    if Barr_Direction.value != 'Move To':
        direction = 0
        if Barr_Direction.value == 'Close':
            direction = -1
            speed = calibrations.speed_close.cal_inv(tempspeed, 0)[0]
        elif Barr_Direction.value == 'Open':
            direction = 1
            speed = calibrations.speed_open.cal_inv(tempspeed, 0)[0]
        trough_lock.acquire()
        cmdsend.send(['Speed', speed])
        cmdsend.send(['Direction', direction])
        cmdsend.send(['Start', ''])
        lastdirection.value = direction
        trough_lock.release()
    else:
        direction = _moveto_direction()
        if direction == -1:
            speed = calibrations.speed_close.cal_inv(tempspeed, 0)[0]
        else:
            speed = calibrations.speed_open.cal_inv(tempspeed, 0)[0]
        trough_lock.acquire()
        cmdsend.send(['Speed', speed])
        cmdsend.send(['Direction', direction])
        cmdsend.send(['MoveTo', Barr_Target_Frac])
        lastdirection.value = direction
        trough_lock.release()
    pass

Barr_Start = Button(description="Start")
Barr_Start.button_style = "success"
Barr_Start.on_click(on_click_Start)

def on_click_Stop(change):
    from IPython import get_ipython
    trough_lock = get_ipython().user_ns["Trough_Control"].trough_lock
    trough_lock.acquire()
    cmdsend = get_ipython().user_ns["Trough_Control"].cmdsend
    cmdsend.send(['Stop', ''])
    trough_lock.release()
    pass

Barr_Stop = Button(description="Stop")
Barr_Stop.button_style = "danger"
Barr_Stop.on_click(on_click_Stop)
