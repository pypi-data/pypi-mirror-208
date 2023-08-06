"""Utilities for:
* writing and reading calibration files stored in the local
user directory `.Trough/calibrations`.
* fitting calibration data to generate calibration parameters.
* converting between raw signal and user-friendly values.
"""


class Calibration:
    def __init__(self, name, units, timestamp, param, param_stdev,
                 param_inv, param_inv_stdev,
                 cal_data_x, cal_data_y, fit_type="polynomial",
                 fit_eqn_str="y = C0 + C1*x + C2*x*x + C3*x*x*x + ...",
                 fit_ceof_lbls=["C0", "C1", "C2", "C3", "C4", "C5", "C6",
                                  "C7"], additional_data = {}):
        """
        Defines a calibration of type `name`.
        Parameters
        ----------
        name: str
            calibration name.

        units: str
            string representation of the units the calibration yields.

        timestamp: float
            Unix floating point timestamp.

        param:list
            list of the numerical parameters for the fit yielding the
            calibration.

        param_stdev: list
            list of the numerical values for the estimated standard
            deviation of the parameters from the fit.
        param_inv: list
            list of the numerical values for the fit (or equation) yielding the
            inverse of the calibration (return to the raw value).
        param_inv_stdev: list
            list of the numerical values for the estimated standard deviation of
            the parameters for the inversion.
        cal_data_x: list
            x-data used for the calibration fit.

        cal_data_y: list
            y-data used for the calibration fit.

        fit_type: str
            string name for the fit type. Defaults to "polynomial"

        fit_eqn_str: str
            string representation of the fit equation. Defaults to
            "y = C0 + C1*x + C2*x*x + C3*x*x*x + ..."

        fit_ceof_lbls: list
            list of string labels for the coefficients, which should
            correlate to symbols in the fit_eqn_str. Defaults to ["C0", "C1",
            ...]. Automatically, truncated to the actual number of
            coefficients determined by the order of the polynomial.

        additional_data:dict
            a dictionary of key:value pairs where the keys are a short
            descriptive string. They can contain any additional data
            necessary for doing calculations on the data.
        """
        self.name = name
        self.units = units
        self.timestamp = timestamp
        self.param = param
        self.param_stdev = param_stdev
        self.param_inv = param_inv
        self.param_inv_stdev  = param_inv_stdev
        self.cal_data_x = cal_data_x
        self.cal_data_y = cal_data_y
        self.fit_type = fit_type
        self.fit_eqn_str = fit_eqn_str
        self.fit_coef_lbls = fit_ceof_lbls
        if self.fit_type == "polynomial" and\
                len(self.param) != len(self.fit_coef_lbls):
            self.fit_coef_lbls = self.fit_coef_lbls[0:len(self.param)]
        self.additional_data = additional_data

    @classmethod
    def cal_from_html(cls, html):
        """This takes in an html str, parses it and returns a new
        calibration.

        Parameters
        ----------
        html: str
            The html to be parsed to create the calibration object

        Returns
        -------
        calibration: calibration
            a calibration object.
        """
        from AdvancedHTMLParser import AdvancedHTMLParser as Parser

        document = Parser()
        document.parseStr(html)
        name = document.getElementById('name').text
        units = document.getElementById('units').text
        fit_type = document.getElementById('fit_type').text
        timestamp = float(document.getElementById('timestamp').text)
        fit_eqn_str = document.getElementById('fit_eqn_str').text
        coef_lbl_el = document.getElementById('coef_labels')
        coef_lbls = []
        for k in coef_lbl_el.children:
            if k.tagName == 'td':
                coef_lbls.append(k.text)
        coef_el = document.getElementById('coefficients')
        coef_val = []
        for k in coef_el.children:
            if k.tagName == 'td':
                coef_val.append(float(k.text))
        stdev_el = document.getElementById('stdev')
        coef_stdev = []
        for k in stdev_el:
            if k.tagName == 'td':
                coef_stdev.append(float(k.text))
        inv_coef_el = document.getElementById('inv_coefficients')
        inv_coef_val = []
        for k in inv_coef_el.children:
            if k.tagName == 'td':
                inv_coef_val.append(float(k.text))
        inv_stdev_el = document.getElementById('inv_stdev')
        inv_coef_stdev = []
        for k in inv_stdev_el:
            if k.tagName == 'td':
                inv_coef_stdev.append(float(k.text))
        cal_el = document.getElementById('calibration_data')
        cal_x = []
        cal_y = []
        for k in cal_el.getElementById('cal_data_x'):
            if k.tagName == 'td':
                cal_x.append(float(k.text))
        for k in cal_el.getElementById('cal_data_y'):
            if k.tagName == 'td':
                cal_y.append(float(k.text))
        cal_el = document.getElementById('additional_data')
        add_data = {}
        if cal_el:
            for k, j in zip(cal_el.getElementById('additional_data_keys'),
                cal_el.getElementById('additional_data_values')):
                key = ''
                value = None
                if k.tagName == 'td':
                    key = str(k.text)
                if j.tagName == 'td':
                    value = str(j.text)
                add_data[key] = value
        return Calibration(name, units, timestamp, coef_val, coef_stdev,
                           inv_coef_val, inv_coef_stdev,
                 cal_x, cal_y, fit_type=fit_type, fit_eqn_str=fit_eqn_str,
                           fit_ceof_lbls=coef_lbls, additional_data=add_data)

    def cal_to_html(self):
        """This routine creates an html str that would be human-readable in a
        browser detailing the calibration. This can be written to a file to
        store the calibration.

        Returns
        -------
        calib_div: str
            string containing the html detailing the calibration.
        """
        from AdvancedHTMLParser import AdvancedTag as Domel
        from datetime import datetime
        calib_div = Domel('div')
        calib_title = Domel('h3')
        calib_title.appendInnerHTML('Calibration of '+str(self.name))
        calib_div.appendChild(calib_title)

        calib_info = Domel('table')
        calib_info.setAttribute('class', 'calib_info')
        calib_info.setAttribute('id', 'calib_info')
        calib_info.setAttribute('border', '1')
        tr = Domel('tr')
        tr.appendInnerHTML('<th>Calibration of</th><th>Units returned</th>'
                           '<th>Fit function</th><th>Time</th>'
                           '<th>Timestamp</th>')
        calib_info.appendChild(tr)
        tr = Domel('tr')
        isotime = (datetime.fromtimestamp(self.timestamp)).isoformat()
        tr.appendInnerHTML('<td id = "name">'+str(self.name)+'</td>'
                           '<td id = "units">'+str(self.units)+'</td>'
                           '<td id = "fit_type">'+str(self.fit_type)+'</td>'
                           '<td id = "iso_time">'+str(isotime)+'</td>'
                           '<td id = "timestamp">'+str(self.timestamp)+'</td>')
        calib_info.appendChild(tr)
        calib_div.appendChild(calib_info)

        p = Domel('p')
        p.setAttribute('id', 'fit_eqn_str')
        p.appendInnerHTML('Fit Equation: ' + self.fit_eqn_str)
        calib_div.appendChild(p)

        parameters = Domel('table')
        parameters.setAttribute('class', 'parameters')
        parameters.setAttribute('id', 'parameters')
        parameters.setAttribute('border', '1')
        caption = Domel('caption')
        caption.appendInnerHTML('Parameters')
        parameters.appendChild(caption)
        tr = Domel('tr')
        tr.setAttribute('id', 'coef_labels')
        innerstr = '<th>Labels</th>'
        for k in self.fit_coef_lbls:
            innerstr += '<td>'+str(k) + '</td>'
        tr.appendInnerHTML(innerstr)
        parameters.appendChild(tr)
        tr = Domel('tr')
        tr.setAttribute('id', 'coefficients')
        innerstr = '<th>Coefficients</th>'
        for k in self.param:
            innerstr += '<td>'+str(k)+'</td>'
        tr.appendInnerHTML(innerstr)
        parameters.appendChild(tr)
        tr = Domel('tr')
        tr.setAttribute('id', 'stdev')
        innerstr = '<th>Standard Deviation</th>'
        for k in self.param_stdev:
            innerstr += '<td>'+str(k)+'</td>'
        tr.appendInnerHTML(innerstr)
        parameters.appendChild(tr)
        calib_div.appendChild(parameters)

        inverse = Domel('table')
        inverse.setAttribute('class', 'inverse')
        inverse.setAttribute('id', 'inverse')
        inverse.setAttribute('border', '1')
        caption = Domel('caption')
        caption.appendInnerHTML('Inverse Parameters')
        inverse.appendChild(caption)
        tr = Domel('tr')
        tr.setAttribute('id', 'coef_labels')
        innerstr = '<th>Labels</th>'
        for k in self.fit_coef_lbls:
            innerstr += '<td>'+str(k) + '</td>'
        tr.appendInnerHTML(innerstr)
        inverse.appendChild(tr)
        tr = Domel('tr')
        tr.setAttribute('id', 'inv_coefficients')
        innerstr = '<th>Coefficients</th>'
        for k in self.param_inv:
            innerstr += '<td>'+str(k)+'</td>'
        tr.appendInnerHTML(innerstr)
        inverse.appendChild(tr)
        tr = Domel('tr')
        tr.setAttribute('id', 'inv_stdev')
        innerstr = '<th>Standard Deviation</th>'
        for k in self.param_inv_stdev:
            innerstr += '<td>'+str(k)+'</td>'
        tr.appendInnerHTML(innerstr)
        inverse.appendChild(tr)
        calib_div.appendChild(inverse)

        fit_data = Domel('table')
        fit_data.setAttribute('class', 'calibration_data')
        fit_data.setAttribute('id', 'calibration_data')
        fit_data.setAttribute('border', '1')
        caption = Domel('caption')
        caption.appendInnerHTML('Calibration Data')
        fit_data.appendChild(caption)
        tr = Domel('tr')
        tr.setAttribute('id', 'cal_data_x')
        innerstr = '<th>X Calibration Data</th>'
        for k in self.cal_data_x:
            innerstr += '<td>'+str(k)+'</td>'
        tr.appendInnerHTML(innerstr)
        fit_data.appendChild(tr)
        tr = Domel('tr')
        tr.setAttribute('id', 'cal_data_y')
        innerstr = '<th>Y Calibration Data</th>'
        for k in self.cal_data_y:
            innerstr += '<td>'+str(k)+'</td>'
        tr.appendInnerHTML(innerstr)
        fit_data.appendChild(tr)
        calib_div.appendChild(fit_data)

        add_data = Domel('table')
        add_data.setAttribute('class','additonal_data')
        add_data.setAttribute('id','additional_data')
        add_data.setAttribute('border', '1')
        caption = Domel('caption')
        caption.appendInnerHTML('Additional Data')
        add_data.appendChild(caption)
        tr = Domel('tr')
        tr.setAttribute('id','additional_data_keys')
        tr2 = Domel('tr')
        tr2.setAttribute('id', 'additional_data_values')
        innerstr = ""
        innerstr2 = ""
        for k in self.additional_data.keys():
            innerstr += '<td>' + str(k) + '</td>'
            innerstr2 += '<td>' + str(self.additional_data[k]) + '</td>'
        if innerstr != "":
            tr.appendInnerHTML(innerstr)
            tr2.appendInnerHTML(innerstr2)
            add_data.appendChild(tr)
            add_data.appendChild(tr2)
            calib_div.appendChild(add_data)
        return calib_div.asHTML()

    def _cal_apply(self, data, stdev, inverse=False):
        """Apply the calibration to some data.

        Parameters
        ----------
        data: object
            either a float or iterable of floats

        stdev: object
            either a float or iterable of floats containing the uncertainty
            in the data

        inverse: keyword (default = False). Controls whether applies forward
        (raw -> calibration in units, False) or reverse (value in units ->
        raw, True) calibrations.

        Returns
        -------
        object
            the data after applying the calibration: a float or iterable of
            floats depending on what was passed to the operation.

        object
            the standard deviation of the data after applying the
            calibration: a float or iterable of floats depending on what was
            passed to the operation.
        """
        param = []
        param_stdev = []
        if inverse:
            param = self.param_inv
            param_stdev = self.param_inv_stdev
        else:
            param = self.param
            param_stdev = self.param_stdev
        cal_data = None
        cal_stdev = None
        from collections.abc import Iterable
        from round_using_error.round_using_error import numbers_rndwitherr
        if isinstance(data, Iterable):
            cal_data = []
            cal_stdev = []
            import numpy as np
            npdata = np.array(data)
            npstdev = np.array(stdev)
            # calculate the new calibrated values and errors
            npcal_data = np.zeros(len(data))
            npcal_stdev = np.zeros(len(data))
            if self.fit_type == 'polynomial':
                coef_n = 0
                for j, k in zip(param, param_stdev):
                    npcal_data += j*npdata**coef_n
                    if coef_n == 0:
                        npcal_stdev += 0
                    else:
                        npcal_stdev += (coef_n*j*npdata**(coef_n-1)*npstdev)**2 + \
                                 (npdata**coef_n*k)**2
                    coef_n += 1
                npcal_stdev = npcal_stdev**0.5
                for j, k in zip(npcal_data, npcal_stdev):
                    j, k = numbers_rndwitherr(j, k)
                    cal_data.append(j)
                    cal_stdev.append(k)
            else:
                raise NotImplementedError('Only polynomial calibration '
                                          'implemented.')
        elif isinstance(data, float):
            # calculate the new calibrated value and error.
            # each polynomial term contributes x^2*n*u(x)^2 +
            # n^2*Cn^2*x^(2n-2)*u(Cn)^2 to the square of the uncertainty.
            cal_data = 0
            cal_stdev = 0
            if self.fit_type == 'polynomial':
                coef_n = 0
                for j, k in zip(param, param_stdev):
                    cal_data += j*data**coef_n
                    if coef_n == 0:
                        cal_stdev += 0
                    else:
                        cal_stdev += (coef_n*j*data**(coef_n-1)*stdev)**2\
                                     + (data**coef_n*k)**2
                    coef_n += 1
                cal_stdev = cal_stdev**0.5
                cal_data, cal_stdev = numbers_rndwitherr(cal_data, cal_stdev)
            else:
                raise NotImplementedError('Only polynomial calibration '
                                          'implemented.')
        else:
            raise TypeError('Data must be a float or an iterable of floats.')
        return cal_data, cal_stdev

    def cal_apply(self, data, stdev):
        return self._cal_apply(data, stdev)

    def cal_inv(self, data, stdev):
        return self._cal_apply(data, stdev, inverse=True)

