from typing import Dict

from py_agata.py_agata import Agata
from py_agata.utils import glucose_vector_to_dataframe
from py_agata.error import *


class Analyzer:
    """
    A class to be used by ReplayBG for analyzing results.

    ...
    Attributes
    ----------
    -

    Methods
    -------
    analyze_replay_results(replay_results, data)
        Function that analyze the results of ReplayBG replay simulation.
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
    def analyze_replay_results(
            replay_results: Dict,
            data: pd.DataFrame = None,
    ) -> Dict:
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
            Pandas dataframe which contains the data to be used by the tool. If present, also analyzes glucose fit vs
            data.
        """
        agata = Agata(glycemic_target='diabetes')

        analysis = dict()
        fields = ['median', 'ci5th', 'ci25th', 'ci75th', 'ci95th']
        glu = ['glucose', 'cgm']
        for f in fields:

            analysis[f] = dict()

            for g in glu:

                # Transform the glucose profile under examination to a dataframe compatible with Agata
                ts = replay_results['model'].ts if g == 'glucose' else replay_results['model'].yts
                profile = glucose_vector_to_dataframe(replay_results[g][f], ts)

                # Analyse the glucose profile
                analysis[f][g] = agata.analyze_glucose_profile(profile)

        total_insulin = np.zeros(shape=(replay_results['insulin_bolus']["realizations"].shape[0],))
        total_bolus_insulin = np.zeros(shape=(replay_results['insulin_bolus']["realizations"].shape[0],))
        total_correction_bolus_insulin = np.zeros(shape=(replay_results['insulin_bolus']["realizations"].shape[0],))
        total_basal_insulin = np.zeros(shape=(replay_results['insulin_bolus']["realizations"].shape[0],))

        total_cho = np.zeros(shape=(replay_results['cho']["realizations"].shape[0],))
        total_hypotreatments = np.zeros(shape=(replay_results['cho']["realizations"].shape[0],))
        total_meal_announcements = np.zeros(shape=(replay_results['cho']["realizations"].shape[0],))

        correction_bolus_insulin_number = np.zeros(shape=(replay_results['insulin_bolus']["realizations"].shape[0],))
        hypotreatment_number = np.zeros(shape=(replay_results['cho']["realizations"].shape[0],))

        exercise_session_number = np.zeros(shape=(replay_results['vo2']["realizations"].shape[0],))
        # TODO: add other metrics for exercise (e.g., average VO2 per session, duration of each session)

        for r in range(total_insulin.size):

            # Compute insulin amounts for each realization
            total_insulin[r] = np.sum(replay_results['insulin_bolus']["realizations"][r, :]) + np.sum(replay_results['insulin_basal']["realizations"][r, :])
            total_bolus_insulin[r] = np.sum(replay_results['insulin_bolus']["realizations"][r, :])
            total_basal_insulin[r] = np.sum(replay_results['insulin_basal']["realizations"][r, :])
            total_correction_bolus_insulin[r] = np.sum(replay_results['correction_bolus']["realizations"][r, :])

            # Compute CHO amounts for each realization
            total_cho[r] = np.sum(replay_results['cho']["realizations"][r, :])
            total_hypotreatments[r] = np.sum(replay_results['hypotreatments']["realizations"][r, :])
            total_meal_announcements[r] = np.sum(replay_results['meal_announcement']["realizations"][r, :])

            # Compute numbers for each realization
            correction_bolus_insulin_number[r] = np.where(replay_results['correction_bolus']["realizations"])[0].size
            hypotreatment_number[r] = np.where(replay_results['hypotreatments']["realizations"])[0].size

            # Compute exercise metrics for each realization
            e = np.where(replay_results['hypotreatments']["realizations"])[0]
            if e.size == 0:
                exercise_session_number[r] = 0
            else:
                d = np.diff(e)
                idxs = np.where(d > 1)[0]
                exercise_session_number[r] = 1 + idxs.size

        p = [50, 5, 25, 75, 95]
        for f in range(len(fields)):
            analysis[fields[f]]["event"] = dict()

            analysis[fields[f]]["event"]["total_insulin"] = np.percentile(total_insulin, p[f])
            analysis[fields[f]]["event"]["total_bolus_insulin"] = np.percentile(total_bolus_insulin, p[f])
            analysis[fields[f]]["event"]["total_basal_insulin"] = np.percentile(total_basal_insulin, p[f])
            analysis[fields[f]]["event"]["total_correction_bolus_insulin"] = np.percentile(
                total_correction_bolus_insulin, p[f])

            analysis[fields[f]]["event"]["total_cho"] = np.percentile(total_cho, p[f])
            analysis[fields[f]]["event"]["total_hypotreatments"] = np.percentile(total_hypotreatments, p[f])
            analysis[fields[f]]["event"]["total_meal_announcements"] = np.percentile(total_meal_announcements, p[f])

            analysis[fields[f]]["event"]["correction_bolus_insulin_number"] = np.percentile(
                correction_bolus_insulin_number, p[f])
            analysis[fields[f]]["event"]["hypotreatment_number"] = np.percentile(hypotreatment_number, p[f])

            analysis[fields[f]]["event"]["exercise_session_number"] = np.percentile(exercise_session_number, p[f])

        if data is not None:
            for f in fields:

                analysis[f]["twin"] = dict()

                profile = replay_results['glucose'][f][::replay_results['model'].yts]

                data_hat = glucose_vector_to_dataframe(profile, replay_results['model'].yts,
                                                       pd.to_datetime(data.t.values[0]).to_pydatetime())

                analysis[f]["twin"]["rmse"] = rmse(data, data_hat)
                analysis[f]["twin"]["mard"] = mard(data, data_hat)
                analysis[f]["twin"]["clarke"] = clarke(data, data_hat)
                analysis[f]["twin"]["cod"] = cod(data, data_hat)
                analysis[f]["twin"]["g_rmse"] = g_rmse(data, data_hat)

        return analysis

    @staticmethod
    def analyze_replay_results_interval(
            replay_results_interval: list,
            data_interval: list = None,
    ) -> Dict:
        """
        Function that analyzes the results of ReplayBG simulation (intervals).

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
        category = ['cho', 'hypotreatments', 'insulin_bolus', 'correction_bolus', 'insulin_basal', 'vo2',
                    'meal_announcement']

        for c in category:
            replay_results[c] = dict()
            replay_results[c]['realizations'] = [r[c]['realizations'] for r in replay_results_interval]
            replay_results[c]['realizations'] = np.concatenate(replay_results[c]['realizations'], axis=1)

        replay_results['model'] = replay_results_interval[0]['model']
        t_data = [r['rbg_data'].t_data for r in replay_results_interval]
        replay_results['rbg_data'] = replay_results_interval[0]['rbg_data']
        replay_results['rbg_data'].t_data = np.concatenate(t_data, axis=0)

        return Analyzer.analyze_replay_results(replay_results=replay_results, data=data)
