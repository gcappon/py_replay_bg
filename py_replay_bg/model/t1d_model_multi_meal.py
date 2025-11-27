# This fixes circular imports for type checking
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from py_replay_bg.replay.custom_ra import CustomRaBase

import numpy as np
import pandas as pd

import os
import pickle

from datetime import datetime

import copy

from py_replay_bg.model.model_parameters_t1d import ModelParametersT1DMultiMeal

from py_replay_bg.model.logpriors_t1d import log_prior_multi_meal, log_prior_multi_meal_extended

from py_replay_bg.model.model_step_equations_t1d import twin_multi_meal, twin_multi_meal_extended
from py_replay_bg.model.model_step_equations_t1d import model_step_equations_multi_meal

from py_replay_bg.data import ReplayBGData
from py_replay_bg.environment import Environment
from py_replay_bg.dss import DSS
from py_replay_bg.sensors import Sensors


class T1DModelMultiMeal:
    """
    A class that represents the type 1 diabetes multi meal model.

    ...
    Attributes
    ----------
    ts: int
        The integration time step (min).
    yts: int
        The measurement (cgm) sample time.
    t: int
        The simulation timespan [min].
    tsteps: int
        The total simulation length [integration steps]
    tysteps: int
        The total simulation length [sample steps]
    nx: int
        The number of model states.
    model_parameters: ModelParameters
        An object containing the model parameters.

    unknown_parameters: np.ndarray
        An array that contains the list of unknown parameters to be estimated.
    start_guess: np.ndarray
        An array that contains the initial starting point to be used by the mcmc procedure.
    start_guess_sigma: np.ndarray
        An array that contains the initial starting SD of unknown parameters to be used by the mcmc procedure.
    pos_x: np.ndarray
        An array that contains the position of parameter x in unknown_parameters.

    exercise: bool
        A boolean indicating if the model includes the exercise.

    twinning_method : str
        The method used to twin the model.
    extended : bool
        A flag indicating whether to use the "extended" model for twinning

    x0: list
        The initial conditions for the model state. If None cold_boot will be set to True.
    previous_day_draws: dict
        The previous day draws. To be used to set the initial conditions.
    previous_data_name: str
        The name of the previous portion of data. To be used to initialize the initial conditions.
    previous_Ra: np.ndarray
        The remaining Ra from the previous portion of data. It is used as forcing input during simulation.

    Methods
    -------
    simulate(rbg_data, modality, environment, dss, sensors)
        Function that simulates the model and returns the obtained results. This is the complete version suitable for
        replay.
    neg_log_posterior(theta, rbg_data):
        Function that computes the negative log posterior of unknown parameters.
    log_posterior(theta, rbg_data):
        Function that computes the log posterior of unknown parameters.
    check_realization(theta):
        Function that checks if a realization is valid or not depending on the prior constraints.
    check_realization_exercise(theta):
        Function that checks if a realization is valid or not depending on the prior constraints (exercise model).
    """

    def __init__(self,
                 data: pd.DataFrame,
                 bw: float,
                 u2ss: float | None = None,
                 x0: list | None = None,
                 previous_data_name: str | None = None,
                 environment: Environment | None = None,
                 twinning_method: str = 'mcmc',
                 extended: bool = False,
                 is_twin: bool = False
                 ):
        """
        Constructs all the necessary attributes of the object.

        Parameters
        ----------
        data : pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        bw: float
            The body weight of the patient.
        u2ss: float, optional, default : None
            The u2ss to be used. If not specified the u2ss is assumed to be equal to the average basal of the data.
        x0: list, optional, default : None
            The initial conditions for the model state. If None cold_boot will be set to True.
        previous_data_name : str, optional, default : None
            The name of the previous data portion. This is used to correcly "transfer" the initial model conditions to
            the current portion of data.
        environment: Environment, optional, default : None
            An object that represents the hyperparameters to be used by ReplayBG.
        twinning_method : str, {'mcmc', 'map'}, optional, default : 'mcmc'
            The method to used to twin the model.
        extended : bool, default : False
            A flag indicating whether to use the "extended" model for twinning
        is_twin: bool, optional, default : False
            Whether or not the model is being created during twinning.
        """
        # Time constants during simulation
        self.ts = 1  # Integration step
        self.yts = environment.yts  # Measurement sampling time
        self.t = int((np.array(data.t)[-1].astype(datetime) - np.array(data.t)[0].astype(datetime)) / (
                60 * 1000000000) + self.yts)
        self.tsteps = self.t  # / self.ts
        self.tysteps = int(self.t / self.yts)

        # Model dimensionality
        self.nx = 21
        if extended:
            self.nx += 9

        # Model parameters
        self.model_parameters = ModelParametersT1DMultiMeal(data, bw, u2ss, extended)

        # Unknown parameters
        self.unknown_parameters = ['Gb', 'SG', 'p2', 'ka2', 'kd', 'kempt']

        # initial guess for unknown parameter
        self.start_guess = np.array(
            [self.model_parameters.Gb, self.model_parameters.SG, self.model_parameters.p2,
             self.model_parameters.ka2, self.model_parameters.kd, self.model_parameters.kempt])

        # initial guess for the SD of each parameter
        self.start_guess_sigma = np.array([1, 5e-4, 1e-3, 1e-3, 1e-3, 1e-3])

        # Get the hour of the day for each data point
        t = np.array(data.t.dt.hour.values).astype(int)

        # Set if we are using the extended model
        self.extended = extended

        if is_twin:

            # Attach breakfast SI if data between 4:00 - 11:00 are available
            self.pos_SI_B = 0
            if np.any(np.logical_and(t >= 4, t < 11)):
                self.pos_SI_B = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'SI_B')
                self.start_guess = np.append(self.start_guess, self.model_parameters.SI_B)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)

            # Attach lunch SI if data between 11:00 - 17:00 are available
            self.pos_SI_L = 0
            if np.any(np.logical_and(t >= 11, t < 17)):
                self.pos_SI_L = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'SI_L')
                self.start_guess = np.append(self.start_guess, self.model_parameters.SI_L)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)

            # Attach dinner SI if data between 0:00 - 4:00 or 17:00 - 24:00 are available
            self.pos_SI_D = 0
            if np.any(np.logical_or(t < 4, t >= 17)):
                self.pos_SI_D = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'SI_D')
                self.start_guess = np.append(self.start_guess, self.model_parameters.SI_D)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)

            # Attach kabs and beta breakfast if there is a breakfast
            self.pos_kabs_B = 0
            self.pos_beta_B = 0
            if np.any(np.array(data.cho_label) == 'B'):
                self.pos_kabs_B = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_B')
                self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_B)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
                self.pos_beta_B = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'beta_B')
                self.start_guess = np.append(self.start_guess, self.model_parameters.beta_B)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

            # Attach kabs and beta lunch if there is a lunch
            self.pos_kabs_L = 0
            self.pos_beta_L = 0
            if np.any(np.array(data.cho_label) == 'L'):
                self.pos_kabs_L = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_L')
                self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_L)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
                self.pos_beta_L = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'beta_L')
                self.start_guess = np.append(self.start_guess, self.model_parameters.beta_L)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

            # Attach kabs and beta dinner if there is a dinner
            self.pos_kabs_D = 0
            self.pos_beta_D = 0
            if np.any(np.array(data.cho_label) == 'D'):
                self.pos_kabs_D = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_D')
                self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_D)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
                self.pos_beta_D = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'beta_D')
                self.start_guess = np.append(self.start_guess, self.model_parameters.beta_D)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

            # Attach kabs and beta snack if there is a snack
            self.pos_kabs_S = 0
            self.pos_beta_S = 0
            if np.any(np.array(data.cho_label) == 'S'):
                self.pos_kabs_S = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_S')
                self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_S)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
                self.pos_beta_S = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'beta_S')
                self.start_guess = np.append(self.start_guess, self.model_parameters.beta_S)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

            # Attach kabs and hypotreatment if there is an hypotreatment
            self.pos_kabs_H = 0
            if np.any(np.array(data.cho_label) == 'H'):
                self.pos_kabs_H = self.start_guess.shape[0]
                self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_H')
                self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_H)
                self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)

            # If using the extended model, attach additional parameters
            if self.extended:

                # This is the index of 03:55 of the second day
                idx_355 = np.where(t == 3)[0][-1]
                # This is the index of 03:55 of the second day (in simulation steps)
                self.split_point = idx_355 * self.yts

                self.pos_SI_B2 = 0
                if np.any(np.logical_and(t[idx_355:] >= 4, t[idx_355:] < 11)):
                    self.pos_SI_B2 = self.start_guess.shape[0]
                    self.unknown_parameters = np.append(self.unknown_parameters, 'SI_B2')
                    self.start_guess = np.append(self.start_guess, self.model_parameters.SI_B2)
                    self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)

                # Attach kabs and beta breakfast 2 if there is a breakfast 2
                self.pos_kabs_B2 = 0
                self.pos_beta_B2 = 0
                if np.any(np.array(data.cho_label) == 'B2'):
                    self.pos_kabs_B2 = self.start_guess.shape[0]
                    self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_B2')
                    self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_B2)
                    self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
                    self.pos_beta_B2 = self.start_guess.shape[0]
                    self.unknown_parameters = np.append(self.unknown_parameters, 'beta_B2')
                    self.start_guess = np.append(self.start_guess, self.model_parameters.beta_B2)
                    self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)
                # Attach kabs and beta snack 2 if there is a snack 2
                self.pos_kabs_S2 = 0
                self.pos_beta_S2 = 0
                if np.any(np.array(data.cho_label) == 'S2'):
                    self.pos_kabs_S2 = self.start_guess.shape[0]
                    self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_S2')
                    self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_S2)
                    self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
                    self.pos_beta_S2 = self.start_guess.shape[0]
                    self.unknown_parameters = np.append(self.unknown_parameters, 'beta_S2')
                    self.start_guess = np.append(self.start_guess, self.model_parameters.beta_S2)
                    self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)
                # Attach kabs and beta lunch 2 if there is a lunch 2
                self.pos_kabs_L2 = 0
                self.pos_beta_L2 = 0
                if np.any(np.array(data.cho_label) == 'L2'):
                    self.pos_kabs_L2 = self.start_guess.shape[0]
                    self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_L2')
                    self.start_guess = np.append(self.start_guess, self.model_parameters.kabs_L2)
                    self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
                    self.pos_beta_L2 = self.start_guess.shape[0]
                    self.unknown_parameters = np.append(self.unknown_parameters, 'beta_L2')
                    self.start_guess = np.append(self.start_guess, self.model_parameters.beta_L2)
                    self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

        # Exercise
        self.exercise = environment.exercise

        # Pre-initialization (for performance)
        self.G = np.empty([self.tsteps, ])
        self.x = np.zeros([self.nx, self.tsteps])
        self.CGM = np.empty([self.tysteps, ])

        # If previous_data_name is not None load previous_day_draws otherwise set it to None
        self.previous_data_name = previous_data_name
        self.previous_day_draws = None
        if self.previous_data_name is not None:
            with open(os.path.join(environment.replay_bg_path, 'results', twinning_method,
                                   twinning_method + '_' + previous_data_name + '.pkl'), 'rb') as file:
                previous_day_twinning_results = pickle.load(file)
            self.previous_day_draws = previous_day_twinning_results['draws']

        # Remember the twinning method
        self.twinning_method = twinning_method

        # Set initial conditions
        self.x0 = None if x0 is None else x0.copy()

        # IMPORTANT: manage the "remaining" rate of appearance due to meals in the previous portion of data.
        #   The rationale is to compute the Ra signal according to the "free" evolution of the meal system using x0 as
        #   starting point. The such Ra will represent a forcing input to the plasma glucose compartment during the
        #   simulation.

        # Create the "remaining" rate of appearance input of the previous day
        self.previous_Ra = np.zeros([self.tsteps, ])
        if self.previous_data_name is not None:

            # Get the initial values of the meal submodel
            xk = self.x0[2:17]

            # Set model parameter values (if some parameters were not twinned, set them to the population value.
            if twinning_method == 'mcmc':
                kgri = self.previous_day_draws['kempt']['samples_1'][0]
                kempt = self.previous_day_draws['kempt']['samples_1'][0]
                if "kabs_B" in self.previous_day_draws:
                    kabs_B = self.previous_day_draws['kabs_B']['samples_1'][0]
                else:
                    kabs_B = self.model_parameters.kabs_B
                if "kabs_L" in self.previous_day_draws:
                    kabs_L = self.previous_day_draws['kabs_L']['samples_1'][0]
                else:
                    kabs_L = self.model_parameters.kabs_L
                if "kabs_D" in self.previous_day_draws:
                    kabs_D = self.previous_day_draws['kabs_D']['samples_1'][0]
                else:
                    kabs_D = self.model_parameters.kabs_D
                if "kabs_S" in self.previous_day_draws:
                    kabs_S = self.previous_day_draws['kabs_S']['samples_1'][0]
                else:
                    kabs_S = self.model_parameters.kabs_S
                if "kabs_H" in self.previous_day_draws:
                    kabs_H = self.previous_day_draws['kabs_H']['samples_1'][0]
                else:
                    kabs_H = self.model_parameters.kabs_H
            else:
                kgri = self.previous_day_draws['kempt']
                kempt = self.previous_day_draws['kempt']
                if "kabs_B" in self.previous_day_draws:
                    kabs_B = self.previous_day_draws['kabs_B']
                else:
                    kabs_B = self.model_parameters.kabs_B
                if "kabs_L" in self.previous_day_draws:
                    kabs_L = self.previous_day_draws['kabs_L']
                else:
                    kabs_L = self.model_parameters.kabs_L
                if "kabs_D" in self.previous_day_draws:
                    kabs_D = self.previous_day_draws['kabs_D']
                else:
                    kabs_D = self.model_parameters.kabs_D
                if "kabs_S" in self.previous_day_draws:
                    kabs_S = self.previous_day_draws['kabs_S']
                else:
                    kabs_S = self.model_parameters.kabs_S
                if "kabs_H" in self.previous_day_draws:
                    kabs_H = self.previous_day_draws['kabs_H']
                else:
                    kabs_H = self.model_parameters.kabs_H

            # Compute the Ra forcing input
            for k in range(self.tsteps):
                xk[0] = xk[0] / (1 + self.ts * kgri)
                xk[1] = (xk[1] + self.ts * kgri * xk[0]) / (1 + self.ts * kempt)
                xk[2] = (xk[2] + self.ts * kempt * xk[1]) / (1 + self.ts * kabs_B)

                xk[3] = xk[3] / (1 + self.ts * kgri)
                xk[4] = (xk[4] + self.ts * kgri * xk[3]) / (1 + self.ts * kempt)
                xk[5] = (xk[5] + self.ts * kempt * xk[4]) / (1 + self.ts * kabs_L)

                xk[6] = xk[6] / (1 + self.ts * kgri)
                xk[7] = (xk[7] + self.ts * kgri * xk[6]) / (1 + self.ts * kempt)
                xk[8] = (xk[8] + self.ts * kempt * xk[7]) / (1 + self.ts * kabs_D)

                xk[9] = xk[9] / (1 + self.ts * kgri)
                xk[10] = (xk[10] + self.ts * kgri * xk[9]) / (1 + self.ts * kempt)
                xk[11] = (xk[11] + self.ts * kempt * xk[10]) / (1 + self.ts * kabs_S)

                xk[12] = xk[12] / (1 + self.ts * kgri)
                xk[13] = (xk[13] + self.ts * kgri * xk[12]) / (1 + self.ts * kempt)
                xk[14] = (xk[14] + self.ts * kempt * xk[13]) / (1 + self.ts * kabs_H)

                self.previous_Ra[k] = self.model_parameters.f * (
                        kabs_B * xk[2] + kabs_L * xk[5] + kabs_D * xk[8] + kabs_S * xk[11] + kabs_H * xk[
                    14])

        # Set to 0 the initial conditions of meal-related compartments
        if self.x0 is not None:
            self.x0[2:17] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def simulate(self,
                 rbg_data: ReplayBGData,
                 modality: str,
                 environment: Environment | None,
                 dss: DSS | None,
                 sensors: Sensors = None,
                 forcing_Ra: CustomRaBase | None = None
                 ) -> np.ndarray | tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray
    ]:
        """
        Function that simulates the model and returns the obtained results. This is the complete version suitable for
        replay.

        Parameters
        ----------
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.
        modality: str, {'twinning', 'replay'}
            A string that defines whether the simulation was called while twinning or replaying.
        environment: Environment
            An object that represents the hyperparameters to be used by ReplayBG.
        dss: DSS
            An object that represents the hyperparameters of the dss. Unused during twinning.
        sensors: Sensors
            An object that represents the sensors used during simulation.
        forcing_Ra: ForcingRaBase
            An object that represents the forcing Ra input to be used during simulation. Default is None.

        Returns
        -------
        G: np.ndarray
            An array containing the simulated glucose concentration (mg/dl).
        IG: np.ndarray
            An array containing the simulated interstitial glucose concentration (mg/dl).
        CGM: np.ndarray
            An array containing the simulated CGM trace (mg/dl).
        bolus: np.ndarray
            An array containing the simulated insulin bolus events (U/min). Also includes the correction insulin
            boluses.
        correction_bolus: np.ndarray
            An array containing the simulated corrective insulin bolus events (U/min).
        basal: np.ndarray
            An array containing the simulated basal insulin events (U/min).
        cho: np.ndarray
            An array containing the simulated CHO events (g/min).
        hypotreatments: np.ndarray
            An array containing the simulated hypotreatments events (g/min).
        meal_announcement: np.ndarray
            An array containing the simulated meal announcements events needed for bolus calculation (g/min).
        x: np.ndarray
            A matrix containing all the simulated states.

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

        # Rename parameters for brevity
        mp = self.model_parameters

        # Utility flag for checking the modality (this boosts performance since the check will be done once)
        is_replay = modality == 'replay'

        # Make copies of the inputs if replay to avoid to overwrite fields
        bolus = rbg_data.bolus * 1
        basal = rbg_data.basal * 1
        meal = rbg_data.meal * 1
        meal_type = copy.copy(rbg_data.meal_type)
        meal_announcement = rbg_data.meal_announcement * 1
        correction_bolus = bolus * 0
        hypotreatments = meal * 0

        # Shift the insulin vectors according to the delays
        bolus_delayed = np.append(np.zeros(shape=(mp.tau.__trunc__(),)), bolus)
        basal_delayed = np.append(np.ones(shape=(mp.tau.__trunc__(),)) * mp.u2ss, basal)

        # Shift the meal vector according to the delays
        meal_B_delayed = np.append(np.zeros(shape=(mp.beta_B.__trunc__(),)), rbg_data.meal_B)
        meal_L_delayed = np.append(np.zeros(shape=(mp.beta_L.__trunc__(),)), rbg_data.meal_L)
        meal_D_delayed = np.append(np.zeros(shape=(mp.beta_D.__trunc__(),)), rbg_data.meal_D)
        meal_S_delayed = np.append(np.zeros(shape=(mp.beta_S.__trunc__(),)), rbg_data.meal_S)

        meal_H = rbg_data.meal_H * 1

        # If using the extended model, shift also the meal vectors of the second day
        if self.extended:
            meal_B2_delayed = np.append(np.zeros(shape=(mp.beta_B2.__trunc__(),)), rbg_data.meal_B2)
            meal_L2_delayed = np.append(np.zeros(shape=(mp.beta_L2.__trunc__(),)), rbg_data.meal_L2)
            meal_S2_delayed = np.append(np.zeros(shape=(mp.beta_S2.__trunc__(),)), rbg_data.meal_S2)

        # Set constant model coefficients
        logGb = np.log(mp.Gb)
        log60 = np.log(60.0)
        logGb_r2 = logGb ** mp.r2
        log60_r2 = log60 ** mp.r2
        risk_coeff = 10.0 * mp.r1
        k1 = 1.0 / (1.0 + mp.kgri)
        k2 = 1.0 / (1.0 + mp.kempt)
        kd_fac = 1.0 / (1.0 + mp.kd)

        # Get the initial conditions
        ki1 = mp.u2ss / mp.kd
        ki2 = mp.kd / mp.ka2 * ki1
        mp.Ipb = mp.ka2 / mp.ke * ki2

        # If initial model conditions are None, set the default initial conditions, i.e., steady-state
        if self.x0 is None:
            if self.extended:
                self.x[:, 0] = [mp.G0, mp.Xpb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0,
                                mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, ki1, ki2, mp.Ipb, mp.G0]
            else:
                self.x[:, 0] = [mp.G0, mp.Xpb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0,
                                mp.Qgutb, ki1, ki2, mp.Ipb, mp.G0]

        # otherwise, set the initial model condition appropriately.
        else:
            # IMPORTANT: Scale the initial conditions of the insulin compartment to avoid "fake meal/bolus" effects

            # Compute the k1, k2, and Ipb, macro parameters, using the model parameters of the previous portion of data
            # (i.e., the one that "generated" the provided x0)
            if self.twinning_method == 'mcmc':
                ki1_old = mp.u2ss / self.previous_day_draws['kd']['samples_1'][0]
                ki2_old = self.previous_day_draws['kd']['samples_1'][0] / self.previous_day_draws['ka2']['samples_1'][
                    0] * ki1_old
                Ipb_old = self.previous_day_draws['ka2']['samples_1'][0] / mp.ke * ki2_old
            else:
                ki1_old = mp.u2ss / self.previous_day_draws['kd']
                ki2_old = self.previous_day_draws['kd'] / self.previous_day_draws['ka2'] * ki1_old
                Ipb_old = self.previous_day_draws['ka2'] / mp.ke * ki2_old

            self.x0 = self.x0[:17] + [0] * 9 + self.x0[17:] if self.extended and len(self.x0) < 30 else self.x0

            # Scale as --> initial_old:initial_new = ki1old:ki1new
            self.x[:, 0] = self.x0
            self.x[self.nx - 4, 0] = ki1 * self.x[self.nx - 4, 0] / ki1_old
            self.x[self.nx - 3, 0] = ki2 * self.x[self.nx - 3, 0] / ki2_old
            self.x[self.nx - 2, 0] = mp.Ipb * self.x[
                self.nx - 2, 0] / Ipb_old  # Ipb and Ipb_old are always the same (= ka2 / ke * kd / ka2 * u2ss / kd = u2ss / ke)

        # Set the initial glucose value
        self.G[0] = self.x[self.nx - 1, 0]

        # Run simulation in two ways depending on the modality to speed up the twinning process
        if is_replay:

            # Set the initial cgm value if modality is 'replay' and make copies of meal vectors
            self.CGM[0] = sensors.cgm.measure(self.x[self.nx - 1, 0], t=0, past_ig=self.x[self.nx - 1, :0])

            meal_B = rbg_data.meal_B * 1
            meal_L = rbg_data.meal_L * 1
            meal_D = rbg_data.meal_D * 1
            meal_S = rbg_data.meal_S * 1

            for k in np.arange(1, self.tsteps):
                # Meal generation module
                if rbg_data.cho_source == 'generated':
                    # Call the meal generator function handler
                    ch, ma, t, dss = dss.meal_generator_handler(self.G[0:k],
                                                                meal[0:k] * mp.to_g,
                                                                meal_type[0:k],
                                                                meal_announcement[0:k],
                                                                hypotreatments[0:k],
                                                                bolus[0:k] * mp.to_g,
                                                                basal[0:k] * mp.to_g,
                                                                rbg_data.t_hour[0:k],
                                                                k - 1,
                                                                dss,
                                                                environment.blueprint)
                    ch_mgkg = ch * mp.to_mgkg
                    # Add the CHO to the input (remember to add the delay)
                    if t == 'B':
                        if (k + mp.beta_B.__trunc__()) < self.tsteps:
                            meal_B[k] = meal_B[k] + ch_mgkg
                            meal_B_delayed[k + mp.beta_B.__trunc__()] = meal_B_delayed[
                                                                            k + mp.beta_B.__trunc__()] + ch_mgkg
                    elif t == 'L':
                        if (k + mp.beta_L.__trunc__()) < self.tsteps:
                            meal_L[k] = meal_L[k] + ch_mgkg
                            meal_L_delayed[k + mp.beta_L.__trunc__()] = meal_L_delayed[
                                                                            k + mp.beta_L.__trunc__()] + ch_mgkg
                    elif t == 'D':
                        if (k + mp.beta_D.__trunc__()) < self.tsteps:
                            meal_D[k] = meal_D[k] + ch_mgkg
                            meal_D_delayed[k + mp.beta_D.__trunc__()] = meal_D_delayed[
                                                                            k + mp.beta_D.__trunc__()] + ch_mgkg
                    elif t == 'S':
                        if (k + mp.beta_S.__trunc__()) < self.tsteps:
                            meal_S[k] = meal_S[k] + ch_mgkg
                            meal_S_delayed[k + mp.beta_S.__trunc__()] = meal_S_delayed[
                                                                            k + mp.beta_S.__trunc__()] + ch_mgkg

                    # Update the event vectors
                    meal_announcement[k] = meal_announcement[k] + ma
                    meal_type[k] = t

                    # Add the CHO to the non-delayed meal vector.
                    meal[k] = meal[k] + ch_mgkg

                # Bolus generation module
                if rbg_data.bolus_source == 'dss':
                    # Call the bolus calculator function handler
                    bo, dss = dss.bolus_calculator_handler(self.G[0:k],
                                                           meal_announcement[0:k],
                                                           meal_type[0:k],
                                                           hypotreatments[0:k],
                                                           bolus[0:k] * mp.to_g,
                                                           basal[0:k] * mp.to_g,
                                                           rbg_data.t_hour[0:k],
                                                           k - 1,
                                                           dss)
                    bo_mgkg = bo * mp.to_mgkg

                    # Add the bolus to the input bolus vector.
                    if (k + mp.tau.__trunc__()) < self.tsteps:
                        bolus_delayed[k + mp.tau.__trunc__()] = bolus_delayed[k + mp.tau.__trunc__()] + bo_mgkg

                    # Add the bolus to the non-delayed bolus vector.
                    bolus[k] = bolus[k] + bo_mgkg

                # Basal rate generation module
                if rbg_data.basal_source == 'dss':
                    # Call the basal rate function handler
                    ba, dss = dss.basal_handler(self.G[0:k],
                                                meal_announcement[0:k],
                                                meal_type[0:k],
                                                hypotreatments[0:k],
                                                bolus[0:k] * mp.to_g,
                                                basal[0:k] * mp.to_g,
                                                rbg_data.t_hour[0:k],
                                                k - 1,
                                                dss)
                    ba_mgkg = ba * mp.to_mgkg
                    # Add the basal to the input basal vector.
                    if (k + mp.tau.__trunc__()) < self.tsteps:
                        basal_delayed[k + mp.tau.__trunc__()] = basal_delayed[
                                                                    k + mp.tau.__trunc__()] + ba_mgkg

                    # Add the bolus to the non-delayed bolus vector.
                    basal[k] = basal[k] + ba_mgkg

                # Hypotreatment generation module
                if dss.enable_hypotreatments:
                    # Call the hypotreatment handler
                    ht, dss = dss.hypotreatments_handler(self.G[0:k],
                                                         meal_announcement[0:k],
                                                         meal_type[0:k],
                                                         hypotreatments[0:k],
                                                         bolus[0:k] * mp.to_g,
                                                         basal[0:k] * mp.to_g,
                                                         rbg_data.t_hour[0:k],
                                                         k - 1,
                                                         dss)
                    ht_mgkg = ht * mp.to_mgkg
                    meal_H[k] = meal_H[k] + ht_mgkg

                    # Update the hypotreatments event vectors
                    hypotreatments[k] = hypotreatments[k] + ht

                # Correction bolus delivery module if it is enabled
                if dss.enable_correction_boluses:
                    # Call the correction boluses handler
                    cb, dss = dss.correction_boluses_handler(self.G[0:k],
                                                             meal_announcement[0:k],
                                                             meal_type[0:k],
                                                             hypotreatments[0:k],
                                                             bolus[0:k] * mp.to_g,
                                                             basal[0:k] * mp.to_g,
                                                             rbg_data.t_hour[0:k],
                                                             k - 1,
                                                             dss)
                    cb_mgkg = cb * mp.to_mgkg
                    # Add the cb to the input bolus vector.
                    if (k + mp.tau.__trunc__()) < self.tsteps:
                        bolus_delayed[k + mp.tau.__trunc__()] = bolus_delayed[
                                                                    k + mp.tau.__trunc__()] + cb_mgkg

                    # Add the bolus to the non-delayed bolus vector.
                    bolus[k] = bolus[k] + cb_mgkg

                    # Update the correction_bolus event vectors
                    correction_bolus[k] = correction_bolus[k] + cb

                if forcing_Ra is not None:
                    current_forcing_Ra = forcing_Ra.simulate_forcing_ra(rbg_data.t_hour[0:k], k)
                else:
                    current_forcing_Ra = 0

                # Integration step
                self.x[:, k] = model_step_equations_multi_meal(bolus_delayed[k] + basal_delayed[k],
                                                               meal_B_delayed[k],
                                                               meal_L_delayed[k],
                                                               meal_D_delayed[k],
                                                               meal_S_delayed[k],
                                                               meal_H[k],
                                                               rbg_data.t_hour[k],
                                                               self.x[:, k - 1],
                                                               logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                                               mp.r2,
                                                               mp.kempt,
                                                               mp.kd,
                                                               mp.ka2,
                                                               mp.ke,
                                                               mp.p2,
                                                               mp.SI_B,
                                                               mp.SI_L,
                                                               mp.SI_D,
                                                               mp.VI,
                                                               mp.VG,
                                                               mp.Ipb,
                                                               mp.SG,
                                                               mp.Gb,
                                                               mp.f,
                                                               mp.kabs_B,
                                                               mp.kabs_L,
                                                               mp.kabs_D,
                                                               mp.kabs_S,
                                                               mp.kabs_H,
                                                               mp.alpha,
                                                               self.previous_Ra[k], current_forcing_Ra)

                self.G[k] = self.x[self.nx - 1, k]

                # Get the cgm
                if np.mod(k, sensors.cgm.ts) == 0:
                    if np.mod(k + sensors.cgm.t_offset, sensors.cgm.max_lifetime) == 0:
                        # connect new sensor
                        sensors.cgm.connect_new_cgm(connected_at=k)
                        # manage offset
                    self.CGM[int(k / sensors.cgm.ts)] = sensors.cgm.measure(self.x[self.nx - 1, k],
                                                                            t=(k - sensors.cgm.connected_at) / (
                                                                                    24 * 60),
                                                                            past_ig=self.x[self.nx - 1, :k], )

            # Add the list of events that generated the forcing Ra to the meal vector for logging purposes
            if forcing_Ra is not None:
                meal = np.array([m + f for m, f in zip(meal, forcing_Ra.get_events())])

            # TODO: add vo2
            return (self.x[0, :].copy(),
                    self.x[:, -1].copy(),
                    self.CGM.copy(),
                    bolus * mp.to_g,
                    correction_bolus,
                    basal * mp.to_g,
                    meal * mp.to_g,
                    hypotreatments,
                    meal_announcement,
                    self.x.copy())

        else:

            # Run simulation
            if self.extended:

                self.x = twin_multi_meal_extended(self.tsteps,
                                                  self.x,
                                                  bolus_delayed,
                                                  basal_delayed,
                                                  meal_B_delayed,
                                                  meal_L_delayed,
                                                  meal_D_delayed,
                                                  meal_S_delayed,
                                                  meal_H,
                                                  meal_B2_delayed,
                                                  meal_L2_delayed,
                                                  meal_S2_delayed,
                                                  rbg_data.t_hour,
                                                  self.split_point,
                                                  logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                                  mp.r2,
                                                  mp.kempt,
                                                  mp.kd,
                                                  mp.ka2,
                                                  mp.ke,
                                                  mp.p2,
                                                  mp.SI_B,
                                                  mp.SI_L,
                                                  mp.SI_D,
                                                  mp.SI_B2,
                                                  mp.VI,
                                                  mp.VG,
                                                  mp.Ipb,
                                                  mp.SG,
                                                  mp.Gb,
                                                  mp.f,
                                                  mp.kabs_B,
                                                  mp.kabs_L,
                                                  mp.kabs_D,
                                                  mp.kabs_S,
                                                  mp.kabs_H,
                                                  mp.kabs_B2,
                                                  mp.kabs_L2,
                                                  mp.kabs_S2,
                                                  mp.alpha,
                                                  self.previous_Ra)

            else:

                self.x = twin_multi_meal(self.tsteps,
                                         self.x,
                                         bolus_delayed,
                                         basal_delayed,
                                         meal_B_delayed,
                                         meal_L_delayed,
                                         meal_D_delayed,
                                         meal_S_delayed,
                                         meal_H,
                                         rbg_data.t_hour,
                                         logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                         mp.r2,
                                         mp.kempt,
                                         mp.kd,
                                         mp.ka2,
                                         mp.ke,
                                         mp.p2,
                                         mp.SI_B,
                                         mp.SI_L,
                                         mp.SI_D,
                                         mp.VI,
                                         mp.VG,
                                         mp.Ipb,
                                         mp.SG,
                                         mp.Gb,
                                         mp.f,
                                         mp.kabs_B,
                                         mp.kabs_L,
                                         mp.kabs_D,
                                         mp.kabs_S,
                                         mp.kabs_H,
                                         mp.alpha,
                                         self.previous_Ra)

            # Return just the glucose vector if modality == 'twinning'
            return self.x[self.nx - 1, :]

    def __log_likelihood(self, theta: np.ndarray, rbg_data: ReplayBGData):
        """
        Internal function that computes the log likelihood of unknown parameters.

        Parameters
        ----------
        theta : np.ndarray
            The current guess of unknown model parameters.
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.

        Returns
        -------
        log_likelihood: float
            The value of the log likelihood of current unknown model parameters guess.
        
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

        # Set model parameters to current guess
        (self.model_parameters.Gb,
         self.model_parameters.SG,
         self.model_parameters.p2,
         self.model_parameters.ka2,
         self.model_parameters.kd,
         self.model_parameters.kempt) = theta[0:6]

        if self.model_parameters.beta_S < 0:
            print("BETA < 0 - LL")

        self.model_parameters.SI_B = theta[self.pos_SI_B] if self.pos_SI_B else self.model_parameters.SI_B
        self.model_parameters.SI_L = theta[self.pos_SI_L] if self.pos_SI_L else self.model_parameters.SI_L
        self.model_parameters.SI_D = theta[self.pos_SI_D] if self.pos_SI_D else self.model_parameters.SI_D

        self.model_parameters.kabs_B = theta[self.pos_kabs_B] if self.pos_kabs_B else self.model_parameters.kabs_B
        self.model_parameters.kabs_L = theta[self.pos_kabs_L] if self.pos_kabs_L else self.model_parameters.kabs_L
        self.model_parameters.kabs_D = theta[self.pos_kabs_D] if self.pos_kabs_D else self.model_parameters.kabs_D
        self.model_parameters.kabs_S = theta[self.pos_kabs_S] if self.pos_kabs_S else self.model_parameters.kabs_S
        self.model_parameters.kabs_H = theta[self.pos_kabs_H] if self.pos_kabs_H else self.model_parameters.kabs_H

        self.model_parameters.beta_B = theta[self.pos_beta_B] if self.pos_beta_B else self.model_parameters.beta_B
        self.model_parameters.beta_L = theta[self.pos_beta_L] if self.pos_beta_L else self.model_parameters.beta_L
        self.model_parameters.beta_D = theta[self.pos_beta_D] if self.pos_beta_D else self.model_parameters.beta_D

        self.model_parameters.beta_S = theta[self.pos_beta_S] if self.pos_beta_S else self.model_parameters.beta_S

        # Enforce constraints
        self.model_parameters.kgri = self.model_parameters.kempt

        # Simulate the model
        G = self.simulate(rbg_data=rbg_data, modality='twinning', environment=None, dss=None)

        # Sample the simulation
        G = G[0::self.yts]

        # Compute and return the log likelihood
        return -0.5 * np.sum(
            ((G[rbg_data.glucose_idxs] - rbg_data.glucose[rbg_data.glucose_idxs]) / self.model_parameters.SDn) ** 2)

    def __log_likelihood_extended(self, theta: np.ndarray, rbg_data: ReplayBGData):
        """
        Internal function that computes the log likelihood of unknown parameters (extended model).

        Parameters
        ----------
        theta : np.ndarray
            The current guess of unknown model parameters.
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.

        Returns
        -------
        log_likelihood_extended: float
            The value of the log likelihood of current unknown model parameters guess.

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

        # Set model parameters to current guess
        (self.model_parameters.Gb,
         self.model_parameters.SG,
         self.model_parameters.p2,
         self.model_parameters.ka2,
         self.model_parameters.kd,
         self.model_parameters.kempt) = theta[0:6]

        self.model_parameters.SI_B = theta[self.pos_SI_B] if self.pos_SI_B else self.model_parameters.SI_B
        self.model_parameters.SI_L = theta[self.pos_SI_L] if self.pos_SI_L else self.model_parameters.SI_L
        self.model_parameters.SI_D = theta[self.pos_SI_D] if self.pos_SI_D else self.model_parameters.SI_D

        self.model_parameters.kabs_B = theta[self.pos_kabs_B] if self.pos_kabs_B else self.model_parameters.kabs_B
        self.model_parameters.kabs_L = theta[self.pos_kabs_L] if self.pos_kabs_L else self.model_parameters.kabs_L
        self.model_parameters.kabs_D = theta[self.pos_kabs_D] if self.pos_kabs_D else self.model_parameters.kabs_D
        self.model_parameters.kabs_S = theta[self.pos_kabs_S] if self.pos_kabs_S else self.model_parameters.kabs_S
        self.model_parameters.kabs_H = theta[self.pos_kabs_H] if self.pos_kabs_H else self.model_parameters.kabs_H

        self.model_parameters.beta_B = theta[self.pos_beta_B] if self.pos_beta_B else self.model_parameters.beta_B
        self.model_parameters.beta_L = theta[self.pos_beta_L] if self.pos_beta_L else self.model_parameters.beta_L
        self.model_parameters.beta_D = theta[self.pos_beta_D] if self.pos_beta_D else self.model_parameters.beta_D
        self.model_parameters.beta_S = theta[self.pos_beta_S] if self.pos_beta_S else self.model_parameters.beta_S

        self.model_parameters.SI_B2 = theta[self.pos_SI_B2] if self.pos_SI_B2 else self.model_parameters.SI_B2

        self.model_parameters.kabs_B2 = theta[self.pos_kabs_B2] if self.pos_kabs_B2 else self.model_parameters.kabs_B2
        self.model_parameters.kabs_L2 = theta[self.pos_kabs_L2] if self.pos_kabs_L2 else self.model_parameters.kabs_L2
        self.model_parameters.kabs_S2 = theta[self.pos_kabs_S2] if self.pos_kabs_S2 else self.model_parameters.kabs_S2

        self.model_parameters.beta_B2 = theta[self.pos_beta_B2] if self.pos_beta_B2 else self.model_parameters.beta_B2
        self.model_parameters.beta_L2 = theta[self.pos_beta_L2] if self.pos_beta_L2 else self.model_parameters.beta_L2
        self.model_parameters.beta_S2 = theta[self.pos_beta_S2] if self.pos_beta_S2 else self.model_parameters.beta_S2

        # Enforce constraints
        self.model_parameters.kgri = self.model_parameters.kempt

        # Simulate the model
        G = self.simulate(rbg_data=rbg_data, modality='twinning', environment=None, dss=None)

        # Sample the simulation
        G = G[0::self.yts]

        # Compute and return the log likelihood
        return -0.5 * np.sum(
            ((G[rbg_data.glucose_idxs] - rbg_data.glucose[rbg_data.glucose_idxs]) / self.model_parameters.SDn) ** 2)

    def neg_log_posterior(self, theta: np.ndarray, rbg_data: ReplayBGData):
        res = - self.log_posterior(theta, rbg_data)
        return res

    def neg_log_posterior_extended(self, theta: np.ndarray, rbg_data: ReplayBGData):
        res = - self.log_posterior_extended(theta, rbg_data)
        return res

    def log_posterior(self, theta: np.ndarray, rbg_data: ReplayBGData):
        """
        Function that computes the log posterior of unknown parameters.

        Parameters
        ----------
        theta : np.ndarray
            The current guess of unknown model parameters.
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.

        Returns
        -------
        log_posterior: float
            The value of the log posterior of current unknown model parameters guess.
        
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
        p = log_prior_multi_meal(self.model_parameters.VG,
                                 self.pos_SI_B, self.model_parameters.SI_B,
                                 self.pos_SI_L, self.model_parameters.SI_L,
                                 self.pos_SI_D, self.model_parameters.SI_D,
                                 self.pos_kabs_B, self.model_parameters.kabs_B,
                                 self.pos_kabs_L, self.model_parameters.kabs_L,
                                 self.pos_kabs_D, self.model_parameters.kabs_D,
                                 self.pos_kabs_S, self.model_parameters.kabs_S,
                                 self.pos_kabs_H, self.model_parameters.kabs_H,
                                 self.pos_beta_B, self.model_parameters.beta_B,
                                 self.pos_beta_L, self.model_parameters.beta_L,
                                 self.pos_beta_D, self.model_parameters.beta_D,
                                 self.pos_beta_S, self.model_parameters.beta_S,
                                 theta)

        if p == -np.inf:
            return -np.inf
        return p + self.__log_likelihood(theta, rbg_data)

    def log_posterior_extended(self, theta: np.ndarray, rbg_data: ReplayBGData):
        """
        Function that computes the log posterior of unknown parameters (extended model).

        Parameters
        ----------
        theta : np.ndarray
            The current guess of unknown model parameters.
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.

        Returns
        -------
        log_posterior_extended: float
            The value of the log posterior of current unknown model parameters guess.

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
        p = log_prior_multi_meal_extended(self.model_parameters.VG,
                                          self.pos_SI_B, self.model_parameters.SI_B,
                                          self.pos_SI_L, self.model_parameters.SI_L,
                                          self.pos_SI_D, self.model_parameters.SI_D,
                                          self.pos_kabs_B, self.model_parameters.kabs_B,
                                          self.pos_kabs_L, self.model_parameters.kabs_L,
                                          self.pos_kabs_D, self.model_parameters.kabs_D,
                                          self.pos_kabs_S, self.model_parameters.kabs_S,
                                          self.pos_kabs_H, self.model_parameters.kabs_H,
                                          self.pos_beta_B, self.model_parameters.beta_B,
                                          self.pos_beta_L, self.model_parameters.beta_L,
                                          self.pos_beta_D, self.model_parameters.beta_D,
                                          self.pos_beta_S, self.model_parameters.beta_S,
                                          self.pos_SI_B2, self.model_parameters.SI_B2,
                                          self.pos_kabs_B2, self.model_parameters.kabs_B2,
                                          self.pos_kabs_L2, self.model_parameters.kabs_L2,
                                          self.pos_kabs_S2, self.model_parameters.kabs_S2,
                                          self.pos_beta_B2, self.model_parameters.beta_B2,
                                          self.pos_beta_L2, self.model_parameters.beta_L2,
                                          self.pos_beta_S2, self.model_parameters.beta_S2,
                                          theta)
        if p == -np.inf:
            return -np.inf
        return p + self.__log_likelihood_extended(theta, rbg_data)

    def check_realization(self, theta: np.ndarray):
        """
        Function that checks if a copula extraction is valid or not depending on the prior constraints.

        Parameters
        ----------
        theta : np.ndarray
            The copula extraction of unknown model parameters.

        Returns
        -------
        is_ok: bool
            The flag indicating if the extraction is ok or not.

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
        return log_prior_multi_meal(self.model_parameters.VG,
                                    self.pos_SI_B, self.model_parameters.SI_B,
                                    self.pos_SI_L, self.model_parameters.SI_L,
                                    self.pos_SI_D, self.model_parameters.SI_D,
                                    self.pos_kabs_B, self.model_parameters.kabs_B,
                                    self.pos_kabs_L, self.model_parameters.kabs_L,
                                    self.pos_kabs_D, self.model_parameters.kabs_D,
                                    self.pos_kabs_S, self.model_parameters.kabs_S,
                                    self.pos_kabs_H, self.model_parameters.kabs_H,
                                    self.pos_beta_B, self.model_parameters.beta_B,
                                    self.pos_beta_L, self.model_parameters.beta_L,
                                    self.pos_beta_D, self.model_parameters.beta_D,
                                    self.pos_beta_S, self.model_parameters.beta_S,
                                    theta) != -np.inf

    def check_realization_extended(self, theta: np.ndarray):
        """
        Function that checks if a copula extraction is valid or not depending on the prior constraints. (extended model)

        Parameters
        ----------
        theta : np.ndarray
            The copula extraction of unknown model parameters.

        Returns
        -------
        is_ok: bool
            The flag indicating if the extraction is ok or not.

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
        return log_prior_multi_meal_extended(self.model_parameters.VG,
                                             self.pos_SI_B, self.model_parameters.SI_B,
                                             self.pos_SI_L, self.model_parameters.SI_L,
                                             self.pos_SI_D, self.model_parameters.SI_D,
                                             self.pos_kabs_B, self.model_parameters.kabs_B,
                                             self.pos_kabs_L, self.model_parameters.kabs_L,
                                             self.pos_kabs_D, self.model_parameters.kabs_D,
                                             self.pos_kabs_S, self.model_parameters.kabs_S,
                                             self.pos_kabs_H, self.model_parameters.kabs_H,
                                             self.pos_beta_B, self.model_parameters.beta_B,
                                             self.pos_beta_L, self.model_parameters.beta_L,
                                             self.pos_beta_D, self.model_parameters.beta_D,
                                             self.pos_beta_S, self.model_parameters.beta_S,
                                             self.pos_SI_B2, self.model_parameters.SI_B2,
                                             self.pos_kabs_B2, self.model_parameters.kabs_B2,
                                             self.pos_kabs_L2, self.model_parameters.kabs_L2,
                                             self.pos_kabs_S2, self.model_parameters.kabs_S2,
                                             self.pos_beta_B2, self.model_parameters.beta_B2,
                                             self.pos_beta_L2, self.model_parameters.beta_L2,
                                             self.pos_beta_S2, self.model_parameters.beta_S2,
                                             theta) != -np.inf
