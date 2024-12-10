import copy

import numpy as np
from typing import Dict

from tqdm import tqdm

from py_replay_bg.data import ReplayBGData
from py_replay_bg.environment import Environment
from py_replay_bg.model.t1d_model_single_meal import T1DModelSingleMeal
from py_replay_bg.model.t1d_model_multi_meal import T1DModelMultiMeal
from py_replay_bg.dss import DSS
from py_replay_bg.sensors import CGM, Sensors


class Replayer:
    """
    A class that orchestrates the replay process.

    ...
    Attributes
    ----------
    rbg_data: ReplayBGData
        The data to be used by ReplayBG during simulation.
    draws: dict
        An array containing the model parameter realizations to be used for simulating the model.
    n_replay: int, {1000, 100, 10}
        The number of replay to be performed.
    sensors: list[Sensors] | None
        The sensors to be used in each of the replay simulations.
    environment: Environment
        An object that represents the hyperparameters to be used by ReplayBG.
    model: T1DModelSingleMeal | T1DModelMultiMeal
        An object that represents the physiological model to be used by ReplayBG.
    dss: DSS
        An object that represents the hyperparameters of the integrated decision support system.
    twinning_method: str, {'mcmc', 'map'}
        The twinning method used to estimate the parameters.

    Methods
    -------
    replay_scenario():
        Replays the given scenario.
    """
    def __init__(self,
                 rbg_data: ReplayBGData,
                 draws: Dict,
                 u2ss: float,
                 n_replay: int,
                 sensors: list[Sensors] | None,
                 environment: Environment,
                 model: T1DModelSingleMeal | T1DModelMultiMeal,
                 dss: DSS,
                 twinning_method: str
                 ):
        """
        Constructs all the necessary attributes for the Replayer object.

        Parameters
        ----------
        rbg_data: ReplayBGData
            The data to be used by ReplayBG during simulation.
        draws: dict
            An array containing the model parameter realizations to be used for simulating the model.
        u2ss: float
            The steady state of the basal insulin infusion.
        n_replay: int, {1000, 100, 10}
            The number of Monte Carlo replays to be performed. Ignored if twinning_method is 'map'.
        sensors: list[Sensors] | None
            The sensors to be used in each of the replay simulations.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.
        dss: DSS
            An object that represents the hyperparameters of the integrated decision support system.
        twinning_method: str, {'mcmc', 'map'}
            The twinning method used to estimate the parameters.

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

        # The data and draws to be used to run the replay
        self.rbg_data = rbg_data
        self.draws = draws
        self.u2ss = u2ss

        # The twinning method used to estimate the parameters
        self.twinning_method = twinning_method

        # The number of replays (if twinning_method is 'map', it will be ignored)
        self.n_replay = n_replay

        # The list of Sensors objects
        self.sensors = sensors

        # The environment, model, and dss objects to be used during the replay
        self.environment = environment
        self.model = model
        self.dss = dss

    def replay_scenario(self) -> Dict:
        """
        Replays the given scenario.

        Parameters
        ----------
        -

        Returns
        -------
        replay_results: dict
            The replayed scenario results with fields:
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
            sensors: dict
                A dictionary which contains the sensors used during the replayed scenario.
            rbg_data: ReplayBGData
                The data to be used by ReplayBG during simulation.
            model: T1DModelSingleMeal | T1DModelMultiMeal
                An object that represents the physiological model to be used by ReplayBG.

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
        # if twinning_method is 'map' force n to 1
        if self.twinning_method == 'map':
            n = 1
        else:
            n = self.draws[self.model.unknown_parameters[0]]['samples_'+str(self.n_replay)].shape[0]

        # Initialize results
        cgm = dict()
        cgm['realizations'] = np.zeros(shape=(n, self.model.tysteps))

        glucose = dict()
        glucose['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        x_end = dict()
        x_end['realizations'] = np.zeros(shape=(n, self.model.nx))
        
        insulin_bolus = dict()
        insulin_bolus['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        correction_bolus = dict()
        correction_bolus['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        insulin_basal = dict()
        insulin_basal['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        cho = dict()
        cho['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        hypotreatments = dict()
        hypotreatments['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        meal_announcement = dict()
        meal_announcement['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        vo2 = dict()
        vo2['realizations'] = np.zeros(shape=(n, self.model.tsteps))

        new_sensors = True if self.sensors is None else False
        if new_sensors:
            self.sensors = []

        if not new_sensors:
            if self.twinning_method == 'map':
                if not len(self.sensors) == 1:
                    raise Exception("The number of provided sensors must be the same as the number of replays.")
            else:
                if not len(self.sensors) == self.n_replay:
                    raise Exception("The number of provided sensors must be the same as the number of replays.")

        if self.environment.verbose:
            iterations = tqdm(range(n))
        else:
            iterations = range(0, n)

        for r in iterations:

            if self.twinning_method == 'mcmc':
                # set the model parameters
                for p in self.model.unknown_parameters:
                    setattr(self.model.model_parameters, p, self.draws[p]['samples_'+str(self.n_replay)][r])
            else:
                # set the model parameters
                for p in self.model.unknown_parameters:
                    setattr(self.model.model_parameters, p, self.draws[p])
            self.model.model_parameters.u2ss = self.u2ss

            if new_sensors:
                # connect a new set of sensors
                sensors = self.__init_sensors(model=self.model)
                sensors.cgm.connect_new_cgm()
                self.sensors.append(sensors)

            # TODO: add vo2
            (glucose['realizations'][r], x_end['realizations'][r], cgm['realizations'][r],
             insulin_bolus['realizations'][r], correction_bolus['realizations'][r],
             insulin_basal['realizations'][r], cho['realizations'][r], hypotreatments['realizations'][r],
             meal_announcement['realizations'][r], x) = self.model.simulate(rbg_data=self.rbg_data,
                                                                            modality='replay',
                                                                            environment=self.environment,
                                                                            dss=self.dss,
                                                                            sensors=self.sensors[r])

            # Update the t_offset of the cgm sensors
            self.sensors[r].cgm.add_offset((self.model.t - self.sensors[r].cgm.connected_at) / (24 * 60))
            self.sensors[r].cgm.connected_at = 0

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

        # Pack results
        results = dict()
        results['glucose'] = glucose
        results['x_end'] = x_end
        results['cgm'] = cgm
        results['insulin_bolus'] = insulin_bolus
        results['correction_bolus'] = correction_bolus
        results['insulin_basal'] = insulin_basal
        results['cho'] = cho
        results['hypotreatments'] = hypotreatments
        results['meal_announcement'] = meal_announcement
        results['vo2'] = vo2
        results['sensors'] = copy.copy(self.sensors)
        results['rbg_data'] = copy.copy(self.rbg_data)
        results['model'] = copy.copy(self.model)

        return results

    @staticmethod
    def __init_sensors(model) -> Sensors:
        """
        Utility function that initializes the sensor core object.

        Parameters
        ----------
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.

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
        cgm = CGM(ts=model.yts)

        # return the object
        return Sensors(cgm=cgm)
