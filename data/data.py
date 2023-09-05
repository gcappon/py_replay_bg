import numpy as np


class ReplayBGData:
    """
    A class that encloses in an optimal way the data to be used by ReplayBG during simulation.

    ...
    Attributes
    ----------
    t: array
        An array containing the time of the day (hours).
    idx: array
        An array containing the indexes of the original data dataframe.
    glucose: array
        An array containing the glucose measurements (mg/dl).
    bolus: array
        An array containing the bolus data (U/min).
    basal: array
        An array containing the basal data (U/min).
    meal: array
        An array containing the meal data (g/min).
    meal_announcement: array
        An array containing the meal announcements (g/min).
    meal_type: array
        An array containing the meal types data (char).
    bolus_label: array
        An array containing the bolus label data (char).
    cho_label: array
        An array containing the meal label data (char).
    exercise: array
        An array containing the exercise data (-).

    Methods
    -------
    None
    """
    def __init__(self, data, rbg):
        """
        Constructs all the necessary attributes for the Visualizer object.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg: ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        None

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

        # From the time retain only the hour since is the only thing actually needed during the simulation
        self.t_hour, self.t_min = self.__time_setup(data, rbg)

        # Save idxs
        self.idx = np.arange(0, data.shape[0])

        # Unpack glucose only if exists
        if 'glucose' in data:
            self.glucose = data.glucose.values.astype(float)

        # Unpack insulin
        self.bolus, self.bolus_label, self.basal = self.__insulin_setup(data, rbg)
        self.meal, self.meal_announcement, self.meal_type = self.__meal_setup(data, rbg)

        # TODO: manage exercise
        self.exercise = []

    def __time_setup(self, data, rbg):
        """
        Unpacks the time data.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg: ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        t_hour: array
            An array containing the time data (hour).
        t_min: array
            An array containing the time data (min).

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
        t_hour = np.zeros([rbg.model.tsteps, ])
        t_min = np.zeros([rbg.model.tsteps, ])

        t_m = np.array(data.t.dt.minute.values).astype(int)
        t_h = np.array(data.t.dt.hour.values).astype(int)

        # Set the bolus vector
        for t in range(data.shape[0]):
            t_hour[ int( t * rbg.model.yts / rbg.model.ts ) : int( (t + 1) * rbg.model.yts / rbg.model.ts) ] = t_h[t]
            t_min[int(t * rbg.model.yts / rbg.model.ts): int((t + 1) * rbg.model.yts / rbg.model.ts)] = np.arange(t_m[t],t_m[t] + rbg.model.yts)

        return t_hour, t_min

    def __insulin_setup(self, data, rbg):
        """
        Unpacks the insulin data.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg: ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        bolus: array
            An array containing the bolus data (U/min).
        basal: array
            An array containing the basal data (U/min).

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
        basal = np.zeros([rbg.model.tsteps, ])
        bolus = np.zeros([rbg.model.tsteps, ])
        bolus_label = np.empty([rbg.model.tsteps, ], dtype=str)

        if rbg.environment.bolus_source == 'data':

            # Find the boluses
            b_idx = np.where(data.bolus)[0]

            # Set the bolus vector
            for i in range(np.size(b_idx)):
                bolus[
                int(b_idx[i] * rbg.model.yts / rbg.model.ts): int((b_idx[i] + 1) * rbg.model.yts / rbg.model.ts)] = \
                data['bolus'][b_idx[i]] * 1000 / rbg.model.model_parameters['BW']  # mU/(kg*min)
                bolus_label[
                int(b_idx[i] * rbg.model.yts / rbg.model.ts): int((b_idx[i] + 1) * rbg.model.yts / rbg.model.ts)] = \
                    data['bolus_label'][b_idx[i]]

        if rbg.environment.basal_source == 'data':

            # Set the basal vector
            for time in range(0, np.size(np.arange(0, rbg.model.tsteps, rbg.model.yts))):
                basal[int(time * rbg.model.yts / rbg.model.ts): int((time + 1) * rbg.model.yts / rbg.model.ts)] = \
                data['basal'][time] * 1000 / rbg.model.model_parameters['BW']  # mU/(kg*min)

        if rbg.environment.basal_source == 'u2ss':
            basal[:] = rbg.model.model_parameters['u2ss']

        return bolus, bolus_label, basal

    def __meal_setup(self, data, rbg):
        """
        Unpacks the meal data.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg: ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        meal: array
            An array containing the meal data (g/min).
        meal_announcement: array
            An array containing the meal announcements (g/min).
        meal_type: array
            An array containing the meal types data (char).

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

        # Initialize the meal vector
        meal = np.zeros([rbg.model.tsteps, ])

        # Initialize the mealAnnouncements vector
        meal_announcement = np.zeros([rbg.model.tsteps, ])

        # Initialize the meal type vector
        meal_type = np.empty([rbg.model.tsteps, ], dtype=str)

        if rbg.environment.cho_source == 'data':

            # Find the meals
            m_idx = np.where(data.cho)[0]

            # Set the meal vector
            for i in range(np.size(m_idx)):
                meal[
                int(m_idx[i] * rbg.model.yts / rbg.model.ts): int((m_idx[i] + 1) * rbg.model.yts / rbg.model.ts)] = \
                data['cho'][m_idx[i]] * 1000 / rbg.model.model_parameters['BW']  # mg/(kg*min)
                meal_announcement[int(m_idx[i] * rbg.model.yts / rbg.model.ts)] = data['cho'][m_idx[
                    i]] * rbg.model.yts / rbg.model.ts  # mg/(kg*min)

                if rbg.environment.scenario == 'single-meal':

                    # Set the first meal to the MAIN meal (the one that can be delayed by beta) using the label 'M', set the other meal inputs to others using the label 'O'
                    if i == 0:
                        meal_type[int(m_idx[i] * rbg.model.yts / rbg.model.ts): int(
                            (m_idx[i] + 1) * rbg.model.yts / rbg.model.ts)] = 'M'
                    else:
                        meal_type[int(m_idx[i] * rbg.model.yts / rbg.model.ts): int(
                            (m_idx[i] + 1) * rbg.model.yts / rbg.model.ts)] = 'O'

                if rbg.environment.scenario == 'multi-meal':
                    meal_type[int(m_idx[i] * rbg.model.yts / rbg.model.ts): int(
                        (m_idx[i] + 1) * rbg.model.yts / rbg.model.ts)] = data['cho_label'][m_idx[i]]

        return meal, meal_announcement, meal_type
