from IPython import get_ipython
# Only load if in IPython to allow build of docs
if get_ipython():
    cmdsend = get_ipython().user_ns["Trough_Control"].cmdsend
    datarcv = get_ipython().user_ns["Trough_Control"].datarcv
    trough_lock = get_ipython().user_ns["Trough_Control"].trough_lock

# Boilerplate style for long descriptions on ipywidget
longdesc = {'description_width': 'initial'}

class trough_run():
    def __init__(self, id, filename, title, units, target, speed, moles,
                 plate_circ, dataframe=None, timestamp=None):
        """Create a new run object
        Parameters
        ----------
        id: int
            0 based index of run in current notebook
        filename: str
            String representation of the filename used to store the data,
            with not type extension. This probably should not contain a path.
        title: str
            User friendly title (suggested default is same as filename).
        units: str
            Units for the displayed barrier positions (cm, cm^2 or Ang^2/molec).
        target: float
            Numerical value in units for the targeted final trough area.
        speed: float
            Numerical value in units for the speed to move the barriers.
        moles: float
            moles of molecules initially spread in the trough.
        plate_circ: float
            circumference of the Whilhelmy plate in mm.
        dataframe: DataFrame or None
        timestamp: float or None
        """
        from plotly import graph_objects as go
        import time
        from datetime import datetime
        self.id = id
        self.filename = filename
        self.title = title
        self.units = units
        self.target = target
        self.speed = speed
        self.moles = moles
        self.plate_circ = plate_circ
        self.livefig = go.FigureWidget(layout_template='simple_white')
        self.df = dataframe
        # Empty holder for the collection control parts, which can be
        #  cleared at the end of a run.
        self.collect_control = None
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
        self.datestr = (datetime.fromtimestamp(self.timestamp)).isoformat()
        # load data into livefig if there is any?
        if self.df is not None:
            if len(self.df) > 0:
                x_data = []
                self.livefig.update_yaxes(title = "$\Pi\,(mN/m)$")
                if self.speed > 0:
                    if self.units == 'cm':
                        x_data = self.df['Separation (cm)']
                        self.livefig.update_xaxes(title="Separation (cm)")
                    if self.units == 'cm^2':
                        x_data = self.df['Area (cm^2)']
                        self.livefig.update_xaxes(title="$Area\,(cm^2)$")
                    if self.units == 'Angstrom^2/molec':
                        x_data = self.df['Area per molecule (A^2)']
                        self.livefig.update_xaxes(title="$Area\,per\,"
                                        "molecule\,({\overset{\circ}{A}}^2)$")
                else:
                    x_data = self.df['time_stamp']-self.df['time_stamp'][0]
                self.livefig.add_scatter(y=self.df['Surface Pressure (mN/m)'], x=x_data)

    @classmethod
    def from_html(self, html):
        """Create a run from an html representation
        Parameters
        ----------
        html: str
            The html to be parsed to create the run object

        Returns
        -------
        trough_run: trough_run
            A trough_run object
        """
        from AdvancedHTMLParser import AdvancedHTMLParser as Parser
        from pandas import read_html
        # parse the document
        document = Parser()
        document.parseStr(html)
        id = int(document.getElementById('id').text)
        filename = document.getElementById('filename').text
        title = document.getElementById('title').text
        units = document.getElementById('units').text
        target = float(document.getElementById('target').text)
        speed = float(document.getElementById('speed').text)
        moles = float(document.getElementById('moles').text)
        plate_circ = float(document.getElementById('plate_circ').text)
        dataframe = read_html(html, index_col=0, attrs = {'id': 'run_data'})[0]
        timestamp = float(document.getElementById('timestamp').text)
        # return as run object
        return trough_run(id, filename, title, units, target, speed, moles,
                 plate_circ, dataframe, timestamp)

    def run_caption(self):
        """Returns an html table with info about the run to use as a caption"""
        caption = ''
        caption += '<table><tr><th>Run ID</th><th>Title</th>'
        caption += '<th>Storage File Name</th>'
        caption += '<th>Target (' + str(self.units) + ')</th>'
        caption += '<th>Speed (' + str(self.units) + '/min)</th>'
        caption += '<th>Moles</th><th>Plate Circumference (mm)</th></tr>'
        caption += '<tr><td>' + str(self.id) + '</td>'
        caption += '<td>' + str(self.title) + '</td>'
        caption += '<td>' + str(self.filename) + '</td>'
        caption += '<td>' + str(self.target) + '</td>'
        caption += '<td>' + str(self.speed) + '</td>'
        caption += '<td>' + str(self.moles) + '</td>'
        caption += '<td>' + str(self.plate_circ) + '</td></tr>'
        caption += '</table>'
        return caption

    def _end_of_run(self):
        from IPython import get_ipython
        Trough_GUI = get_ipython().user_ns["Trough_GUI"]
        # This hides the control stuff
        self.close_collect_control()
        # Store data
        self.write_run('')
        # start background updating
        if not Trough_GUI.updater_running.value:
            Trough_GUI.run_updater.value = True
            Trough_GUI.start_status_updater()
        return

    def init_collect_control(self):
        """This initializes the collection control widgets and VBox that
        contains them. The VBox may be accessed as `self.collect_control`"""
        from ipywidgets import Button, HBox, VBox
        from IPython import get_ipython
        Trough_GUI = get_ipython().user_ns["Trough_GUI"]
        Bar_Sep = Trough_GUI.status_widgets.Bar_Sep
        Bar_Area = Trough_GUI.status_widgets.Bar_Area
        Bar_Area_per_Molec = Trough_GUI.status_widgets.Bar_Area_per_Molec
        degC = Trough_GUI.status_widgets.degC
        surf_press = Trough_GUI.status_widgets.surf_press
        Barr_Units = Trough_GUI.command_widgets.Barr_Units
        Barr_Speed = Trough_GUI.command_widgets.Barr_Speed
        Barr_Target = Trough_GUI.command_widgets.Barr_Target

        run_start_stop = Button(description="Run",
                                button_style="success")

        def _on_run_start_stop(change):
            from threading import Thread
            from numpy import sign
            from IPython import get_ipython
            from Trough.Trough_GUI.conversions import sqcm_to_cm, angpermolec_to_sqcm
            Trough_GUI = get_ipython().user_ns["Trough_GUI"]
            Bar_Sep = Trough_GUI.status_widgets.Bar_Sep
            Bar_Area = Trough_GUI.status_widgets.Bar_Area
            Bar_Area_per_Molec = Trough_GUI.status_widgets.Bar_Area_per_Molec
            moles_molec = Trough_GUI.status_widgets.moles_molec
            Barr_Units = Trough_GUI.command_widgets.Barr_Units
            Barr_Speed = Trough_GUI.command_widgets.Barr_Speed
            Barr_Target = Trough_GUI.command_widgets.Barr_Target
            # Check if we are stopping a run
            if run_start_stop.description == "Stop":
                _on_stop_run()
                return
            # take over status updating
            # First shutdown currently running updater
            if Trough_GUI.updater_running.value:
                Trough_GUI.run_updater.value = False
                while Trough_GUI.updater_running.value:
                    # wait
                    pass
            # Start run
            # Convert "Start" to "Stop" button
            Trough_GUI.run_updater.value = True
            run_start_stop.description = "Stop"
            run_start_stop.button_style = "danger"
            # start barriers
            trough_lock.acquire()
            direction = 0
            tempspeed = 0
            temp_targ = 0
            speed = 0
            skimmer_correction = float(
                Trough_GUI.calibrations.barriers_open.additional_data[
                    "skimmer correction (cm^2)"])
            width = float(Trough_GUI.calibrations.barriers_open.additional_data[
                              "trough width (cm)"])
            target_speed = float(Barr_Speed.value)
            if Barr_Units.value == 'cm':
                direction = int(
                    sign(float(Barr_Target.value) - float(Bar_Sep.value)))
                tempspeed = target_speed
                temp_targ = float(Barr_Target.value)
            elif Barr_Units.value == "cm^2":
                direction = int(
                    sign(float(Barr_Target.value) - float(Bar_Area.value)))
                tempspeed = (target_speed - skimmer_correction) / width
                temp_targ = \
                    sqcm_to_cm(float(Barr_Target.value), 0,
                               Trough_GUI.calibrations)[0]
            elif Barr_Units.value == "Angstrom^2/molec":
                direction = int(sign(
                    float(Barr_Target.value) - float(Bar_Area_per_Molec.value)))
                tempspeed = (target_speed - skimmer_correction) / width / 1e16 * float(
                    moles_molec.value) * 6.02214076e23
                temp_targ = sqcm_to_cm(
                    *angpermolec_to_sqcm(float(Barr_Target.value), 0,
                                         float(moles_molec.value)),
                    Trough_GUI.calibrations)[0]
            if direction < 0:
                target = \
                    Trough_GUI.calibrations.barriers_close.cal_inv(
                        float(temp_targ), 0)[
                        0]
                speed = \
                Trough_GUI.calibrations.speed_close.cal_inv(tempspeed, 0)[0]
            else:
                target = \
                    Trough_GUI.calibrations.barriers_open.cal_inv(
                        float(temp_targ), 0)[
                        0]
                speed = \
                Trough_GUI.calibrations.speed_open.cal_inv(tempspeed, 0)[0]
            cmdsend.send(['Speed', speed])
            cmdsend.send(['Direction', direction])
            cmdsend.send(['MoveTo', target])
            trough_lock.release()
            # display data as collected and periodically update status widgets
            # spawn updater thread that updates both status widgets and the figure.
            updater = Thread(target=collect_data_updater,
                             args=(trough_lock, cmdsend,
                                   datarcv,
                                   Trough_GUI.calibrations,
                                   Trough_GUI.lastdirection,
                                   Trough_GUI.run_updater,
                                   Trough_GUI.updater_running,
                                   self))
            updater.start()
            return

        def _on_stop_run():
            from IPython import get_ipython
            Trough_GUI = get_ipython().user_ns["Trough_GUI"]
            run_start_stop.description = "Done"
            run_start_stop.disabled = True
            run_start_stop.button_style = ""
            # Stop run
            if Trough_GUI.updater_running.value:
                Trough_GUI.run_updater.value = False
            # when collection stops it will call _end_of_run.
            return

        run_start_stop.on_click(_on_run_start_stop)

        run_start_stop.description = "Run"
        run_start_stop.disabled = False
        run_start_stop.button_style = "success"
        collect_control1 = HBox([surf_press, run_start_stop])
        position = None
        x_units = Barr_Units.value
        if Barr_Units.value == 'cm':
            position = Bar_Sep
        elif Barr_Units.value == 'cm^2':
            position = Bar_Area
            x_units = "$cm^2$"
        elif Barr_Units.value == 'Angstrom^2/molec':
            position = Bar_Area_per_Molec
            x_units = "$Area\,per\,molecule\,({\overset{\circ}{A}}^2)$"
        collect_control2 = HBox([degC, position])
        self.collect_control = VBox([collect_control1, collect_control2])
        x_min = 0
        x_max = 1
        if float(Barr_Target.value) < float(position.value):
            x_min = 0.98 * float(Barr_Target.value)
            x_max = 1.02 * float(position.value)
        else:
            x_min = 0.98 * float(position.value)
            x_max = 1.02 * float(Barr_Target.value)
        if float(Barr_Speed.value) == 0:
            x_units = 'Time (s)'
            x_min = 0
            x_max = 600  # 10 minutes
        self.livefig.update_yaxes(title="$\Pi\,(mN/m)$",
                                                 range=[0, 60])
        self.livefig.update_xaxes(title=x_units,
                                                 range=[x_min, x_max])
        self.livefig.add_scatter(x=[], y=[])
        return

    def close_collect_control(self):
        """This closes `self.collect_control` which also minimizes
        the objects maintained on the Python side."""
        self.collect_control.close()
        self.collect_control = None
        return

    def __repr__(self):
        from IPython.display import HTML, display
        display(self.livefig)
        display(HTML(self.run_caption()))
        return ''

    def to_html(self):
        """Create an html string representing a run"""
        from AdvancedHTMLParser import AdvancedTag as Domel
        # create the html
        run_div = Domel('div')
        run_info = Domel('table')
        run_info.setAttribute('class','run_info')
        run_info.setAttribute('id','run_info')
        run_info.setAttribute('border','1')
        tr = Domel('tr')
        tr.appendInnerHTML('<th>ID</th><th>Filename</th><th>Title</th><th>Units'
                       '</th><th>Target</th><th>Speed</th><th>Moles</th>'
                       '<th>Plate Circumference (mm)</th><th>Time</th><th>Time '
                       'Stamp</th>')
        run_info.appendChild(tr)
        tr = Domel('tr')
        tr.appendInnerHTML('<td id="id">'+str(self.id)+'</td>'
                           '<td id="filename">'+str(self.filename) + '</td>'
                           '<td id="title">'+str(self.title) + '</td>'
                           '<td id="units">' + str(self.units)+'</td>'
                           '<td id="target">'+str(self.target) +'</td>'
                           '<td id="speed">'+str(self.speed)+'</td>'
                           '<td id="moles">' + str(self.moles)+'</td>'
                           '<td id="plate_circ">'+str(self.plate_circ) + '</td>'
                           '<td id="datestr">'+str(self.datestr)+'</td>'
                           '<td id="timestamp">' + str(self.timestamp)+'</td>')
        run_info.appendChild(tr)
        run_div.appendChild(run_info)
        dfstr = self.df.to_html(table_id="run_data")
        run_div.appendInnerHTML('<!--placeholder to avoid bug that strips table tag-->\n'+dfstr+'\n<!--avoid tag loss-->\n')
        return run_div.asHTML()

    def write_run(self, dirpath, **kwargs):
        """
        Writes a run file with the base filename `run.filename` into the
        directory specified. If a file with the current name exists
        attempts to make the name unique by appending self.timestamp
        to the filename. Currently only produces
        an html file that is also human-readable. Other file formats may be
        available in the future through the use of key word arguments.

        Parameters
        ----------
        dirpath:
            pathlike object or string. Empty string means the current working
            directory.

        kwargs:
            optional key word arguments for future adaptability
        """
        from pathlib import Path
        from warnings import warn
        fileext = '.trh.run.html'
        filename = str(self.filename)
        fullpath = Path(dirpath, filename)
        if fullpath.exists():
            basename = self.filename
            for k in Path(self.filename).suffixes:
                basename = basename.replace(k, '')
            if basename.split("_")[-1].isnumeric():
                split = basename.split("_")
                if int(split[-1]) == self.timestamp:
                    warn("Run file not written as it already exists.")
                    return
                basename = ''
                for k in range(0,len(split)-1):
                    basename += split[k] +"_"
            filename = basename + str(int(self.timestamp)) + fileext
            self.filename = filename
            self.write_run(dirpath)
            return
        svhtml = '<!DOCTYPE html><html><body>' + self.to_html() + \
                 '</body></html>'
        f = open(fullpath, 'w')
        f.write(svhtml)
        f.close()
        return



