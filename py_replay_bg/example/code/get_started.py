import os
import numpy as np
import pandas as pd

from multiprocessing import freeze_support

from py_replay_bg.py_replay_bg import ReplayBG
from py_replay_bg.visualizer import Visualizer
from py_replay_bg.analyzer import Analyzer


if __name__ == '__main__':
    freeze_support()

    # Set verbosity
    verbose = True
    plot_mode = False

    # Set other parameters for twinning
    blueprint = 'multi-meal'
    save_folder = os.path.join(os.path.abspath(''),'..','..','..')
    parallelize = True

    # Load data
    data = pd.read_csv(os.path.join(os.path.abspath(''), '..', 'data', 'data_day_1.csv'))
    data.t = pd.to_datetime(data['t'])

    # Load patient_info
    patient_info = pd.read_csv(os.path.join(os.path.abspath(''), '..', 'data', 'patient_info.csv'))
    p = np.where(patient_info['patient'] == 1)[0][0]
    # Set bw and u2ss
    bw = float(patient_info.bw.values[p])
    u2ss = float(patient_info.u2ss.values[p])

    # Instantiate ReplayBG
    rbg = ReplayBG(blueprint=blueprint, save_folder=save_folder,
                   yts=5, exercise=False,
                   seed=1,
                   verbose=verbose, plot_mode=plot_mode)

    # Set save name
    save_name = 'data_day_1'

    # Step 1. Run twinning procedure
    rbg.twin(data=data, bw=bw, save_name=save_name,
             twinning_method='mcmc',
             parallelize=parallelize,
             n_steps=5000,
             u2ss=u2ss)

    # Step 2a. Replay the twin with the same input data to get the initial conditions for the subsequent day
    replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                                twinning_method='mcmc',
                                save_workspace=True,
                                save_suffix='_step_2a')

    # Visualize results and compare with the original glucose data
    Visualizer.plot_replay_results(replay_results, data=data)
    # Analyze results
    analysis = Analyzer.analyze_replay_results(replay_results, data=data)
    # Print, for example, the fit MARD and the average glucose
    print('Fit MARD: %.2f %%' % analysis['median']['twin']['mard'])
    print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])

    # Step 2b. Replay the twin with different input data (-30% bolus insulin) to experiment how glucose changes
    data.bolus = data.bolus * .7
    replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                                twinning_method='mcmc',
                                save_workspace=True,
                                u2ss=u2ss,
                                save_suffix='_step_2b')

    # Visualize results
    Visualizer.plot_replay_results(replay_results)
    # Analyze results
    analysis = Analyzer.analyze_replay_results(replay_results)

    # Print, for example, the average glucose
    print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])
