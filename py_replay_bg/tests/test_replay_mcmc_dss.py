import os
import numpy as np

from py_replay_bg.tests import load_test_data, load_patient_info

from py_replay_bg.py_replay_bg import ReplayBG
from py_replay_bg.visualizer import Visualizer
from py_replay_bg.analyzer import Analyzer

from py_replay_bg.dss.default_dss_handlers import standard_bolus_calculator_handler

def test_replay_bg():

    # Set verbosity
    verbose = True
    plot_mode = False

    # Set other parameters for twinning
    blueprint = 'multi-meal'
    save_folder = os.path.join(os.path.abspath(''))

    # load patient_info
    patient_info = load_patient_info()
    p = np.where(patient_info['patient'] == 1)[0][0]
    # Set bw and u2ss
    bw = float(patient_info.bw.values[p])
    u2ss = float(patient_info.u2ss.values[p])

    # Instantiate ReplayBG
    rbg = ReplayBG(blueprint=blueprint, save_folder=save_folder,
                   yts=5, exercise=False,
                   seed=1,
                   verbose=verbose, plot_mode=plot_mode)

    # Load data and set save_name
    data = load_test_data(day=1)
    save_name = 'data_day_' + str(1)

    # Set params of the bolus calculator
    bolus_calculator_handler_params = dict()
    bolus_calculator_handler_params['cr'] = 7
    bolus_calculator_handler_params['cf'] = 25
    bolus_calculator_handler_params['gt'] = 110

    print("Replaying " + save_name)

    # Replay the twin using a correction insulin bolus injection strategy and the standard formula for
    # meal insulin boluses
    replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                                n_replay=10,
                                twinning_method='mcmc',
                                save_workspace=True,
                                u2ss=u2ss,
                                save_suffix='_replay_mcmc_dss',
                                enable_correction_boluses=True,
                                bolus_source='dss', bolus_calculator_handler=standard_bolus_calculator_handler,
                                bolus_calculator_handler_params=bolus_calculator_handler_params)

    # Visualize and analyze results
    Visualizer.plot_replay_results(replay_results, data=data)
    analysis = Analyzer.analyze_replay_results(replay_results, data=data)
    print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])
    print('TIR: %.2f %%' % analysis['median']['glucose']['time_in_ranges']['time_in_target'])
    print('N Days: %.2f days' % analysis['median']['glucose']['data_quality']['number_days_of_observation'])
