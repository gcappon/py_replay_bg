import os
import numpy as np
import pandas as pd
from replay_bg import ReplayBG
from datetime import datetime, timedelta

from multiprocessing import freeze_support


def load_test_data(real=True):
    if real:
        # Load real data
        df = pd.read_csv(os.path.join('example', 'data', 'single-meal_example.csv'))
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
        d = {'t': t, 'glucose': glucose, 'cho': cho, 'choLabel': choLabel, 'bolus': bolus, 'bolusLabel': bolusLabel,
             'basal': basal, 'exercise': exercise}
        df = pd.DataFrame(data=d)

    return df


if __name__ == '__main__':
    freeze_support()

    # Get test data
    data = load_test_data(real=True)

    # Set other parameters for identification
    modality = 'replay'
    BW = 100
    scenario = 'single-meal'
    save_name = 'test'
    save_suffix = 'gg'

    # Instantiate ReplayBG
    rbg = ReplayBG(modality=modality, data=data, BW=BW, scenario=scenario, save_name=save_name, save_suffix=save_suffix,
                   n_steps=100, parallelize=False,
                   cho_source='generated',
                   verbose=True)

    # Run it
    rbg.run(data=data, BW=BW)