def Run(run_name):
    """
    This routine creates a GUI for initializing, starting, collecting and
    completing a run. If the run has been completed it will simply reload it
    from the local datafile.

    Parameters
    ----------
    run_name: str or Path
    This should generally be the name for the file the data will be stored in
    without a file type extension. Recommend a naming scheme that produces
    Unique filenames, such as `Trough_run_<username>_<timestamp>`. The file
    name will be `run_name.trh.run.html`.
    """
    from pathlib import Path
    from ipywidgets import Text, Dropdown, HBox, VBox, Accordion, Label, Button
    from ipywidgets import Output
    from IPython.display import display
    from IPython import get_ipython
    Trough_GUI = get_ipython().user_ns["Trough_GUI"]
    Bar_Sep = Trough_GUI.status_widgets.Bar_Sep
    Bar_Area = Trough_GUI.status_widgets.Bar_Area
    Bar_Area_per_Molec = Trough_GUI.status_widgets.Bar_Area_per_Molec
    degC = Trough_GUI.status_widgets.degC
    surf_press = Trough_GUI.status_widgets.surf_press
    zero_press = Trough_GUI.status_widgets.zero_press
    plate_circumference = Trough_GUI.status_widgets.plate_circumference
    moles_molec = Trough_GUI.status_widgets.moles_molec
    Barr_Units = Trough_GUI.command_widgets.Barr_Units
    Barr_Speed = Trough_GUI.command_widgets.Barr_Speed
    Barr_Target = Trough_GUI.command_widgets.Barr_Target
    name_to_run = {}
    completed_runs = []
    out_elem = Output() # place to target displays of widgets
    for k in Trough_GUI.runs:
        name_to_run[k.title]= k
        completed_runs.append(k.title)
    # Check if run completed, if so reload data, display and exit
    # TODO figure out how to handle ID# if loaded into different index
    datafilepath = Path.cwd()/Path(str(run_name) + '.trh.run.html') # or should it be gz
    if datafilepath.exists():
        # display the data as a live plotly plot.
        f = open(datafilepath,'r')
        html = f.read()
        f.close()
        Trough_GUI.runs.append(Trough_GUI.Collect_data.trough_run.from_html(html))
        display(Trough_GUI.runs[-1])
        return
    # Build run setup GUI
    run_title = Text(description = "Run Title",
                     value = str(run_name),
                     disabled = False)
    def changed_base_on(change):
        # update settings to match the chosen model run
        if base_on.value == 'None':
            return
        modelrun = name_to_run[str(base_on.value)]
        plate_circumference.value = str(modelrun.plate_circ)
        moles_molec.value = str(modelrun.moles)
        Barr_Units.value = str(modelrun.units)
        Barr_Speed.value = str(modelrun.speed)
        Barr_Target.value = str(modelrun.target)
        pass

    base_on = Dropdown(description = "Base on",
                       options=['None'] + completed_runs,
                       value='None')
    base_on.observe(changed_base_on, names='value')
    top_HBox = HBox([run_title, base_on])
    # Displayed status widgets
    status_HBox1 = HBox([Bar_Sep, Bar_Area, Bar_Area_per_Molec])
    status_HBox2 = HBox([surf_press, degC])
    status_VBox = VBox([status_HBox1, status_HBox2])
    status_Acc = Accordion([status_VBox])
    status_Acc.set_title(0,"Status")
    status_Acc.selected_index = 0
    # Displayed settings widgets
    settings_HBox1 = HBox([zero_press, plate_circumference, moles_molec])
    settings_HBox2 = HBox([Barr_Units, Barr_Speed])
    store_settings = Button(description="Store Settings")

    def on_store_settings(change):
        from IPython.display import HTML
        # create the run object
        id = len(Trough_GUI.runs)
        Trough_GUI.runs.append(trough_run(id,run_name+'.trh.run.html', run_title.value,
                                          Barr_Units.value,
                                          float(Barr_Target.value),
                                          float(Barr_Speed.value),
                                          float(moles_molec.value),
                                          float(plate_circumference.value)))
        # Create the collection display
        Trough_GUI.runs[-1].init_collect_control()
        out_elem.clear_output()
        with out_elem:
            display(Trough_GUI.runs[-1].livefig)
            display(Trough_GUI.runs[-1].collect_control)
            display(HTML(Trough_GUI.runs[-1].run_caption()))
        return

    store_settings.on_click(on_store_settings)
    settings_HBox3 = HBox([Label("Target", style=longdesc), Barr_Target,
                           store_settings])
    settings_VBox = VBox([settings_HBox1,settings_HBox2, settings_HBox3])
    settings_Acc = Accordion([settings_VBox])
    settings_Acc.set_title(0, "Settings")
    status_Acc.selected_index = 0
    Barr_Target.disabled = False
    with out_elem:
        display(top_HBox, status_Acc, settings_Acc)
    display(out_elem)
    return

