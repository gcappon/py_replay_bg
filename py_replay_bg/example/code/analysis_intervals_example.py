import os
import pickle

from py_replay_bg.visualizer import Visualizer
from py_replay_bg.analyzer import Analyzer


# Set the interval to analyze
start_day = 1
end_day = 2

# Set the location of the 'results' folder
results_folder_location = os.path.join(os.path.abspath(''),'..','..','..')

# Initialize results list
replay_results_interval = []

for day in range(start_day, end_day+1):
    with open(os.path.join(results_folder_location, 'results', 'workspaces', 'data_day_' + str(day) + '_replay_intervals_map.pkl'), 'rb') as file:
        replay_results = pickle.load(file)
    replay_results_interval.append(replay_results)

# Visualize and analyze MCMC results
Visualizer.plot_replay_results_interval(replay_results_interval=replay_results_interval)
analysis = Analyzer.analyze_replay_results_interval(replay_results_interval=replay_results_interval)
print(" ----- Analysis using MAP-derived  twins ----- ")
print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])
print('TIR: %.2f %%' % analysis['median']['glucose']['time_in_ranges']['time_in_target'])
print('N Days: %.2f days' % analysis['median']['glucose']['data_quality']['number_days_of_observation'])

# Initialize results list
replay_results_interval = []

for day in range(start_day, end_day + 1):
    with open(os.path.join(results_folder_location, 'results', 'workspaces', 'data_day_' + str(day) + '_replay_intervals_mcmc.pkl'), 'rb') as file:
        replay_results = pickle.load(file)
    replay_results_interval.append(replay_results)

# Visualize and analyze MAP results
Visualizer.plot_replay_results_interval(replay_results_interval=replay_results_interval)
analysis = Analyzer.analyze_replay_results_interval(replay_results_interval=replay_results_interval)
print(" ----- Analysis using MCMC-derived  twins ----- ")
print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])
print('TIR: %.2f %%' % analysis['median']['glucose']['time_in_ranges']['time_in_target'])
print('N Days: %.2f days' % analysis['median']['glucose']['data_quality']['number_days_of_observation'])
