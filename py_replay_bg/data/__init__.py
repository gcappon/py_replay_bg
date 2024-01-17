import numpy as np


class ReplayBGData:
    """
    A class that encloses in an optimal way the data to be used by ReplayBG during simulation.

    ...
    Attributes
    ----------
    t_hour: np.ndarray
        An array containing the time of the day (hour).
    t_min: np.ndarray
        An array containing the time of the day (minute).
    idx: np.ndarray
        An array containing the indexes of the original data dataframe.
    glucose_idxs: np.ndarray
        An array containing the indexes where the glucose values are not nan in the original dataframe.
    glucose: np.ndarray
        An array containing the glucose measurements (mg/dl).
    bolus: np.ndarray
        An array containing the bolus data (U/min).
    basal: np.ndarray
        An array containing the basal data (U/min).
    meal: np.ndarray
        An array containing the meal data (g/min).
    meal_M: np.ndarray
        An array containing the main meal data (g/min). Present only if scenario is `single-meal`.
    meal_O: np.ndarray
        An array containing the meal data of the secondary (other) meals (g/min). Present only if scenario is
        `single-meal`.
    meal_B: np.ndarray
        An array containing the meal breakfast data (g/min). Present only if scenario is `multi-meal`.
    meal_L: np.ndarray
        An array containing the meal lunch data (g/min). Present only if scenario is `multi-meal`.
    meal_D: np.ndarray
        An array containing the meal dinner data (g/min). Present only if scenario is `multi-meal`.
    meal_S: np.ndarray
        An array containing the meal snack data (g/min). Present only if scenario is `multi-meal`.
    meal_H: np.ndarray
        An array containing the meal hypotreatment data (g/min). Present only if scenario is `multi-meal`.
    meal_announcement: np.ndarray
        An array containing the meal announcements (g/min).
    meal_type: np.ndarray
        An array containing the meal types data (str).
    bolus_label: np.ndarray
        An array containing the bolus label data (str).
    cho_label: np.ndarray
        An array containing the meal label data (str).
    exercise: np.ndarray
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
        self.__time_setup(data, rbg)

        # Save idxs
        self.idx = np.arange(0, data.shape[0])

        # Unpack glucose only if exists
        if 'glucose' in data:
            self.glucose = data.glucose.values.astype(float)
            self.glucose_idxs = np.where(np.isnan(self.glucose) == False)[0]

        # Unpack insulin
        self.__insulin_setup(data, rbg)
        self.__meal_setup(data, rbg)

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
        self.t_hour = np.zeros([rbg.model.tsteps, ])
        self.t_min = np.zeros([rbg.model.tsteps, ])

        t_m = np.array(data.t.dt.minute.values).astype(int)
        t_h = np.array(data.t.dt.hour.values).astype(int)

        # Set the bolus vector
        for t in range(data.shape[0]):
            self.t_hour[(t * rbg.model.yts):((t + 1) * rbg.model.yts)] = t_h[t]
            self.t_min[(t * rbg.model.yts):((t + 1) * rbg.model.yts)] = np.arange(t_m[t], t_m[t] + rbg.model.yts)

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
        self.basal = np.zeros([rbg.model.tsteps, ])
        self.bolus = np.zeros([rbg.model.tsteps, ])
        self.bolus_label = np.empty([rbg.model.tsteps, ], dtype=str)

        if rbg.environment.bolus_source == 'data':

            # Find the boluses
            b_idx = np.where(data.bolus)[0]

            # Set the bolus vector
            for i in range(np.size(b_idx)):
                self.bolus[
                (b_idx[i] * rbg.model.yts): ((b_idx[i] + 1) * rbg.model.yts)] = \
                data['bolus'][b_idx[i]] * rbg.model.model_parameters.to_mgkg  # mU/(kg*min)
                self.bolus_label[
                (b_idx[i] * rbg.model.yts): ((b_idx[i] + 1) * rbg.model.yts)] = \
                    data['bolus_label'][b_idx[i]]

        if rbg.environment.basal_source == 'data':

            # Set the basal vector
            for time in range(0, np.size(np.arange(0, rbg.model.tsteps, rbg.model.yts))):
                self.basal[(time * rbg.model.yts): ((time + 1) * rbg.model.yts)] = \
                data['basal'][time] * rbg.model.model_parameters.to_mgkg  # mU/(kg*min)

        if rbg.environment.basal_source == 'u2ss':
            self.basal[:] = rbg.model.model_parameters['u2ss']

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

        # Initialize the meal vector
        self.meal = np.zeros([rbg.model.tsteps, ])

        # Initialize the mealAnnouncements vector
        self.meal_announcement = np.zeros([rbg.model.tsteps, ])

        # Initialize the meal type vector
        self.meal_type = np.empty([rbg.model.tsteps, ], dtype=str)

        if rbg.environment.scenario == 'single-meal':
            self.meal_M = np.zeros([rbg.model.tsteps, ])
            self.meal_O = np.zeros([rbg.model.tsteps, ])

        if rbg.environment.scenario == 'multi-meal':
            self.meal_B = np.zeros([rbg.model.tsteps, ])
            self.meal_L = np.zeros([rbg.model.tsteps, ])
            self.meal_D = np.zeros([rbg.model.tsteps, ])
            self.meal_S = np.zeros([rbg.model.tsteps, ])
            self.meal_H = np.zeros([rbg.model.tsteps, ])

        if rbg.environment.cho_source == 'data':

            # Find the meals
            m_idx = np.where(data.cho)[0]

            # Set the main meal vector
            for i in range(np.size(m_idx)):
                self.meal[
                (m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)] = \
                data['cho'][m_idx[i]] * rbg.model.model_parameters.to_mgkg  # mg/(kg*min)
                self.meal_announcement[(m_idx[i] * rbg.model.yts)] = data['cho'][m_idx[
                    i]] * rbg.model.yts  # mg/(kg*min)

                if rbg.environment.scenario == 'single-meal':

                    # Set the first meal to the MAIN meal (the one that can be delayed by beta) using the label 'M', set the other meal inputs to others using the label 'O'
                    if i == 0:
                        self.meal_type[(m_idx[i] * rbg.model.yts): (
                            (m_idx[i] + 1) * rbg.model.yts)] = 'M'
                        self.meal_M[(m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)] = self.meal[(m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)]
                    else:
                        self.meal_type[(m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)] = 'O'
                        self.meal_O[(m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)] = self.meal[(m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)]

                if rbg.environment.scenario == 'multi-meal':
                    self.meal_type[(m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)] = data['cho_label'][m_idx[i]]

                    if data['cho_label'][m_idx[i]] == 'B':
                        self.meal_B[(m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)] = self.meal[(m_idx[i] * rbg.model.yts):((m_idx[i] + 1) * rbg.model.yts)]
                    if data['cho_label'][m_idx[i]] == 'L':
                        self.meal_L[(m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)] = self.meal[(
                            m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)]
                    if data['cho_label'][m_idx[i]] == 'D':
                        self.meal_D[(m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)] = self.meal[(
                            m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)]
                    if data['cho_label'][m_idx[i]] == 'S':
                        self.meal_S[(m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)] = self.meal[(
                            m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)]
                    if data['cho_label'][m_idx[i]] == 'H':
                        self.meal_H[(m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)] = self.meal[(
                            m_idx[i] * rbg.model.yts):(
                            (m_idx[i] + 1) * rbg.model.yts)]