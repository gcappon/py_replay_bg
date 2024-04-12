# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 16:41:07 2024

@author: bio
"""

import os
import pandas as pd
import pickle
from matplotlib import pyplot as plt
import seaborn as sns
from py_replay_bg.py_replay_bg import ReplayBG

# Get data
data = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg','example','data', 'single-meal_example.csv'))
data.t = pd.to_datetime(data['t'])

# Step 1. Identification
modality = 'identification' # set modality as 'identification'
bw = 100 # set the patient body weight
scenario = 'single-meal' # set the type of scenario corresponding to the data at hand (can be single-meal or multi-meal)
save_name = 'test_single_meal' # set a save name
basal_scenario = 'over_basal'
n_steps = 25000 # set the number of steps that will be used for identification (for multi-meal it should be at least 100k)
save_folder = os.path.abspath('') # set the results folder to the current folder

# Instantiate ReplayBG

rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, basal_scenario=basal_scenario, save_name=save_name, save_folder=save_folder, n_steps=n_steps)

# Run it
rbg.run(data=data, bw=bw)

# Step 2. Replay
modality = 'replay' # change modality as 'replay'

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder)

# Run it
rbg.run(data=data, bw=bw)

# Step 2 bis. Replay with less insulin
data.bolus = data.bolus * .7 # Reduce insulin boluses by 30%

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder)

# Run it
rbg.run(data=data, bw=bw)



