import numpy as np


def ada_hypotreatments_handler(glucose, meal_announcement, meal_type, hypotreatments, bolus, basal, time, time_index, dss):
    """
    Implements the default hypotreatment strategy: "take an hypotreatment of 10 g every 15 minutes while in hypoglycemia".

    Parameters
    ----------
    glucose: array
        An array vector as long the simulation length containing all the simulated glucose concentrations (mg/dl)
        up to time_index. The values after time_index should be ignored.
    cho: array
        An array vector as long the simulation length containing all the cho intakes (g/min) up to time_index.
        It does not contain hypotreatment intakes. The values after time_index should be ignored.
    hypotreatments: array
        An array vector as long the simulation length containing all the hypotreatment intakes (g/min) up to time_index.
        If the scenario is single meal, hypotreatments will contain only the hypotreatments generated by this function
        during the simulation. If the scenario is multi-meal, hypotreatments will ALSO contain the hypotreatments already
        present in the given data that labeled as such. The values after time_index should be ignored.
    bolus: array
        An array vector as long the simulation length containing all the insulin boluses (U/min) up to time_index.
        The values after time_index should be ignored.
    basal: array
        An array vector as long the simulation length containing all the insulin basal (U/min) up to time_index.
        The values after time_index should be ignored.
    time: array
        An array vector as long the simulation length containing the time corresponding to the current step (hours) up to time_index.
        The values after time_index should be ignored.
    time_index: int
        The index corresponding to the previous step of the replay simulation.
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.

    Returns
    -------
    ht: float
        The hypotreatment to administer at time[time_index + 1].
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.
        dss is also an output since it contains hypotreatments_handler_params that beside being a
        dict that contains the parameters to pass to  this function, it also serves as memory area.
        It is possible to store values inside it and the ada_hypotreatments_handler function will be able
        to access to them in the next call of the function.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """
    ht = 0

    # If glucose is lower than 70...
    if glucose[time_index] < 70:

        # ...and if there are no CHO intakes in the last 15 minutes, then take an HT
        if time_index >= 15 and not np.any(hypotreatments[(time_index - 15):time_index]):
            ht = 15

    return ht, dss


def corrects_above_250_handler(glucose, meal_announcement, meal_type, hypotreatments, bolus, basal, time, time_index, dss):
    """
    Implements the default correction bolus strategy: "take a correction bolus of 1 U every 1 hour while above 250 mg/dl".

    Parameters
    ----------
    glucose: array
        An array vector as long the simulation length containing all the simulated glucose concentrations (mg/dl)
        up to time_index. The values after time_index should be ignored.
    cho: array
        An array vector as long the simulation length containing all the cho intakes (g/min) up to time_index.
        It does not contain hypotreatment intakes. The values after time_index should be ignored.
    hypotreatments: array
        An array vector as long the simulation length containing all the hypotreatment intakes (g/min) up to time_index.
        If the scenario is single meal, hypotreatments will contain only the hypotreatments generated by this function
        during the simulation. If the scenario is multi-meal, hypotreatments will ALSO contain the hypotreatments already
        present in the given data that labeled as such. The values after time_index should be ignored.
    bolus: array
        An array vector as long the simulation length containing all the insulin boluses (U/min) up to time_index.
        The values after time_index should be ignored.
    basal: array
        An array vector as long the simulation length containing all the insulin basal (U/min) up to time_index.
        The values after time_index should be ignored.
    time: array
        An array vector as long the simulation length containing the time corresponding to the current step (hours) up to time_index.
        The values after time_index should be ignored.
    time_index: int
        The index corresponding to the previous simulation step of the replay simulation.
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.

    Returns
    -------
    cb: float
        The correction bolus to administer at time[time_index + 1].
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.
        dss is also an output since it contains correction_boluses_handler_params that beside being a
        dict that contains the parameters to pass to  this function, it also serves as memory area.
        It is possible to store values inside it and the corrects_above_250_handler function will be able
        to access to them in the next call of the function.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """

    cb = 0

    # If glucose is higher than 250...
    if glucose[time_index] > 100:

        # ...and if there are no boluses in the last 60 minutes, then take a CB
        if time_index >= 60 and not np.any(bolus[(time_index - 60):time_index]):
            cb = 1

    return cb, dss


def default_basal_handler(glucose, meal_announcement, meal_type, hypotreatments, bolus, basal, time, time_index, dss):
    """
    Implements the default basal rate controller: "if G < 70, basal = 0; otherwise, basal = 0.01 U/min".

    Parameters
    ----------
    glucose: array
        An array vector as long the simulation length containing all the simulated glucose concentrations (mg/dl)
        up to time_index. The values after time_index should be ignored.
    meal_announcement: array
        An array vector as long the simulation length containing all the meal announcements (g) up to time_index.
        The values after time_index should be ignored.
    bolus: array
        An array vector as long the simulation length containing all the insulin boluses (U/min) up to time_index.
        The values after time_index should be ignored.
    basal: array
        An array vector as long the simulation length containing all the insulin basal (U/min) up to time_index.
        The values after time_index should be ignored.
    time: array
        An array vector as long the simulation length containing the time corresponding to the current step (hours) up to time_index.
        The values after time_index should be ignored.
    time_index: int
        The index corresponding to the previous simulation step of the replay simulation.
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.

    Returns
    -------
    b: float
        The basal insulin rate to administer at time[time_index+1].
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.
        dss is also an output since it contains basal_handler_params that beside being a
        dict that contains the parameters to pass to  this function, it also serves as memory area.
        It is possible to store values inside it and the default_basal_handler function will be able
        to access to them in the next call of the function.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """

    b = 0.01

    # If G < 70...
    if glucose[time_index] < 70:
        # ...set basal rate to 0
        b = 0

    return b, dss


