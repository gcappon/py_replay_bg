import pandas as pd
import os


def load_test_data(day):
    df = pd.read_csv(os.path.join(os.path.abspath(''), '..' , 'data', 'data_day_' + str(day) + '.csv'))
    df.t = pd.to_datetime(df['t'])
    return df


def load_patient_info():
    df = pd.read_csv(os.path.join(os.path.abspath(''), '..', 'data', 'patient_info.csv'))
    return df
