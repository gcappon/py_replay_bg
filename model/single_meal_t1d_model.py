import random
from datetime import datetime
import numpy as np
from numba import jit

class SingleMealT1DModel:
    """
    A class that represents the physiological model hyperparameters to be used by ReplayBG.

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

    Methods
    -------
    def simulate(rbg_data, rbg):
        Function that simulates the model and returns the obtained results.

    """
    def __init__(self, data, BW, ts = 1, yts = 5, glucose_model = 'IG'):
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
        """

        #Time constants during simulation
        self.ts = ts
        self.yts = yts
        self.t = int( (np.array(data.t)[-1].astype(datetime)-np.array(data.t)[0].astype(datetime))/(60*1000000000) + self.yts) 
        self.tsteps = int(self.t / self.ts)
        self.tysteps = int(self.t / self.yts) 
        
        #Glucose equation selection
        self.glucose_model = glucose_model #glucose equation selection {'BG','IG'}

        #Model dimensionality
        self.nx = 9

        #Model parameters
        self.model_parameters = self.__get_default_model_parameters(data, BW)

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
        model_paramters: dict 
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
        model_parameters = {}

        #Initial conditions
        model_parameters['Xpb'] = 0 #Insulin action initial condition
        model_parameters['Qgutb'] = 0 #Intestinal content initial condition

        #Glucose-insulin submodel parameters
        model_parameters['VG'] = 1.45 #dl/kg
        model_parameters['SG'] = 2.5e-2 #1/min
        model_parameters['Gb'] = 119.13 #mg/dL
        model_parameters['r1'] = 1.4407 #unitless
        model_parameters['r2'] = 0.8124 #unitless
        model_parameters['alpha'] = 7 #1/min
        model_parameters['SI'] = 10.35e-4 / model_parameters['VG'] #mL/(uU*min)
        model_parameters['p2'] = 0.012 #1/min 
        model_parameters['u2ss'] = np.mean(data.basal) * 1000 / BW #mU/(kg*min)
        model_parameters['Ipb'] = (model_parameters['ka1'] / model_parameters['ke']) * model_parameters['u2ss'] / (model_parameters['ka1'] + model_parameters['kd']) + (model_parameters['ka2'] / model_parameters['ke']) * (model_parameters['kd'] / model_parameters['ka2']) * model_parameters['u2ss'] / (model_parameters['ka1']+ model_parameters['kd']) #from eq. 5 steady-state 

        #Subcutaneous insulin absorption submodel parameters
        model_parameters['VI'] = 0.126 #L/kg
        model_parameters['ke'] = 0.127 #1/min
        model_parameters['kd'] = 0.026 #1/min
        model_parameters['ka1'] = 0.0034 #1/min (virtually 0 in 77% of the cases)
        model_parameters['ka1'] = 0
        model_parameters['ka2'] = 0.014 #1/min
        model_parameters['tau'] = 8 #min

        #Oral glucose absorption submodel parameters
        model_parameters['kabs'] = 0.012; #1/min
        model_parameters['kgri'] = 0.18; # = kmax % 1/min
        model_parameters['kempt'] = 0.18; #1/min 
        model_parameters['beta'] = 0; #min
        model_parameters['f'] = 0.9; #dimensionless
                
        #Exercise submodel parameters
        model_parameters['VO2rest'] = 0.33 #dimensionless, VO2rest was derived from heart rate round(66/(220-30))
        model_parameters['VO2max'] = 1 #dimensionless, VO2max is normalized and estimated from heart rate (220-age) = 100%. 
        model_parameters['e1'] = 1.6 #dimensionless
        model_parameters['e2'] = 0.78 #dimensionless
                
        #Patient specific parameters
        model_parameters['BW'] = BW #kg

        #Measurement noise specifics
        model_parameters['typeN'] = 'SD'
        model_parameters['SDn'] = 5
                
        #Initial conditions
        #TODO: if data contains the glucose vector, get the initial value from there
        model_parameters['G0'] = model_parameters['Gb']
                                      
        return model_parameters

    #@jit
    def simulate(self, rbg_data, rbg):
        """
        Function that simulates the model and returns the obtained results.

        Parameters
        ----------
        rbg_data : ReplayBGData
            The data to be used by ReplayBG during simulation.
        BW : ReplayBG
            The instance of ReplayBG.

        Returns
        -------
        TODO: [G, CGM, insulinBolus, correctionBolus, insulinBasal, CHO, hypotreatments, mealAnnouncements, vo2, x]
        G: array
            An array containing the simulated glucose concentration (mg/dl).
        CGM: array
            An array containing the simulated CGM trace (mg/dl).
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

        #Rename parameters for brevity
        mp = self.model_parameters

        #Set the basal plasma insulin
        mp['Ipb'] = (mp['ka1'] / mp['ke']) * mp['u2ss'] / (mp['ka1'] + mp['kd']) + (mp['ka2'] / mp['ke']) * (mp['kd'] / mp['ka2']) * mp['u2ss'] / (mp['ka1']+ mp['kd']) #from eq. 5 steady-state 

        #Set the initial model conditions
        initial_conditions = np.array([mp['G0'],
            mp['Xpb'], 
            mp['u2ss'] / ( mp['ka1'] + mp['kd'] ),                             
            mp['kd'] / mp['ka2'] * mp['u2ss'] / ( mp['ka1'] + mp['kd'] ),
            mp['ka1'] / mp['ke'] * mp['u2ss'] / ( mp['ka1'] + mp['kd'] ) + mp['ka2'] / mp['ke'] * mp['kd'] / mp['ka2'] * mp['u2ss'] / ( mp['ka1'] + mp['kd'] ),
            0,
            0,
            mp['Qgutb'],
            mp['G0']])
        
        #Initialize the glucose and cgm vectors
        G = np.empty([self.tsteps,])
        CGM = np.empty([self.tysteps,])
        
        #Set the initial glucose value
        if self.glucose_model == 'IG': 
            G[0] = initial_conditions[self.nx-1] #y(k) = IG(k)
        if self.glucose_model == 'BG':
            G[0] = initial_conditions[0] #(k) = BG(k)
        
        #Set the initial cgm value
        if rbg.sensors.cgm.model == 'IG': 
            CGM[0] = initial_conditions[self.nx-1] #y(k) = IG(k)
        if rbg.sensors.cgm.model == 'CGM': 
            CGM[0] = rbg.sensors.cgm.measure(initial_conditions[self.nx-1],0)

        #Initialize the state matrix
        x = np.zeros([self.nx, self.tsteps])
        x[:,0] = initial_conditions

        #Simulate the physiological model
        for k in np.arange(1, self.tsteps):
            
            #Simulate a step
            x[:,k] = self.__model_step_equations(rbg_data.bolus[k-1] + rbg_data.basal[k-1], rbg_data.meal[k-1], x[:,k-1]) #TODO: k or k-1?

            #Get teh glucose measurement
            if self.glucose_model == 'IG': 
                G[k] = x[self.nx-1,k] #y(k) = IG(k)
            if self.glucose_model == 'BG':
                G[k] = x[0,k] #(k) = BG(k)

            #Get the cgm
            if np.mod(k,rbg.sensors.cgm.ts) == 0:
                if rbg.sensors.cgm.model == 'IG': 
                    CGM[int(k / rbg.sensors.cgm.ts)] = x[self.nx, k] #y(k) = IG(k)
                if rbg.sensors.cgm.model == 'CGM': 
                    CGM[int(k / rbg.sensors.cgm.ts)] = rbg.sensors.cgm.measure(x[self.nx, k], k / (24 * 60))
            
        return G, CGM, x

    #@jit
    def __model_step_equations(self, I, CHO, xkm1):
        """
        Internal function that simulates a step of the model using backward-euler method.

        Parameters
        ----------
        I : float
            The (basal + bolus) insulin given as input.
        CHO : float
            The meal cho given as input.
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

        #Rename model parameters for brevity
        mp = self.model_parameters

        # unpack states
        G, X, Isc1, Isc2, Ip, Qsto1, Qsto2, Qgut, IG = xkm1[0], xkm1[1], xkm1[2], xkm1[3], xkm1[4], xkm1[5], xkm1[6], xkm1[7], xkm1[8]

        #Compute glucose risk
        risk = self.__hypoglycemic_risk(G = G, r1 = mp['r1'], r2 = mp['r2'])

        #Compute the model state at time k using backward Euler method
        Qsto1 = ( Qsto1 + self.ts * CHO ) / ( 1 + self.ts * mp['kgri'] )
        Qsto2 = ( Qsto2 + self.ts * mp['kgri'] * Qsto1 ) / ( 1 + self.ts * mp['kempt'] )
        Qgut = ( Qgut + self.ts * mp['kempt'] * Qsto2 ) / ( 1 + self.ts * mp['kabs'] )
        
        Ra = mp['f'] * mp['kabs'] * Qgut
        
        Isc1 = ( Isc1 + self.ts * I ) / ( 1 + self.ts * ( mp['ka1'] + mp['kd'] ) )
        Isc2 = ( Isc2 + self.ts * mp['kd'] * Isc1 ) / ( 1 + self.ts * mp['ka2'] )
        Ip = ( Ip + self.ts * ( mp['ka1'] * Isc1 + mp['ka2'] * Isc2 ) ) / ( 1 + self.ts * mp['ke'] )
        
        X = ( X + self.ts * mp['p2'] * ( mp['SI'] / mp['VI'] ) * ( Ip - mp['Ipb'] ) ) / ( 1 + self.ts * mp['p2'] )
        
        G = ( G + self.ts * ( mp['SG'] * mp['Gb'] + Ra / mp['VG'] ) ) / ( 1 + self.ts * ( mp['SG'] + ( 1 + mp['r1'] * risk ) * X ) )
        IG = ( IG + (self.ts / mp['alpha'] ) * G ) / ( 1 + self.ts / mp['alpha'] )

        return [G, X, Isc1, Isc2, Ip, Qsto1, Qsto2, Qgut, IG]

    #@jit
    def __hypoglycemic_risk(self,G, r1, r2):
        """
        Internal function that computes the hypoglycemic risk function.

        Parameters
        ----------
        G : float
            The current value of glucose (mg/dl).
        r1 : float
            The first parameter of the fuction.
        r2 : float
            The second parameter of the fuction.

        Returns
        -------
        risk: float
            The hypoglycemic risk value (dimensionless).
        
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

        #Setting the risk model threshold
        G_th = 60
        
        #Set default risk
        risk = 1

        #Compute the risk
        if G < 119.13 and G >= G_th:
            risk = risk + 10*r1*(np.log(G)**r2 - np.log(119.13)**r2)**2
        if G < G_th:
            risk = risk + 10*r1*(np.log(G_th)**r2 - np.log(119.13)**r2)**2

        return risk