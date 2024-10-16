import numpy as np

import os
import pickle

from datetime import datetime

import copy

from py_replay_bg.model.model_parameters_t1d import ModelParametersT1DSingleMeal

from py_replay_bg.model.logpriors_t1d import log_prior_single_meal, log_prior_single_meal_exercise

from py_replay_bg.model.model_step_equations_t1d import identify_single_meal, identify_single_meal_exercise
from py_replay_bg.model.model_step_equations_t1d import model_step_equations_single_meal, model_step_equations_single_meal_exercise


class T1DModelSingleMeal:
    """
    A class that represents the type 1 diabetes model.

    ...
    Attributes 
    ----------
    yts: int
        The measurement (cgm) sample time.
    t: int
        The simulation timespan [min].
    tsteps: int
        The total simulation length [integration steps]
    tysteps: int
        The total simulation length [sample steps]
    glucose_model: string, {'IG','BG'}
        The model equation to be used as measured glucose.
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
    X0: list
        The initial conditions for the model state. If None cold_boot will be set to True.
    exercise: bool
        A boolean indicating if the model includes the exercise.
    
    Methods
    -------
    simulate(rbg_data, rbg):
        Function that simulates the model and returns the obtained results.
    log_posterior(theta, rbg_data):
        Function that computes the log posterior of unknown parameters.
    check_copula_extraction(theta):
        Function that checks if a copula extraction is valid or not.
    """

    def __init__(self, data, bw, yts=5, glucose_model='IG', u2ss=None, X0=None, previous_data_name=None, exercise=False, environment=None, identification_method='mcmc'):
        """
        Constructs all the necessary attributes for the Model object.

        Parameters
        ----------
        data : pandas.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        bw: float
            The body weight of the patient.
        yts: int, optional, default : 5 
            The measurement (cgm) sample time.
        glucose_model: str, {'IG','BG'}, optional, default : 'IG'
            The model equation to be used as measured glucose.
        X0: list, optional, default : None
            The initial conditions for the model state. If None cold_boot will be set to True.
        exercise: bool, optional, default : False
            A boolean indicating if the model includes the exercise.
        """

        # Time constants during simulation
        # self.ts = ts # DEPRECATED -> IT WILL BE ALWAYS = 1
        self.ts = 1
        self.yts = yts
        self.t = int((np.array(data.t)[-1].astype(datetime) - np.array(data.t)[0].astype(datetime)) / (
                60 * 1000000000) + self.yts)
        self.tsteps = self.t  # / self.ts
        self.tysteps = int(self.t / self.yts)

        # Glucose equation selection
        self.glucose_model = glucose_model

        # Model dimensionality
        self.nx = 9

        # Model parameters
        self.model_parameters = ModelParametersT1DSingleMeal(data, bw, u2ss)

        # Unknown parameters
        self.unknown_parameters = ['Gb', 'SG', 'ka2', 'kd', 'kempt']

        # initial guess for unknown parameter
        self.start_guess = np.array(
            [self.model_parameters.Gb, self.model_parameters.SG,
             self.model_parameters.ka2, self.model_parameters.kd, self.model_parameters.kempt])

        # initial guess for the SD of each parameter
        self.start_guess_sigma = np.array([1, 5e-4, 1e-3, 1e-3, 1e-3])

        # Attach SI
        self.pos_SI = self.start_guess.shape[0]
        self.unknown_parameters = np.append(self.unknown_parameters, 'SI')
        self.start_guess = np.append(self.start_guess, self.model_parameters.SI)
        self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)
        # Attach kabs
        self.pos_kabs = self.start_guess.shape[0]
        self.unknown_parameters = np.append(self.unknown_parameters, 'kabs')
        self.start_guess = np.append(self.start_guess, self.model_parameters.kabs)
        self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
        # Attach beta
        self.pos_beta = self.start_guess.shape[0]
        self.unknown_parameters = np.append(self.unknown_parameters, 'beta')
        self.start_guess = np.append(self.start_guess, self.model_parameters.beta)
        self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

        # Exercise
        self.exercise = exercise

        # Pre-initialization (for performance)
        self.G = np.empty([self.tsteps, ])
        self.x = np.zeros([self.nx, self.tsteps])
        self.CGM = np.empty([self.tysteps, ])
        self.A = np.empty([self.nx - 3, self.nx - 3])
        self.B = np.empty([self.nx - 3, ])

        # If previous_data_name is not None load previous_day_draws otherwise set it to None
        self.previous_data_name = previous_data_name
        self.previous_day_draws = None
        if self.previous_data_name is not None:
            with open(os.path.join(environment.replay_bg_path, 'results', identification_method,
                                   identification_method+'_' + previous_data_name + '.pkl'), 'rb') as file:
                previous_day_identification_results = pickle.load(file)
            self.previous_day_draws = previous_day_identification_results['draws']

        # Set initial conditions
        self.X0 = X0

        # IMPORTANT: manage the "remaining" rate of appearance due to meals in the previous portion of data.
        #   The rationale is to compute the Ra signal according to the "free" evolution of the meal system using X0 as
        #   starting point. The such Ra will represent a forcing input to the plasma glucose compartment during the
        #   simulation.

        # Create the "remaining" rate of appearance input of the previous day
        self.previous_Ra = np.zeros([self.tsteps, ])
        if self.previous_data_name is not None:

            # Get the initial values of the meal submodel
            xk = self.X0[2:5]
            # Set model parameter values
            if identification_method == 'mcmc':
                kgri = self.previous_day_draws['kempt']['samples_1'][0]
                kempt = self.previous_day_draws['kempt']['samples_1'][0]
                kabs = self.previous_day_draws['kabs']['samples_1'][0]
            else:
                kgri = self.previous_day_draws['kempt']
                kempt = self.previous_day_draws['kempt']
                kabs = self.previous_day_draws['kabs']

            # Compute the Ra forcing input
            for k in range(self.tsteps):
                xk[0] = xk[0] / (1 + self.ts * kgri)
                xk[1] = (xk[1] + self.ts * kgri * xk[0]) / (1 + self.ts * kempt)
                xk[2] = (xk[2] + self.ts * kempt * xk[1]) / (1 + self.ts * kabs)
                self.previous_Ra[k] = self.model_parameters.f * kabs * xk[2]

        # Set to 0 the initial conditions of meal-related compartments
        if self.X0 is not None:
            self.X0[2:5] = [0, 0, 0]

        # Remember identification method
        self.identification_method = identification_method

    def simulate(self, rbg_data, modality, rbg, sensors=None):
        """
        Function that simulates the model and returns the obtained results. This is the complete version suitable for
        replay.

        Parameters
        ----------
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.
        rbg : ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        G: np.ndarray
            An array containing the simulated glucose concentration (mg/dl).
        CGM: np.ndarray
            An array containing the simulated CGM trace (mg/dl).
        insulin_bolus: np.ndarray
            An array containing the simulated insulin bolus events (U/min). Also includes the correction insulin boluses.
        correction_bolus: np.ndarray
            An array containing the simulated corrective insulin bolus events (U/min).
        insulin_basal: np.ndarray
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
        basal_delayed = np.append(np.ones(shape=(mp.tau.__trunc__(),)) * basal[0], basal)

        # Shift the meal vector according to the delays
        meal_delayed = np.append(np.zeros(shape=(mp.beta.__trunc__(),)), meal)

        # Get the initial conditions
        k1 = mp.u2ss / mp.kd
        k2 = mp.kd / mp.ka2 * k1
        mp.Ipb = mp.ka2 / mp.ke * k2

        # If initial model conditions are None, set the default initial conditions, i.e., steady-state
        if self.X0 is None:
            self.x[:, 0] = [mp.G0, mp.Xpb, 0, 0, mp.Qgutb, k1, k2, mp.Ipb, mp.G0]
        # otherwise, set the initial model condition appropriately.
        else:
            # IMPORTANT: Scale the initial conditions of the insulin compartment to avoid "fake meal/bolus" effects

            # First, compute the k1, k2, and Ipb, macro parameters, using the model parameters associated to the current portion of data
            k1 = mp.u2ss / mp.kd
            k2 = mp.kd / mp.ka2 * k1
            mp.Ipb = mp.ka2 / mp.ke * k2

            # Second, do the same thing, but using the model parameters of the previous portion of data (i.e., the one that "generated" the provided X0)
            if self.identification_method == 'mcmc':
                k1_old = mp.u2ss / self.previous_day_draws['kd']['samples_1'][0]
                k2_old = self.previous_day_draws['kd']['samples_1'][0] / \
                         self.previous_day_draws['ka2']['samples_1'][0] * k1_old
                Ipb_old = self.previous_day_draws['ka2']['samples_1'][0] / mp.ke * k2_old
            else:
                k1_old = mp.u2ss / self.previous_day_draws['kd']
                k2_old = self.previous_day_draws['kd'] / self.previous_day_draws['ka2'] * k1_old
                Ipb_old = self.previous_day_draws['ka2'] / mp.ke * k2_old

            # Scale as --> initial_old:initial_new = k1old:k1new
            self.x[:, 0] = self.X0
            self.x[5, 0] = k1 * self.x[5, 0] / k1_old
            self.x[6, 0] = k2 * self.x[6, 0] / k2_old
            self.x[7, 0] = mp.Ipb * self.x[7, 0] / Ipb_old  # Ipb and Ipb_old are always the same (= ka2 / ke * kd / ka2 * u2ss / kd = u2ss / ke)

        # Set the initial glucose value
        self.G[0] = self.x[self.nx - 1, 0] if self.glucose_model == 'IG' else self.x[0, 0]

        # Set the input state-space matrix
        k1 = 1 / (1 + mp.kgri)
        k2 = mp.kgri / (1 + mp.kempt)
        k3 = 1 / (1 + mp.kempt)
        kb = 1 / (1 + mp.kabs)
        ki1 = 1 / (1 + mp.kd)
        ki2 = 1 / (1 + mp.ka2)
        kie = 1 / (1 + mp.ke)
        self.A[:] = [[k1, 0, 0, 0, 0, 0],
                      [k2, k3, 0, 0, 0, 0],
                      [0, mp.kempt * kb, kb, 0, 0, 0],
                      [0, 0, 0, ki1, 0, 0],
                      [0, 0, 0, mp.kd * ki2, ki2, 0],
                      [0, 0, 0, 0, mp.ka2 * kie, kie]]

        # Run simulation in two ways depending on the modality to speed up the identification process
        if is_replay:

            # Set the initial cgm value if modality is 'replay' and make copies of meal vectors
            if sensors.cgm.model == 'IG':
                self.CGM[0] = self.x[self.nx - 1, 0]  # y(k) = IG(k)
            elif sensors.cgm.model == 'CGM':
                self.CGM[0] = sensors.cgm.measure(self.x[self.nx - 1, 0], 0)

            for k in np.arange(1, self.tsteps):
                # Meal generation module
                if rbg.environment.cho_source == 'generated':
                    # Call the meal generator function handler
                    ch, ma, t, rbg.dss = rbg.dss.meal_generator_handler(self.G[0:k], meal[0:k] * mp.to_g, meal_type[0:k], meal_announcement[0:k], hypotreatments[0:k],
                                                                        bolus[0:k] * mp.to_g, basal[0:k] * mp.to_g,
                                                                        rbg_data.t_hour[0:k], k-1, rbg.dss, rbg.environment.scenario)
                    ch_mgkg = ch * mp.to_mgkg
                    # Add the CHO to the input (remember to add the delay)
                    if t == 'M':
                        if (k+mp.beta.__trunc__()) < self.tsteps:
                            meal_delayed[k+mp.beta.__trunc__()] = meal_delayed[k+mp.beta.__trunc__()] + ch_mgkg
                    elif t == 'O':
                        meal_delayed[k] = meal_delayed[k] + ch_mgkg

                    # Update the event vectors
                    meal_announcement[k] = meal_announcement[k] + ma
                    meal_type[k] = t

                    # Add the CHO to the non-delayed meal vector.
                    meal[k] = meal[k] + ch_mgkg

                # Bolus generation module
                if rbg.environment.bolus_source == 'dss':
                    # Call the bolus calculator function handler
                    bo, rbg.dss = rbg.dss.bolus_calculator_handler(self.G[0:k], meal_announcement[0:k], meal_type[0:k], hypotreatments[0:k], bolus[0:k] * mp.to_g,
                                                                   basal[0:k] * mp.to_g, rbg_data.t_hour[0:k], k-1, rbg.dss)
                    bo_mgkg = bo * mp.to_mgkg

                    # Add the bolus to the input bolus vector.
                    if(k+mp.tau.__trunc__()) < self.tsteps:
                        bolus_delayed[k + mp.tau.__trunc__()] = bolus_delayed[k + mp.tau.__trunc__()] + bo_mgkg

                    # Add the bolus to the non-delayed bolus vector.
                    bolus[k] = bolus[k] + bo_mgkg

                # Basal rate generation module
                if rbg.environment.basal_source == 'dss':
                    # Call the basal rate function handler
                    ba, rbg.dss = rbg.dss.basal_handler(self.G[0:k], meal_announcement[0:k], meal_type[0:k], hypotreatments[0:k], bolus[0:k] * mp.to_g,
                                                        basal[0:k] * mp.to_g, rbg_data.t_hour[0:k], k-1, rbg.dss)
                    ba_mgkg = ba * mp.to_mgkg
                    # Add the basal to the input basal vector.
                    if (k + mp.tau.__trunc__()) < self.tsteps:
                        basal_delayed[k + mp.tau.__trunc__()] = basal_delayed[
                                                                    k + mp.tau.__trunc__()] + ba_mgkg

                    # Add the bolus to the non-delayed bolus vector.
                    basal[k] = basal[k] + ba_mgkg

                # Hypotreatment generation module
                if rbg.dss.enable_hypotreatments:
                    # Call the hypotreatment handler
                    ht, rbg.dss = rbg.dss.hypotreatments_handler(self.G[0:k], meal_announcement[0:k], meal_type[0:k], hypotreatments[0:k],
                                                                 bolus[0:k] * mp.to_g, basal[0:k] * mp.to_g, rbg_data.t_hour[0:k], k - 1, rbg.dss)
                    ht_mgkg = ht * mp.to_mgkg
                    meal_delayed[k] = meal_delayed[k] + ht_mgkg

                    # Update the hypotreatments event vectors
                    hypotreatments[k - 1] = hypotreatments[k - 1] + ht

                # Correction bolus delivery module if it is enabled
                if rbg.dss.enable_correction_boluses:
                    # Call the correction boluses handler
                    cb, rbg.dss = rbg.dss.correction_boluses_handler(self.G[0:k], meal_announcement[0:k], meal_type[0:k], hypotreatments[0:k],
                                                                 bolus[0:k] * mp.to_g, basal[0:k] * mp.to_g, rbg_data.t_hour[0:k], k - 1, rbg.dss)
                    cb_mgkg = cb * mp.to_mgkg
                    # Add the cb to the input bolus vector.
                    if (k + mp.tau.__trunc__()) < self.tsteps:
                        bolus_delayed[k + mp.tau.__trunc__()] = bolus_delayed[
                                                                    k + mp.tau.__trunc__()] + cb_mgkg

                    # Add the bolus to the non-delayed bolus vector.
                    bolus[k] = bolus[k] + cb_mgkg

                    # Update the correction_bolus event vectors
                    correction_bolus[k - 1] = correction_bolus[k - 1] + cb

                # Integration step
                self.x[:, k] = model_step_equations_single_meal(self.A, bolus_delayed[k - 1] + basal_delayed[k - 1], meal_delayed[k - 1], rbg_data.t_hour[k - 1],
                                                                self.x[:, k - 1], self.B, mp.r1, mp.r2, mp.kgri, mp.kd, mp.p2, mp.SI,
                                                                mp.VI, mp.VG, mp.Ipb, mp.SG, mp.Gb, mp.f, mp.kabs, mp.alpha, self.previous_Ra[k-1])

                self.G[k] = self.x[self.nx - 1, k] if self.glucose_model == 'IG' else self.x[0, k]

                # Get the cgm
                if np.mod(k, sensors.cgm.ts) == 0:
                    if sensors.cgm.model == 'IG':
                        self.CGM[int(k / sensors.cgm.ts)] = self.x[self.nx-1, k]  # y(k) = IG(k)
                    if sensors.cgm.model == 'CGM':
                        if k+sensors.cgm.t_offset >= sensors.cgm.max_lifetime:
                            # connect new sensor
                            sensors.cgm.connect_new_cgm(connected_at=k)
                            # gestire offset
                        self.CGM[int(k / sensors.cgm.ts)] = sensors.cgm.measure(self.x[self.nx - 1, k], (k - sensors.cgm.connected_at) / (24 * 60))

            # TODO: add vo2
            return self.x[0, :].copy(), self.x[:, -1].copy(), self.CGM.copy(), bolus * mp.to_g, correction_bolus, basal * mp.to_g, meal * mp.to_g, hypotreatments, meal_announcement, self.x.copy()

        else:

            # Run simulation
            self.x = identify_single_meal(self.tsteps, self.x, self.A, self.B, bolus_delayed, basal_delayed,meal_delayed, rbg_data.t_hour,
                        mp.r1, mp.r2, mp.kgri, mp.kd, mp.p2, mp.SI, mp.VI, mp.VG, mp.Ipb, mp.SG, mp.Gb, mp.f, mp.kabs, mp.alpha, self.previous_Ra)

            #Return just the glucose vector if modality == 'identification'
            return self.x[self.nx - 1, :] if self.glucose_model == 'IG' else self.x[0, :]

    def __log_likelihood(self, theta, rbg_data):
        """
        Internal function that computes the log likelihood of unknown parameters.

        Parameters
        ----------
        theta : array
            The current guess of unknown model parameters.
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.

        Returns
        -------
        log_likelihood: float
            The value of the log likelihood of current unknown model paraemters guess.

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
        self.model_parameters.Gb, self.model_parameters.SG, self.model_parameters.ka2, self.model_parameters.kd, self.model_parameters.kempt, self.model_parameters.SI, self.model_parameters.kabs, self.model_parameters.beta = theta

        # Enforce constraints
        self.model_parameters.kgri = self.model_parameters.kempt

        # Simulate the model
        G = self.simulate(rbg_data=rbg_data, modality='identification', rbg=None)

        # Sample the simulation
        G = G[0::self.yts]

        # Compute and return the log likelihood
        return -0.5 * np.sum(
            ((G[rbg_data.glucose_idxs] - rbg_data.glucose[rbg_data.glucose_idxs]) / self.model_parameters.SDn) ** 2)

    def neg_log_posterior(self, theta, rbg_data):
        return - self.log_posterior(theta, rbg_data)

    def log_posterior(self, theta, rbg_data):
        """
        Function that computes the log posterior of unknown parameters.

        Parameters
        ----------
        theta : array
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
        p = log_prior_single_meal(self.model_parameters.VG, theta)
        return -np.inf if p == -np.inf else p + self.__log_likelihood(theta, rbg_data)

    def check_extraction(self, theta):
        """
        Function that checks if a copula extraction is valid or not depending on the prior constraints.

        Parameters
        ----------
        theta : array
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
        return log_prior_single_meal(self.model_parameters.VG, theta) != -np.inf

    def check_extraction_exercise(self, theta):
        """
        Function that checks if a copula extraction is valid or not depending on the prior constraints.

        Parameters
        ----------
        theta : array
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
        return log_prior_single_meal_exercise(self.model_parameters.VG, theta) != -np.inf
