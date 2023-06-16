
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

        
        
        #Unpack data 
        rbg_data = ReplayBGData(data = data, BW = BW, rbg = rbg)

    def log_like(self, theta, rbg_data, rbg):

        #Unpack the model