import os
import numpy as np
import pandas as pd
from py_replay_bg.py_replay_bg import ReplayBG
from datetime import datetime, timedelta

from multiprocessing import freeze_support

from tqdm import tqdm

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
        t = np.arange(datetime(2023, 1, 1, 6, 0, 0), datetime(2023, 1, 1, 12, 0, 0), timedelta(minutes=5)).astype(
            datetime)
        glucose = np.arange(360, 360 + t.size, 1)
        cho = np.zeros(t.size)
        cho[0] = 10
        # cho[5] = 20
        bolus = np.zeros(t.size)
        bolus[0] = 1
        # bolus[5] = 2
        basal = np.zeros(t.size) + 0.01 / 60
        choLabel = np.repeat('', t.size)
        choLabel[0] = 'B'
        bolusLabel = np.repeat('', t.size)
        bolusLabel[0] = 'B'
        exercise = np.zeros(t.size)
        d = {'t': t, 'glucose': glucose, 'cho': cho, 'cho_label': choLabel, 'bolus': bolus, 'bolus_label': bolusLabel,
             'basal': basal, 'exercise': exercise}
        df = pd.DataFrame(data=d)

    return df


#if __name__ == '__main__':
def test_replay_bg():
    freeze_support()

    # Get test data
    data = load_test_data(real=True, single_meal=True)

    # Set other parameters for identification
    modality = 'identification'
    bw = 100
    scenario = 'single-meal'
    save_name = 'test_single_meal'
    save_suffix = ''
    save_folder = os.path.abspath('')

    # Instantiate ReplayBG
    rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder, save_suffix=save_suffix,
                   n_steps=100000, parallelize=True, verbose=True)

    # Run it
    rbg.run(data=data, bw=bw)
