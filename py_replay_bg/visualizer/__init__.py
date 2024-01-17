from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt


class Visualizer:
    """
    A class to be used by ReplayBG for plotting.

    ...
    Attributes
    ----------
    None

    Methods
    -------
    plot_replaybg_results(cgm, glucose, insulin_bolus, insulin_basal, cho, hypotreatments, correction_bolus, vo2, data, rbg)
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Visualizer object.

        Parameters
        ----------
        None

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

    def plot_replaybg_results(self, cgm, glucose, insulin_bolus, insulin_basal, cho, hypotreatments, correction_bolus,
                              vo2, data, rbg):
        """
        Function that plots the results of ReplayBG simulation.

        Parameters
        ----------
        cgm: dict
            A dictionary which contains the obtained cgm traces simulated via ReplayBG.
        glucose: dict
            A dictionary which contains the obtained glucose traces simulated via ReplayBG.
        insulin_bolus: dict
            A dictionary which contains the insulin boluses simulated via ReplayBG.
        insulin_basal: dict
            A dictionary which contains the basal insulin simulated via ReplayBG.
        cho: dict
            A dictionary which contains the meals simulated via ReplayBG.
        hypotreatments: dict
            A dictionary which contains the hypotreatments simulated via ReplayBG.
        correction_bolus: dict
            A dictionary which contains the correction boluses simulated via ReplayBG.
        vo2: dict
            A dictionary which contains the vo2 simulated via ReplayBG.
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        rbg: ReplayBG
            The instance of ReplayBG.

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
        if rbg.model.exercise:
            fig, ax = plt.subplots(4, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1, 1, 1]})
        else:
            fig, ax = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})

        if rbg.environment.modality == 'identification':
            ax[0].plot(data.t, data.glucose, marker='*', color='red', linewidth=2, label='CGM data [mg/dl]')

        ax[0].plot(data.t, cgm['median'], marker='o', color='black', linewidth=2, label='CGM replay (Median) [mg/dl]')
        ax[0].fill_between(data.t, cgm['ci25th'], cgm['ci75th'], color='black', alpha=0.2,
                           label='CGM replay (CI 25-75th) [mg/dl]')

        ax[0].plot(data.t, glucose['median'][::rbg.model.yts], marker='o', color='blue', linewidth=2,
                   label='Glucose replay (Median) [mg/dl]')
        ax[0].fill_between(data.t, glucose['ci25th'][::rbg.model.yts], glucose['ci75th'][::rbg.model.yts], color='blue',
                           alpha=0.3, label='Glucose replay (CI 25-75th) [mg/dl]')

        ax[0].grid()
        ax[0].legend()

        # Subplot 2: Meals

        if rbg.environment.modality == 'replay':
            t = np.arange(data.t.iloc[0], data.t.iloc[-1] + timedelta(minutes=rbg.model.yts),
                          timedelta(minutes=1)).astype(datetime)

            cho_events = np.sum(cho['realizations'], axis=0) / cho['realizations'].shape[0]
            ht_events = np.sum(hypotreatments['realizations'], axis=0) / hypotreatments['realizations'].shape[0]

            markerline, stemlines, baseline = ax[1].stem(t, cho_events, basefmt='k:', label='CHO replay (Mean) [g/min]')
            plt.setp(stemlines, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))
            plt.setp(markerline, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))

            markerline, stemlines, baseline = ax[1].stem(t, ht_events, basefmt='k:', label='HT replay (Mean) [g/min]')
            plt.setp(stemlines, 'color', (0.0 / 255, 204.0 / 255, 204.0 / 255))
            plt.setp(markerline, 'color', (0.0 / 255, 204.0 / 255, 204.0 / 255))

        else:
            markerline, stemlines, baseline = ax[1].stem(data.t, data.cho, basefmt='k:', label='CHO data [g/min]')
            plt.setp(stemlines, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))
            plt.setp(markerline, 'color', (70.0 / 255, 130.0 / 255, 180.0 / 255))

        ax[1].grid()
        ax[1].legend()

        # Subplot 3: Insulin

        if rbg.environment.modality == 'replay':
            t = np.arange(data.t.iloc[0], data.t.iloc[-1] + timedelta(minutes=rbg.model.yts),
                          timedelta(minutes=1)).astype(datetime)

            bolus_events = np.sum(insulin_bolus['realizations'], axis=0) / insulin_bolus['realizations'].shape[0]
            cb_events = np.sum(correction_bolus['realizations'], axis=0) / correction_bolus['realizations'].shape[0]
            basal_rate = np.sum(insulin_basal['realizations'], axis=0) / insulin_basal['realizations'].shape[0]

            markerline, stemlines, baseline = ax[2].stem(t, bolus_events, basefmt='k:',
                                                         label='Bolus insulin replay (Mean) [U/min]')
            plt.setp(stemlines, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))
            plt.setp(markerline, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))

            markerline, stemlines, baseline = ax[2].stem(t, cb_events, basefmt='k:',
                                                         label='CB insulin replay (Mean) [U/min]')
            plt.setp(stemlines, 'color', (51.0 / 255, 102.0 / 255, 0.0 / 255))
            plt.setp(markerline, 'color', (51.0 / 255, 102.0 / 255, 0.0 / 255))

            ax[2].plot(t, basal_rate * 60, color='black', linewidth=2, label='Basal insulin replay (Mean) [U/h]')

        else:

            markerline, stemlines, baseline = ax[2].stem(data.t, data.bolus, basefmt='k:',
                                                         label='Bolus insulin data [U/min]')
            plt.setp(stemlines, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))
            plt.setp(markerline, 'color', (50.0 / 255, 205.0 / 255, 50.0 / 255))
            ax[2].plot(data.t, data.basal * 60, color='black', linewidth=2, label='Basal insulin data [U/h]')

        ax[2].grid()
        ax[2].legend()

        # Subplot 4: Exercise

        if rbg.model.exercise:

            if rbg.environment.modality == 'replay':
                t = np.arange(data.t.iloc[0], data.t.iloc[-1] + timedelta(minutes=rbg.model.yts),
                              timedelta(minutes=1)).astype(datetime)

                vo2_events = np.sum(vo2['realizations'], axis=0) / vo2['realizations'].shape[0]

                markerline, stemlines, baseline = ax[3].stem(t, vo2_events, basefmt='k:', label='VO2 replay (Mean) [-]')
                plt.setp(stemlines, 'color', (249.0 / 255, 115.0 / 255, 6.0 / 255))
                plt.setp(markerline, 'color', (249.0 / 255, 115.0 / 255, 6.0 / 255))

            else:
                markerline, stemlines, baseline = ax[3].stem(data.t, data.bolus, basefmt='k:', label='VO2 data [-]')
                plt.setp(stemlines, 'color', (249.0 / 255, 115.0 / 255, 6.0 / 255))
                plt.setp(markerline, 'color', (249.0 / 255, 115.0 / 255, 6.0 / 255))

            ax[3].grid()
            ax[3].legend()

        plt.show()