def collect_data_updater(trough_lock, cmdsend, datarcv, cals, lastdirection,
                   run_updater, updater_running, run):
    """This is run in a separate thread and will update the figure and
    all status widgets at an interval of 2 seconds or a little longer. While
    this is running nothing else will be able to talk to the trough.

    Parameters
    ----------
    trough_lock: threading.lock
        When acquired this routine will talk to the trough. It is not
        released until the routine exits to avoid any data loss. It does
        call the status_widgets updater as often as it can while collecting
        the data.

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

    run: trough_run
        This object contains the live figure and the place to store the data.
    """
    import time
    from IPython import get_ipython
    Trough_GUI = get_ipython().user_ns["Trough_GUI"]
    # Set the shared I'm running flag.
    updater_running.value = True
    trough_lock.acquire()
    while run_updater.value:
        min_next_time = time.time() + 2.0
        cmdsend.send(['Send',''])
        waiting = True
        while waiting:
            if datarcv.poll():
                datapkg =datarcv.recv()
                # update figure and then call update_status
                if len(datapkg[1]) >= 1:
                    update_collection(datapkg, cals, lastdirection, run_updater, updater_running, run)
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
                Trough_GUI.status_widgets.update_status(update_dict, cals,
                                                        lastdirection)
                waiting = False
        if time.time()< min_next_time:
            time.sleep(min_next_time - time.time())
    # Release lock and set the shared I'm running flag to False before exiting.
    trough_lock.release()
    updater_running.value = False
    run._end_of_run()
    return

