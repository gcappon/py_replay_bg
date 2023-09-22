import numpy as np
import pandas as pd

from datetime import datetime

import copy

from utils.stats import log_lognorm, log_gamma, log_norm


class T1DModel:
    """
    A class that represents the multi meal type 1 diabetes model.

    ...
    Attributes 
    ----------
    is_single_meal: bool
        A flag indicating if the model will be used as single meal or multi meal.
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
    unknown_parameters: array
        An array that contains the list of unknown parameters to be estimated.
    start_guess: array
        An array that contains the initial starting point to be used by the mcmc procedure.
    start_guess_sigma: array
        An array that contains the initial starting SD of unknown parameters to be used by the mcmc procedure.
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

    def __init__(self, data, BW, yts=5, glucose_model='IG', is_single_meal=True, exercise=False):
        """
        Constructs all the necessary attributes for the Model object.

        Parameters
        ----------
        data : pandas.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        yts: int, optional, default : 5 
            The measurement (cgm) sample time.
        glucose_model: string, {'IG','BG'}, optional, default : 'IG'
            The model equation to be used as measured glucose.
        exercise: bool, optional, default : False
            A boolean indicating if the model includes the exercise.
        """

        self.is_single_meal = is_single_meal

        # Time constants during simulation
        # DEPRECATED self.ts = ts -> ALWAYS = 1
        self.yts = yts
        self.t = int((np.array(data.t)[-1].astype(datetime) - np.array(data.t)[0].astype(datetime)) / (
                60 * 1000000000) + self.yts)

        self.tsteps = self.t
        self.tysteps = int(self.t / self.yts)

        # Glucose equation selection
        self.glucose_model = glucose_model  # glucose equation selection {'BG','IG'}

        # Model dimensionality
        self.nx = 9 if self.is_single_meal else 21

        # Model parameters
        self.model_parameters = ModelParameters(data, BW, self.is_single_meal)

        # Unknown parameters
        self.unknown_parameters = ['Gb', 'SG', 'ka2', 'kd', 'kempt']

        # initial guess for unknown parameter
        self.start_guess = np.array(
            [self.model_parameters.Gb, self.model_parameters.SG,
             self.model_parameters.ka2, self.model_parameters.kd, self.model_parameters.kempt])

        # initial guess for the SD of each parameter
        self.start_guess_sigma = np.array([1, 5e-4, 1e-3, 1e-3, 1e-3])

        # Get the hour of the day for each data point
        t = np.array(data.t.dt.hour.values).astype(int)

        if self.is_single_meal:
            # Attach SI
            self.pos_SI = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'SI')
            self.start_guess = np.append(self.start_guess, self.model_parameters.SI)
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)
            # Attach kabs and beta
            self.pos_kabs = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'kabs')
            self.start_guess = np.append(self.start_guess, self.model_parameters.kabs)
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
            self.pos_beta = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'beta')
            self.start_guess = np.append(self.start_guess, self.model_parameters.beta)
            self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

        else:
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

        # Exercise
        self.exercise = exercise

        # Pre-initialization (for performance)
        self.G = np.empty([self.tsteps, ])
        self.x = np.zeros([self.nx, self.tsteps])
        self.CGM = np.empty([self.tysteps, ])
        self.A = np.empty([self.nx - 3, self.nx - 3])
        self.B = np.empty([self.nx - 3, ])

    def __get_initial_conditions(self, mp):

        k1 = mp.u2ss / mp.kd
        k2 = mp.kd / mp.ka2 * k1
        # Set the basal plasma insulin
        mp.Ipb = mp.ka2 / mp.ke * k2

        # Return the initial model conditions
        return [mp.G0, mp.Xpb, 0, 0, mp.Qgutb, k1, k2, mp.Ipb, mp.G0] if self.is_single_meal else [mp.G0, mp.Xpb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, 0, 0, mp.Qgutb, k1, k2, mp.Ipb, mp.G0]

    def simulate(self, rbg_data, modality, rbg):
        """
        Function that simulates the model and returns the obtained results. This is the complete version suitable for replay.

        Parameters
        ----------
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.
        rbg : ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        G: array
            An array containing the simulated glucose concentration (mg/dl).
        CGM: array
            An array containing the simulated CGM trace (mg/dl).
        insulin_bolus: array
            An array containing the simulated insulin bolus events (U/min). Also includes the correction insulin boluses.
        correction_bolus: array
            An array containing the simulated corrective insulin bolus events (U/min).
        insulin_basal: array
            An array containing the simulated basal insulin events (U/min).
        CHO: array
            An array containing the simulated CHO events (g/min).
        hypotreatments: array
            An array containing the simulated hypotreatments events (g/min).
        meal_announcement: array
            An array containing the simulated meal announcements events needed for bolus calculation (g/min).
        x: matrix
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

        # Utility flag for checking the modality
        is_replay = modality == 'replay'

        # Get the initial conditions
        initial_conditions = self.__get_initial_conditions(mp)

        # Set the initial glucose value
        self.G[0] = initial_conditions[self.nx - 1] if self.glucose_model == 'IG' else initial_conditions[0]

        # Initialize the state matrix
        self.x[:, 0] = initial_conditions

        # Create the state-space matrix for the inputs
        if self.is_single_meal:
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
                          [0, 0, 0, 0, mp.ka2 * kie, kie]
                          ]

        else:
            k1 = 1 / (1 + mp.kgri)
            k2 = mp.kgri / (1 + mp.kempt)
            k3 = 1 / (1 + mp.kempt)
            kb = 1 / (1 + mp.kabs_B)
            kl = 1 / (1 + mp.kabs_L)
            kd = 1 / (1 + mp.kabs_D)
            ks = 1 / (1 + mp.kabs_S)
            kh = 1 / (1 + mp.kabs_H)
            ki1 = 1 / (1 + mp.kd)
            ki2 = 1 / (1 + mp.ka2)
            kie = 1 / (1 + mp.ke)
            self.A[:] = [[k1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [k2, k3, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, mp.kempt * kb, kb, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, k1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, k2, k3, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, mp.kempt * kl, kl, 0,
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, k1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, k2, k3,
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, mp.kempt * kd,
                           kd, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, k1, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, k2, k3, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, mp.kempt * ks,
                           ks, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, k1, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, k2, k3, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, mp.kempt * kh,
                           kh, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ki1, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, mp.kd * ki2,
                           ki2, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                           mp.ka2 * kie, kie]
                          ]
        #Initialize the input vectors
        if is_replay:

            # Set the initial cgm value
            if rbg.sensors.cgm.model == 'IG':
                self.CGM[0] = initial_conditions[self.nx - 1]  # y(k) = IG(k)
            elif rbg.sensors.cgm.model == 'CGM':
                self.CGM[0] = rbg.sensors.cgm.measure(initial_conditions[self.nx - 1], 0)

            # Make copies of the inputs if replay to avoid to overwrite fields
            bolus = rbg_data.bolus * 1
            basal = rbg_data.basal * 1
            meal = rbg_data.meal * 1
            if self.is_single_meal:
                meal_delayed = np.append(np.zeros(shape=(mp.beta.__trunc__(),)), meal)
            else:
                meal_B = rbg_data.meal_B * 1
                meal_L = rbg_data.meal_L * 1
                meal_S = rbg_data.meal_D * 1
                meal_D = rbg_data.meal_S * 1
                meal_H = rbg_data.meal_H * 1

                meal_B_delayed = np.append(np.zeros(shape=(mp.beta_B.__trunc__(),)), meal_B)
                meal_L_delayed = np.append(np.zeros(shape=(mp.beta_L.__trunc__(),)), meal_L)
                meal_D_delayed = np.append(np.zeros(shape=(mp.beta_D.__trunc__(),)), meal_D)
                meal_S_delayed = np.append(np.zeros(shape=(mp.beta_S.__trunc__(),)), meal_S)


            meal_type = copy.copy(rbg_data.meal_type)
            meal_announcement = rbg_data.meal_announcement * 1

            correction_bolus = bolus * 0
            hypotreatments = meal * 0  # Hypotreatments definition is not present in single-meal --> set to 0

        else:

            if self.is_single_meal:
                meal = rbg_data.meal
                # Shift the meal vector according to the delays
                meal_delayed = np.append(np.zeros(shape=(mp.beta.__trunc__(),)), meal)

            else:

                meal_B = rbg_data.meal_B
                meal_L = rbg_data.meal_L
                meal_D = rbg_data.meal_D
                meal_H = rbg_data.meal_H
                meal_S = rbg_data.meal_S

                # Shift the meal vector according to the delays
                meal_B_delayed = np.append(np.zeros(shape=(mp.beta_B.__trunc__(),)), meal_B)
                meal_L_delayed = np.append(np.zeros(shape=(mp.beta_L.__trunc__(),)), meal_L)
                meal_D_delayed = np.append(np.zeros(shape=(mp.beta_D.__trunc__(),)), meal_D)
                meal_S_delayed = np.append(np.zeros(shape=(mp.beta_S.__trunc__(),)), meal_S)

        bolus = rbg_data.bolus * 1
        basal = rbg_data.basal * 1

        # Shift the insulin vectors according to the delays
        bolus_delayed = np.append(np.zeros(shape=(mp.tau.__trunc__(),)), bolus)
        basal_delayed = np.append(np.ones(shape=(mp.tau.__trunc__(),)) * basal[0], basal)

        #Run simulation in two ways depending on the modality to speed-up the identification process
        if is_replay:

            for k in np.arange(1, self.tsteps):
                # Meal generation module
                if rbg.environment.cho_source == 'generated':
                    # Call the meal generator function handler
                    ch, ma, t, rbg.dss = rbg.dss.meal_generator_handler(self.G[0:k], meal[0:k] * mp.to_g, meal_type[0:k], meal_announcement[0:k], hypotreatments[0:k],
                                                                        bolus[0:k] * mp.to_g, basal[0:k] * mp.to_g,
                                                                        rbg_data.t_hour[0:k], k-1, rbg.dss, self.is_single_meal)
                    ch_mgkg = ch * mp.to_mgkg
                    # Add the CHO to the input (remember to add the delay)
                    if self.is_single_meal:
                        if t == 'M':
                            if (k+mp.beta.__trunc__()) < self.tsteps:
                                meal_delayed[k+mp.beta.__trunc__()] = meal_delayed[k+mp.beta.__trunc__()] + ch_mgkg
                        elif t == 'O':
                            meal_delayed[k] = meal_delayed[k] + ch_mgkg
                    else:
                        if t == 'B':
                            if(k+mp.beta_B.__trunc__()) < self.tsteps:
                                meal_B[k] = meal_B[k] + ch_mgkg
                                meal_B_delayed[k+mp.beta_B.__trunc__()] = meal_B_delayed[k+mp.beta_B.__trunc__()] + ch_mgkg
                        elif t == 'L':
                            if (k + mp.beta_L.__trunc__()) < self.tsteps:
                                meal_L[k] = meal_L[k] + ch_mgkg
                                meal_L_delayed[k + mp.beta_L.__trunc__()] = meal_L_delayed[k + mp.beta_L.__trunc__()] + ch_mgkg
                        elif t == 'D':
                            if(k+mp.beta_D.__trunc__()) < self.tsteps:
                                meal_D[k] = meal_D[k] + ch_mgkg
                                meal_D_delayed[k+mp.beta_D.__trunc__()] = meal_D_delayed[k+mp.beta_D.__trunc__()] + ch_mgkg
                        elif t == 'S':
                            if (k + mp.beta_S.__trunc__()) < self.tsteps:
                                meal_S[k] = meal_S[k] + ch_mgkg
                                meal_S_delayed[k + mp.beta_S.__trunc__()] = meal_S_delayed[k + mp.beta_S.__trunc__()] + ch_mgkg

                    # Update the event vectors
                    meal_announcement[k] = meal_announcement[k] + ma
                    meal_type[k] = t #TODO: it should be delayed

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
                    if self.is_single_meal:
                        meal_delayed[k] = meal_delayed[k] + ht_mgkg
                    else:
                        meal_H[k] = meal_H[k] + ht_mgkg

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

                #Integration step
                if self.is_single_meal:
                    self.x[:, k] = self.__model_step_equations_single_meal(self.A, mp,
                                                                          bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                                          meal_delayed[k - 1],
                                                                          rbg_data.t_hour[k - 1],
                                                                          self.x[:, k - 1], self.B)  # k-1
                else:
                    self.x[:, k] = self.__model_step_equations_multi_meal(self.A, mp, bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                      meal_B_delayed[k - 1], meal_L_delayed[k - 1],
                                                      meal_D_delayed[k - 1], meal_S_delayed[k - 1], meal_H[k - 1],
                                                      rbg_data.t_hour[k - 1], self.x[:, k - 1], self.B)  # k-1

                self.G[k] = self.x[self.nx - 1, k] if self.glucose_model == 'IG' else self.x[0, k]

                # Get the cgm
                if np.mod(k, rbg.sensors.cgm.ts) == 0:
                    if rbg.sensors.cgm.model == 'IG':
                        self.CGM[int(k / rbg.sensors.cgm.ts)] = self.x[self.nx, k]  # y(k) = IG(k)
                    if rbg.sensors.cgm.model == 'CGM':
                        self.CGM[int(k / rbg.sensors.cgm.ts)] = rbg.sensors.cgm.measure(self.x[self.nx - 1, k], k / (24 * 60))

            # TODO: add vo2
            return self.x[0, :].copy(), self.CGM.copy(), bolus * mp.to_g, correction_bolus, basal * mp.to_g, meal * mp.to_g, hypotreatments, meal_announcement, self.x.copy()

        else:

            if self.is_single_meal:

                #Run simulation
                for k in np.arange(1, self.tsteps):
                    # Integration step
                    self.x[:, k] = self.__model_step_equations_single_meal(self.A, mp, bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                          meal_delayed[k - 1], rbg_data.t_hour[k - 1], self.x[:, k - 1], self.B)
            else:

                #Run simulation
                for k in np.arange(1, self.tsteps):
                    # Integration step
                    self.x[:, k] = self.__model_step_equations_multi_meal(self.A, mp, bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                          meal_B_delayed[k - 1], meal_L_delayed[k - 1],
                                                          meal_D_delayed[k - 1], meal_S_delayed[k - 1], meal_H[k - 1],
                                                          rbg_data.t_hour[k - 1], self.x[:, k - 1], self.B)
            #Return just the glucose vector if modality == 'identification'
            return self.x[self.nx - 1, :] if self.glucose_model == 'IG' else self.x[0, :]

    def __model_step_equations_single_meal(self, A, mp, I, CHO, hour_of_the_day, xkm1, B):
        """
        Internal function that simulates a step of the model using backward-euler method.

        Parameters
        ----------
        I : float
            The (basal + bolus) insulin given as input.
        CHO_B : float
            The meal breakfast cho given as input.
        CHO_L : float
            The meal lunch cho given as input.
        CHO_D : float
            The meal dinner cho given as input.
        CHO_S : float
            The meal snack cho given as input.
        CHO_H : float
            The meal hypotreatment cho given as input.
        hour_of_the_day : float
            The hour of the day given as input.
        xkm1 : array
            The model state values at the previous step (k-1).

        Returns
        -------
        xk: array
            The model state values at the current step k.

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

        xk = xkm1

        # Compute glucose risk
        risk = 1

        # Compute the risk
        if 119.13 > xkm1[0] >= 60:
            risk = risk + 10 * mp.r1 * (np.log(xkm1[0]) ** mp.r2 - np.log(119.13) ** mp.r2) ** 2
        elif xkm1[0] < 60:
            risk = risk + 10 * mp.r1 * (np.log(60) ** mp.r2 - np.log(119.13) ** mp.r2) ** 2

        # Compute the model state at time k using backward Euler method

        B[:] = [CHO / (1 + mp.kgri), 0, 0,
             I / (1 + mp.kd), 0, 0]

        xk[2:8] = A @ xkm1[2:8] + B

        xk[1] = (xkm1[1] + mp.p2 * (mp.SI / mp.VI) * (xk[7] - mp.Ipb)) / (1 + mp.p2)
        xk[0] = (xkm1[0] + mp.SG * mp.Gb + mp.f * mp.kabs * xk[4] / mp.VG) / (1 + mp.SG + (1 + mp.r1 * risk) * xk[1])
        xk[8] = (xkm1[8] + mp.alpha * xk[0]) / (1 + mp.alpha)

        return xk

    def __model_step_equations_multi_meal(self, A, mp, I, CHO_B, CHO_L, CHO_D, CHO_S, CHO_H, hour_of_the_day, xkm1, B):
        """
        Internal function that simulates a step of the model using backward-euler method.

        Parameters
        ----------
        I : float
            The (basal + bolus) insulin given as input.
        CHO_B : float
            The meal breakfast cho given as input.
        CHO_L : float
            The meal lunch cho given as input.
        CHO_D : float
            The meal dinner cho given as input.
        CHO_S : float
            The meal snack cho given as input.
        CHO_H : float
            The meal hypotreatment cho given as input.
        hour_of_the_day : float
            The hour of the day given as input.
        xkm1 : array
            The model state values at the previous step (k-1).

        Returns
        -------
        xk: array
            The model state values at the current step k.
        
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

        xk = xkm1

        # Set the insulin sensitivity based on the time of the day
        if hour_of_the_day < 4 or hour_of_the_day >= 17:
            SI = mp.SI_D
        elif 4 <= hour_of_the_day < 11:
            SI = mp.SI_B
        else:
            SI = mp.SI_L
        # Compute glucose risk

        # Set default risk
        risk = 1

        # Compute the risk
        if 119.13 > xkm1[0] >= 60:
            risk = risk + 10 * mp.r1 * (np.log(xkm1[0]) ** mp.r2 - np.log(119.13) ** mp.r2) ** 2
        elif xkm1[0] < 60:
            risk = risk + 10 * mp.r1 * (np.log(60) ** mp.r2 - np.log(119.13) ** mp.r2) ** 2

        # Compute the model state at time k using backward Euler method

        kc = 1 / (1 + mp.kgri)
        B[:] = [CHO_B * kc, 0, 0,
             CHO_L * kc, 0, 0,
             CHO_D * kc, 0, 0,
             CHO_S * kc, 0, 0,
             CHO_H * kc, 0, 0,
             I / (1 + mp.kd), 0, 0]

        xk[2:20] = A @ xkm1[2:20] + B

        xk[1] = (xkm1[1] + mp.p2 * (SI / mp.VI) * (xk[19] - mp.Ipb)) / (1 + mp.p2)
        xk[0] = (xkm1[0] + mp.SG * mp.Gb + mp.f * (
                    mp.kabs_B * xk[4] + mp.kabs_L * xk[7] + mp.kabs_D * xk[10] + mp.kabs_S * xk[13] + mp.kabs_H * xk[
                17]) / mp.VG) / (1 + mp.SG + (1 + mp.r1 * risk) * xk[1])
        xk[20] = (xkm1[20] + mp.alpha * xk[0]) / (1 + mp.alpha)

        return xk

    def __log_prior_single_meal(self, theta):
        """
        Internal function that computes the log prior of unknown parameters.

        Parameters
        ----------
        theta : array
            The current guess of unknown model parameters.

        Returns
        -------
        log_prior: float
            The value of the log prior of current unknown model parameters guess.

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

        # unpack the model parameters
        Gb, SG, ka2, kd, kempt, SI, kabs, beta = theta

        # compute each log prior
        logprior_SI = log_gamma(SI * self.model_parameters.VG, 3.3, 1 / 5e-4)

        logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
        logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf
        logprior_ka2 = log_lognorm(ka2, mu=-4.2875, sigma=0.4274) if 0 < ka2 < kd and ka2 < 1 else -np.inf
        logprior_kd = log_lognorm(kd, mu=-3.5090, sigma=0.6187) if 0 < ka2 < kd and kd < 1 else -np.inf
        logprior_kempt = log_lognorm(kempt, mu=-1.9646, sigma=0.7069) if 0 < kempt < 1 else -np.inf

        logprior_kabs = log_lognorm(kabs, mu=-5.4591,
                                    sigma=1.4396) if kempt >= kabs and 0 < kabs < 1 else -np.inf

        logprior_beta = 0 if 0 <= beta <= 60 else -np.inf

        # Sum everything and return the value
        return logprior_SI + logprior_Gb + logprior_SG + logprior_ka2 + logprior_kd + logprior_kempt + logprior_kabs + logprior_beta

    def __log_prior_multi_meal(self, theta):
        """
        Internal function that computes the log prior of unknown parameters.

        Parameters
        ----------
        theta : array
            The current guess of unknown model parameters.

        Returns
        -------
        log_prior: float
            The value of the log prior of current unknown model parameters guess.
        
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

        # unpack the model parameters
        # SI, Gb, SG, p2, ka2, kd, kempt, kabs, beta = theta

        Gb, SG, ka2, kd, kempt = theta[0:5]

        SI_B = theta[self.pos_SI_B] if self.pos_SI_B else self.model_parameters.SI_B
        SI_L = theta[self.pos_SI_L] if self.pos_SI_L else self.model_parameters.SI_L
        SI_D = theta[self.pos_SI_D] if self.pos_SI_D else self.model_parameters.SI_D

        kabs_B = theta[self.pos_kabs_B] if self.pos_kabs_B else self.model_parameters.kabs_B
        kabs_L = theta[self.pos_kabs_L] if self.pos_kabs_L else self.model_parameters.kabs_L
        kabs_D = theta[self.pos_kabs_D] if self.pos_kabs_D else self.model_parameters.kabs_D
        kabs_S = theta[self.pos_kabs_S] if self.pos_kabs_S else self.model_parameters.kabs_S
        kabs_H = theta[self.pos_kabs_H] if self.pos_kabs_H else self.model_parameters.kabs_H

        beta_B = theta[self.pos_beta_B] if self.pos_beta_B else self.model_parameters.beta_B
        beta_L = theta[self.pos_beta_L] if self.pos_beta_L else self.model_parameters.beta_L
        beta_D = theta[self.pos_beta_D] if self.pos_beta_D else self.model_parameters.beta_D
        beta_S = theta[self.pos_beta_S] if self.pos_beta_S else self.model_parameters.beta_S

        # compute each log prior
        # NB: gamma.pdf(0.001 * 1.45, 3.3, scale=5e-4) <=> gampdf(0.001*1.45, 3.3, 5e-4)
        logprior_SI_B = log_gamma(SI_B * self.model_parameters.VG, 3.3, 1 / 5e-4)
        logprior_SI_L = log_gamma(SI_B * self.model_parameters.VG, 3.3, 1 / 5e-4)
        logprior_SI_D = log_gamma(SI_B * self.model_parameters.VG, 3.3, 1 / 5e-4)

        logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
        logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf
        # logprior_p2 = np.log(stats.norm.pdf(np.sqrt(p2), 0.11, 0.004)) if 0 < p2 < 1 else -np.inf
        logprior_ka2 = log_lognorm(ka2, mu=-4.2875, sigma=0.4274) if 0 < ka2 < kd and ka2 < 1 else -np.inf
        logprior_kd = log_lognorm(kd, mu=-3.5090, sigma=0.6187) if 0 < ka2 < kd and kd < 1 else -np.inf
        logprior_kempt = log_lognorm(kempt, mu=-1.9646, sigma=0.7069) if 0 < kempt < 1 else -np.inf

        logprior_kabs_B = log_lognorm(kabs_B, mu=-5.4591,
                                      sigma=1.4396) if kempt >= kabs_B and 0 < kabs_B < 1 else -np.inf
        logprior_kabs_L = log_lognorm(kabs_L, mu=-5.4591,
                                      sigma=1.4396) if kempt >= kabs_L and 0 < kabs_L < 1 else -np.inf
        logprior_kabs_D = log_lognorm(kabs_D, mu=-5.4591,
                                      sigma=1.4396) if kempt >= kabs_D and 0 < kabs_D < 1 else -np.inf
        logprior_kabs_S = log_lognorm(kabs_S, mu=-5.4591,
                                      sigma=1.4396) if kempt >= kabs_S and 0 < kabs_S < 1 else -np.inf
        logprior_kabs_H = log_lognorm(kabs_H, mu=-5.4591,
                                      sigma=1.4396) if kempt >= kabs_H and 0 < kabs_H < 1 else -np.inf

        logprior_beta_B = 0 if 0 <= beta_B <= 60 else -np.inf
        logprior_beta_L = 0 if 0 <= beta_L <= 60 else -np.inf
        logprior_beta_D = 0 if 0 <= beta_D <= 60 else -np.inf
        logprior_beta_S = 0 if 0 <= beta_S <= 60 else -np.inf

        # Sum everything and return the value
        return logprior_SI_B + logprior_SI_L + logprior_SI_D + logprior_Gb + logprior_SG + logprior_ka2 + logprior_kd + logprior_kempt + logprior_kabs_B + logprior_kabs_L + logprior_kabs_D + logprior_kabs_S + logprior_kabs_H + logprior_beta_B + logprior_beta_L + logprior_beta_D + logprior_beta_S

    def __log_likelihood_single_meal(self, theta, rbg_data):
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

    def __log_likelihood_multi_meal(self, theta, rbg_data):
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
        self.model_parameters.Gb, self.model_parameters.SG, self.model_parameters.ka2, self.model_parameters.kd, self.model_parameters.kempt = theta[
                                                                                                                                               0:5]

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
        G = self.simulate(rbg_data=rbg_data, modality='identification', rbg=None)

        # Sample the simulation
        G = G[0::self.yts]

        # Compute and return the log likelihood
        return -0.5 * np.sum(
            ((G[rbg_data.glucose_idxs] - rbg_data.glucose[rbg_data.glucose_idxs]) / self.model_parameters.SDn) ** 2)

    def log_posterior_single_meal(self, theta, rbg_data):
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
        p = self.__log_prior_single_meal(theta)
        return -np.inf if p == -np.inf else p + self.__log_likelihood_single_meal(theta, rbg_data)

    def log_posterior_multi_meal(self, theta, rbg_data):
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
        p = self.__log_prior_multi_meal(theta)
        return -np.inf if p == -np.inf else p + self.__log_likelihood_multi_meal(theta, rbg_data)

    def check_copula_extraction(self, theta):
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
        return self.__log_prior_single_meal(theta) != -np.inf if self.is_single_meal else self.__log_prior_multi_meal(theta) != -np.inf


class ModelParameters:

    def __init__(self, data, BW, is_single_meal):

        """
        Function that returns the default parameters values of the model.

        Parameters
        ----------
        data : pd.DataFrame
                Pandas dataframe which contains the data to be used by the tool.
        BW : double
            The patient's body weight.

        Returns
        -------
        model_parameters: dict
            A dictionary containing the default model parameters.

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
        # Initial conditions
        self.Xpb = 0.0  # Insulin action initial condition
        self.Qgutb = 0.0  # Intestinal content initial condition

        # Glucose-insulin submodel parameters
        self.VG = 1.45  # dl/kg
        self.SG = 2.5e-2  # 1/min
        self.Gb = 119.13  # mg/dL
        self.r1 = 1.4407  # unitless
        self.r2 = 0.8124  # unitless
        self.alpha = 7  # 1/min
        if is_single_meal:
            self.SI = 10.35e-4 / self.VG  # mL/(uU*min)
        else:
            self.SI_B = 10.35e-4 / self.VG  # mL/(uU*min)
            self.SI_L = 10.35e-4 / self.VG  # mL/(uU*min)
            self.SI_D = 10.35e-4 / self.VG  # mL/(uU*min)
        self.p2 = 0.012  # 1/min
        self.u2ss = np.mean(data.basal) * 1000 / BW  # mU/(kg*min)

        # Subcutaneous insulin absorption submodel parameters
        self.VI = 0.126  # L/kg
        self.ke = 0.127  # 1/min
        self.kd = 0.026  # 1/min
        # model_parameters['ka1'] = 0.0034  # 1/min (virtually 0 in 77% of the cases)
        #self.ka1 = 0.0
        self.ka2 = 0.014  # 1/min
        self.tau = 8  # min
        self.Ipb = self.ke * self.u2ss / self.kd + (self.ka2 / self.ke) * (self.kd / self.ka2) * self.u2ss / self.kd  # from eq. 5 steady-state

        # Oral glucose absorption submodel parameters
        if is_single_meal:
            self.kabs = 0.012  # 1/min
            self.beta = 0  # 1/min
        else:
            self.kabs_B = 0.012  # 1/min
            self.kabs_L = 0.012  # 1/min
            self.kabs_D = 0.012  # 1/min
            self.kabs_S = 0.012  # 1/min
            self.kabs_H = 0.012  # 1/min
            self.beta_B = 0  # min
            self.beta_L = 0  # min
            self.beta_D = 0  # min
            self.beta_S = 0  # min
        self.kgri = 0.18  # = kmax % 1/min
        self.kempt = 0.18  # 1/min
        self.f = 0.9  # dimensionless

        # Exercise submodel parameters
        self.VO2rest = 0.33  # dimensionless, VO2rest was derived from heart rate round(66/(220-30))
        self.VO2max = 1  # dimensionless, VO2max is normalized and estimated from heart rate (220-age) = 100%.
        self.e1 = 1.6  # dimensionless
        self.e2 = 0.78  # dimensionless

        # Patient specific parameters
        self.BW = BW  # kg
        self.to_g = self.BW / 1000
        self.to_mgkg = 1000 / self.BW

        # Measurement noise specifics
        self.SDn = 5

        # Initial conditions
        if 'glucose' in data:
            idx = np.where(data.glucose.isnull().values == False)[0][0]
            self.G0 = data.glucose[idx]
        else:
            self.G0 = self.Gb

