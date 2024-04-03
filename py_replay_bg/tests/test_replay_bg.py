import os
import pandas as pd
from py_replay_bg.py_replay_bg import ReplayBG

def load_test_data(real=True, single_meal=True):
    if real:

        if single_meal:
            # Load real single meal data
            df = pd.read_csv(os.path.join(os.path.abspath(''),'py_replay_bg', 'example', 'data', 'single-meal_example.csv'))
            df.t = pd.to_datetime(df['t'])
        else:
            # Load real multi meal data
            df = pd.read_csv(os.path.join(os.path.abspath(''),'py_replay_bg', 'example', 'data', 'multi-meal_example.csv'))
            df.t = pd.to_datetime(df['t'])
    else:
        # Set fake data
        # Load real multi meal data
        df = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg', 'example', 'data', 'multi-meal-fake_example.csv'))
        df.t = pd.to_datetime(df['t'])

    return df

def test_replay_bg():

    # Get test data
    data = load_test_data(real=True, single_meal=False)

    # Set other parameters for identification
    modality = 'identification'
    bw = 100
    scenario = 'multi-meal'
    save_name = 'multi-meal_fake'
    n_steps = 500000
    save_suffix = ''
    save_folder = os.path.abspath('')

    # Instantiate ReplayBG
    rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder, save_suffix=save_suffix,
                   cgm_model='CGM', n_steps=n_steps, parallelize=True, save_workspace=False, analyze_results=False, verbose=True, plot_mode=True)

    # Run it
    results = rbg.run(data=data, bw=bw, n_replay=1)