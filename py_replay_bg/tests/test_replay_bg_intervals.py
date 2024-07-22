import os
import pandas as pd
import numpy as np
from py_replay_bg.py_replay_bg import ReplayBG

def load_test_data(day):
    df = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg', 'example', 'data', 'data_day' + str(day) + '.csv'))
    df.t = pd.to_datetime(df['t'])
    return df

def load_patient_info():
    df = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg', 'example', 'data', 'patient_info.csv'))
    return df

def test_replay_bg():

    # Set verbosity
    verbose = True
    plot_mode = False

    # Set other parameters for identification
    scenario = 'multi-meal'
    n_steps = 5000  # Suggested n_steps is >= 50k
    save_folder = os.path.join(os.path.abspath(''), '..', '..')

    # load patient_info
    patient_info = load_patient_info()
    p = np.where(patient_info['patient'] == 1)[0][0]
    # Set bw and u2ss
    bw = float(patient_info.bw.values[p])
    u2ss = float(patient_info.u2ss.values[p])


    # Day 1
    X0 = None
    data = load_test_data(day=1)
    save_name = 'data_day_1'
    print("Identifying " + save_name)

    # Instantiate ReplayBG for identification
    rbg = ReplayBG(modality='identification', data=data, bw=bw, scenario=scenario, save_name=save_name,
                   save_folder=save_folder, n_steps=n_steps,
                   parallelize=True, save_workspace=False, analyze_results=False,
                   verbose=verbose, plot_mode=plot_mode,
                   X0=X0, u2ss=u2ss)
    # Run it
    rbg.run(data=data, bw=bw)

    # Run again for obtaining X0
    rbg = ReplayBG(modality='replay', data=data, bw=bw, scenario=scenario, save_name=save_name,
                   save_folder=save_folder, n_steps=n_steps,
                   parallelize=True, save_workspace=False, analyze_results=False,
                   verbose=verbose, plot_mode=plot_mode,
                   X0=X0, u2ss=u2ss)
    # Run it
    results = rbg.run(data=data, bw=bw, n_replay=1)

    # Set X0 for next day
    X0 = results['x_end']['realizations'][0].tolist()

    # Day 2
    data = load_test_data(day=2)
    save_name = 'data_day_2'

    # Override initial conditions of glucose (to avoid jumps of glucose values during identification)
    idx = np.where(data.glucose.isnull().values == False)[0][0]
    X0[0] = data.glucose.values[idx]
    X0[-1] = data.glucose.values[idx]

    # Instantiate ReplayBG for identification
    rbg = ReplayBG(modality='identification', data=data, bw=bw, scenario=scenario, save_name=save_name,
                   save_folder=save_folder, n_steps=n_steps,
                   parallelize=True, save_workspace=False, analyze_results=False,
                   verbose=verbose, plot_mode=plot_mode,
                   X0=X0, u2ss=u2ss, previous_data_name='data_day_1')
    # Run it
    rbg.run(data=data, bw=bw)