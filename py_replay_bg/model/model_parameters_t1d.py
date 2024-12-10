import numpy as np
import pandas as pd


class ModelParametersT1D:
    def __init__(self,
                 data: pd.DataFrame,
                 bw: float,
                 u2ss: float
                 ):

        """
        Function that returns the default parameters values of the t1d model.

        Parameters
        ----------
        data : pd.DataFrame
                Pandas dataframe which contains the data to be used by the tool.
        bw : float
            The patient's body weight.
        u2ss : float
            The steady state of the basal insulin infusion

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
        self.p2 = 0.012  # 1/min

        if u2ss is None:
            self.u2ss = np.mean(data.basal) * 1000 / bw  # mU/(kg*min)
        else:
            self.u2ss = u2ss

        # Subcutaneous insulin absorption submodel parameters
        self.VI = 0.126  # L/kg
        self.ke = 0.127  # 1/min
        self.kd = 0.026  # 1/min
        # model_parameters['ka1'] = 0.0034  # 1/min (virtually 0 in 77% of the cases)
        # self.ka1 = 0.0
        self.ka2 = 0.014  # 1/min
        self.tau = 8  # min
        self.Ipb = self.ke * self.u2ss / self.kd + (self.ka2 / self.ke) * (self.kd / self.ka2) * self.u2ss / self.kd  # from eq. 5 steady-state

        # Oral glucose absorption submodel parameters
        self.kgri = 0.18  # = kmax % 1/min
        self.kempt = 0.18  # 1/min
        self.f = 0.9  # dimensionless

        # Exercise submodel parameters
        self.vo2rest = 0.33  # dimensionless, VO2rest was derived from heart rate round(66/(220-30))
        self.vo2max = 1  # dimensionless, VO2max is normalized and estimated from heart rate (220-age) = 100%.
        self.e1 = 1.6  # dimensionless
        self.e2 = 0.78  # dimensionless

        # Patient specific parameters
        self.bw = bw  # kg
        self.to_g = self.bw / 1000
        self.to_mgkg = 1000 / self.bw

        # Measurement noise specifics
        self.SDn = 5

        # Glucose starting point
        if 'glucose' in data:
            idx = np.where(data.glucose.isnull().values == False)[0][0]
            self.G0 = data.glucose[idx]
        else:
            self.G0 = self.Gb


class ModelParametersT1DMultiMeal(ModelParametersT1D):

    def __init__(self,
                 data: pd.DataFrame,
                 bw: float,
                 u2ss: float
                 ):

        """
        Function that returns the default parameters values of the t1d model in a multi-meal blueprint.

        Parameters
        ----------
        data : pd.DataFrame
                Pandas dataframe which contains the data to be used by the tool.
        bw : float
            The patient's body weight.
        u2ss : float
            The steady state of the basal insulin infusion

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
        # Initialize common parameters
        super().__init__(data, bw, u2ss)

        # Glucose-insulin submodel parameters
        self.SI_B = 10.35e-4 / self.VG  # mL/(uU*min)
        self.SI_L = 10.35e-4 / self.VG  # mL/(uU*min)
        self.SI_D = 10.35e-4 / self.VG  # mL/(uU*min)

        # Oral glucose absorption submodel parameters
        self.kabs_B = 0.012  # 1/min
        self.kabs_L = 0.012  # 1/min
        self.kabs_D = 0.012  # 1/min
        self.kabs_S = 0.012  # 1/min
        self.kabs_H = 0.012  # 1/min
        self.beta_B = 0  # min
        self.beta_L = 0  # min
        self.beta_D = 0  # min
        self.beta_S = 0  # min


class ModelParametersT1DSingleMeal(ModelParametersT1D):

    def __init__(self,
                 data: pd.DataFrame,
                 bw: float,
                 u2ss: float
                 ):

        """
        Function that returns the default parameters values of the t1d model in a single-meal blueprint.

        Parameters
        ----------
        data : pd.DataFrame
                Pandas dataframe which contains the data to be used by the tool.
        bw : float
            The patient's body weight.
        u2ss : float
            The steady state of the basal insulin infusion

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
        # Initialize common parameters
        super().__init__(data, bw, u2ss)

        # Glucose-insulin submodel parameters
        self.SI = 10.35e-4 / self.VG  # mL/(uU*min)

        # Oral glucose absorption submodel parameters
        self.kabs = 0.012  # 1/min
        self.beta = 0  # 1/min
