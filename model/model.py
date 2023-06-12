import random
from datetime import datetime
import numpy as np

class Model:
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
    pathology: string, {'t1d','t2d','pbh'}
        The pathology of the model to be simulated. 
    exercise : boolean
        A boolean indicating wheter to use the exercise submodel or not.
    seed : int
        An integer that specifies the random seed. For reproducibility.
    nx : int
        The number of model states.
    Methods
    -------
    None
    """
    def __init__(self, data, environment, ts = 1, yts = 5, glucose_model = 'IG', pathology = 't1d', exercise = False, seed = 1):
        """
        Constructs all the necessary attributes for the Model object.

        Parameters
        ----------
        data : pandas.DataFrame
            Pandas dataframe which contains the data to be used by the tool
        environment: Environment
            An object that contains the general parameters to be used by ReplayBG.
        ts: int, optional, default : 1 
            The integration time step.
        yts: int, optional, default : 5 
            The measurement (cgm) sample time.
        glucose_model: string, {'IG','BG'}, optional, default : 'IG'
            The model equation to be used as measured glucose.
        pathology: string, {'t1d','t2d','pbh'}, optional, default : 't1d'
            The pathology of the model to be simulated. 
        exercise : boolean, optional, default : False
            A boolean indicating wheter to use the exercise submodel or not.
        seed : int, optional, default : 1
            An integer that specifies the random seed. For reproducibility.
        """

        #Time constants during simulation
        self.ts = ts
        self.yts = yts
        self.t = int( (np.array(data.t)[-1].astype(datetime)-np.array(data.t)[0].astype(datetime))/(60*1000000000) + self.yts) 
        self.tsteps = int(self.t / self.ts)
        self.tysteps = int(self.t / self.yts) 
        
        #Glucose selection
        self.glucose_model = glucose_model #glucose selection {'BG','IG'}

        #Pathology selection
        self.pathology = pathology #model selection {'t1d','t2d','pbh'}

        #Is exercise submodel active?
        self.exercise = exercise

        #Set the random seed
        self.seed = seed
        random.seed(seed)

        #Model dimensionality
        if self.pathology == 't1d':
            
            if environment.scenario == 'single-meal':
                self.nx = 9
            elif environment.scenario == 'multi-meal':
                self.nx = 21

            if self.exercise:
                self.nx = self.nx + 1
    
        elif self.pathology == 't2d':
            pass #TODO: implement t2d model
        elif self.pathology == 'pbh':
            pass #TODO: implement pbh model
        elif self.pathology == 'healthy':
            pass #TODO: implement healthy model