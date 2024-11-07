import os
import numpy as np
import pandas as pd

from multiprocessing import freeze_support

from py_replay_bg.py_replay_bg import ReplayBG
from py_replay_bg.visualizer import Visualizer
from py_replay_bg.analyzer import Analyzer


if __name__ == '__main__':
    freeze_support()

    # Set verbosity
    verbose = True
    plot_mode = False

    # Set the number of steps for MCMC
    n_steps = 5000  # 5k is for testing. In production, this should be >= 50k

    # Set other parameters for twinning
    scenario = 'multi-meal'
    save_folder = os.path.join(os.path.abspath(''),'..','..','..')
    parallelize = True

    # load patient_info
    patient_info = pd.read_csv(os.path.join(os.path.abspath(''), '..', 'data', 'patient_info.csv'))
    p = np.where(patient_info['patient'] == 1)[0][0]
    # Set bw and u2ss
    bw = float(patient_info.bw.values[p])
    u2ss = float(patient_info.u2ss.values[p])

    # Instantiate ReplayBG
    rbg = ReplayBG(scenario=scenario, save_folder=save_folder,
                   yts=5, exercise=False,
                   seed=1,
                   verbose=verbose, plot_mode=plot_mode)

    # Load data and set save_name
    data = pd.read_csv(os.path.join(os.path.abspath(''), '..', 'data', 'data_day_1.csv'))
    data.t = pd.to_datetime(data['t'])
    save_name = 'data_day_1'

    print("Twinning " + save_name)

    # Step 1. Identification Run twinning procedure
    rbg.twin(data=data, bw=bw, save_name=save_name,
             twinning_method='mcmc',
             parallelize=parallelize,
             n_steps=n_steps,
             u2ss=u2ss)

    # Replay the twin with the same input data to get the initial conditions for the subsequent day
    replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                                twinning_method='mcmc',
                                save_workspace=True,
                                u2ss=u2ss,
                                save_suffix='_twin_mcmc')

    Visualizer.plot_replay_results(replay_results, data=data)
    analysis = Analyzer.analyze_replay_results(replay_results, data=data)
    print('Fit MARD: %.2f %%' % analysis['median']['twin']['mard'])

import os
import pandas as pd
from py_replay_bg.py_replay_bg import ReplayBG

# Get data
data = pd.read_csv(os.path.join(os.path.abspath(''),'..', 'data', 'multi-meal_example.csv'))
data.t = pd.to_datetime(data['t'])

# Step 1. Identification
modality = 'twinning' # set modality as 'identification'
bw = 100 # set the patient body weight
scenario = 'multi-meal' # set the type of scenario corresponding to the data at hand (can be single-meal or multi-meal)
save_name = 'test_multi_meal' # set a save name
n_steps = 2500 # set the number of steps that will be used for identification (for multi-meal it should be at least 50k)
save_folder = os.path.abspath('') # set the results folder to the current folder

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder, n_steps=n_steps)

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