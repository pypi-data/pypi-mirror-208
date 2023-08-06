# Langmuir Trough
This software is a custom controller and GUI for the research Langmuir trough 
in the Gutow Lab at UW Oshkosh. It is written in Python and expects to run in a
Jupyter notebook environment. However, all of the parts that are not elements
of the user interface should work in a vanilla Python environment.

Hardware requirements:
Raspberry Pi compatible system with a [Pi-Plates 
DAQC2](https://pi-plates.com/daqc2r1/) data acquisition plate 
and a trough controlled by the DAQC2 plate. This software could be used with 
a trough controlled some other way by rewriting the routines in `trough_util.
py`. The GUI front end would need no rewriting to use with a different 
trough if a custom backend controlling the barriers, reading the temperature 
and Whilhelmy balance is written. The backend needs to continually monitor 
the trough and respond to the following commands: `Stop, Send, Start, 
Direction, Speed, MoveTo, MotorCal, ConstPi, DataLabels, ShutDown`.

**If you do not have compatible hardware the GUI will run with a simulated 
trough, allowing you to see how it works.**

## Usage

Once installed:

1. Turn on the power supply for the trough.
2. In a terminal navigate to the directory containing the trough software.
3. Start the virtual environment `pipenv shell`.
4. Launch Jupyter `jupyter notebook` (`jupyter lab` also works and is now 
   more stable).
5. Create a folder for the new day using the **New** menu near the top right 
   of the Jupyter browser page. Give it an appropriate name.
6. Switch to that folder by clicking on it.
7. Start a new ipython notebook using the **New** menu. Give it a
   name that describes the experiment.
8. In the first cell initialize the trough by running the command `from 
   Trough import Trough_GUI`. This will take a while to run the first time 
   it is run each day because it needs to check the movement of the barriers.
9. To control and monitor the trough or do calibrations run the command 
   `Trough_GUI.Controls(Trough_GUI.calibrations)`
10. Do not do any real runs without making sure the calibrations are correct.
11. To start data collection (a run) run the command 
    `Trough_GUI.Collect_data.Run("name_for_run")`, 
    where you replace name_for_run with the text for the name of the run (no 
    spaces).
12. Set the run conditions.
13. You can start data collection by clicking the green "Run" button.
14. If you set the speed to zero the data collection will be displayed 
    versus time and will not stop until you click the red "Stop" button.

## Installation
### *OS setup - Ubuntu on Pi*

By default in Ubuntu 20.04 for Pis the gpio and spi groups do not exist.
The i2c group does (not always).

1. Make sure that the following packages are installed `rpi.gpio-common 
python3-pigpio python3-gpiozero python3-rpi.gpio`.
2. You can avoid having to create a gpio group, by assigning users who need
    gpio access to the dialout group. Check that /dev/gpiomem is part of that 
   group and that the dialout group has rw access. If not you will need to set
    it.
3. Users also need to be members of the i2c group. If it does not exist create 
    it and then make that the group for /dev/i2c-1 with group rw permissions. 
   THIS MAY NOT BE NECESSARY. 
4. The spi group needs to be created (addgroup?).
5. Additionally the spi group needs to be given rw access to the spi devices
   at each boot. To do this create a one line rule in a file named 
   `/etc/udev/rules.d/50-spidev.rules` containing `SUBSYSTEM=="spidev", 
   GROUP="spi", MODE="0660"`. The file should have rw permission for root 
   and read permission for everyone else.
6. Make sure you have [pip](https://pip.pypa.io/en/stable/) installed for 
   python 3: `python3 -m pip --version` or `pip3 --version`. If you do not, 
   install using `apt 
   install python3-pip`.

### *Trough Software Installation*

To avoid library conflicts the software should be installed into a [virtual environment](https://docs.python.org/3/tutorial/venv.html?highlight=virtual%20environments).
Instructions for doing this using [pipenv](https://pipenv.pypa.io/en/latest/)
follow.

Log into your chosen user account:
1. Install [pipenv](https://pipenv.pypa.io/en/latest/): `pip3 install 
   --user pipenv`. You may
need to add `~/.local/bin` to your `PATH` to make `pipenv`
available in your command shell. More discussion: 
[The Hitchhiker's Guide to
Python](https://docs.python-guide.org/dev/virtualenvs/).
2. Create a directory for the virtual environment you will be installing
   into (example: `$ mkdir Trough`).
3. Navigate into the directory `$ cd Trough`.
4. Create the virtual environment and enter it `$ pipenv shell`. To get out of
   the environment you can issue the `$ exit` command on the command line.
5. While still in the shell install the latest trough software and all its
 requirements
   `$ pip install -U langmuir_trough`.
6. Still within the environment shell test
   this by starting jupyter `$ jupyter notebook`. Jupyter should launch in your 
   browser.
    1. Open a new notebook using the default (Python 3) kernel.
    2. In the first cell import the Trough_GUI: 
       `from Trough import Trough_GUI`.
        When run this cell sets things up and tries to talk to the trough.
7. If you wish, you can make this environment available to an alternate Jupyter
install as a special kernel when you are the user.
    1. Make sure you are running in your virtual environment `$ pipenv shell` 
       in the directory for  virtual environment will do that.
    2. Issue the command to add this as a kernel to your personal space: 
    `$ python -m ipykernel install --user --name=<name-you-want-for-kernel>`.
    3. More information is available in the Jupyter/Ipython documentation. 
    A simple tutorial from Nikolai Jankiev (_Parametric Thoughts_) can be
     found [here](https://janakiev.com/til/jupyter-virtual-envs/). 

## Change Log
* 0.8.1 (May 15, 2023)
  * BUG_FIX: Needed to reset cycles_on and cycles_off when speed updated.
* 0.8.0 (May 12, 2023)
  * Added capability to do very slow compressions (< 1 cm/min) by moving the 
    barriers intermittently at near their lowest continuous speed.
  * Now record datapoint time_stamps as actual_time_stamp - run_time_stamp. 
    This avoids round off errors in the html based data storage file.
  * BUG_FIXES:
    * Errors in conversion of speeds between units.
    * Make start boost voltage direction dependent.
    * Fix inconsistent sign on skimmer corrections.
    * Correct hanging of GUI updates during barrier calibrations.
    * Fix wrong target value when units were cm**2.
* 0.7.0 (Apr. 28, 2023)
  * Added Access to [pandas_GUI](https://jupyterphysscilab.github.io/jupyter_Pandas_GUI)
    tools as `Trough_GUI.newPlot()`, `Trough_GUI.newFit()` and 
    `Trough_GUI.newCalculatedColumn()`.
  * BUG_FIX: Opening a new notebook and importing Trough_GUI no longer 
    clobbers an already running notebook that is talking to the trough 
    A-to-D hardware.
  * BUG_FIX: Stopping a data collection run now makes sure the barriers are 
    stopped.
* 0.6.0 (Mar. 29, 2023)
  * Documentation updates including Gutow Lab Standard Operating Procedures 
    (SOPs).
  * Refactored everything to inside the module `Trough`.
* 0.5.2 (Mar. 16, 2023) Now works in Jupyter Lab.
  * Adjusted widget updating/clearing to work in Jupyter lab.
  * Added JupyterLab >= 3.6.1 to requirements.
* 0.5.1 (Mar. 9, 2023) 
  * Include `spidev` package in requirements. 
  * More details reported when unable to "find trough".
* 0.5.0 (Mar. 4, 2023) First version with working GUI
* 0.1.0 First pypi compatible package version.

## Known issues
* 0.5.0 - 0.8.0 The estimated error on values converted to metric units 
  based on calibration fits appears to be too pessimistic.
* Inconsistent rendering of Latex ipywidget labels with ipywidgets >= 8.0. 
  Until figured out requiring ipywidgets < 8.0.
* Runs don't label graph axes reliably for x-axis units other than cm. This 
  appears to be associated with Latex in ipywidgets as well.

## Development

### [CodeRepository](https://github.com/gutow/Langmuir_Trough.git) | [Docs](https://gutow.github.io/Langmuir_Trough)

1. For development purposes clone the GIT repository.
2. Create the virtual environment to run it in within the development 
   directory `pipenv shell`.
3. Within the shell pip install for development `pip install -e .`.

### Constructing the Documentation

1. Make sure pdoc is installed and updated in the virtual environment `pip 
   install -U pdoc`.
2. Update any `.md` files included in `_init_.py`.
   * Generally URLs should be absolute, not relative.
3. At the root level run pdoc `pdoc --logo-link
https://gutow.github.io/Langmuir_Trough/ --footer-text "Langmuir_Trough vX.X.X" 
--math -html -o docs Trough` where `X.X.X` is the version number.
4. Because of the way the document building process works the background tasks 
   will be started. **You will have to stop the document build after the 
   documentation is done building (watch the `doc` folder) with a `^C` to 
   terminate it.**

### Releasing on PyPi

Proceed only if testing of the build is successful.

1. Update packaging software `pip install -U setuptools wheel twine`
2. Double check the version number in `setup.py`.
3. Rebuild the release: `python -m setup sdist bdist_wheel`.
4. Upload it: `python -m twine upload dist/*`
5. Make sure it works by installing it in a clean virtual environment. `pip 
   install -U ...`. **Copy the actual link from pypi.org.**
   `. If it does not work, pull the release.

### Ideas/Things to do
* Make more robust by wrapping data collection in `try ...` so that it can 
  exit more gracefully and give up barrier monitoring?
* Add explanation of how to use the barrier watch deamon to prevent barrier 
  crashing if software fails.
