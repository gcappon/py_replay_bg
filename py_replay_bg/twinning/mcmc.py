import os

import matplotlib.pyplot as plt
from matplotlib import pylab

from typing import Dict

import numpy as np
import emcee

from multiprocessing import Pool

import pickle
from tqdm import tqdm
import copy

from py_replay_bg.data import ReplayBGData
from py_replay_bg.model.t1d_model_single_meal import T1DModelSingleMeal
from py_replay_bg.model.t1d_model_multi_meal import T1DModelMultiMeal

from py_replay_bg.environment import Environment


class MCMC:
    """
    A class that orchestrates the twinning process.

    ...
    Attributes 
    ----------
    n_steps: int
        Number of steps to use for the main chain.
    save_chains: bool
        A flag that specifies whether to save the resulting mcmc chains and copula samplers.
    callback_ncheck: int
        Number of steps to be awaited before checking the callback functions.
    n_burn_in: int
        Number of burn_in steps.
    parallelize: bool
        Whether to parallelize the twinning procedure.
    n_processes: int
        Number of parallel processes to run.

    Methods
    -------
    twin(rbg_data, model, save_name, environment)
        Runs the twinning procedure.
    """

    def __init__(self,
                 n_steps: int = 50000,
                 save_chains: bool = False,
                 callback_ncheck: int = 1000,
                 n_burn_in: int = 10000,
                 parallelize: bool = True,
                 n_processes: None | int = None
                 ):
        """
        Constructs all the necessary attributes for the MCMC object.

        Parameters
        ----------
        n_steps: int, optional, default : 50000
            Number of steps to use for the main chain.
        save_chains: bool, optional, default : False
            A flag that specifies whether to save the resulting mcmc chains and copula samplers.
        callback_ncheck: int, optional, default : 1000
            Number of steps to be awaited before checking the callback functions.
        n_burn_in: int, optional, default : 10000
            Number of burn_in steps.
        parallelize: bool
            Whether to parallelize the twinning procedure.
        n_processes: int
            Number of parallel processes to run.

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

        # Number of steps to use for the main chain
        self.n_steps = n_steps

        # Save the chains?
        self.save_chains = save_chains

        # Number of steps to be awaited before checking the callback functions
        self.callback_ncheck = callback_ncheck

        # Number of burn_in steps
        self.n_burn_in = n_burn_in

        # Parallelization options
        self.parallelize = parallelize
        self.n_processes = n_processes

    def twin(self,
             rbg_data: ReplayBGData,
             model: T1DModelSingleMeal | T1DModelMultiMeal,
             save_name: str,
             environment: Environment) -> Dict:
        """
        Runs the twinning procedure.

        Parameters
        ----------
        rbg_data: ReplayBGData
            An object containing the data to be used during the twinning procedure.
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.
        save_name : str
            A string used to label, thus identify, each output file and result.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.

        Returns
        -------
        draws: dict
            A dictionary containing the chain and the samples obtained from the MCMC procedure and the copula
            sampling, respectively.

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
        # Number of unknown parameters to twin
        n_dim = len(model.unknown_parameters)

        # Number of walkers to use. It should be at least twice the number of dimensions (here 50 times).
        n_walkers = 50 * n_dim

        # Set the initial positions of the walkers.
        start = model.start_guess + model.start_guess_sigma * np.random.randn(n_walkers, n_dim)
        start[start < 0] = 0

        # Initialize the sampler
        pool = None
        if self.parallelize:
            pool = Pool(processes=self.n_processes)

        log_posterior_func = model.log_posterior_extended if model.extended else model.log_posterior

        sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_posterior_func,
                                        moves=[
                                            (emcee.moves.DEMove(sigma=1.0e-3), 0.2),
                                            (emcee.moves.DESnookerMove(gammas=0.1), 0.8)
                                        ],
                                        pool=pool,
                                        args=[rbg_data])

        # Run the burn-in chain
        sampler, state = self.__run_chain(
            sampler=sampler,
            is_burn_in=True,
            state=start,
            rbg_data=rbg_data,
            environment=environment,
            model=model
        )

        # Run production chain
        sampler, state = self.__run_chain(
            sampler=sampler,
            is_burn_in=False,
            state=state,
            rbg_data=rbg_data,
            environment=environment,
            model=model
        )

        # Extract the chain
        tau = sampler.get_autocorr_time(quiet=True)
        burnin = int(self.n_steps * 0.5)
        thin = int(0.5 * np.min(tau))
        chain = sampler.get_chain(discard=burnin, flat=True, thin=thin)

        # Get the draws to be used during replay
        draws = dict()
        for up in range(len(model.unknown_parameters)):
            draws[model.unknown_parameters[up]] = dict()
            draws[model.unknown_parameters[up]]['samples_1000'] = np.empty(1000)
            if self.save_chains:
                draws[model.unknown_parameters[up]]['chain'] = chain[:, up]

        # Set the number of desired samples
        to_sample = 1000

        # Extract samples from the chain (i.e., the posterior distribution)
        if environment.verbose:
            print('Extracting samples from posterior - ' + str(to_sample) + ' realizations')

        to_be_sampled = [True] * to_sample
        while any(to_be_sampled):

            # Get the idxs of the missing samples
            tbs = np.where(to_be_sampled)[0]

            # Get the new samples
            draw = np.floor(np.random.uniform(0, len(chain), size=len(tbs))).astype(int)
            samples = chain[draw]

            # For each sample...
            for i in range(0, len(tbs)):

                # ...check if it is ok. If so...
                if model.check_realization(samples[i]):

                    # ...flag it and fill the final vector
                    to_be_sampled[tbs[i]] = False
                    for up in range(len(model.unknown_parameters)):
                        draws[model.unknown_parameters[up]]['samples_'+str(to_sample)][tbs[i]] = samples[i, up]

        # Subsample realizations
        draws = self.__subsample(draws=draws, rbg_data=rbg_data, environment=environment, model=model)

        # TODO: Check physiological plausibility

        # Clean-up draws from "extended" parameters
        if model.extended:
            if 'SI_B2' in draws:
                del draws['SI_B2']
            if 'kabs_B2' in draws:
                del draws['kabs_B2']
            if 'beta_B2' in draws:
                del draws['beta_B2']
            if 'kabs_L2' in draws:
                del draws['kabs_L2']
            if 'beta_L2' in draws:
                del draws['beta_L2']
            if 'kabs_S2' in draws:
                del draws['kabs_S2']
            if 'beta_S2' in draws:
                del draws['beta_S2']

        # Save results
        twinning_results = dict()
        twinning_results['draws'] = draws
        twinning_results['u2ss'] = model.model_parameters.u2ss

        # Attach also chain if needed
        if self.save_chains:
            twinning_results['sampler'] = sampler
            twinning_results['tau'] = tau
            twinning_results['thin'] = thin
            twinning_results['burnin'] = burnin

        with open(os.path.join(environment.replay_bg_path, 'results', 'mcmc',
                               'mcmc_' + save_name + '.pkl'), 'wb') as file:
            pickle.dump(twinning_results, file)

        return draws

    def __run_chain(self, sampler, is_burn_in, state, rbg_data, environment, model):
        """
        Utility function to run MCMC sampling
        """

        # If is the burn-in run...
        if is_burn_in:
            message = " - Running burn-in chain..."
            n = self.n_burn_in

        # If is the production run...
        else:
            message = " - Running production chain..."
            n = self.n_steps

            # Also remember to reset the sampler
            sampler.reset()

        if environment.plot_mode:
            pbar = None
            first = True

            if environment.verbose:
                print(message)
                pbar = tqdm(total=n)

            for _ in range(int(np.ceil(n / self.callback_ncheck))):

                if first:
                    state = sampler.run_mcmc(initial_state=state,
                                             nsteps=self.callback_ncheck,
                                             skip_initial_state_check=True)
                    first = False

                else:
                    state = sampler.run_mcmc(initial_state=None,
                                             nsteps=self.callback_ncheck,
                                             skip_initial_state_check=True)

                plot_progress(sampler, environment, model, rbg_data)

                if environment.verbose:
                    pbar.update(self.callback_ncheck)

            pylab.close()

            if environment.verbose:
                pbar.close()

        else:

            if environment.verbose:
                print(message)

            state = sampler.run_mcmc(state, n, progress=environment.verbose, skip_initial_state_check=True)

        if environment.verbose:

            acceptance_rate = np.mean(sampler.acceptance_fraction)
            print(
                "    - Mean acceptance fraction: {0:.3f}".format(
                    acceptance_rate
                )
            )
            print(
                "    - Mean auto correlation time: {0:.3f} steps".format(
                    np.mean(sampler.get_autocorr_time(quiet=True))
                )
            )

        # Return results
        return sampler, state

    @staticmethod
    def __subsample(draws: Dict,
                    rbg_data: ReplayBGData,
                    environment: Environment,
                    model: T1DModelSingleMeal | T1DModelMultiMeal) -> Dict:
        """
        Sub-samples n parameters realizations starting from the original 1000 draws.

        Parameters
        ----------
        draws: dict
            A dictionary containing the chain and the samples obtained from the MCMC procedure and the copula sampling,
            respectively.
        rbg_data: ReplayBGData
            An object containing the data to be used during the twinning procedure.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        model: T1DModelSingleMeal | T1DModelMultiMeal
            An object that represents the physiological model to be used by ReplayBG.

        Returns
        -------
        draws: dict
            A (sub sampled) dictionary containing the chain and the samples obtained from the MCMC procedure and
            the copula sampling, respectively.

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
        if environment.verbose:
            print('Subsampling realizations...')

        for up in range(len(model.unknown_parameters)):
            draws[model.unknown_parameters[up]]['samples_'+str(100)] = np.empty(100)
            draws[model.unknown_parameters[up]]['samples_' + str(10)] = np.empty(10)
            draws[model.unknown_parameters[up]]['samples_' + str(1)] = np.empty(1)

        model = copy.copy(model)
        environment = copy.copy(environment)
        rbg_data = copy.copy(rbg_data)

        # Set "fake" environment core variable for simulation
        environment.modality = 'replay'

        # Test 1: "if no insulin is injected, BG must go above 300 mg/dl in 1000 min"
        iterations = range(0, 1000)

        # Set simulation data
        # rbg_data = ReplayBGData(data=data, rbg=rbg_fake)

        glucose = dict()
        glucose['realizations'] = np.zeros(shape=(1000, model.tsteps))

        # For each parameter set...
        for r in iterations:

            # set the model parameters
            for p in model.unknown_parameters:
                setattr(model.model_parameters, p, draws[p]['samples_1000'][r])
            model.model_parameters.kgri = model.model_parameters.kempt

            glucose['realizations'][r] = model.simulate(rbg_data=rbg_data,
                                                        modality='twinning',
                                                        environment=environment,
                                                        dss=None)

        glucose_prc = dict()
        for p in range(0, 100):
            glucose_prc[p] = np.percentile(glucose['realizations'], p+1, axis=0)

        distances = np.empty(1000)
        for p in range(0, 100):
            for r in range(0, 1000):
                distances[r] = np.sqrt(np.mean((glucose_prc[p] - glucose['realizations'][r]) ** 2))
            idx = np.argmin(distances)

            # 100 realizations
            for up in range(len(model.unknown_parameters)):
                draws[model.unknown_parameters[up]]['samples_100'][p] = (
                    draws)[model.unknown_parameters[up]]['samples_1000'][idx]
            # 10 realizations
            if (p+1) % 10 == 0:
                for up in range(len(model.unknown_parameters)):
                    draws[model.unknown_parameters[up]]['samples_10'][p//10-1] = (
                        draws)[model.unknown_parameters[up]]['samples_1000'][idx]
            # 1 realization
            if (p + 1) == 50:
                for up in range(len(model.unknown_parameters)):
                    draws[model.unknown_parameters[up]]['samples_1'][0] = (
                        draws)[model.unknown_parameters[up]]['samples_1000'][idx]

        return draws


def plot_progress(sampler, environment, model, rbg_data):
    last_sample = sampler.get_chain(flat=True)[-1]

    model = copy.copy(model)
    environment = copy.copy(environment)

    # set the model parameters
    for p in range(len(model.unknown_parameters)):
        setattr(model.model_parameters, model.unknown_parameters[p], last_sample[p])
    model.model_parameters.kgri = model.model_parameters.kempt

    g = model.simulate(rbg_data=rbg_data, modality='twinning', environment=environment, dss=None)
    pylab.close()

    pylab.ion()  # Force interactive

    fig, ax = pylab.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})

    # Subplot 1: Glucose
    ax[0].plot(rbg_data.glucose, marker='o', color='red', linewidth=2, label='Glucose (data) [mg/dl]')
    ax[0].plot(g[0::model.yts], marker='o', color='black', linewidth=2, label='Glucose (fit) [mg/dl]')

    ax[0].grid()
    ax[0].legend()

    # Subplot 2: Meals
    markerline, stemlines, baseline = ax[1].stem(rbg_data.meal_data * 5, basefmt='k:', label='CHO [g]')
    color_meals = (70.0 / 255, 130.0 / 255, 180.0 / 255)
    plt.setp(stemlines, 'color', color_meals)
    plt.setp(markerline, 'color', color_meals)
    ax[1].grid()
    ax[1].legend()

    # Subplot 3: Insulin
    markerline, stemlines, baseline = ax[2].stem(rbg_data.bolus_data * 5, basefmt='k:', label='Bolus insulin [U]')
    color_boluses = (50.0 / 255, 205.0 / 255, 50.0 / 255)
    plt.setp(stemlines, 'color', color_boluses)
    plt.setp(markerline, 'color', color_boluses)

    ax[2].plot(rbg_data.basal_data * 60, color='black', linewidth=2, label='Basal insulin [U/h]')

    ax[2].grid()
    ax[2].legend()
    pylab.show()  # This does not bloc
    pylab.pause(1)
