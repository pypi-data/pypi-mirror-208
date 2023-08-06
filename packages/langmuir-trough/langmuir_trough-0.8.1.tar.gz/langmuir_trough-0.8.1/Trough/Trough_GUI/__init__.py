# Start up the trough if necessary
from Trough import Trough_Control
from IPython import get_ipython
# Allow building of documentation by not loading if not in IPython
if get_ipython():
    user_ns = get_ipython().user_ns
    user_ns["Trough_Control"] = Trough_Control
if not Trough_Control.trough_util.is_trough_initialized():
    Trough_Control.cmdsend, Trough_Control.datarcv, \
    Trough_Control.TROUGH = Trough_Control.trough_util.init_trough()

# Place to store runs
runs = []

from multiprocessing import Value
from ctypes import c_bool
#  last direction barriers moved -1 closing, 0 unknown, 1 opening
lastdirection = Value('i', 0)
run_updater = Value(c_bool, True)
updater_running = Value(c_bool, False)

from . import status_widgets, calibration_utils, Collect_data

calibrations = calibration_utils.Calibrations()

# Now we should be able to import Monitor_Calibrate
from .Monitor_Calibrate import Monitor_Setup_Trough as Controls
from .status_widgets import start_status_updater
from threading import Thread
status_update_thread = Thread(target=status_widgets.status_updater,
                              args=(Trough_Control.trough_lock,
                                    Trough_Control.cmdsend,
                                    Trough_Control.datarcv,
                                    calibrations,
                                    lastdirection,
                                    run_updater,
                                    updater_running))
status_update_thread.start()

def newCalculatedColumn():
    """
    Uses jupyter-pandas-GUI.new_pandas_column_GUI to provide a GUI expression
    composer. This method finds the datasets and launches the GUI.
    """
    import pandas as pd
    from pandas_GUI import new_pandas_column_GUI
    df_info = []
    for i in range(len(runs)):
        if isinstance(runs[i].df, pd.DataFrame):
            df_info.append([runs[i].df, 'Trough_GUI.runs['+str(i)+'].df',
                            str(runs[i].title)])
    new_pandas_column_GUI(df_info)
    pass

def newPlot():
    """
    Uses jupyter-pandas-GUI.plot_pandas_GUI to provide a GUI expression
    composer. This method finds the datasets and launches the GUI.
    """
    import pandas as pd
    from pandas_GUI import plot_pandas_GUI
    df_info = []
    for i in range(len(runs)):
        if isinstance(runs[i].df,pd.DataFrame):
            df_info.append([runs[i].df, 'Trough_GUI.runs['+str(i)+'].df',
                            str(runs[i].title)])
    plot_pandas_GUI(df_info)
    pass

def newFit():
    """
    Uses jupyter-pandas-GUI.fit_pandas_GUI to provide a GUI expression
    composer. This method finds the datasets and launches the GUI.
    """
    import pandas as pd
    from pandas_GUI import fit_pandas_GUI
    df_info = []
    for i in range(len(runs)):
        if isinstance(runs[i].df,pd.DataFrame):
            df_info.append([runs[i].df, 'Trough_GUI.runs['+str(i)+'].df',
                            str(runs[i].title)])
    fit_pandas_GUI(df_info)
    pass