def default_meal_generator_handler(glucose, meal, meal_type, meal_announcement, hypotreatments, bolus, basal, time, time_index, dss,
                                   is_single_meal):
    """
    Implements the default meal generation policy: "put a main meal of 50 g of CHO in the first instant and announce
    only 40g". If the model is single meal, the meal type will be 'M', otherwise it will be a breakfast, 'B'.

    Parameters
    ----------
    glucose: array
        An array vector as long the simulation length containing all the simulated glucose concentrations (mg/dl)
        up to time_index. The values after time_index should be ignored.
    meal_announcement: array
        An array vector as long the simulation length containing all the meal announcements (g) up to time_index.
        The values after time_index should be ignored.
    bolus: array
        An array vector as long the simulation length containing all the insulin boluses (U/min) up to time_index.
        The values after time_index should be ignored.
    basal: array
        An array vector as long the simulation length containing all the insulin basal (U/min) up to time_index.
        The values after time_index should be ignored.
    time: array
        An array vector as long the simulation length containing the time corresponding to the current step (hours) up to time_index.
        The values after time_index should be ignored.
    time_index: int
        The index corresponding to the previous simulation step of the replay simulation.
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.
    is_single_meal: bool
        A flag indicating if the handler is being used by a single meal model or not.

    Returns
    -------
    c: float
        The meal to have at time[time_index+1] (g/min).
    ma: float
        The generated meal announcement intake to administer at time(timeIndex+1) (g/min);
    type: string
        The type of the generated meal. Can be 'M' or 'O' if is_single_meal, 'B' 'L' 'D' or 'S' otherwise.
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.
        dss is also an output since it contains meal_generator_handler_params that beside being a
        dict that contains the parameters to pass to  this function, it also serves as memory area.
        It is possible to store values inside it and the default_meal_generator_handler function will be able
        to access to them in the next call of the function.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """

    # Default output values
    c = 0
    ma = 0
    type = ''

    # If this is the first time instant...
    if time_index == 0:

        # ...generate a snack meal of 50 g and announce just 40 g
        c = 50
        ma = 40

        if is_single_meal:
            type = 'M'
        else:
            type = 'B'

    return c, ma, type, dss


def standard_bolus_calculator_handler(glucose, meal_announcement, meal_type, hypotreatments, bolus, basal, time, time_index, dss):

    """
    Implements the default bolus calculator formula: B = CHO/CR + (GT-GC)/CF - IOB

    Parameters
    ----------
    glucose: array
        An array vector as long the simulation length containing all the simulated glucose concentrations (mg/dl)
        up to time_index. The values after time_index should be ignored.
    meal_announcement: array
        An array vector as long the simulation length containing all the meal announcements (g) up to time_index.
        The values after time_index should be ignored.
    bolus: array
        An array vector as long the simulation length containing all the insulin boluses (U/min) up to time_index.
        The values after time_index should be ignored.
    basal: array
        An array vector as long the simulation length containing all the insulin basal (U/min) up to time_index.
        The values after time_index should be ignored.
    time: array
        An array vector as long the simulation length containing the time corresponding to the current step (hours) up to time_index.
        The values after time_index should be ignored.
    time_index: int
        The index corresponding to the previous simulation step of the replay simulation.
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.

    Returns
    -------
    b: float
        The bolus insulin rate to administer at time[time_index+1].
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.
        dss is also an output since it contains bolus_calculator_handler_params that beside being a
        dict that contains the parameters to pass to  this function, it also serves as memory area.
        It is possible to store values inside it and the standard_bolus_calculator_handler function will be able
        to access to them in the next call of the function.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """

    b = 0

    # If a meal is announced...
    if meal_announcement[time_index] > 0:

        # compute iob
        ts = 5

        k1 = 0.0173
        k2 = 0.0116
        k3 = 6.73

        iob_6h_curve = np.zeros(shape=(360,))

        for t in range(0, 360):
            iob_6h_curve[t] = 1 - 0.75 * ((- k3 / (k2 * (k1 - k2)) * (np.exp(-k2 * t / 0.75) - 1) + k3 / (
                        k1 * (k1 - k2)) * (np.exp(-k1 * t / 0.75) - 1)) / (2.4947e4))
        iob_6h_curve = iob_6h_curve[ts::ts]

        iob = np.convolve(bolus, iob_6h_curve)
        iob = iob[bolus.shape[0] - 1]

        # ...give a bolus
        b = np.max([0, meal_announcement[time_index] / dss.CR + (glucose[time_index] - dss.GT) / dss.CF - iob])

    return b, dss