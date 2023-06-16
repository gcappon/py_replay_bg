
from data.data import ReplayBGData

from physiology.model_diff_t1d import model_diff_single_meal_t1d

import pymc as pm
from pymc.ode import DifferentialEquation
import pytensor

import numpy as np

class Identifier:

    def __init__(self):
        pass
    

    def identify(self, rbg, data : dict, BW : float):

        #Set default parameter values
        rbg.model.set_default_model_parameters(data = data, BW = BW, environment = rbg.environment)
        
        #TODO: Set model initial conditions (to start replay according to data)
        #idx_first_non_nan = find(~isnan(data.glucose),1,'first');
        #rbg.model.model_parameters['G0'] = data.glucose(idxFirstNonNan);
        rbg.model.model_parameters['G0'] = data.glucose[0]


        #Get model initial conditions
        mp = rbg.model.model_parameters 
        x0 = np.array([mp['G0'],
                       mp['Xpb'], 
                       mp['u2ss'] / ( mp['ka1'] + mp['kd'] ),                             
                       mp['kd'] / mp['ka2'] * mp['u2ss'] / ( mp['ka1'] + mp['kd'] ),
                       mp['ka1'] / mp['ke'] * mp['u2ss'] / ( mp['ka1'] + mp['kd'] ) + mp['ka2'] / mp['ke'] * mp['kd'] / mp['ka2'] * mp['u2ss'] / ( mp['ka1'] + mp['kd'] ),
                       0,
                       0,
                       mp['Qgutb'],
                       mp['G0']])
        
        #Unpack data 
        rbg_data = ReplayBGData(data = data, BW = BW, rbg = rbg)

    def log_like(theta, rbg_data, rbg):

        #Unpack the model