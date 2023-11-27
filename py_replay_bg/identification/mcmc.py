import os

import numpy as np
import zeus

from multiprocessing import Pool

from copulas.multivariate import GaussianMultivariate
from copulas.univariate import ParametricType, Univariate

import pickle

import copy
import pandas as pd

from py_replay_bg.data import ReplayBGData

from datetime import datetime, timedelta

from tqdm import tqdm

class MCMC:
    """
    A class that orchestrates the identification process.

    ...
    Attributes 
    ----------
    model: Model
        An object that represents the physiological model hyperparameters to be used by ReplayBG.
    n_dim: int 
        Number of unknown parameters to identify.
    n_walkers: int
        Number of walkers to use.
    n_steps: int
        Number of steps to use for the main chain.
    to_sample: int
        Number of samples to generate via the copula.
    save_chains: bool
        A flag that specifies whether to save the resulting mcmc chains and copula samplers.
    callback_ncheck: int
        Number of steps to be awaited before checking the callback functions.

    Methods
    -------
    identify(rbg_data, rbg):
        Runs the identification procedure.
    """

    def __init__(self, model,
                 n_steps=10000,
                 to_sample=1000,
                 save_chains=False,
                 callback_ncheck=100):
        """
        Constructs all the necessary attributes for the MCMC object.

        Parameters
        ----------
        model: Model
            An object that represents the physiological model hyperparameters to be used by ReplayBG.
        n_steps: int, optional, default : 10000
            Number of steps to use for the main chain.
        to_sample: int, optional, default : 1000
            Number of samples to generate via the copula.
        callback_ncheck: int, optional, default : 100
            Number of steps to be awaited before checking the callback functions.

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

        # Physiological model to identify
        self.model = model

        # Number of unknown parameters to identify
        self.n_dim = len(self.model.unknown_parameters)

        # Number of walkers to use. It should be at least twice the number of dimensions.
        self.n_walkers = 2 * self.n_dim

        # Number of steps to use for the main chain
        self.n_steps = n_steps

        # Chain thin factor to use
        self.thin_factor = int(np.ceil(n_steps / 1000))

        # Number of samples to generate via the copula
        self.to_sample = to_sample

        # Save the chains?
        self.save_chains = save_chains

        # Number of steps to be awaited before checking the callback functions
        self.callback_ncheck = callback_ncheck

    def identify(self, data, rbg_data, rbg):
        """
        Runs the identification procedure.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg_data: ReplayBGData
            An object containing the data to be used during the identification procedure.
        rbg: ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        draws: dict
            A dictionary containing the chain and the samples obtained from the MCMC procedure and the copula sampling, respectively.

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

        # Set the initial positions of the walkers.
        start = self.model.start_guess + self.model.start_guess_sigma * np.random.randn(self.n_walkers, self.n_dim)
        start[start < 0] = 0

        # Create the callbacks
        cb0 = zeus.callbacks.AutocorrelationCallback(ncheck=self.callback_ncheck)
        cb1 = zeus.callbacks.SplitRCallback(ncheck=self.callback_ncheck)
        cb2 = zeus.callbacks.MinIterCallback(nmin=100)

        # Initialize and run the sampler
        pool = None
        if rbg.environment.parallelize:
            pool = Pool(processes=rbg.environment.n_processes)

        posterior_func = self.model.log_posterior_single_meal if self.model.is_single_meal else self.model.log_posterior_multi_meal
        sampler = zeus.EnsembleSampler(self.n_walkers, self.n_dim, posterior_func, args=[rbg_data],
                                       verbose=rbg.environment.verbose, pool=pool, maxsteps=10)
        sampler.run_mcmc(start, self.n_steps, callbacks=[cb0, cb1, cb2])
        sampler.summary  # Print summary diagnostics
        print('R =', cb1.estimates, flush=True)
        # Get the chain
        chain = sampler.get_chain(flat=True, thin=self.thin_factor, discard=0.5)

        # Fit the copula
        univariate = Univariate(parametric=ParametricType.NON_PARAMETRIC)
        distributions = GaussianMultivariate(distribution=univariate)
        distributions.fit(chain)

        # Get the draws to be used during replay
        draws = dict()
        for up in range(len(rbg.model.unknown_parameters)):
            draws[rbg.model.unknown_parameters[up]] = dict()
            draws[rbg.model.unknown_parameters[up]]['samples'] = np.empty(self.to_sample)
            draws[rbg.model.unknown_parameters[up]]['chain'] = chain[:, up]

        if rbg.environment.verbose:
            print('Extracting samples from copula')

        to_be_sampled = [True] * self.to_sample
        while any(to_be_sampled):

            #Get the idxs of the missing samples
            tbs = np.where(to_be_sampled)[0]

            #Get the new samples
            samples = distributions.sample(len(tbs)).to_numpy()

            #For each sample...
            for i in range(0, len(tbs)):

                #...check if it is ok. If so...
                if self.model.check_copula_extraction(samples[i]):

                    # ...flag it and fill the final vector
                    to_be_sampled[tbs[i]] = False
                    for up in range(len(rbg.model.unknown_parameters)):
                        draws[rbg.model.unknown_parameters[up]]['samples'][tbs[i]] = samples[i,up]


        # Check physiological plausibility
        draws['physiological_plausibility'] = self.__check_physiological_plausibility(draws, data, rbg)

        # save results
        identification_results = dict()
        identification_results['draws'] = draws

        # Attach also chains and copula sampler if needed
        if self.save_chains:
            identification_results['sampler'] = sampler
            identification_results['distributions'] = distributions

        with open(os.path.join(rbg.environment.replay_bg_path, 'results', 'draws',
                               'draws_' + rbg.environment.save_name + '.pkl'), 'wb') as file:
            pickle.dump(identification_results, file)

        return draws

    def __check_physiological_plausibility(self, draws, data, rbg):
        """
        Check the physiological plausibility of the identified parameters.

        Parameters
        ----------
        draws: dict
            A dictionary containing the chain and the samples obtained from the MCMC procedure and the copula sampling, respectively.
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg: ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        physiological_plausibility: dict
            A dictionary containing the results of the "plausibility" tests.

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

        if rbg.environment.verbose:
            print('Running physiological plausibility checks...')

        # Initialize the return vector
        physiological_plausibility = dict()

        physiological_plausibility['test_1'] = np.full((self.to_sample,), True)
        physiological_plausibility['test_2'] = np.full((self.to_sample,), True)
        physiological_plausibility['test_3'] = np.full((self.to_sample,), True)
        physiological_plausibility['test_4'] = np.full((self.to_sample,), True)

        rbg_fake = copy.copy(rbg)
        rbg_fake.model = copy.copy(rbg.model)
        rbg_fake.environment = copy.copy(rbg.environment)

        # Set "fake" model core variable for simulation
        rbg_fake.model.tsteps = 1440
        rbg_fake.model.tysteps = int(rbg_fake.model.tsteps / rbg_fake.model.yts)
        rbg_fake.model.glucose_model = 'IG'

        # Disable exercise
        rbg_fake.model.exercise = False

        # Set new bigger x, G, CGM
        rbg_fake.model.G = np.empty([1440, ])
        rbg_fake.model.x = np.zeros([rbg_fake.model.nx, 1440])
        rbg_fake.model.CGM = np.empty([int(rbg_fake.model.tsteps / rbg_fake.model.yts), ])

        # Set "fake" environment core variable for simulation
        rbg_fake.environment.modality = 'replay'

        # Set "fake" data
        data_fake_time = np.arange(data.t[0], data.t[0] + timedelta(minutes=rbg_fake.model.tsteps),
                                   timedelta(minutes=rbg_fake.model.yts)).astype(datetime)
        glucose = np.zeros(rbg_fake.model.tysteps)
        basal = np.zeros(rbg_fake.model.tysteps)
        bolus = np.zeros(rbg_fake.model.tysteps)
        bolusLabel = np.repeat('', rbg_fake.model.tysteps)
        cho = np.zeros(rbg_fake.model.tysteps)
        choLabel = np.repeat('', rbg_fake.model.tysteps)
        exercise = np.zeros(rbg_fake.model.tysteps)
        d = {'t': data_fake_time, 'glucose': glucose, 'cho': cho, 'cho_label': choLabel, 'bolus': bolus,
             'bolus_label': bolusLabel, 'basal': basal, 'exercise': exercise}
        data_fake = pd.DataFrame(data=d)

        # Test 1: "if no insulin is injected, BG must go above 300 mg/dl in 1000 min"
        if rbg.environment.verbose:
            iterations = tqdm(range(self.to_sample), desc='Test 1 of 4')
        else:
            iterations = range(0, self.to_sample)

        # Set simulation data
        data_fake_test_1 = copy.copy(data_fake)
        rbg_data_fake = ReplayBGData(data=data_fake_test_1, rbg=rbg_fake)

        # For each parameter set...
        for r in iterations:

            # set the model parameters
            for p in rbg_fake.model.unknown_parameters:
                setattr(rbg_fake.model.model_parameters,p,draws[p]['samples'][r])
            rbg_fake.model.model_parameters.kgri = rbg_fake.model.model_parameters.kempt

            if (rbg_fake.sensors.cgm.model == 'CGM'):
                rbg_fake.sensors.cgm.connect_new_cgm()

            g = rbg_fake.model.simulate(rbg_data=rbg_data_fake, modality='identification', rbg=None)

            # Check G
            if not np.any(g > 300):
                physiological_plausibility['test_1'][r] = False

        # Test 2: "if a bolus of 15 U is injected, BG should drop below 100 mg/dl"
        if rbg.environment.verbose:
            iterations = tqdm(range(self.to_sample), desc='Test 2 of 4')
        else:
            iterations = range(0, self.to_sample)

        # Set simulation data
        data_fake_test_2 = copy.copy(data_fake)
        data_fake_test_2.at[0, 'bolus'] = 3
        basal = np.zeros(rbg_fake.model.tysteps) + np.mean(data.basal)
        data_fake_test_2.basal = basal

        if data_fake_test_2.t.dt.hour.values[0] < 4 or data_fake_test_2.t.dt.hour.values[0] >= 17:
            data_fake_test_2.at[0, 'bolus_label'] = 'D'
        else:
            if data_fake_test_2.t.dt.hour.values[0] >= 4 and data_fake_test_2.t.dt.hour.values[0] < 11:
                data_fake_test_2.at[0, 'bolus_label'] = 'B'
            else:
                data_fake_test_2.at[0, 'bolus_label'] = 'L'

        rbg_data_fake = ReplayBGData(data=data_fake_test_2, rbg=rbg_fake)

        # For each parameter set...
        for r in iterations:

            # set the model parameters
            for p in rbg_fake.model.unknown_parameters:
                setattr(rbg_fake.model.model_parameters, p, draws[p]['samples'][r])
            rbg_fake.model.model_parameters.kgri = rbg_fake.model.model_parameters.kempt

            if (rbg_fake.sensors.cgm.model == 'CGM'):
                rbg_fake.sensors.cgm.connect_new_cgm()

            g = rbg_fake.model.simulate(rbg_data=rbg_data_fake, modality='identification', rbg=None)

            # Check G
            if not np.any(g < 100):
                physiological_plausibility['test_2'][r] = False

        # Test 3: "it exists a basal insulin value such that glucose stays between 90 and 160 mg/dl", 
        if rbg.environment.verbose:
            iterations = tqdm(range(self.to_sample), desc='Test 3 of 4')
        else:
            iterations = range(0, self.to_sample)

        # Set simulation data
        data_fake_test_3 = copy.copy(data_fake)

        max_check = 25
        l_basal = 0
        r_basal = 0.5
        basal = np.zeros(rbg_fake.model.tysteps) + (r_basal + l_basal) / 2
        data_fake_test_3.basal = basal
        rbg_data_fake = ReplayBGData(data=data_fake_test_3, rbg=rbg_fake)

        # For each parameter set...
        for r in iterations:

            # set the model parameters
            for p in rbg_fake.model.unknown_parameters:
                setattr(rbg_fake.model.model_parameters, p, draws[p]['samples'][r])
            rbg_fake.model.model_parameters.kgri = rbg_fake.model.model_parameters.kempt

            if (rbg_fake.sensors.cgm.model == 'CGM'):
                rbg_fake.sensors.cgm.connect_new_cgm()

            converged = False
            check = 0
            while check < max_check and not converged:

                # ...and simulate the scenario using the given data
                g = rbg_fake.model.simulate(rbg_data=rbg_data_fake, modality='identification', rbg=None)

                # Check G
                if np.all(np.logical_and(g >= 90, g <= 160)):
                    converged = True
                else:
                    if np.any(g < 90) and np.any(g > 160):
                        physiological_plausibility['test_3'][r] = False
                        converged = True
                    else:
                        if np.any(g < 90):
                            r_basal = data_fake_test_3.basal[0]
                        else:
                            l_basal = data_fake_test_3.basal[0]

                        basal = np.zeros(rbg_fake.model.tysteps) + (r_basal + l_basal) / 2
                        data_fake_test_3.basal = basal
                        rbg_data_fake = ReplayBGData(data=data_fake_test_3, rbg=rbg_fake)

                        check = check + 1

        # Test 4: "a variation of basal insulin of 0.01 U/h does not vary basal glucose more than 20 mg/dl"
        if rbg.environment.verbose:
            iterations = tqdm(range(self.to_sample), desc='Test 4 of 4')
        else:
            iterations = range(0, self.to_sample)

        # Set simulation data
        data_fake_test_4 = copy.copy(data_fake)
        basal = np.zeros(rbg_fake.model.tysteps) + np.mean(data.basal)
        data_fake_test_4.basal = basal
        rbg_data_fake = ReplayBGData(data=data_fake_test_4, rbg=rbg_fake)

        # For each parameter set...
        for r in iterations:

            # set the model parameters
            for p in rbg_fake.model.unknown_parameters:
                setattr(rbg_fake.model.model_parameters,p,draws[p]['samples'][r])
            rbg_fake.model.model_parameters.kgri = rbg_fake.model.model_parameters.kempt

            if (rbg_fake.sensors.cgm.model == 'CGM'):
                rbg_fake.sensors.cgm.connect_new_cgm()

            g = rbg_fake.model.simulate(rbg_data=rbg_data_fake, modality='identification', rbg=None)

            mean1 = np.mean(g[int(g.shape[0] / 2):])

            data_fake_test_4 = copy.copy(data_fake)
            basal = np.zeros(rbg_fake.model.tysteps) + np.mean(data.basal) + 0.01
            data_fake_test_4.basal = basal
            rbg_data_fake = ReplayBGData(data=data_fake_test_4, rbg=rbg_fake)

            g = rbg_fake.model.simulate(rbg_data=rbg_data_fake, modality='identification', rbg=None)

            mean2 = np.mean(g[int(g.shape[0] / 2):])

            if np.abs(mean2 - mean1) > 20:
                physiological_plausibility['test_4'][r] = False

        return physiological_plausibility
