import os
import pandas as pd

def load_test_data(day):
    df = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg', 'example', 'data', 'data_day_' + str(day) + '.csv'))
    df.t = pd.to_datetime(df['t'])
    return df

def load_patient_info():
    df = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg', 'example', 'data', 'patient_info.csv'))
    return df