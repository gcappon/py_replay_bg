import os
import pickle

from py_replay_bg.visualizer import Visualizer
from py_replay_bg.analyzer import Analyzer

def test_replay_bg():

    # Set the location of the 'results' folder
    results_folder_location = os.path.join(os.path.abspath(''))

    with open(os.path.join(results_folder_location, 'results', 'workspaces', 'data_day_1_replay_mcmc.pkl'), 'rb') as file:
        replay_results = pickle.load(file)

    # Visualize and analyze MCMC results
    Visualizer.plot_replay_results(replay_results)
    analysis = Analyzer.analyze_replay_results(replay_results)
    print(" ----- Analysis using MCMC-derived  twins ----- ")
    print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])
    print('TIR: %.2f %%' % analysis['median']['glucose']['time_in_ranges']['time_in_target'])
    print('N Days: %.2f days' % analysis['median']['glucose']['data_quality']['number_days_of_observation'])

    with open(os.path.join(results_folder_location, 'results', 'workspaces', 'data_day_1_replay_map.pkl'), 'rb') as file:
        replay_results = pickle.load(file)

    # Visualize and analyze MAP results
    Visualizer.plot_replay_results(replay_results)
    analysis = Analyzer.analyze_replay_results(replay_results)
    print(" ----- Analysis using MAP-derived  twins ----- ")
    print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])
    print('TIR: %.2f %%' % analysis['median']['glucose']['time_in_ranges']['time_in_target'])
    print('N Days: %.2f days' % analysis['median']['glucose']['data_quality']['number_days_of_observation'])