def update_collection(datapkg, cals, lastdirection, run_updater, updater_running, run):
    """Updates the graph and the data storage"""
    from pandas import DataFrame, concat
    import numpy as np
    from IPython import get_ipython
    Trough_GUI = get_ipython().user_ns["Trough_GUI"]
    plate_circumference = Trough_GUI.status_widgets.plate_circumference
    moles_molec = Trough_GUI.status_widgets.moles_molec
    # do all the calculations on the new data
    time_stamp = np.array(datapkg[0])
    pos_raw = np.array(datapkg[1])
    pos_raw_stdev = np.array(datapkg[2])
    bal_raw = np.array(datapkg[3])
    bal_raw_stdev = np.array(datapkg[4])
    temp_raw = np.array(datapkg[5])
    temp_raw_stdev = np.array(datapkg[6])
    sep_cm = None
    sep_cm_stdev = None
    if lastdirection.value < 0:
        sep_cm, sep_cm_stdev = cals.barriers_close.cal_apply(pos_raw,
                                                             pos_raw_stdev)
    else:
        sep_cm, sep_cm_stdev = cals.barriers_close.cal_apply(pos_raw,
                                                             pos_raw_stdev)
    sep_cm = np.array(sep_cm)
    sep_cm_stdev = np.array(sep_cm_stdev)
    area_sqcm = sep_cm*float(cals.barriers_open.additional_data[ \
                               "trough width (cm)"])
    area_sqcm_stdev = sep_cm_stdev*float(cals.barriers_open.additional_data[ \
                               "trough width (cm)"])


    area_per_molec_ang_sq_stdev = area_sqcm_stdev * 1e16 / moles_molec.value / 6.02214076e23
    area_per_molec_ang_sq = area_sqcm * 1e16 / moles_molec.value / 6.02214076e23
    mgrams, mgrams_err = cals.balance.cal_apply(bal_raw,bal_raw_stdev)
    mgrams = np.array(mgrams)
    mgrams_err = np.array(mgrams_err)
    surf_press_err = mgrams_err * 9.80665 / plate_circumference.value
    surf_press_data = (Trough_GUI.status_widgets.tare_pi-mgrams)*9.80665\
                      /plate_circumference.value
    tempC, tempC_stdev = cals.temperature.cal_apply(temp_raw, temp_raw_stdev)

    # add data to the dataframe
    newdata = DataFrame({"time_stamp":time_stamp,
                         "position_raw": pos_raw,
                         "postion_raw_stdev":pos_raw_stdev,
                         "balance_raw":bal_raw,
                         "balance_raw_stdev":bal_raw_stdev,
                         "temperature_raw":temp_raw,
                         "temperature_raw_stdev":temp_raw_stdev,
                         "Separation (cm)":sep_cm,
                         "Separation stdev":sep_cm_stdev,
                         "Area (cm^2)":area_sqcm,
                         "Area stdev":area_sqcm_stdev,
                         "Area per molecule (A^2)":area_per_molec_ang_sq,
                         "Area per molec stdev": area_per_molec_ang_sq_stdev,
                         "mg":mgrams,
                         "mg stdev":mgrams_err,
                         "Surface Pressure (mN/m)":surf_press_data,
                         "Surface Pressure stdev":surf_press_err,
                         "Deg C":tempC,
                         "Deg C stdev":tempC_stdev})
    if not isinstance(run.df, DataFrame):
        run.df = newdata.copy()
    else:
        run.df = concat([run.df,newdata], ignore_index=True) # This may be
        # costly. If so make the data frame only at the end.
        # TODO should I lock the dataframe or only make np.arrays until done.
    # update the graph
    x_data =[]
    y_data = run.df["Surface Pressure (mN/m)"]
    lastpos = None
    initpos = None
    if run.speed == 0:
        x_data = run.df["time_stamp"]-run.df["time_stamp"][0]
    else:
        if run.units == "cm":
            x_data = run.df["Separation (cm)"]
            lastpos = run.df["Separation (cm)"][len(run.df["Separation (cm)"])-1]
            initpos = run.df["Separation (cm)"][0]
        if run.units == "cm^2":
            x_data = run.df["Area (cm^2)"]
            lastpos = run.df["Area (cm^2)"][len(run.df["Area (cm^2)"])-1]
            initpos = run.df["Area (cm^2)"][0]
        if run.units == "Angstrom^2/molec":
            x_data = run.df["Area per molecule (A^2)"]
            lastpos = run.df["Area per molecule (A^2)"][len(run.df["Area per molecule (A^2)"])-1]
            initpos = run.df["Area per molecule (A^2)"][0]
    run.livefig.data[0].x = x_data
    run.livefig.data[0].y = y_data
    if (lastpos < initpos) and (lastpos <= run.target):
        # Stop collecting
        run_updater.value = False
    if (lastpos > initpos) and (lastpos >= run.target):
        # Stop collecting
        run_updater.value = False
    return