import os
import numpy as np

from utils import load_test_data, load_patient_info

from py_replay_bg.py_replay_bg import ReplayBG
from py_replay_bg.visualizer import Visualizer
from py_replay_bg.analyzer import Analyzer

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

print("Replaying " + save_name)

# Replay the twin with the same input data used for twinning
replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                            twinning_method='map',
                            save_workspace=True,
                            save_suffix='_replay_map', snack_absorption=.5, snack_absorption_delay=60)

# Visualize and analyze results
Visualizer.plot_replay_results(replay_results, data=data)
analysis = Analyzer.analyze_replay_results(replay_results, data=data)
print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])
print('TIR: %.2f %%' % analysis['median']['glucose']['time_in_ranges']['time_in_target'])
print('N Days: %.2f days' % analysis['median']['glucose']['data_quality']['number_days_of_observation'])
