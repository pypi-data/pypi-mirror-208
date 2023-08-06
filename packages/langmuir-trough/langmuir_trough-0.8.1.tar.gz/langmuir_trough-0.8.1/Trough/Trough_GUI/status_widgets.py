"""This file contains widgets that display updating trough information and
can be used in multiple ipywidget panels within the same notebook."""

from ipywidgets import Layout, Text, Button, FloatText
from ipywidgets import HTML as richLabel

# Boilerplate style for long descriptions on ipywidget
longdesc = {'description_width': 'initial'}

# Used for surface pressure. Balance zero set during calibration.
tare_pi = 72.00
Bal_Raw = Text(description='Balance Raw:',
               disabled=True,
               style=longdesc)
mg = Text(description="mg",
          disabled=True,
          style=longdesc)
surf_press = Text(description="$\pi$ (mN/m)",
                  disabled=True,
                  style=longdesc)
plate_circumference = FloatText(description="Plate circumference (mm)",
                                value=21.5,
                                style=longdesc)

def set_zero_pressure(change):
    global tare_pi
    tare_pi = float(mg.value)
    pass

zero_press = Button(description="Zero Pressure")
zero_press.on_click(set_zero_pressure)

Temp_Raw = Text(description="Temperature Raw", disabled=True,
                style=longdesc)
degC = Text(description="$^o C$",
            disabled=True,
            style=longdesc)
Barr_Raw = Text(description="Barrier Raw", disabled=True,
                style=longdesc)
Bar_Frac = Text(description="% open", disabled=True, style=longdesc)
Bar_Sep = Text(description="Separation (cm)", disabled=True,
               style=longdesc)
Bar_Area = Text(description="Area ($cm^2$)", disabled=True, style=longdesc)
Bar_Area_per_Molec = Text(description="$\mathring{A^2}$/molecule",
                          disabled=True, style=longdesc)
moles_molec = FloatText(description="moles of molecules",
                        value=3.00e-8, style=longdesc)

Status = richLabel(layout=Layout(border="solid"), value=
'<p>Status messages will appear here.</p>')

def update_status(raw_data:dict, calibrations, lastdirection):
    """
    Call this routine to update the contents of all the status widgets.

    Parameters
    ----------
    raw_data: dict
        dictionary of latest raw data values for each
        sensor and their standard deviation
        (e.g. {'bal_raw':3.20,'bal_dev':0.005,'barr_raw':0.5,'barr_dev':0.002,
        'temp_raw':2.24, 'temp_dev':0.01, 'messages':''})

    calibrations: Calibrations
        Object containing the calibrations for the trough (currently
        `.balance`, `.barriers` and `.temperature`). A call to
        `.balance.cal_apply(raw_data['bal_raw'],raw_data['bal_dev'])`
        will return the balance reading in the calibration units (`.balance.units`).
    """
    from round_using_error import rndwitherr
    if "barr_raw" in raw_data.keys():
        # Only update if there is data
        if calibrations.balance.units != 'mg':
            raise ValueError('Expect balance to be calibrated in mg. Instead got '
                             + calibrations.balance.units + '.')
        Bal_Raw.value = rndwitherr(raw_data['bal_raw'], raw_data['bal_dev'],
                                         lowmag=-4, highmag=4)[0]
        mgrams, mgrams_err = calibrations.balance.cal_apply(raw_data['bal_raw'],
                                                      raw_data['bal_dev'])
        mg.value = rndwitherr(mgrams,mgrams_err, lowmag=-4, highmag=4)[0]
        surf_press_err = mgrams_err*9.80665/plate_circumference.value
        surf_press.value = rndwitherr((tare_pi-mgrams)*\
                               9.80665/plate_circumference.value,
                               surf_press_err, lowmag=-4, highmag=4)[0]
        if calibrations.temperature.units != 'C':
            raise ValueError('Expected temperature to be calibrated in C. '
                             'Instead got ' + calibrations.temperature.units + '.')
        Temp_Raw.value = rndwitherr(raw_data['temp_raw'], raw_data['temp_dev'],
                                         lowmag=-4, highmag=4)[0]
        degC.value = str(calibrations.temperature.cal_apply(raw_data['temp_raw'],
                                                          raw_data['temp_dev'])[0])
        Barr_Raw.value = rndwitherr(raw_data['barr_raw'], raw_data['barr_dev'],
                                         lowmag=-4, highmag=4)[0]
        Bar_Frac.value = rndwitherr(raw_data['barr_raw']*100,
                                                raw_data['barr_dev']*100,
                                         lowmag=-4, highmag=4)[0]
        if calibrations.barriers_open.units != 'cm':
            raise ValueError('Expected barrier separation to be calibrated in cm. '
                             'Instead got ' + calibrations.barriers.units + '.')
        if calibrations.barriers_close.units != 'cm':
            raise ValueError('Expected barrier separation to be calibrated in cm. '
                             'Instead got ' + calibrations.barriers.units + '.')
        if lastdirection.value < 0:
            # barriers were or are closing
            sep_cm, sep_cm_stdev = calibrations.barriers_close.cal_apply(
                raw_data['barr_raw'],raw_data['barr_dev'])
            area_cm_sq_error = sep_cm_stdev * \
                               float(calibrations.barriers_close. \
                               additional_data["trough width (cm)"])
            area_cm_sq = sep_cm * float(calibrations.barriers_close. \
                         additional_data["trough width (cm)"]) - \
                         float(calibrations.barriers_close. \
                         additional_data["skimmer correction (cm^2)"])
        else:
            sep_cm, sep_cm_stdev = calibrations.barriers_open.cal_apply(
                raw_data['barr_raw'],raw_data['barr_dev'])
            area_cm_sq_error = sep_cm_stdev * float(calibrations. \
                               barriers_open.additional_data[ \
                               "trough width (cm)"])
            area_cm_sq = sep_cm * float(calibrations.barriers_open.additional_data[ \
                     "trough width (cm)"]) - float(calibrations.barriers_open. \
                     additional_data["skimmer correction (cm^2)"])
        area_per_molec_ang_sq_error = area_cm_sq_error*1e16/moles_molec.value/6.02214076e23
        area_per_molec_ang_sq = area_cm_sq*1e16/moles_molec.value/6.02214076e23
        Bar_Sep.value = str(sep_cm)
        Bar_Area.value = rndwitherr(area_cm_sq,area_cm_sq_error, lowmag=-4,
                                         highmag=4)[0]
        Bar_Area_per_Molec.value = rndwitherr(area_per_molec_ang_sq,
                                                   area_per_molec_ang_sq_error,
                                                   lowmag=-4, highmag=4)[0]
    status_msgs = Status.value
    for k in raw_data['messages']:
        status_msgs+='<p>' + str(k) + '</p>'
    Status.value = status_msgs
    pass

