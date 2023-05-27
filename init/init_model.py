import random
import time
from datetime import datetime, timedelta
import numpy as np

def init_model(data, sample_time, glucose_model, pathology,
                     exercise, seed, environment):
    """
    Initializes the 'model' core variable.

    Parameters
    ----------
    data : pd.DataFrame
        Pandas dataframe which contains the data to be used by the tool
    sample_time : int
        An integer that specifies the data sample time
    glucose_model : string
        A string that specifies the glucose model to use
    pathology: string
        A string that specifies the pathology related to the given data
    exercise : boolean
        A boolean indicating wheter to use the exercise submodel or not
    seed : int
        An integer that specifies the random seed. For reproducibility
    environment : dict
        A dictionary that contains general parameters to be used by ReplayBG

    Returns
    -------
    model : dict
        A dictionary that contains general parameters of the physiological model

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None

    Copyright
    --------
    (C) 2023 Giacomo Cappon
    This file is part of ReplayBG.
    """
        
    if environment['verbose']:
        print('Setting up the model hyperparameters...')
        tic = time.perf_counter()
    
    #Initialize the model dict
    model = {}

    #Time constants within the simulation
    model['TS'] = 1 #integration time
    model['YTS'] = sample_time #sample time
    model['T'] = int( (np.array(data.t)[-1].astype(datetime)-np.array(data.t)[0].astype(datetime))/(60*1000000000) + sample_time) #simulation timespan [min]
    model['TSTEPS'] = int(model['T']/model['TS']) #total simulation length [integration steps]
    model['TYSTEPS'] = int(model['T']/model['YTS']) #total simulation length [sample steps]
    
    #Data hyperparameters
    model['glucose_model'] = glucose_model #glucose selection {'BG','IG'}
    model['pathology'] = pathology #model selection {'t1d','t2d','pbh'}
    
    #Is exercise submodel active?
    model['exercise'] = exercise
    
    #Model dimensionality
    if model['pathology'] == 't1d':
        if environment['scenario'] == 'single-meal':
            model['nx'] = 9 #number of states
        elif environment['scenario'] == 'multi-meal':
            model['nx'] = 21 #number of states

        if exercise:
            model.nx = model.nx + 1
    
    elif model['pathology'] == 't2d':
        pass #TODO: implement t2d model
    elif model['pathology'] == 'pbh':
        pass #TODO: implement pbh model
    elif model['pathology'] == 'healthy':
            pass #TODO: implement healthy model
    
    #Random seed
    model['seed'] = seed
    random.seed(seed)
    
    if environment['verbose']:
        toc = time.perf_counter()
        print(f"DONE. (Elapsed time {toc - tic:0.4f} seconds)")

    return model 