class Calibrations:
    def __init__(self):
        self.balance = self._create_cal('balance')
        self.barriers_open = self._create_cal('barriers_open')
        self.barriers_close = self._create_cal('barriers_close')
        self.temperature = self._create_cal('temperature')
        self.speed_open = self._create_cal('speed_open')
        self.speed_close = self._create_cal('speed_close')

    def _create_cal(self, name):
        """Utility function to that returns the latest calibration of type
        name or a default calibration if no actual calibration is found.

        Parameters
        ----------
        name: str
            string name for the calibration type (current options: 'balance',
            'barriers_open', 'barriers_close', 'speed_open',
            'speed_close' or 'temperature').
        """
        from pathlib import Path
        basepath = Path('~/.Trough/calibrations').expanduser()
        fullpath = ''
        calib = None
        if not basepath.exists():
            basepath.mkdir(parents=True)
        filelist = list(basepath.glob(name + '_*.trh.cal.html'))
        filelist.sort()
        if len(filelist) > 0:
            fullpath = filelist[-1:][0]
            f = open(fullpath, 'r')
            temphtml = f.read()
            f.close()
            calib = Calibration.cal_from_html(temphtml)
        if fullpath == '':
            # we have no calibration so will use a default.
            if name == 'balance':
                calib = Calibration('balance', 'mg', 0, [-1.875,
                                   12.5], [0, 0], [0.15, 0.08],[0, 0],[], [])
            elif name == 'barriers_open':
                calib = Calibration('barriers_open', 'cm', 0,
                                    [2.82464693, 6.69130383, 15.2853999, -21.1208151, 8.88980052],
                                    [0.00924811, 0.14164452, 0.62535698, 0.96585892, 0.47972807],
                                    [-0.55434678, 0.28071635, -0.03813755, 0.00318368, -9.0986e-05],
                                    [0.01263813, 0.00817224, 0.00180902, 1.6526e-04, 5.3290e-06], [], [],
                                    additional_data={
                                    "trough width (cm)":9.525,
                                    "skimmer correction (cm^2)":-0.5})
            elif name == 'barriers_close':
                calib = Calibration('barriers_close', 'cm', 0,
                                    [2.83251612, 8.41377796, 8.14408400, -10.8669094, 4.00818630],
                                    [0.00971215, 0.19059196, 0.94421041, 1.52692244, 0.78492412],
                                    [-0.39502418, 0.17268411, -0.01457292, 0.00106258, -2.3141e-05],
                                    [0.01786868, 0.01221316, 0.00278932, 2.6067e-04, 8.5808e-06], [], [],
                                    additional_data={
                                    "trough width (cm)": 9.525,
                                    "skimmer correction (cm^2)": -0.5})
            elif name == 'temperature':
                calib = Calibration('temperature', 'C', 0, [-1.083, 6.555], [0, 0],
                                    [0.9521, 0.14786], [], [], [])
            elif name == 'speed_open':
                calib = Calibration('speed_open', 'cm/min', 0, [0, 9.85],
                                    [0, 0], [0, 0.1015], [0, 0], [], [])
            elif name == 'speed_close':
                calib = Calibration('speed_close', 'cm/min', 0, [0.0, 6.57],
                                    [0, 0], [0, 0.1523], [0, 0], [], [])
            else:
                raise ValueError('Valid names are "balance", "barriers_open", '
                                 '"barriers_close", "temperature", "speed_open"'
                                 ', or "speed_close".')
        return calib

    def read_cal(self, name):
        """This routine reads in a calibration file. If it is the standard
        html file it uses `calibration.cal_from_html()` operation to convert
        it to a calibration.

        Parameters
        ----------
        name: str
            either the basename (current options: 'balance', 'barriers_open',
             'barriers_close', 'speed_open', 'speed_close' or
            'temperature') or a string representation of the path to the
            calibration file to be read. If one of the basenames is used
            this code will look for the most recent calibration of that type
            in the directory '~\.Trough\calibrations'.

        Returns
        -------
        Calibration
        """
        from pathlib import Path
        temppath = Path(name)
        path_parent = temppath.parent
        path_suffixes = temppath.suffixes
        fullpath = Path()
        if str(path_parent) == '.' and len(path_suffixes) == 0:
            basepath = Path('~/.Trough/calibrations').expanduser()
            filelist = list(basepath.glob(name+'_*.trh.cal.html'))
            filelist.sort()
            fullpath = filelist[-1:][0]
        else:
            fullpath = temppath
        f = open(fullpath, 'r')
        tempdoc = f.read()
        f.close()
        return Calibration.cal_from_html(tempdoc)

    def write_cal(self, dirpath, cal, **kwargs):
        """
        Writes a calibration file with the base filename `cal.name + int(
        cal.timestamp)` into the directory specified. Currently only produces
        an html file that is also human-readable. Other file formats may be
        available in the future through the use of key word arguments.

        Parameters
        ----------
        dirpath:
            pathlike object or string

        cal: Calibration
            a calibration object containing the information about the
            calibration to write to the file.

        kwargs:
            optional key word arguments for future adaptability
        """
        from pathlib import Path
        fileext = '.trh.cal.html'
        filename = str(cal.name) + '_' + str(int(cal.timestamp))+fileext
        fullpath = Path(dirpath, filename)
        svhtml = '<!DOCTYPE html><html><body>' + cal.cal_to_html() + \
                 '</body></html>'
        f = open(fullpath, 'w')
        f.write(svhtml)
        f.close()
        pass

    def poly_fit(self, data_x, data_y, order, yerr=None):
        """Does a polynomial fit of the specified order using the x and y
        values provided.

        Parameters
        ----------
        data_x: list
            of numerical x values.

        data_y: list
            of numerical y values.

        order: int
            the order of the polynomical used for fitting.

        yerr: float or iterable of float
            absolute error(s) in the y-value. Used to weight the fit. If no
            values are provided the assumption is equal weighting.

        Returns
        -------
        param: list
            of fitted parameters.

        param_stdev: list
            of estimated standard deviation in the parameters.
        """
        import numpy as np
        import lmfit as lmfit
        from round_using_error.round_using_error import numbers_rndwitherr

        # Define the fit model, initial guesses, and constraints
        fitmod = lmfit.models.PolynomialModel(degree=order)
        for k in range(0, order+1):
            fitmod.set_param_hint("c"+str(k), vary=True, value=0.0)

        # Set the weighting if errors provided
        weighting = None
        if yerr:
            from collections.abc import Iterable
            if isinstance(yerr, Iterable):
                weighting = 1/np.array(yerr)
            else:
                weighting = np.array(data_y)*0 + 1/yerr

        # Do fit
        fit = fitmod.fit(np.array(data_y), x=np.array(data_x),
                         weights=weighting, scale_covar = False,
                         nan_policy="omit")
        param = (order+1)*[None]
        param_stdev = (order+1)*[None]
        for k in fit.params.keys():
            pwr = int(str(k)[-1:])
            if pwr <= order:
                rounded = numbers_rndwitherr(fit.params[k].value,
                                             fit.params[k].stderr)
                param[pwr] = rounded[0]
                param_stdev[pwr] = rounded[1]
        return param, param_stdev
