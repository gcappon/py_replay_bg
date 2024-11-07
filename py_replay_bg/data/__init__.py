import numpy as np
import pandas as pd

from datetime import datetime, timedelta

from py_replay_bg.environment import Environment


class ReplayBGData:
    """
    A class that encloses in an optimal way the data to be used by ReplayBG during simulation.

    ...
    Attributes
    ----------
    t_data: np.ndarray
        An array containing the time data contained in the given dataframe.
    t_hour: np.ndarray
        An array containing the time of the day (hour).
    t_min: np.ndarray
        An array containing the time of the day (minute).
    idx: np.ndarray
        An array containing the indexes of the original data dataframe.
    glucose_idxs: np.ndarray
        An array containing the indexes where the glucose values are not nan in the original dataframe. Empty if glucose
        is not present in the given dataframe.
    glucose: np.ndarray
        An array containing the glucose measurements (mg/dl). Empty if glucose is not present in the given dataframe.
    bolus_data: np.ndarray
        An array containing the bolus data contained in the given dataframe (U/min). Empty if bolus_source is not
        'data'.
    bolus: np.ndarray
        An array containing the bolus data (U/min).
    basal_data: np.ndarray
        An array containing the basal data contained in the given dataframe (U/min). Empty if basal_source is not
        'data'.
    basal: np.ndarray
        An array containing the basal data (U/min).
    meal_data: np.ndarray
        An array containing the meal data contained in the given dataframe (g/min). Empty if cho_source is not
        'data'.
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
    exercise: np.ndarray
        An array containing the exercise data (-).
    bolus_source : str, {'data', or 'dss'}
            A string defining whether to use, during replay, the insulin bolus data contained in the 'data' timetable
            (if 'data'), or the boluses generated by the bolus calculator implemented via the provided
            'bolusCalculatorHandler' function.
    basal_source : str, {'data', 'u2ss', or 'dss'}
        A string defining whether to use, during replay, the insulin basal data contained in the 'data' timetable
        (if 'data'), or the basal generated by the controller implemented via the provided 'basalControllerHandler'
        function (if 'dss'), or fixed to the average basal rate used during identification (if 'u2ss').
    cho_source : str, {'data', 'generated'}
        A string defining whether to use, during replay, the CHO data contained in the 'data' timetable (if 'data'),
        or the CHO generated by the meal generator implemented via the provided 'mealGeneratorHandler' function.

    Methods
    -------
    None
    """

    def __init__(self,
                 data: pd.DataFrame,
                 model,
                 environment: Environment,
                 bolus_source: str = 'data',
                 basal_source: str = 'data',
                 cho_source: str = 'data'):
        """
        Constructs all the necessary attributes for the Visualizer object.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.
        bolus_source : str, {'data', or 'dss'}, optional, default : 'data'
            A string defining whether to use, during replay, the insulin bolus data contained in the 'data' timetable
            (if 'data'), or the boluses generated by the bolus calculator implemented via the provided
            'bolusCalculatorHandler' function.
        basal_source : str, {'data', 'u2ss', or 'dss'}, optional, default : 'data'
            A string defining whether to use, during replay, the insulin basal data contained in the 'data' timetable
            (if 'data'), or the basal generated by the controller implemented via the provided 'basalControllerHandler'
            function (if 'dss'), or fixed to the average basal rate used during identification (if 'u2ss').
        cho_source : str, {'data', 'generated'}, optional, default : 'data'
            A string defining whether to use, during replay, the CHO data contained in the 'data' timetable (if 'data'),
            or the CHO generated by the meal generator implemented via the provided 'mealGeneratorHandler' function.

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
        # Set the data sources
        self.basal_source = basal_source
        self.bolus_source = bolus_source
        self.cho_source = cho_source

        # From the time retain only the hour since is the only thing actually needed during the simulation
        self.__time_setup(data, model, environment)

        # Save idxs
        self.idx = np.arange(0, data.shape[0])

        # Set glucose from given data
        self.glucose = []
        self.glucose_idxs = []
        # Unpack glucose only if exists
        if 'glucose' in data:
            self.glucose = data.glucose.values.astype(float)
            self.glucose_idxs = np.where(~np.isnan(self.glucose))[0]

        # Unpack insulin
        self.__insulin_setup(data, model, environment)
        self.__meal_setup(data, model, environment)

        # TODO: manage exercise
        self.exercise = []

    def __time_setup(self,
                     data: pd.DataFrame,
                     model,
                     environment: Environment
                     ) -> None:
        """
        Unpacks the time data.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.

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
        self.t_data = data['t'].to_numpy()
        self.t_hour = np.zeros([model.tsteps, ])
        self.t_min = np.zeros([model.tsteps, ])

        t_m = np.array(data.t.dt.minute.values).astype(int)
        t_h = np.array(data.t.dt.hour.values).astype(int)

        # Set the bolus vector
        for t in range(data.shape[0]):
            self.t_hour[(t * environment.yts):((t + 1) * environment.yts)] = t_h[t]
            self.t_min[(t * environment.yts):((t + 1) * environment.yts)] = np.arange(t_m[t], t_m[t] + environment.yts)

    def __insulin_setup(self,
                        data: pd.DataFrame,
                        model,
                        environment: Environment
                        ) -> None:
        """
        Unpacks the insulin data.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.

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
        self.basal = np.zeros([model.tsteps, ])
        self.bolus = np.zeros([model.tsteps, ])
        self.bolus_label = np.empty([model.tsteps, ], dtype=str)

        self.bolus_data = []
        self.basal_data = []
        if self.bolus_source == 'data':

            self.bolus_data = data.bolus.values

            # Find the boluses
            b_idx = np.where(data.bolus)[0]

            # Set the bolus vector
            for i in range(np.size(b_idx)):
                self.bolus[(b_idx[i] * environment.yts): ((b_idx[i] + 1) * environment.yts)] = data['bolus'][b_idx[i]] * model.model_parameters.to_mgkg  # mU/(kg*min)
                self.bolus_label[(b_idx[i] * environment.yts): ((b_idx[i] + 1) * environment.yts)] = data['bolus_label'][b_idx[i]]

        if self.basal_source == 'data':

            self.basal_data = data.basal.values

            # Set the basal vector
            for time in range(0, np.size(np.arange(0, model.tsteps, environment.yts))):
                self.basal[(time * environment.yts): ((time + 1) * environment.yts)] = \
                    data['basal'][time] * model.model_parameters.to_mgkg  # mU/(kg*min)

        if self.basal_source == 'u2ss':
            self.basal[:] = model.model_parameters['u2ss']

    def __meal_setup(self,
                     data: pd.DataFrame,
                     model,
                     environment: Environment
                     ) -> None:
        """
        Unpacks the meal data.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.

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
        self.meal = np.zeros([model.tsteps, ])

        # Initialize the mealAnnouncements vector
        self.meal_announcement = np.zeros([model.tsteps, ])

        # Initialize the meal type vector
        self.meal_type = np.empty([model.tsteps, ], dtype=str)

        if environment.scenario == 'single-meal':
            self.meal_M = np.zeros([model.tsteps, ])
            self.meal_O = np.zeros([model.tsteps, ])

        if environment.scenario == 'multi-meal':
            self.meal_B = np.zeros([model.tsteps, ])
            self.meal_L = np.zeros([model.tsteps, ])
            self.meal_D = np.zeros([model.tsteps, ])
            self.meal_S = np.zeros([model.tsteps, ])
            self.meal_H = np.zeros([model.tsteps, ])

        self.meal_data = []
        if self.cho_source == 'data':

            self.meal_data = data.cho.values

            # Find the meals
            m_idx = np.where(data.cho)[0]

            # Set the main meal vector
            for i in range(np.size(m_idx)):
                self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = data['cho'][m_idx[i]] * model.model_parameters.to_mgkg  # mg/(kg*min)
                self.meal_announcement[(m_idx[i] * environment.yts)] = data['cho'][m_idx[i]] * environment.yts  # mg/(kg*min)

                if environment.scenario == 'single-meal':

                    # Set the first meal to the MAIN meal (the one that can be delayed by beta) using the label 'M',
                    # set the other meal inputs to others using the label 'O'
                    if i == 0:
                        self.meal_type[(m_idx[i] * environment.yts): ((m_idx[i] + 1) * environment.yts)] = 'M'
                        self.meal_M[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)]
                    else:
                        self.meal_type[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = 'O'
                        self.meal_O[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)]

                if environment.scenario == 'multi-meal':
                    self.meal_type[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = data['cho_label'][m_idx[i]]

                    if data['cho_label'][m_idx[i]] == 'B':
                        self.meal_B[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)]
                    if data['cho_label'][m_idx[i]] == 'L':
                        self.meal_L[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)]
                    if data['cho_label'][m_idx[i]] == 'D':
                        self.meal_D[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)]
                    if data['cho_label'][m_idx[i]] == 'S':
                        self.meal_S[(m_idx[i] * environment.yts):(
                                (m_idx[i] + 1) * environment.yts)] = self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)]
                    if data['cho_label'][m_idx[i]] == 'H':
                        self.meal_H[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)] = self.meal[(m_idx[i] * environment.yts):((m_idx[i] + 1) * environment.yts)]
