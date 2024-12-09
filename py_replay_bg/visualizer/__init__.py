from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt

from typing import Dict

import pandas as pd
from tqdm import tqdm

from py_replay_bg.data import ReplayBGData
from py_replay_bg.environment import Environment
from py_replay_bg.model.t1d_model_single_meal import T1DModelSingleMeal
from py_replay_bg.model.t1d_model_multi_meal import T1DModelMultiMeal
from py_replay_bg.dss import DSS


class Visualizer:
    """
    A class to be used by ReplayBG for plotting.

    ...
    Attributes
    ----------
    -

    Methods
    -------
    plot_replay_results(replay_results, data)
        Function that plots the results of ReplayBG replay simulation.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Visualizer object.

        Parameters
        ----------
        -

        Returns
        -------
        None

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """
        pass

    @staticmethod
    def plot_replay_results(
            replay_results: Dict,
            data: pd.DataFrame = None,
            title: str = '',
    ) -> None:
        """
        Function that plots the results of ReplayBG simulation.

        Parameters
        ----------
        replay_results: dict
            The replayed scenario results with fields:
            glucose: dict
                A dictionary which contains the obtained glucose traces simulated via ReplayBG.
            cgm: dict
                A dictionary which contains the obtained cgm traces simulated via ReplayBG.
            insulin_bolus: dict
                A dictionary which contains the insulin boluses simulated via ReplayBG.
            correction_bolus: dict
                A dictionary which contains the correction boluses simulated via ReplayBG.
            insulin_basal: dict
                A dictionary which contains the basal insulin simulated via ReplayBG.
            cho: dict
                A dictionary which contains the meals simulated via ReplayBG.
            hypotreatments: dict
                A dictionary which contains the hypotreatments simulated via ReplayBG.
            meal_announcement: dict
                A dictionary which contains the meal announcements simulated via ReplayBG.
            vo2: dict
                A dictionary which contains the vo2 simulated via ReplayBG.
            sensors: dict
                A dictionary which contains the sensors used during the replayed scenario.
            rbg_data: ReplayBGData
                The data to be used by ReplayBG during simulation.
            model: T1DModelSingleMeal | T1DModelMultiMeal
                An object that represents the physiological model to be used by ReplayBG.
        data: pd.DataFrame, optional, default: None
            Pandas dataframe which contains the data to be used by the tool. If present, adds glucose data to the
            glucose subplot.

        Returns
        -------
        None

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """
        # Subplot 1: Glucose

        fig, ax = None, None
        if replay_results['model'].exercise:
            fig, ax = plt.subplots(4, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1, 1, 1]})
        else:
            fig, ax = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})

        if data is not None:
            ax[0].plot(data.t, data.glucose, marker='*', color='red', linewidth=2, label='CGM data [mg/dl]')
        ax[0].plot(replay_results['rbg_data'].t_data, replay_results['cgm']['median'], marker='o', color='black', linewidth=2, label='CGM replay (Median) [mg/dl]')
        ax[0].fill_between(replay_results['rbg_data'].t_data, replay_results['cgm']['ci25th'], replay_results['cgm']['ci75th'], color='black', alpha=0.2,
                           label='CGM replay (CI 25-75th) [mg/dl]')

        ax[0].plot(replay_results['rbg_data'].t_data, replay_results['glucose']['median'][::replay_results['model'].yts], marker='o', color='blue', linewidth=2,
                   label='Glucose replay (Median) [mg/dl]')
        ax[0].fill_between(replay_results['rbg_data'].t_data, replay_results['glucose']['ci25th'][::replay_results['model'].yts], replay_results['glucose']['ci75th'][::replay_results['model'].yts], color='blue',
                           alpha=0.3, label='Glucose replay (CI 25-75th) [mg/dl]')

        ax[0].grid()
        ax[0].legend()

        # Subplot 2: Meals
        t = np.arange(replay_results['rbg_data'].t_data[0]+ pd.Timedelta(minutes=0), replay_results['rbg_data'].t_data[-1] + pd.Timedelta(minutes=replay_results['model'].yts),
                      timedelta(minutes=1)).astype(datetime)

        cho_events = np.sum(replay_results['cho']['realizations'], axis=0) / replay_results['cho']['realizations'].shape[0]
        ht_events = np.sum(replay_results['hypotreatments']['realizations'], axis=0) / replay_results['hypotreatments']['realizations'].shape[0]

        markerline, stemlines, baseline = ax[1].stem(t, cho_events, basefmt='k:', label='CHO replay (Mean) [g/min]')
        plt.setp(stemlines, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))
        plt.setp(markerline, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))

        markerline, stemlines, baseline = ax[1].stem(t, ht_events, basefmt='k:', label='HT replay (Mean) [g/min]')
        plt.setp(stemlines, 'color', (0.0 / 255, 204.0 / 255, 204.0 / 255))
        plt.setp(markerline, 'color', (0.0 / 255, 204.0 / 255, 204.0 / 255))

        ax[1].grid()
        ax[1].legend()

        # Subplot 3: Insulin

        bolus_events = np.sum(replay_results['insulin_bolus']['realizations'], axis=0) / replay_results['insulin_bolus']['realizations'].shape[0]
        cb_events = np.sum(replay_results['correction_bolus']['realizations'], axis=0) / replay_results['correction_bolus']['realizations'].shape[0]
        basal_rate = np.sum(replay_results['insulin_basal']['realizations'], axis=0) / replay_results['insulin_basal']['realizations'].shape[0]

        markerline, stemlines, baseline = ax[2].stem(t, bolus_events, basefmt='k:',
                                                     label='Bolus insulin replay (Mean) [U/min]')
        plt.setp(stemlines, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))
        plt.setp(markerline, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))

        markerline, stemlines, baseline = ax[2].stem(t, cb_events, basefmt='k:',
                                                     label='CB insulin replay (Mean) [U/min]')
        plt.setp(stemlines, 'color', (51.0 / 255, 102.0 / 255, 0.0 / 255))
        plt.setp(markerline, 'color', (51.0 / 255, 102.0 / 255, 0.0 / 255))

        ax[2].plot(t, basal_rate * 60, color='black', linewidth=2, label='Basal insulin replay (Mean) [U/h]')

        ax[2].grid()
        ax[2].legend()

        # Subplot 4: Exercise

        if replay_results['model'].exercise:

            vo2_events = np.sum(replay_results['vo2']['realizations'], axis=0) / replay_results['vo2']['realizations'].shape[0]

            markerline, stemlines, baseline = ax[3].stem(t, vo2_events, basefmt='k:', label='VO2 replay (Mean) [-]')
            plt.setp(stemlines, 'color', (249.0 / 255, 115.0 / 255, 6.0 / 255))
            plt.setp(markerline, 'color', (249.0 / 255, 115.0 / 255, 6.0 / 255))

            ax[3].grid()
            ax[3].legend()

        fig.suptitle(title, fontweight='bold')
        plt.show()


    @staticmethod
    def plot_replay_results_interval(
            replay_results_interval: list,
            data_interval: list = None,
            title: str = '',
    ) -> None:
        """
        Function that plots the results of ReplayBG simulation (intervals).

        Parameters
        ----------
        replay_results_interval: list
            A list dictionaries of replayed scenario results. Each element has fields:
            glucose: dict
                A dictionary which contains the obtained glucose traces simulated via ReplayBG.
            cgm: dict
                A dictionary which contains the obtained cgm traces simulated via ReplayBG.
            insulin_bolus: dict
                A dictionary which contains the insulin boluses simulated via ReplayBG.
            correction_bolus: dict
                A dictionary which contains the correction boluses simulated via ReplayBG.
            insulin_basal: dict
                A dictionary which contains the basal insulin simulated via ReplayBG.
            cho: dict
                A dictionary which contains the meals simulated via ReplayBG.
            hypotreatments: dict
                A dictionary which contains the hypotreatments simulated via ReplayBG.
            meal_announcement: dict
                A dictionary which contains the meal announcements simulated via ReplayBG.
            vo2: dict
                A dictionary which contains the vo2 simulated via ReplayBG.
            sensors: dict
                A dictionary which contains the sensors used during the replayed scenario.
            rbg_data: ReplayBGData
                The data to be used by ReplayBG during simulation.
            model: T1DModelSingleMeal | T1DModelMultiMeal
                An object that represents the physiological model to be used by ReplayBG.
        data_interval: list, optional, default: None
            A list of pandas dataframe which contains the data to be used by the tool. If present, adds glucose data
            to the glucose subplot.

        Returns
        -------
        None

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """
        data = None
        if data_interval is not None:
            data = pd.concat(data_interval, axis=0, ignore_index=True)

        # Pad each array to the maximum shape
        replay_results = dict()


        # Re-map glucose data
        fields = ['median', 'ci5th', 'ci25th', 'ci75th', 'ci95th']
        category = ['glucose', 'cgm']

        for c in category:

            replay_results[c] = dict()

            for f in fields:
                replay_results[c][f] = dict()

                replay_results[c][f] = [r[c][f] for r in replay_results_interval]
                replay_results[c][f] = np.concatenate(replay_results[c][f], axis=0)

        # Re-map cho, insulin, and vo2 data
        category = ['cho', 'hypotreatments', 'insulin_bolus', 'correction_bolus', 'insulin_basal', 'vo2']

        for c in category:
            replay_results[c] = dict()
            replay_results[c]['realizations'] = [r[c]['realizations'] for r in replay_results_interval]
            replay_results[c]['realizations'] = np.concatenate(replay_results[c]['realizations'], axis=1)

        replay_results['model'] = replay_results_interval[0]['model']
        t_data = [r['rbg_data'].t_data for r in replay_results_interval]
        replay_results['rbg_data'] = replay_results_interval[0]['rbg_data']
        replay_results['rbg_data'].t_data = np.concatenate(t_data, axis=0)

        Visualizer.plot_replay_results(replay_results=replay_results, data=data, title=title)
