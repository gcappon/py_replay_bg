import os
import warnings
import pickle
import numpy as np
import pandas as pd

from multiprocessing import Pool
from tqdm import tqdm
from scipy.optimize import minimize

from py_replay_bg.data import ReplayBGData

# Suppress all RuntimeWarnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


class MAP:
    """
    A class that orchestrates the identification process via MAP.
    """

    def __init__(self, model,
                max_iter: int = 100000):
        """
        Constructs all the necessary attributes for the MCMC object.

        Parameters
        ----------
        model: Model
            An object that represents the physiological model hyperparameters to be used by ReplayBG.
        max_iter: int, optional, default : 100000
            Maximum number of iterations.

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

        # Number of times to re-run the procedure
        self.n_rerun = 64

        # Maximum number of iterations
        self.max_iter = max_iter

        # Maximum number of function evaluations
        self.max_fev = 1000000

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
        start = self.model.start_guess + self.model.start_guess_sigma * np.random.randn(self.n_rerun, self.n_dim)
        start[start < 0] = 0

        # Set the pooler
        pool = None
        if rbg.environment.parallelize:
            pool = Pool(processes=rbg.environment.n_processes)

        # Setup the options
        options = dict()
        options['maxiter'] = self.max_iter
        options['maxfev'] = self.max_fev
        options['disp'] = False

        # Select the function to minimize
        neg_log_posterior_func = self.model.neg_log_posterior

        # Initialize results
        results = []

        if pool is None:

            if rbg.environment.verbose:
                iterator = tqdm(range(self.n_rerun))
                iterator.set_description("Min loss: %f" % np.nan)
            else:
                iterator = range(self.n_rerun)

            # Initialize best
            best = -1

            for r in iterator:
                result = run_map(start[r], neg_log_posterior_func, rbg_data, options)
                results.append(result)
                if best == -1 or result['fun'] < results[best]['fun']:
                    best = r
                if rbg.environment.verbose:
                    iterator.set_description("Min loss %f" % results[best]['fun'])

        else:
            # Prepare input arguments as tuples for starmap
            args = [(start[r], neg_log_posterior_func, rbg_data, options) for r in range(self.n_rerun)]

            # Initialize best
            best = -1

            # Get results (verbosity not allowed for the moment)
            results = pool.starmap(run_map, args)

            # Get best
            for r, result in enumerate(results):
                if best == -1 or result['fun'] < results[best]['fun']:
                    best = r

        draws = dict()
        for up in range(len(rbg.model.unknown_parameters)):
            draws[rbg.model.unknown_parameters[up]] = results[best]['x'][up]

        # Save results
        identification_results = dict()
        identification_results['draws'] = draws

        with open(os.path.join(rbg.environment.replay_bg_path, 'results', 'map',
                               'map_' + rbg.environment.save_name + '.pkl'), 'wb') as file:
            pickle.dump(identification_results, file)

        return draws


def run_map(start, func, rbg_data, options):
    result = minimize(func, start, method='Powell', args=(rbg_data,), options=options)
    ret = dict()
    ret['fun'] = result.fun
    ret['x'] = result.x
    return ret