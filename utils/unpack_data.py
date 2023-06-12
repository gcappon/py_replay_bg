import numpy as np

def unpack_data(self,data, rbg):
    """
    Unpacks the data pandas Dataframe to a numpy.

    Parameters
    ----------
    data : pd.DataFrame
        Pandas dataframe which contains the data to be used by the tool

    Returns
    -------
    model : dict
        A dictionary that contains general parameters of the physiological model

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

    #From the time retain only the hour since is the only thing actually needed during the simulation
    t = np.array(data.t.dt.hour.values).astype(int)

    #Unpack glucose only if exists
    if 'glucose' in data:
        glucose = data.glucose.values.astype(float)

    #Unpack insulin
    bolus, basal = insulin_setup(data, rbg)
    cho = []

    #TODO: manage the multimeal and exercise
    bolus_label = []
    cho_label = []
    exercise = []


    return t, glucose, bolus, basal, cho, bolus_label, cho_label, exercise

def insulin_setup(data, rbg):
    pass