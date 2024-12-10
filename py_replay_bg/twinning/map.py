import os
import warnings
import pickle
import numpy as np

from typing import Dict, Callable

from multiprocessing import Pool
from tqdm import tqdm
from scipy.optimize import minimize

from py_replay_bg.data import ReplayBGData
from py_replay_bg.model.t1d_model_single_meal import T1DModelSingleMeal
from py_replay_bg.model.t1d_model_multi_meal import T1DModelMultiMeal

from py_replay_bg.environment import Environment

# Suppress all RuntimeWarnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


class MAP:
    """
    A class that orchestrates the twinning process via MAP.

    Attributes
    ----------
    max_iter: int
        Maximum number of iterations.
    parallelize : bool
        A boolean that specifies whether to parallelize the twinning process.
    n_processes : int
        The number of processes to be spawn if `parallelize` is `True`. If None, the number of CPU cores is used.

    Methods
    -------
    twin(rbg_data, model, save_name, environment)
        Runs the twinning procedure.
    """

    def __init__(self,
                 max_iter: int = 100000,
                 parallelize: bool = False,
                 n_processes: int | None = None,
                 ):
        """
        Constructs all the necessary attributes for the MCMC object.

        Parameters
        ----------
        max_iter: int, optional, default : 100000
            Maximum number of iterations.
        parallelize : bool, optional, default : False
            A boolean that specifies whether to parallelize the twinning process.
        n_processes : int, optional, default : None
            The number of processes to be spawn if `parallelize` is `True`. If None, the number of CPU cores is used.

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

        # Number of times to re-run the procedure
        self.n_rerun = 64

        # Maximum number of iterations
        self.max_iter = max_iter

        # Maximum number of function evaluations
        self.max_fev = 1000000

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
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        save_name : str
            A string used to label, thus identify, each output file and result.

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

        # Set the initial positions of the walkers.
        start = model.start_guess + model.start_guess_sigma * np.random.randn(self.n_rerun, n_dim)
        start[start < 0] = 0

        # Set the pooler
        pool = None
        if self.parallelize:
            pool = Pool(processes=self.n_processes)

        # Set up the options
        options = dict()
        options['maxiter'] = self.max_iter
        options['maxfev'] = self.max_fev
        options['disp'] = False

        # Select the function to minimize
        neg_log_posterior_func = model.neg_log_posterior

        # Initialize results
        results = []

        if pool is None:

            if environment.verbose:
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
                if environment.verbose:
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
        for up in range(n_dim):
            draws[model.unknown_parameters[up]] = results[best]['x'][up]

        # Save results
        twinning_results = dict()
        twinning_results['draws'] = draws
        twinning_results['u2ss'] = model.model_parameters.u2ss

        saved_file = os.path.join(environment.replay_bg_path, 'results', 'map',
                                  'map_' + save_name + '.pkl')

        with open(saved_file, 'wb') as file:
            pickle.dump(twinning_results, file)

        if environment.verbose:
            print('Parameters saved in ' + saved_file)

        return draws


def run_map(start: np.ndarray,
            neg_log_posterior_func: Callable,
            rbg_data: ReplayBGData,
            options: Dict
            ) -> Dict:
    """
    Utility function used to run MAP twinning.

    Parameters
    ----------
    start: np.ndarray
        An object containing the data to be used during the twinning procedure.
    neg_log_posterior_func: Callable
        The function to minimize, i.e., the neg-loglikelihood.
    rbg_data: ReplayBGData
        An object containing the data to be used during the twinning procedure.
    options : Dict
        A dictionary with the options necessary to the minimization function.

    Returns
    -------
    ret: dict
        A dictionary containing the results of the MAP twinning and the final value of the objective function.

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
    result = minimize(neg_log_posterior_func, start, method='Powell', args=(rbg_data,), options=options)
    ret = dict()
    ret['fun'] = result.fun
    ret['x'] = result.x
    return ret
