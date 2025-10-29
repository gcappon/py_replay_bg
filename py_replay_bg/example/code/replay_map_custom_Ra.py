import os
import pickle

import numpy as np

from py_replay_bg.replay.custom_ra import CustomRaBase
from utils import load_test_data, load_patient_info

from py_replay_bg.py_replay_bg import ReplayBG
from py_replay_bg.visualizer import Visualizer


class CustomRa(CustomRaBase):
    """
    Example implementation of the CustomRaBase class to simulate the rate of appearance (Ra) of carbohydrates in the bloodstream
    based on a two-compartment stomach model followed by a gut compartment.
    This reproduces the model inside ReplayBG.
    """
    def __init__(self, CHO, k_empt, k_abs, f=1.0, beta=0, bw=70.0):
        super().__init__()
        self.dt = 1.0  # time step in minutes
        self.CHO = CHO * 1000 / bw  # np.array of CHO at each timestamp converted to mg/(kg*min)
        self.k_empt = k_empt
        self.k_abs = k_abs
        self.f = f
        self.beta = int(beta)  # delay in number of time steps
        self.Q_sto1 = 0.0
        self.Q_sto2 = 0.0
        self.Q_gut = 0.0
        self.bw = bw  # body weight in kg

    def simulate_forcing_ra(self, time: np.ndarray, time_index: int) -> float:
        # Apply delay (beta) in indices
        cho_idx = (time_index - self.beta)
        CHO_input = self.CHO[cho_idx - 1] if cho_idx >= 0 else 0.0

        dQ_sto1 = -self.k_empt * self.Q_sto1 + CHO_input
        dQ_sto2 = self.k_empt * self.Q_sto1 - self.k_empt * self.Q_sto2
        dQ_gut = self.k_empt * self.Q_sto2 - self.k_abs * self.Q_gut

        self.Q_sto1 += dQ_sto1 * self.dt
        self.Q_sto2 += dQ_sto2 * self.dt
        self.Q_gut += dQ_gut * self.dt

        Ra = self.f * self.k_abs * self.Q_gut
        return Ra

    def get_events(self):
        return self.CHO


# Set verbosity
verbose = True
plot_mode = False

# Set other parameters for twinning
blueprint = 'multi-meal'
save_folder = os.path.join(os.path.abspath(''), '..', '..', '..')

# load patient_info
patient_info = load_patient_info()
p = np.where(patient_info['patient'] == 1)[0][0]
# Set bw and u2ss
bw = float(patient_info.bw.values[p])

# Instantiate ReplayBG
rbg = ReplayBG(blueprint=blueprint, save_folder=save_folder,
               yts=5, exercise=False,
               seed=1,
               verbose=verbose, plot_mode=plot_mode)

# Load data and set save_name
data = load_test_data(day=1)
save_name = 'data_day_' + str(1)

# Extract snack CHO and set to zero in data to use the custom Ra
external_snack = np.where(data['cho_label'] == 'S', data['cho'], 0.0)
external_snack = np.repeat(external_snack, 5)
data.loc[data.cho_label == 'S', 'cho'] = 0.0

print("Replaying " + save_name)

with open(os.path.join(save_folder, 'results/map/map_data_day_1.pkl'), 'rb') as f:
    twinning_results = pickle.load(f)
    draws = twinning_results['draws']
    snackRa = CustomRa(CHO=external_snack,
                       k_empt=draws['kempt'],
                       k_abs=draws['kabs_S'],
                       f=0.9,
                       beta=draws['beta_S'], bw=bw)

# Replay the twin with the same input data used for twinning
replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                            twinning_method='map',
                            save_workspace=False,
                            save_suffix='_replay_map',
                            custom_ra=snackRa)

# Visualize and analyze results
Visualizer.plot_replay_results(replay_results, data=data)
