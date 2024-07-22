import numpy as np
from tqdm import tqdm

from py_replay_bg.sensors import CGM, Sensors


class Replayer:
    """
    A class that orchestrates the replay process.

    ...
    Attributes
    ----------
    rbg_data: ReplayBGData
        The data to be used by ReplayBG during simulation.
    draws: array
        An array containing the model parameter realizations to be used for simulating the model.
    rbg: ReplayBG
        The instance of ReplayBG.

    Methods
    -------
    replay_scenario():
        Replays the given scenario.
    """
    def __init__(self, rbg_data, draws, n_replay, rbg, sensors):
        """
        Constructs all the necessary attributes for the Replayer object.

        Parameters
        ----------
        rbg_data: ReplayBGData
            The data to be used by ReplayBG during simulation.
        draws: array
            An array containing the model parameter realizations to be used for simulating the model.
        n_replay: int, {1000, 100, 10}
            The number of replay to be performed.
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
        self.rbg_data = rbg_data
        self.draws = draws
        self.rbg = rbg
        self.n_replay = n_replay
        self.sensors = sensors

    def replay_scenario(self):
        """
        Replays the given scenario.

        Parameters
        ----------
        None

        Returns
        -------
        glucose: dict
            A dictionary which contains the obtained glucose traces simulated via ReplayBG.
        cgm: dict
            A dictionary which contains the obtained cgm traces simulated via ReplayBG.
        insulin_bolus: dict
            A dictionary which contains the insulin boluses simulated via ReplayBG.
        correction_bolus: dict
            A dictionary which contains the correction boluses simulated via ReplayBG.
        insulin_basal: dict
            A dictionary which contains the basal insulin simulated via ReplayBG.
        cho: dict
            A dictionary which contains the meals simulated via ReplayBG.
        hypotreatments: dict
            A dictionary which contains the hypotreatments simulated via ReplayBG.
        meal_announcement: dict
            A dictionary which contains the meal announcements simulated via ReplayBG.
        vo2: dict
            A dictionary which contains the vo2 simulated via ReplayBG.

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

        n = self.draws[self.rbg.model.unknown_parameters[0]]['samples_'+str(self.n_replay)].shape[0]

        cgm = dict()
        cgm['realizations'] = np.zeros(shape=(n, self.rbg.model.tysteps))

        glucose = dict()
        glucose['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        x_end = dict()
        x_end['realizations'] = np.zeros(shape=(n, self.rbg.model.nx))
        
        insulin_bolus = dict()
        insulin_bolus['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        correction_bolus = dict()
        correction_bolus['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        insulin_basal = dict()
        insulin_basal['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        cho = dict()
        cho['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        hypotreatments = dict()
        hypotreatments['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        meal_announcement = dict()
        meal_announcement['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        vo2 = dict()
        vo2['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        new_sensors = True if self.sensors is None else False
        if new_sensors:
            self.sensors = []

        if not new_sensors:
            if not len(self.sensors) == self.n_replay:
                raise Exception("The number of provided sensors must be the same as the number of replays.")

        if self.rbg.environment.verbose:
            iterations = tqdm(range(n))
        else:
            iterations = range(0, n)

        for r in iterations:

            # set the model parameters
            for p in self.rbg.model.unknown_parameters:
                setattr(self.rbg.model.model_parameters,p, self.draws[p]['samples_'+str(self.n_replay)][r])

            if new_sensors:
                # connect a new set of sensors
                if self.rbg.environment.cgm_model == 'CGM':
                    sensors = self.__init_sensors(cgm_model=self.rbg.environment.cgm_model, model=self.rbg.model)
                    sensors.cgm.connect_new_cgm()
                    self.sensors.append(sensors)

            # TODO: add vo2
            glucose['realizations'][r], x_end['realizations'][r], cgm['realizations'][r], insulin_bolus['realizations'][r], correction_bolus['realizations'][r], \
            insulin_basal['realizations'][r], cho['realizations'][r], hypotreatments['realizations'][r], \
            meal_announcement['realizations'][r], x = self.rbg.model.simulate(rbg_data=self.rbg_data,
                                                                              modality='replay',
                                                                                         rbg=self.rbg, sensors=self.sensors[r])

            # Update the t_offset of the cgm sensors
            self.sensors[r].cgm.add_offset(self.rbg.model.t / (24 * 60))


        # Compute median CGM and glucose profiles + CI
        cgm['median'] = np.percentile(cgm['realizations'], 50, axis=0)
        cgm['ci25th'] = np.percentile(cgm['realizations'], 25, axis=0)
        cgm['ci75th'] = np.percentile(cgm['realizations'], 75, axis=0)
        cgm['ci5th'] = np.percentile(cgm['realizations'], 5, axis=0)
        cgm['ci95th'] = np.percentile(cgm['realizations'], 95, axis=0)

        glucose['median'] = np.percentile(glucose['realizations'], 50, axis=0)
        glucose['ci25th'] = np.percentile(glucose['realizations'], 25, axis=0)
        glucose['ci75th'] = np.percentile(glucose['realizations'], 75, axis=0)
        glucose['ci5th'] = np.percentile(glucose['realizations'], 5, axis=0)
        glucose['ci95th'] = np.percentile(glucose['realizations'], 95, axis=0)

        return glucose, x_end, cgm, insulin_bolus, correction_bolus, insulin_basal, cho, hypotreatments, meal_announcement, vo2, self.sensors

    def __init_sensors(self, cgm_model, model):
        """
        Utility function that initializes the sensor core object.

        Parameters
        ----------
        cgm_model: string, {'CGM','IG'}
            A string that specify the cgm model selection.
            If IG is selected, CGM measure will be the noise-free IG state at the current time.
        model: Model
            An object that represents the physiological model hyperparameters to be used by ReplayBG.

        Returns
        -------
        sensors: Sensors
            An object that represents the sensors to be used by ReplayBG.

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
        # Init the CGM sensor
        cgm = CGM(ts=model.yts, model=cgm_model)

        # return the object
        return Sensors(cgm=cgm)