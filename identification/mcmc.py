import os 

from data.data import ReplayBGData

from physiology.model_diff_t1d import model_diff_single_meal_t1d

import pymc as pm
from pymc.ode import DifferentialEquation
import pytensor

import numpy as np
import zeus 
import matplotlib.pyplot as plt 

from multiprocessing import Pool

from copulas.multivariate import GaussianMultivariate
from copulas.univariate import ParametricType, Univariate, BoundedType

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
    n_burn_in: int
        Number of steps to use for the burn_in session.
    n_steps: int
        Number of steps to use for the main chain.
    to_sample: int
        Number of samples to generate via the copula.
    callback_ncheck: int
        Number of steps to be awaited before checking the callback functions.

    Methods
    -------
    identify(rbg_data, rbg):
        Runs the identification procedure.
    """

    def __init__(self, model, 
                 n_burn_in = 1000, 
                 n_steps = 10000, 
                 to_sample = 1000,
                 callback_ncheck = 100):
        """
        Constructs all the necessary attributes for the MCMC object.

        Parameters
        ----------
        model: Model
            An object that represents the physiological model hyperparameters to be used by ReplayBG.
        n_burn_in: int, optional, default : 1000
            Number of steps to use for the burn_in session.
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

        #Physioogical model to identify
        self.model = model

        #Number of unknown parameters to identify
        self.n_dim = len(self.model.unknown_parameters) 

        #Number of walkers to use. It should be at least twice the number of dimensions.
        self.n_walkers = 2*self.n_dim 

        #Number of steps to use for the burn_in session     
        self.n_burn_in = n_burn_in

        #Number of steps to use for the main chain
        self.n_steps = n_steps
        
        #Chain thin factor to use 
        self.thin_factor = int(np.ceil(n_steps/1000))
        
        #Number of samples to generate via the copula
        self.to_sample = to_sample

        #Number of steps to be awaited before checking the callback functions 
        self.callback_ncheck = callback_ncheck

    def identify(self, rbg_data, rbg):
        """
        Runs the identification procedure.

        Parameters
        ----------
        rbg_data: ReplayBGData
            An object containing the data to be used during the identification procedure.
        rbg: ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        draws: dict
            A dictionary containing the chain and the samples obtained from the MCMC procedure and the copula sampling,respectively. 

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
        start[start<0]=0

        #Create the callbacks
        cb0 = zeus.callbacks.AutocorrelationCallback(ncheck = self.callback_ncheck)
        cb1 = zeus.callbacks.SplitRCallback(ncheck = self.callback_ncheck)
        cb2 = zeus.callbacks.MinIterCallback(nmin = self.n_burn_in)

        # Run first explorative session using the default 'DifferentialMove'
        sampler = zeus.EnsembleSampler(self.n_walkers, self.n_dim, self.model.log_posterior, args=[rbg_data, rbg], verbose = rbg.environment.verbose) 
        sampler.run_mcmc(start, self.n_burn_in)

        # Get the burn-in samples
        burn_in = sampler.get_chain()

        # Set the new starting positions of walkers based on their last positions
        start = burn_in[-1]

        #TODO with Pool() as pool: 

        #Initialize and run the "more advanced" sampler
        sampler = zeus.EnsembleSampler(self.n_walkers, self.n_dim, self.model.log_posterior, args=[rbg_data, rbg], verbose = rbg.environment.verbose, moves = zeus.moves.GlobalMove())
        sampler.run_mcmc(start, self.n_steps, callbacks=[cb0, cb1, cb2]) 
        sampler.summary # Print summary diagnostics

        #Get the chain
        chain = sampler.get_chain(flat=True, thin = self.thin_factor)

        #Fit the copula
        univariate = Univariate(parametric=ParametricType.NON_PARAMETRIC)
        dist = GaussianMultivariate(distribution=univariate)
        dist.fit(chain)

        #Get the draws to be used during replay
        draws = dict()
        for up in range(len(rbg.model.unknown_parameters)):
            draws[rbg.model.unknown_parameters[up]] = dict()
            draws[rbg.model.unknown_parameters[up]]['samples'] = np.empty(self.to_sample)
            draws[rbg.model.unknown_parameters[up]]['chain'] = chain[:,up]

        sampled = 0
        for i in range(self.to_sample):
            while True:
                sample = dist.sample(1).to_numpy()[0]
                if self.model.check_copula_extraction(sample):
                    for up in range(len(rbg.model.unknown_parameters)):
                        draws[rbg.model.unknown_parameters[up]][sampled] = sample[up]
                    sampled += 1
                    break
        
        #TODO: check physiological plausibility 

        #save results
        np.savez(os.path.join(rbg.environment.replay_bg_path, 'results', 'draws','draws_' + rbg.environment.save_name + '.npz'), 'draws', 'sampler', 'dist')

        return draws