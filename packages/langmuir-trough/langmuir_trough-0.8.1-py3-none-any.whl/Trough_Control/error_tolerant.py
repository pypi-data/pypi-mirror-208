def etol_call(obj, param):
    """

    Parameters
    ----------
    obj: the callable object
    param: a list containing the parameters in the function call

    Returns
    -------
    result: the return of the callable object

    """
    if callable(obj):
        result = None
        try:
            result = obj(*param)
        except Exception as e:
            result = etol_call(obj,param)
        return result
    else:
        raise TypeError(str(obj) + ' must be a callable object.')