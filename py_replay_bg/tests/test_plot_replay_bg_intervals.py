import os
import pandas as pd
import numpy as np
from py_replay_bg.py_replay_bg import ReplayBG
from matplotlib import pyplot as plt
from datetime import timedelta,datetime


def load_test_data(day):
    df = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg', 'example', 'data', 'data_day' + str(day) + '.csv'))
    df.t = pd.to_datetime(df['t'])
    return df


def load_patient_info():
    df = pd.read_csv(os.path.join(os.path.abspath(''), 'py_replay_bg', 'example', 'data', 'patient_info.csv'))
    return df


def plot_results(t, cgm, glucose, insulin_bolus, insulin_basal, cho, data_cgm=None):

    # Subplot 1: Glucose
    fig, ax = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})
    if data_cgm is not None:
        ax[0].plot(t, data_cgm, marker='o', color='red', linewidth=2,
                   label='Glucose data [mg/dl]')

    ax[0].plot(t, cgm, marker='o', color='black', linewidth=2, label='CGM replay (Median) [mg/dl]')
    t = np.arange(t[0], t[-1] + pd.to_timedelta(5, unit='m'),
                  timedelta(minutes=1)).astype(datetime)
    t=pd.to_datetime(t)
    ax[0].plot(t, glucose, marker='o', color='blue', linewidth=2,
               label='Glucose replay (Median) [mg/dl]')

    ax[0].grid()
    ax[0].legend()

    # Subplot 2: Meals
    markerline, stemlines, baseline = ax[1].stem(t, cho, basefmt='k:', label='CHO data [g/min]')
    plt.setp(stemlines, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))
    plt.setp(markerline, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))

    ax[1].grid()
    ax[1].legend()

    # Subplot 3: Insulin
    markerline, stemlines, baseline = ax[2].stem(t, insulin_bolus, basefmt='k:',
                                                 label='Bolus insulin data [U/min]')
    plt.setp(stemlines, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))
    plt.setp(markerline, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))
    ax[2].plot(t, insulin_basal * 60, color='black', linewidth=2, label='Basal insulin data [U/h]')

    ax[2].grid()
    ax[2].legend()

    plt.show()


def test_replay_bg():

    # Set verbosity
    verbose = True
    plot_mode = False

    # Set other parameters for identification
    scenario = 'multi-meal'
    save_folder = os.path.join(os.path.abspath(''), '..', '..')

    # load patient_info
    patient_info = load_patient_info()
    p = np.where(patient_info['patient'] == 1)[0][0]
    # Set bw and u2ss
    bw = float(patient_info.bw.values[p])
    u2ss = float(patient_info.u2ss.values[p])

    # Initialize initial conditions
    X0 = None

    # Set interval to be showed
    initial_day = 1
    final_day = 2

    # Initialize vectors to be used to generate the plot
    t = None
    glucose = np.empty([])
    cgm = np.empty([])
    insulin_bolus = np.empty([])
    insulin_basal = np.empty([])
    cho = np.empty([])
    data_cgm = np.empty([])

    # Initialize the sensors to use during the replay
    sensors = None

    for day in range(initial_day, final_day+1):

        # Load data
        data = load_test_data(day=day)

        # This is to allow "playing" with the original inputs and see what happens
        data.cho = data.cho*1
        data.basal = data.basal*1
        data.bolus = data.bolus * 1

        # Set save_name
        save_name = 'data_day_' + str(day)

        # Set previous_data_name according to X0 value. If it is not None, previous_data_name will be set to the
        # save_name of the previous day.
        if X0 is None:
            previous_data_name = None
        else:
            previous_data_name = 'data_day_' + str(day - 1)

        # Create ReplayBG
        rbg = ReplayBG(modality='replay', data=data, bw=bw, scenario=scenario, save_name=save_name,
                       save_folder=save_folder,
                       parallelize=True, save_workspace=False, analyze_results=False,
                       verbose=verbose, plot_mode=plot_mode,
                       X0=X0, u2ss=u2ss,
                       previous_data_name=previous_data_name)
        # Run it
        results = rbg.run(data=data, bw=bw, n_replay=1, sensors=sensors)

        # Set the cgm sensors
        sensors = results['sensors']

        # Populate the vectors to be used to generate the plots
        if t is None:
            t = data.t.values
        else:
            t = np.append(t, data.t.values)
        glucose = np.append(glucose, results['glucose']['median'])
        cgm = np.append(cgm, results['cgm']['median'])
        cho = np.append(cho, results['cho']['realizations'][0])
        insulin_basal = np.append(insulin_basal, results['insulin_basal']['realizations'][0])
        insulin_bolus = np.append(insulin_bolus, results['insulin_bolus']['realizations'][0])

        # Set X0 for next day
        X0 = results['x_end']['realizations'][0].tolist()

        data_cgm = np.append(data_cgm, data.glucose.values)

    # Generate the plot (get rid of the first sample if needed since it is spurious)
    plot_results(t=t, glucose=glucose[1:], cgm=cgm[1:], insulin_bolus=insulin_bolus[1:],
                 insulin_basal=insulin_basal[1:], cho=cho[1:], data_cgm=data_cgm[1:])