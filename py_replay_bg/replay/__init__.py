import numpy as np
from tqdm import tqdm


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
    def __init__(self, rbg_data, draws, n_replay, rbg):
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
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg: ReplayBG
            The instance of ReplayBG.

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

        if self.rbg.environment.verbose:
            iterations = tqdm(range(n))
        else:
            iterations = range(0, n)

        for r in iterations:

            # set the model parameters
            for p in self.rbg.model.unknown_parameters:
                setattr(self.rbg.model.model_parameters,p, self.draws[p]['samples_'+str(self.n_replay)][r])

            # connect a new CGM sensor
            if self.rbg.sensors.cgm.model == 'CGM':
                self.rbg.sensors.cgm.connect_new_cgm()

            # TODO: add vo2
            glucose['realizations'][r], x_end['realizations'][r], cgm['realizations'][r], insulin_bolus['realizations'][r], correction_bolus['realizations'][r], \
            insulin_basal['realizations'][r], cho['realizations'][r], hypotreatments['realizations'][r], \
            meal_announcement['realizations'][r], x = self.rbg.model.simulate(rbg_data=self.rbg_data,
                                                                              modality='replay',
                                                                                         rbg=self.rbg)

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

        return glucose, x_end, cgm, insulin_bolus, correction_bolus, insulin_basal, cho, hypotreatments, meal_announcement, vo2
