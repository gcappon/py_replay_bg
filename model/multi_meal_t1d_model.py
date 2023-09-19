import numpy as np
import pandas as pd
import scipy.stats as stats

from datetime import datetime

import copy


class MultiMealT1DModel:
    """
    A class that represents the multi meal type 1 diabetes model.

    ...
    Attributes 
    ----------
    ts: int
        The integration time step.
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
    nx : int
        The number of model states.
    model_parameters: dict 
        A dictionary containing the default model parameters.
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

    def __init__(self, data, BW, ts=1, yts=5, glucose_model='IG', exercise=False):
        """
        Constructs all the necessary attributes for the Model object.

        Parameters
        ----------
        data : pandas.DataFrame
            Pandas dataframe which contains the data to be used by the tool
        ts: int, optional, default : 1 
            The integration time step.
        yts: int, optional, default : 5 
            The measurement (cgm) sample time.
        glucose_model: string, {'IG','BG'}, optional, default : 'IG'
            The model equation to be used as measured glucose.
        exercise: bool, optional, default : False
            A boolean indicating if the model includes the exercise.
        """

        # Time constants during simulation
        self.ts = ts
        self.yts = yts
        self.t = int((np.array(data.t)[-1].astype(datetime) - np.array(data.t)[0].astype(datetime)) / (
                    60 * 1000000000) + self.yts)

        self.tsteps = int(self.t / self.ts)
        self.tysteps = int(self.t / self.yts)

        # Glucose equation selection
        self.glucose_model = glucose_model  # glucose equation selection {'BG','IG'}

        # Model dimensionality
        self.nx = 21

        # Model parameters
        self.model_parameters = self.__get_default_model_parameters(data, BW)

        # Unknown parameters
        # self.unknown_parameters = ['SI', 'Gb', 'SG', 'p2', 'ka2', 'kd', 'kempt', 'kabs', 'beta']
        self.unknown_parameters = ['Gb', 'SG', 'ka2', 'kd', 'kempt']

        # initial guess for unknown parameter
        # self.start_guess = np.array(
        #    [self.model_parameters['SI'], self.model_parameters['Gb'], self.model_parameters['SG'],
        #     self.model_parameters['p2'],
        #     self.model_parameters['ka2'], self.model_parameters['kd'], self.model_parameters['kempt'],
        #     self.model_parameters['kabs'],
        #     self.model_parameters['beta']])
        self.start_guess = np.array(
            [self.model_parameters['Gb'], self.model_parameters['SG'],
             self.model_parameters['ka2'], self.model_parameters['kd'], self.model_parameters['kempt']])

        # initial guess for the SD of each parameter
        # self.start_guess_sigma = np.array([1e-6, 1, 5e-4, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 0.5])
        self.start_guess_sigma = np.array([1, 5e-4, 1e-3, 1e-3, 1e-3])

        # Get the hour of the day for each data point
        t = np.array(data.t.dt.hour.values).astype(int)

        # Attach breakfast SI if data between 4:00 - 11:00 are available
        self.pos_SI_B = 0
        if np.any(np.logical_and(t >= 4, t < 11)):
            self.pos_SI_B = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'SI_B')
            self.start_guess = np.append(self.start_guess, self.model_parameters['SI_B'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)

        # Attach lunch SI if data between 11:00 - 17:00 are available
        self.pos_SI_L = 0
        if np.any(np.logical_and(t >= 11, t < 17)):
            self.pos_SI_L = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'SI_L')
            self.start_guess = np.append(self.start_guess, self.model_parameters['SI_L'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)

        # Attach dinner SI if data between 0:00 - 4:00 or 17:00 - 24:00 are available
        self.pos_SI_D = 0
        if np.any(np.logical_or(t < 4, t >= 17)):
            self.pos_SI_D = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'SI_D')
            self.start_guess = np.append(self.start_guess, self.model_parameters['SI_D'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-6)

        # Attach kabs and beta breakfast if there is a breakfast
        self.pos_kabs_B = 0
        self.pos_beta_B = 0
        if np.any(np.array(data.cho_label) == 'B'):
            self.pos_kabs_B = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_B')
            self.start_guess = np.append(self.start_guess, self.model_parameters['kabs_B'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
            self.pos_beta_B = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'beta_B')
            self.start_guess = np.append(self.start_guess, self.model_parameters['beta_B'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

        # Attach kabs and beta lunch if there is a lunch
        self.pos_kabs_L = 0
        self.pos_beta_L = 0
        if np.any(np.array(data.cho_label) == 'L'):
            self.pos_kabs_L = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_L')
            self.start_guess = np.append(self.start_guess, self.model_parameters['kabs_L'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
            self.pos_beta_L = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'beta_L')
            self.start_guess = np.append(self.start_guess, self.model_parameters['beta_L'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

        # Attach kabs and beta dinner if there is a dinner
        self.pos_kabs_D = 0
        self.pos_beta_D = 0
        if np.any(np.array(data.cho_label) == 'D'):
            self.pos_kabs_D = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_D')
            self.start_guess = np.append(self.start_guess, self.model_parameters['kabs_D'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
            self.pos_beta_D = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'beta_D')
            self.start_guess = np.append(self.start_guess, self.model_parameters['beta_D'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

        # Attach kabs and beta snack if there is a snack
        self.pos_kabs_S = 0
        self.pos_beta_S = 0
        if np.any(np.array(data.cho_label) == 'S'):
            self.pos_kabs_S = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_S')
            self.start_guess = np.append(self.start_guess, self.model_parameters['kabs_S'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)
            self.pos_beta_S = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'beta_S')
            self.start_guess = np.append(self.start_guess, self.model_parameters['beta_S'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 0.5)

        # Attach kabs and hypotreatment if there is an hypotreatment
        self.pos_kabs_H = 0
        if np.any(np.array(data.cho_label) == 'H'):
            self.pos_kabs_H = self.start_guess.shape[0]
            self.unknown_parameters = np.append(self.unknown_parameters, 'kabs_H')
            self.start_guess = np.append(self.start_guess, self.model_parameters['kabs_H'])
            self.start_guess_sigma = np.append(self.start_guess_sigma, 1e-3)

        # Exercise
        self.exercise = exercise

    def __get_default_model_parameters(self, data, BW):
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
        model_parameters = dict()

        # Initial conditions
        model_parameters['Xpb'] = 0.0  # Insulin action initial condition
        model_parameters['Qgutb'] = 0.0  # Intestinal content initial condition

        # Glucose-insulin submodel parameters
        model_parameters['VG'] = 1.45  # dl/kg
        model_parameters['SG'] = 2.5e-2  # 1/min
        model_parameters['Gb'] = 119.13  # mg/dL
        model_parameters['r1'] = 1.4407  # unitless
        model_parameters['r2'] = 0.8124  # unitless
        model_parameters['alpha'] = 7  # 1/min
        model_parameters['SI_B'] = 10.35e-4 / model_parameters['VG']  # mL/(uU*min)
        model_parameters['SI_L'] = 10.35e-4 / model_parameters['VG']  # mL/(uU*min)
        model_parameters['SI_D'] = 10.35e-4 / model_parameters['VG']  # mL/(uU*min)
        model_parameters['p2'] = 0.012  # 1/min
        model_parameters['u2ss'] = np.mean(data.basal) * 1000 / BW  # mU/(kg*min)

        # Subcutaneous insulin absorption submodel parameters
        model_parameters['VI'] = 0.126  # L/kg
        model_parameters['ke'] = 0.127  # 1/min
        model_parameters['kd'] = 0.026  # 1/min
        # model_parameters['ka1'] = 0.0034  # 1/min (virtually 0 in 77% of the cases)
        model_parameters['ka1'] = 0.0
        model_parameters['ka2'] = 0.014  # 1/min
        model_parameters['tau'] = 8  # min
        model_parameters['Ipb'] = (model_parameters['ka1'] / model_parameters['ke']) * model_parameters['u2ss'] / (
                    model_parameters['ka1'] + model_parameters['kd']) + (
                                              model_parameters['ka2'] / model_parameters['ke']) * (
                                              model_parameters['kd'] / model_parameters['ka2']) * model_parameters[
                                      'u2ss'] / (model_parameters['ka1'] + model_parameters[
            'kd'])  # from eq. 5 steady-state

        # Oral glucose absorption submodel parameters
        model_parameters['kabs_B'] = 0.012  # 1/min
        model_parameters['kabs_L'] = 0.012  # 1/min
        model_parameters['kabs_D'] = 0.012  # 1/min
        model_parameters['kabs_S'] = 0.012  # 1/min
        model_parameters['kabs_H'] = 0.012  # 1/min
        model_parameters['kgri'] = 0.18  # = kmax % 1/min
        model_parameters['kempt'] = 0.18  # 1/min
        model_parameters['beta_B'] = 0  # min
        model_parameters['beta_L'] = 0  # min
        model_parameters['beta_D'] = 0  # min
        model_parameters['beta_S'] = 0  # min
        model_parameters['f'] = 0.9  # dimensionless

        # Exercise submodel parameters
        model_parameters['VO2rest'] = 0.33  # dimensionless, VO2rest was derived from heart rate round(66/(220-30))
        model_parameters[
            'VO2max'] = 1  # dimensionless, VO2max is normalized and estimated from heart rate (220-age) = 100%.
        model_parameters['e1'] = 1.6  # dimensionless
        model_parameters['e2'] = 0.78  # dimensionless

        # Patient specific parameters
        model_parameters['BW'] = BW  # kg

        # Measurement noise specifics
        model_parameters['SDn'] = 5

        # Initial conditions
        if 'glucose' in data:
            idx = np.where(data.glucose.isnull().values == False)[0][0]
            model_parameters['G0'] = data.glucose[idx]
        else:
            model_parameters['G0'] = model_parameters['Gb']

        return model_parameters

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

        # Set the basal plasma insulin
        mp['Ipb'] = (mp['ka1'] / mp['ke']) * mp['u2ss'] / (mp['ka1'] + mp['kd']) + (mp['ka2'] / mp['ke']) * (
                    mp['kd'] / mp['ka2']) * mp['u2ss'] / (mp['ka1'] + mp['kd'])  # from eq. 5 steady-state

        # Set the initial model conditions
        initial_conditions = np.array([mp['G0'],
                                       mp['Xpb'],
                                       mp['u2ss'] / (mp['ka1'] + mp['kd']),
                                       mp['kd'] / mp['ka2'] * mp['u2ss'] / (mp['ka1'] + mp['kd']),
                                       mp['ka1'] / mp['ke'] * mp['u2ss'] / (mp['ka1'] + mp['kd']) + mp['ka2'] / mp[
                                           'ke'] * mp['kd'] / mp['ka2'] * mp['u2ss'] / (mp['ka1'] + mp['kd']),
                                       0,
                                       0,
                                       mp['Qgutb'],
                                       0,
                                       0,
                                       mp['Qgutb'],
                                       0,
                                       0,
                                       mp['Qgutb'],
                                       0,
                                       0,
                                       mp['Qgutb'],
                                       0,
                                       0,
                                       mp['Qgutb'],
                                       mp['G0']])

        # Initialize the glucose vector
        G = np.empty([self.tsteps, ])

        # Set the initial glucose value
        if self.glucose_model == 'IG':
            G[0] = initial_conditions[self.nx - 1]  # y(k) = IG(k)
        if self.glucose_model == 'BG':
            G[0] = initial_conditions[0]  # (k) = BG(k)

        # Initialize the state matrix
        x = np.zeros([self.nx, self.tsteps])
        x[:, 0] = initial_conditions

        if modality == 'replay':

            # Initialize the cgm vector
            CGM = np.empty([self.tysteps, ])
            # Set the initial cgm value
            if rbg.sensors.cgm.model == 'IG':
                CGM[0] = initial_conditions[self.nx - 1]  # y(k) = IG(k)
            if rbg.sensors.cgm.model == 'CGM':
                CGM[0] = rbg.sensors.cgm.measure(initial_conditions[self.nx - 1], 0)

            # Make copies of the inputs if replay to avoid to overwrite fields
            bolus = copy.copy(rbg_data.bolus)
            basal = copy.copy(rbg_data.basal)
            meal = copy.copy(rbg_data.meal)
            meal_type = copy.copy(rbg_data.meal_type)
            meal_announcement = copy.copy(rbg_data.meal_announcement)

            correction_bolus = bolus * 0
            hypotreatments = meal * 0  # Hypotreatments definition is not present in single-meal --> set to 0

        else:

            bolus = rbg_data.bolus
            basal = rbg_data.basal
            meal = rbg_data.meal
            meal_type = rbg_data.meal_type
            meal_announcement = rbg_data.meal_announcement

        # Simulate the physiological model
        for k in np.arange(1, self.tsteps):

            if modality == 'replay':

                # Meal generation module
                if rbg.environment.cho_source == 'generated':

                    # Call the meal generator function handler
                    ch, ma, t, rbg.dss = rbg.dss.meal_generator_handler(G, meal, meal_announcement, bolus / 1000 * mp['BW'], basal / 1000 * mp['BW'], rbg_data.t_hour, k - 1, rbg.dss, True)

                    # Update the event vectors
                    meal_announcement[k - 1] = meal_announcement[k - 1] + ma
                    meal_type[k - 1] = t

                    # Add the meal to the input bolus vector.
                    ch = ch * 1000 / mp['BW']
                    meal[k - 1] = meal[k - 1] + ch

                # Bolus generation module
                if rbg.environment.bolus_source == 'dss':

                    # Call the bolus calculator function handler
                    bo, rbg.dss = rbg.dss.bolus_calculator_handler(G, meal_announcement, bolus / 1000 * mp['BW'], basal / 1000 * mp['BW'],
                                                    rbg_data.t_hour, k - 1, rbg.dss)

                    # Add the bolus to the input bolus vector.
                    bo = bo * 1000 / mp['BW']
                    bolus[k - 1] = bolus[k - 1] + bo

                # Basal rate generation module
                if rbg.environment.basal_source == 'dss':
                    # Call the basal rate function handler
                    ba, rbg.dss = rbg.dss.basal_handler(G, meal_announcement, hypotreatments, bolus / 1000 * mp['BW'], basal / 1000 * mp['BW'],
                                                             rbg_data.t_hour, k - 1, rbg.dss)

                    # Add the correction bolus to the input bolus vector.
                    ba = ba * 1000 / mp['BW']
                    basal[k - 1] = basal[k - 1] + ba

                # Hypotreatment generation module
                ht = 0
                if rbg.dss.enable_hypotreatments:

                    # Call the hypotreatment handler
                    ht, rbg.dss = rbg.dss.hypotreatments_handler(G, meal / 1000 * mp['BW'], hypotreatments, bolus / 1000 * mp['BW'], basal / 1000 * mp['BW'], rbg_data.t_hour, k-1, rbg.dss)

                    # Update the hypotreatments event vectors
                    hypotreatments[k - 1] = hypotreatments[k - 1] + ht

                # Correction bolus delivery module if it is enabled
                if rbg.dss.enable_correction_boluses:

                    # Call the correction boluses handler
                    cb, rbg.dss = rbg.dss.correction_boluses_handler(G, meal / 1000 * mp['BW'], hypotreatments, bolus / 1000 * mp['BW'], basal / 1000 * mp['BW'],
                                                             rbg_data.t_hour, k - 1, rbg.dss)

                    # Update the event vectors
                    correction_bolus[k - 1] = correction_bolus[k - 1] + cb

            # Set the breakfast meal input delay
            meal_delay_B = int(np.floor(mp['beta_B'] / self.ts))

            # Extract the correct breakfast meal input
            if k - 1 - meal_delay_B > 0:
                if meal_type[k - 1 - meal_delay_B] == 'B':
                    mea_B = meal[k - 1 - meal_delay_B]
                else:
                    mea_B = 0
            else:
                mea_B = 0

            # Set the lunch meal input delay
            meal_delay_L = int(np.floor(mp['beta_L'] / self.ts))

            # Extract the correct lunch meal input
            if k - 1 - meal_delay_L > 0:
                if meal_type[k - 1 - meal_delay_L] == 'L':
                    mea_L = meal[k - 1 - meal_delay_L]
                else:
                    mea_L = 0
            else:
                mea_L = 0

            # Set the dinner meal input delay
            meal_delay_D = int(np.floor(mp['beta_D'] / self.ts))

            # Extract the correct dinner meal input
            if k - 1 - meal_delay_D > 0:
                if meal_type[k - 1 - meal_delay_D] == 'D':
                    mea_D = meal[k - 1 - meal_delay_D]
                else:
                    mea_D = 0
            else:
                mea_D = 0

            # Set the snack meal input delay
            meal_delay_S = int(np.floor(mp['beta_S'] / self.ts))

            # Extract the correct snack meal input
            if k - 1 - meal_delay_S > 0:
                if meal_type[k - 1 - meal_delay_S] == 'S':
                    mea_S = meal[k - 1 - meal_delay_S]
                else:
                    mea_S = 0
            else:
                mea_S = 0

            # Extract the correct snack meal input
            if meal_type[k - 1] == 'H':
                mea_H = meal[k - 1]
            else:
                mea_H = 0

            if modality == 'replay':
                # Add hypotreatment with no delay
                mea_H = mea_H + hypotreatments[k - 1] * 1000 / mp['BW']

                # Add the correction bolus to the input bolus vector.
                bolus[k - 1] = bolus[k - 1] + correction_bolus[k - 1] * 1000 / mp['BW']

            # Set the insulin input delays
            insulin_delay = int(np.floor(mp['tau'] / self.ts))

            # Extract the correct insulin inputs
            if k - 1 - insulin_delay > 0:
                bol = bolus[k - 1 - insulin_delay]
                bas = basal[k - 1 - insulin_delay]
            else:
                bol = 0
                bas = basal[0]

            # Get the time of the day
            hod = rbg_data.t_hour[k - 1]

            # Simulate a step
            x[:, k] = self.__model_step_equations(bol + bas, mea_B, mea_L, mea_D, mea_S, mea_H, hod, x[:, k - 1]) # k-1

            # Get the glucose measurement
            if self.glucose_model == 'IG':
                G[k] = x[self.nx - 1, k]  # y(k) = IG(k)
            if self.glucose_model == 'BG':
                G[k] = x[0, k]  # (k) = BG(k)

            if modality == 'replay':

                # Get the cgm
                if np.mod(k, rbg.sensors.cgm.ts) == 0:
                    if rbg.sensors.cgm.model == 'IG':
                        CGM[int(k / rbg.sensors.cgm.ts)] = x[self.nx, k]  # y(k) = IG(k)
                    if rbg.sensors.cgm.model == 'CGM':
                        CGM[int(k / rbg.sensors.cgm.ts)] = rbg.sensors.cgm.measure(x[self.nx - 1, k], k / (24 * 60))

        if modality == 'replay':
            # TODO: add vo2
            return G, CGM, bolus / 1000 * mp['BW'], correction_bolus, basal / 1000 * mp['BW'], meal / 1000 * mp['BW'], hypotreatments, meal_announcement, x
        else:
            return G

    def __model_step_equations(self, I, CHO_B, CHO_L, CHO_D, CHO_S, CHO_H, hour_of_the_day, xkm1):
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

        # Rename model parameters for brevity
        mp = self.model_parameters

        # unpack states
        G, X, Isc1, Isc2, Ip, Qsto1_B, Qsto2_B, Qgut_B, Qsto1_L, Qsto2_L, Qgut_L, Qsto1_D, Qsto2_D, Qgut_D, Qsto1_S, Qsto2_S, Qgut_S, Qsto1_H, Qsto2_H, Qgut_H, IG = xkm1

        # Set the insulin sensitivity based on the time of the day
        if hour_of_the_day < 4 or hour_of_the_day >= 17:
            SI = mp['SI_D']
        else:
            if 4 <= hour_of_the_day < 11:
                SI = mp['SI_B']
            else:
                SI = mp['SI_L']

        # Compute glucose risk

        # Setting the risk model threshold
        G_th = 60

        # Set default risk
        risk = 1

        # Compute the risk
        if 119.13 > G >= G_th:
            risk = risk + 10 * mp['r1'] * (np.log(G) ** mp['r2'] - np.log(119.13) ** mp['r2']) ** 2
        if G < G_th:
            risk = risk + 10 * mp['r1'] * (np.log(G_th) ** mp['r2'] - np.log(119.13) ** mp['r2']) ** 2

        # Compute the model state at time k using backward Euler method
        Qsto1_B = (Qsto1_B + self.ts * CHO_B) / (1 + self.ts * mp['kgri'])
        Qsto2_B = (Qsto2_B + self.ts * mp['kgri'] * Qsto1_B) / (1 + self.ts * mp['kempt'])
        Qgut_B = (Qgut_B + self.ts * mp['kempt'] * Qsto2_B) / (1 + self.ts * mp['kabs_B'])

        Qsto1_L = (Qsto1_L + self.ts * CHO_L) / (1 + self.ts * mp['kgri'])
        Qsto2_L = (Qsto2_L + self.ts * mp['kgri'] * Qsto1_L) / (1 + self.ts * mp['kempt'])
        Qgut_L = (Qgut_L + self.ts * mp['kempt'] * Qsto2_L) / (1 + self.ts * mp['kabs_L'])

        Qsto1_D = (Qsto1_D + self.ts * CHO_D) / (1 + self.ts * mp['kgri'])
        Qsto2_D = (Qsto2_D + self.ts * mp['kgri'] * Qsto1_D) / (1 + self.ts * mp['kempt'])
        Qgut_D = (Qgut_D + self.ts * mp['kempt'] * Qsto2_D) / (1 + self.ts * mp['kabs_D'])

        Qsto1_S = (Qsto1_S + self.ts * CHO_S) / (1 + self.ts * mp['kgri'])
        Qsto2_S = (Qsto2_S + self.ts * mp['kgri'] * Qsto1_S) / (1 + self.ts * mp['kempt'])
        Qgut_S = (Qgut_S + self.ts * mp['kempt'] * Qsto2_S) / (1 + self.ts * mp['kabs_S'])

        Qsto1_H = (Qsto1_H + self.ts * CHO_H) / (1 + self.ts * mp['kgri'])
        Qsto2_H = (Qsto2_H + self.ts * mp['kgri'] * Qsto1_H) / (1 + self.ts * mp['kempt'])
        Qgut_H = (Qgut_H + self.ts * mp['kempt'] * Qsto2_H) / (1 + self.ts * mp['kabs_H'])

        Ra_B = mp['f'] * mp['kabs_B'] * Qgut_B
        Ra_L = mp['f'] * mp['kabs_L'] * Qgut_L
        Ra_D = mp['f'] * mp['kabs_D'] * Qgut_D
        Ra_S = mp['f'] * mp['kabs_S'] * Qgut_S
        Ra_H = mp['f'] * mp['kabs_H'] * Qgut_H

        Isc1 = (Isc1 + self.ts * I) / (1 + self.ts * (mp['ka1'] + mp['kd']))
        Isc2 = (Isc2 + self.ts * mp['kd'] * Isc1) / (1 + self.ts * mp['ka2'])
        Ip = (Ip + self.ts * (mp['ka1'] * Isc1 + mp['ka2'] * Isc2)) / (1 + self.ts * mp['ke'])

        X = (X + self.ts * mp['p2'] * (SI / mp['VI']) * (Ip - mp['Ipb'])) / (1 + self.ts * mp['p2'])

        G = (G + self.ts * (mp['SG'] * mp['Gb'] + ( Ra_B + Ra_L + Ra_D + Ra_S + Ra_H ) / mp['VG'])) / (
                    1 + self.ts * (mp['SG'] + (1 + mp['r1'] * risk) * X))
        IG = (IG + (self.ts / mp['alpha']) * G) / (1 + self.ts / mp['alpha'])

        return [G, X, Isc1, Isc2, Ip, Qsto1_B, Qsto2_B, Qgut_B, Qsto1_L, Qsto2_L, Qgut_L, Qsto1_D, Qsto2_D, Qgut_D, Qsto1_S, Qsto2_S, Qgut_S, Qsto1_H, Qsto2_H, Qgut_H, IG]

    def __log_prior(self, theta):
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

        SI_B = theta[self.pos_SI_B] if self.pos_SI_B else self.model_parameters['SI_B']
        SI_L = theta[self.pos_SI_L] if self.pos_SI_L else self.model_parameters['SI_L']
        SI_D = theta[self.pos_SI_D] if self.pos_SI_D else self.model_parameters['SI_D']

        kabs_B = theta[self.pos_kabs_B] if self.pos_kabs_B else self.model_parameters['kabs_B']
        kabs_L = theta[self.pos_kabs_L] if self.pos_kabs_L else self.model_parameters['kabs_L']
        kabs_D = theta[self.pos_kabs_D] if self.pos_kabs_D else self.model_parameters['kabs_D']
        kabs_S = theta[self.pos_kabs_S] if self.pos_kabs_S else self.model_parameters['kabs_S']
        kabs_H = theta[self.pos_kabs_H] if self.pos_kabs_H else self.model_parameters['kabs_H']

        beta_B = theta[self.pos_beta_B] if self.pos_beta_B else self.model_parameters['beta_B']
        beta_L = theta[self.pos_beta_L] if self.pos_beta_L else self.model_parameters['beta_L']
        beta_D = theta[self.pos_beta_D] if self.pos_beta_D else self.model_parameters['beta_D']
        beta_S = theta[self.pos_beta_S] if self.pos_beta_S else self.model_parameters['beta_S']


        # compute each log prior
        logprior_SI_B = np.log(stats.gamma.pdf(SI_B * self.model_parameters['VG'], 3.3, 5e-4)) if 0 < SI_B * \
                                                                                              self.model_parameters[
                                                                                                  'VG'] < 1 else -np.inf
        logprior_SI_L = np.log(stats.gamma.pdf(SI_L * self.model_parameters['VG'], 3.3, 5e-4)) if 0 < SI_L * \
                                                                                              self.model_parameters[
                                                                                                  'VG'] < 1 else -np.inf
        logprior_SI_D = np.log(stats.gamma.pdf(SI_D * self.model_parameters['VG'], 3.3, 5e-4)) if 0 < SI_D * \
                                                                                              self.model_parameters[
                                                                                                  'VG'] < 1 else -np.inf

        logprior_Gb = np.log(stats.norm.pdf(Gb, 119.13, 7.11)) if 70 <= Gb <= 180 else -np.inf
        logprior_SG = np.log(stats.lognorm.pdf(SG, 0.5, scale=np.exp(-3.8))) if 0 < SG < 1 else -np.inf
        # logprior_p2 = np.log(stats.norm.pdf(np.sqrt(p2), 0.11, 0.004)) if 0 < p2 < 1 else -np.inf
        logprior_ka2 = np.log(
            stats.lognorm.pdf(ka2, 0.4274, scale=np.exp(-4.2875))) if 0 < ka2 < kd and ka2 < 1 else -np.inf
        logprior_kd = np.log(
            stats.lognorm.pdf(kd, 0.6187, scale=np.exp(-3.5090))) if 0 < ka2 < kd and kd < 1 else -np.inf
        logprior_kempt = np.log(stats.lognorm.pdf(kempt, 0.7069, scale=np.exp(-1.9646))) if 0 < kempt < 1 else -np.inf

        logprior_kabs_B = np.log(
            stats.lognorm.pdf(kabs_B, 1.4396, scale=np.exp(-5.4591))) if kempt >= kabs_B and 0 < kabs_B < 1 else -np.inf
        logprior_kabs_L = np.log(
            stats.lognorm.pdf(kabs_L, 1.4396, scale=np.exp(-5.4591))) if kempt >= kabs_L and 0 < kabs_L < 1 else -np.inf
        logprior_kabs_D = np.log(
            stats.lognorm.pdf(kabs_D, 1.4396, scale=np.exp(-5.4591))) if kempt >= kabs_D and 0 < kabs_D < 1 else -np.inf
        logprior_kabs_S = np.log(
            stats.lognorm.pdf(kabs_S, 1.4396, scale=np.exp(-5.4591))) if kempt >= kabs_S and 0 < kabs_S < 1 else -np.inf
        logprior_kabs_H = np.log(
            stats.lognorm.pdf(kabs_H, 1.4396, scale=np.exp(-5.4591))) if kempt >= kabs_H and 0 < kabs_H < 1 else -np.inf

        logprior_beta_B = 0 if 0 <= beta_B <= 60 else -np.inf
        logprior_beta_L = 0 if 0 <= beta_L <= 60 else -np.inf
        logprior_beta_D = 0 if 0 <= beta_D <= 60 else -np.inf
        logprior_beta_S = 0 if 0 <= beta_S <= 60 else -np.inf

        # Sum everything and return the value
        # return logprior_SI + logprior_Gb + logprior_SG + logprior_p2 + logprior_ka2 + logprior_kd + logprior_kempt + logprior_kabs + logprior_beta
        return logprior_SI_B + logprior_SI_L + logprior_SI_D + logprior_Gb + logprior_SG + logprior_ka2 + logprior_kd + logprior_kempt + logprior_kabs_B + logprior_kabs_L + logprior_kabs_D + logprior_kabs_S + logprior_kabs_H + logprior_beta_B + logprior_beta_L + logprior_beta_D + logprior_beta_S

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
        # self.model_parameters['SI'], self.model_parameters['Gb'], self.model_parameters['SG'], self.model_parameters[
        #     'p2'], self.model_parameters['ka2'], self.model_parameters['kd'], self.model_parameters['kempt'], \
        # self.model_parameters['kabs'], self.model_parameters['beta'] = theta
        self.model_parameters['Gb'], self.model_parameters['SG'], self.model_parameters['ka2'], self.model_parameters['kd'], self.model_parameters['kempt'] = theta[0:5]
        self.model_parameters['SI_B'] = theta[self.pos_SI_B] if self.pos_SI_B else self.model_parameters['SI_B']
        self.model_parameters['SI_L'] = theta[self.pos_SI_L] if self.pos_SI_L else self.model_parameters['SI_L']
        self.model_parameters['SI_D'] = theta[self.pos_SI_D] if self.pos_SI_D else self.model_parameters['SI_D']

        self.model_parameters['kabs_B'] = theta[self.pos_kabs_B] if self.pos_kabs_B else self.model_parameters['kabs_B']
        self.model_parameters['kabs_L'] = theta[self.pos_kabs_L] if self.pos_kabs_L else self.model_parameters['kabs_L']
        self.model_parameters['kabs_D'] = theta[self.pos_kabs_D] if self.pos_kabs_D else self.model_parameters['kabs_D']
        self.model_parameters['kabs_S'] = theta[self.pos_kabs_S] if self.pos_kabs_S else self.model_parameters['kabs_S']
        self.model_parameters['kabs_H'] = theta[self.pos_kabs_H] if self.pos_kabs_H else self.model_parameters['kabs_H']

        self.model_parameters['beta_B'] = theta[self.pos_beta_B] if self.pos_beta_B else self.model_parameters['beta_B']
        self.model_parameters['beta_L'] = theta[self.pos_beta_L] if self.pos_beta_L else self.model_parameters['beta_L']
        self.model_parameters['beta_D'] = theta[self.pos_beta_D] if self.pos_beta_D else self.model_parameters['beta_D']
        self.model_parameters['beta_S'] = theta[self.pos_beta_S] if self.pos_beta_S else self.model_parameters['beta_S']

        # Enforce contraints
        self.model_parameters['kgri'] = self.model_parameters['kempt']

        # Simulate the model
        G = self.simulate(rbg_data=rbg_data, modality='identification', rbg=None)

        # Sample the simulation
        G = G[0::int(self.yts / self.ts)]

        # Compute and return the log likelihood
        return -0.5 * np.sum(((G[rbg_data.glucose_idxs] - rbg_data.glucose[rbg_data.glucose_idxs]) / self.model_parameters['SDn']) ** 2)

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
        if self.__log_prior(theta) == -np.inf:
            return -np.inf
        else:
            return self.__log_prior(theta) + self.__log_likelihood(theta, rbg_data)

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
        return self.__log_prior(theta) != -np.inf