def status_updater(trough_lock, cmdsend, datarcv, cals, lastdirection,
                   run_updater, updater_running):
    """This is run in a separate thread and will update the status widgets
    every 2 seconds or when it can get access to the pipes to talk to the
    trough.

    Parameters
    ----------
    trough_lock: threading.lock
        When acquired this routine will talk to the trough. Releases it for
        other processes after every update.

    cmdsend: Pipe
        End of Pipe to send commands to the Trough.

    datarcv: Pipe
        End of Pipe to receive data from the Trough.

    cals: Trough_GUI.calibrations
        Used to convert the data to user units.

    lastdirection: multiprocessing.Value
        Of type 'i' to indicate last direction the barriers moved.

    run_updater: multiprocessing.Value
        Of type 'c_bool'. True if this updater should keep running.

    updater_running: multiprocessing.Value
        Of type 'c_bool'. Set to True by this process when it starts
        and set to False before exiting.
    """
    import time
    # Set the shared I'm running flag.
    updater_running.value = True
    while run_updater.value:
        min_next_time = time.time() + 2.0
        trough_lock.acquire()
        cmdsend.send(['Send',''])
        waiting = True
        while waiting:
            if datarcv.poll():
                datapkg =datarcv.recv()
                if len(datapkg[1]) >= 1:
                    update_dict = {'barr_raw':datapkg[1][-1],
                                   'barr_dev':datapkg[2][-1],
                                   'bal_raw':datapkg[3][-1],
                                   'bal_dev':datapkg[4][-1],
                                   'temp_raw':datapkg[5][-1],
                                   'temp_dev':datapkg[6][-1],
                                   'messages':datapkg[7]}
                else:
                    # No updated data, so just pass messages
                    update_dict = {'messages':datapkg[7]}
                update_status(update_dict, cals, lastdirection)
                waiting = False
        trough_lock.release()
        if time.time()< min_next_time:
            time.sleep(min_next_time - time.time())
    # Set the shared I'm running flag to False before exiting.
    updater_running.value = False
    return

def start_status_updater():
    from threading import Thread
    from IPython import get_ipython
    Trough_Control = get_ipython().user_ns["Trough_Control"]
    Trough_GUI = get_ipython().user_ns["Trough_GUI"]
    Trough_GUI.run_updater.value = True
    status_update_thread = Thread(target=status_updater,
                                  args=(Trough_Control.trough_lock,
                                        Trough_Control.cmdsend,
                                        Trough_Control.datarcv,
                                        Trough_GUI.calibrations,
                                        Trough_GUI.lastdirection,
                                        Trough_GUI.run_updater,
                                        Trough_GUI.updater_running))
    status_update_thread.start()
    return