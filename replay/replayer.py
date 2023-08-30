import numpy as np
from tqdm import tqdm


class Replayer:

    def __init__(self, rbg_data, draws, rbg):
        self.rbg_data = rbg_data
        self.draws = draws
        self.rbg = rbg

    def replay_scenario(self):

        n = self.draws[self.rbg.model.unknown_parameters[0]]['samples'].shape[0]

        cgm = dict()
        cgm['realizations'] = np.zeros(shape=(n, self.rbg.model.tysteps))

        glucose = dict()
        glucose['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        insulin_bolus = dict()
        insulin_bolus['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        correction_bolus = dict()
        correction_bolus['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        insulin_basal = dict()
        insulin_basal['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

        CHO = dict()
        CHO['realizations'] = np.zeros(shape=(n, self.rbg.model.tsteps))

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
                self.rbg.model.model_parameters[p] = self.draws[p]['samples'][r]

            # connect a new CGM sensor
            if self.rbg.sensors.cgm.model == 'CGM':
                self.rbg.sensors.cgm.connect_new_cgm()

            # TODO: add vo2
            glucose['realizations'][r], cgm['realizations'][r], insulin_bolus['realizations'][r], correction_bolus['realizations'][r], \
            insulin_basal['realizations'][r], CHO['realizations'][r], hypotreatments['realizations'][r], \
            meal_announcement['realizations'][r], x = self.rbg.model.simulate_for_replay(rbg_data=self.rbg_data,
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

        return glucose, cgm, insulin_bolus, correction_bolus, insulin_basal, CHO, hypotreatments, meal_announcement, vo2
