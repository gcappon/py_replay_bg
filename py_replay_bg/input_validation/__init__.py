import pandas as pd

from py_replay_bg.sensors import CGM


class BasalHandlerValidator:
    """
    Class for validating the 'basal_handler' input parameter of ReplayBG.
    """

    def __init__(self, basal_handler):
        self.basal_handler = basal_handler

    def validate(self):
        if not callable(self.basal_handler):
            raise Exception("'basal_handler' input must be a function.'")


class BasalHandlerParamsValidator:
    """
    Class for validating the 'basal_handler_params' input parameter of ReplayBG.
    """

    def __init__(self, basal_handler_params):
        self.basal_handler_params = basal_handler_params

    def validate(self):
        if self.basal_handler_params is not None:
            if not isinstance(self.basal_handler_params, dict):
                raise Exception("'basal_handler_params' input must be a dict.'")


class BasalSourceValidator:
    """
    Class for validating the 'basal_source' input parameter of ReplayBG.
    """

    def __init__(self, basal_source):
        self.basal_source = basal_source

    def validate(self):
        if not (self.basal_source == 'data' or self.basal_source == 'u2ss' or self.basal_source == 'dss'):
            raise Exception("'basal_source' input must be 'data', 'u2ss', or 'dss'.")


class BolusCalculatorHandlerValidator:
    """
    Class for validating the 'bolus_calculator_handler' input parameter of ReplayBG.
    """

    def __init__(self, bolus_calculator_handler):
        self.bolus_calculator_handler = bolus_calculator_handler

    def validate(self):
        if not callable(self.bolus_calculator_handler):
            raise Exception("'bolus_calculator_handler' input must be a function.'")


class BolusCalculatorHandlerParamsValidator:
    """
    Class for validating the 'bolus_calculator_handler_params' input parameter of ReplayBG.
    """

    def __init__(self, bolus_calculator_handler_params):
        self.bolus_calculator_handler_params = bolus_calculator_handler_params

    def validate(self):
        if self.bolus_calculator_handler_params is not None:
            if not isinstance(self.bolus_calculator_handler_params, dict):
                raise Exception("'bolus_calculator_handler_params' input must be a dict.'")


class BolusSourceValidator:
    """
    Class for validating the 'bolus_source' input parameter of ReplayBG.
    """

    def __init__(self, bolus_source):
        self.bolus_source = bolus_source

    def validate(self):
        if not (self.bolus_source == 'data' or self.bolus_source == 'dss'):
            raise Exception("'bolus_source' input must be 'data' or 'dss'.")


class BWValidator:
    """
    Class for validating the 'bw' input parameter of ReplayBG.
    """

    def __init__(self, bw):
        self.bw = bw

    def validate(self):
        if not (isinstance(self.bw, float) or isinstance(self.bw, int)):
            raise Exception("'bw' input must be a number.'")


class CHOSourceValidator:
    """
    Class for validating the 'cho_source' input parameter of ReplayBG.
    """

    def __init__(self, cho_source):
        self.cho_source = cho_source

    def validate(self):
        if not (self.cho_source == 'data' or self.cho_source == 'generated'):
            raise Exception("'cho_source' input must be 'data' or 'generated'.")


class CorrectionBolusesHandlerValidator:
    """
    Class for validating the 'correction_boluses_handler' input parameter of ReplayBG.
    """

    def __init__(self, correction_boluses_handler):
        self.correction_boluses_handler = correction_boluses_handler

    def validate(self):
        if not callable(self.correction_boluses_handler):
            raise Exception("'correction_boluses_handler' input must be a function.'")


class CorrectionBolusesHandlerParamsValidator:
    """
    Class for validating the 'hypotreatments_handler_params' input parameter of ReplayBG.
    """

    def __init__(self, correction_boluses_handler_params):
        self.correction_boluses_handler_params = correction_boluses_handler_params

    def validate(self):
        if self.correction_boluses_handler_params is not None:
            if not isinstance(self.correction_boluses_handler_params, dict):
                raise Exception("'correction_boluses_handler_params' input must be a dict.'")


class DataValidator:
    """
    Class for validating the 'data' input parameter of ReplayBG.
    """

    def __init__(self, modality, data, blueprint, exercise,
                 bolus_source, basal_source, cho_source):
        self.modality = modality
        self.data = data
        self.blueprint = blueprint
        self.exercise = exercise

        self.bolus_source = bolus_source
        self.basal_source = basal_source
        self.cho_source = cho_source

    def validate(self):

        if not isinstance(self.data, pd.DataFrame):
            raise Exception("'data' input must be a pandas.DataFrame.'")

        if not 't' in self.data:
            raise Exception("'data' must contain the 't' column.'")

        if self.modality == 'twin':

            if not 'glucose' in self.data:
                raise Exception("'data' must contain the 'glucose' column.'")

            if not 'cho' in self.data:
                raise Exception("'data' must contain the 'cho' column.'")
            if self.data.cho.isnull().values.any():
                raise Exception("'data.cho' must not contain nan values.'")

            if not 'bolus' in self.data:
                raise Exception("'data' must contain the 'bolus' column.'")
            if self.data.bolus.isnull().values.any():
                raise Exception("'data.bolus' must not contain nan values.'")

            if not 'basal' in self.data:
                raise Exception("'data' must contain the 'basal' column.'")
            if self.data.basal.isnull().values.any():
                raise Exception("'data.basal' must not contain nan values.'")

            if self.exercise:

                if not 'exercise' in self.data:
                    raise Exception("'data' must contain the 'exercise' column.'")
                if self.data.exercise.isnull().values.any():
                    raise Exception("'data.exercise' must not contain nan values.'")

            if self.blueprint == 'multi-meal':
                # TODO: implement multi-meal extra checks
                # d = {'t': t, 'glucose': glucose, 'cho': cho, 'choLabel' : choLabel, 'bolus' : bolus, 'bolusLabel' : bolusLabel, 'basal' : basal, 'exercise' : exercise}
                pass

        else:

            if self.cho_source == 'data' and not 'cho' in self.data:
                raise Exception("'data' must contain the 'cho' column.'")
            if self.data.cho.isnull().values.any():
                raise Exception("'data.cho' must not contain nan values.'")

            if self.bolus_source == 'data' and not 'bolus' in self.data:
                raise Exception("'data' must contain the 'bolus' column.'")
            if self.data.bolus.isnull().values.any():
                raise Exception("'data.bolus' must not contain nan values.'")

            if self.basal_source == 'data' and not 'basal' in self.data:
                raise Exception("'data' must contain the 'basal' column.'")
            if self.data.basal.isnull().values.any():
                raise Exception("'data.basal' must not contain nan values.'")


class EnableCorrectionBolusesValidator:
    """
    Class for validating the 'enable_correction_boluses' input parameter of ReplayBG.
    """

    def __init__(self, enable_correction_boluses):
        self.enable_correction_boluses = enable_correction_boluses

    def validate(self):
        if not isinstance(self.enable_correction_boluses, bool):
            raise Exception("'enable_correction_boluses' input must be a boolean.'")


class EnableHypotreatmentsValidator:
    """
    Class for validating the 'enable_hypotreatments' input parameter of ReplayBG.
    """

    def __init__(self, enable_hypotreatments):
        self.enable_hypotreatments = enable_hypotreatments

    def validate(self):
        if not isinstance(self.enable_hypotreatments, bool):
            raise Exception("'enable_hypotreatments' input must be a boolean.'")


class ExerciseValidator:
    """
    Class for validating the 'exercise' input parameter of ReplayBG.
    """

    def __init__(self, exercise):
        self.exercise = exercise

    def validate(self):
        if not isinstance(self.exercise, bool):
            raise Exception("'exercise' input must be a boolean.'")


class ExtendedValidator:
    """
    Class for validating the 'extended' input parameter of ReplayBG.
    """

    def __init__(self, extended):
        self.extended = extended

    def validate(self):
        if not isinstance(self.extended, bool):
            raise Exception("'extended' input must be a boolean.'")


class FindStartGuessFirstValidator:
    """
    Class for validating the 'find_start_guess_first' input parameter of ReplayBG.
    """

    def __init__(self, find_start_guess_first):
        self.find_start_guess_first = find_start_guess_first

    def validate(self):
        if not isinstance(self.find_start_guess_first, bool):
            raise Exception("'find_start_guess_first' input must be a boolean.'")


class HypotreatmentsHandlerValidator:
    """
    Class for validating the 'hypotreatments_handler' input parameter of ReplayBG.
    """

    def __init__(self, hypotreatments_handler):
        self.hypotreatments_handler = hypotreatments_handler

    def validate(self):
        if not callable(self.hypotreatments_handler):
            raise Exception("'hypotreatments_handler' input must be a function.'")


class HypotreatmentsHandlerParamsValidator:
    """
    Class for validating the 'hypotreatments_handler_params' input parameter of ReplayBG.
    """

    def __init__(self, hypotreatments_handler_params):
        self.hypotreatments_handler_params = hypotreatments_handler_params

    def validate(self):
        if self.hypotreatments_handler_params is not None:
            if not isinstance(self.hypotreatments_handler_params, dict):
                raise Exception("'hypotreatments_handler_params' input must be a dict.'")


class TwinningMethodValidator:
    """
    Class for validating the 'twinning_method' input parameter of ReplayBG.
    """

    def __init__(self, twinning_method):
        self.twinning_method = twinning_method

    def validate(self):
        if not (self.twinning_method == 'mcmc' or self.twinning_method == 'map'):
            raise Exception("'twinning_method' input must be 'mcmc' or 'map'.")


class MealGeneratorHandlerValidator:
    """
    Class for validating the 'meal_generator_handler' input parameter of ReplayBG.
    """

    def __init__(self, meal_generator_handler):
        self.meal_generator_handler = meal_generator_handler

    def validate(self):
        if not callable(self.meal_generator_handler):
            raise Exception("'meal_generator_handler' input must be a function.'")


class MealGeneratorHandlerParamsValidator:
    """
    Class for validating the 'meal_generator_handler_params' input parameter of ReplayBG.
    """

    def __init__(self, meal_generator_handler_params):
        self.meal_generator_handler_params = meal_generator_handler_params

    def validate(self):
        if self.meal_generator_handler_params is not None:
            if not isinstance(self.meal_generator_handler_params, dict):
                raise Exception("'meal_generator_handler_params' input must be a dict.'")


class ModalityValidator:
    """
    Class for validating the 'modality' input parameter of ReplayBG.
    """

    def __init__(self, modality):
        self.modality = modality

    def validate(self):
        if not (self.modality == 'twinning' or self.modality == 'replay'):
            raise Exception("'modality' input must be 'twinning' or 'replay'.")


class NProcessesValidator:
    """
    Class for validating the 'n_processes' input parameter of ReplayBG.
    """

    def __init__(self, n_processes):
        self.n_processes = n_processes

    def validate(self):
        if not (isinstance(self.n_processes, int) or self.n_processes is None):
            raise Exception("'n_processes' input must be an integer or None.'")


class NReplayValidator:
    """
    Class for validating the 'n_replay' input parameter of ReplayBG.
    """

    def __init__(self, n_replay):
        self.n_replay = n_replay

    def validate(self):
        if not isinstance(self.n_replay, int):
            raise Exception("'n_replay' input must be an integer.'")
        if not (self.n_replay == 1 or self.n_replay == 10 or self.n_replay == 100 or self.n_replay == 1000):
            raise Exception("'n_replay' input must be 1, 10, 100, or 1000.'")


class NStepsValidator:
    """
    Class for validating the 'n_steps' input parameter of ReplayBG.
    """

    def __init__(self, n_steps):
        self.n_steps = n_steps

    def validate(self):
        if not isinstance(self.n_steps, int):
            raise Exception("'n_steps' input must be an integer.'")


class ParallelizeValidator:
    """
    Class for validating the 'parallelize' input parameter of ReplayBG.
    """

    def __init__(self, parallelize):
        self.parallelize = parallelize

    def validate(self):
        if not isinstance(self.parallelize, bool):
            raise Exception("'parallelize' input must be a boolean.'")


class PathologyValidator:
    """
    Class for validating the 'pathology' input parameter of ReplayBG.
    """

    def __init__(self, pathology):
        self.pathology = pathology

    def validate(self):
        if not (
                self.pathology == 't1d' or self.pathology == 't2d' or self.pathology == 'pbh' or self.pathology == 'healthy'):
            raise Exception("'pathology' input must be 't1d', 't2d', 'pbh', or 'healthy'.")


class PlotModeValidator:
    """
    Class for validating the 'plot_mode' input parameter of ReplayBG.
    """

    def __init__(self, plot_mode):
        self.plot_mode = plot_mode

    def validate(self):
        if not isinstance(self.plot_mode, bool):
            raise Exception("'plot_mode' input must be a boolean.'")


class PreviousDataNameValidator:
    """
    Class for validating the 'previous_data_name' input parameter of ReplayBG.
    """

    def __init__(self, previous_data_name):
        self.previous_data_name = previous_data_name

    def validate(self):
        if self.previous_data_name is not None:
            if not isinstance(self.previous_data_name, str):
                raise Exception("'previous_data_name' input must be a string.'")


class SaveChainsValidator:
    """
    Class for validating the 'save_chains' input parameter of ReplayBG.
    """

    def __init__(self, save_chains):
        self.save_chains = save_chains

    def validate(self):
        if not isinstance(self.save_chains, bool):
            raise Exception("'save_chains' input must be a boolean.'")


class SaveFolderValidator:
    """
    Class for validating the 'save_folder' input parameter of ReplayBG.
    """

    def __init__(self,
                 save_folder: str
                 ):
        self.save_folder = save_folder

    def validate(self):
        if not isinstance(self.save_folder, str):
            raise Exception("'save_folder' input must be a string.'")


class SaveNameValidator:
    """
    Class for validating the 'save_name' input parameter of ReplayBG.
    """

    def __init__(self, save_name):
        self.save_name = save_name

    def validate(self):
        if not isinstance(self.save_name, str):
            raise Exception("'save_name' input must be a string.'")


class SaveSuffixValidator:
    """
    Class for validating the 'save_suffix' input parameter of ReplayBG.
    """

    def __init__(self, save_suffix):
        self.save_suffix = save_suffix

    def validate(self):
        if not isinstance(self.save_suffix, str):
            raise Exception("'save_suffix' input must be a string.'")


class SaveWorkspaceValidator:
    """
    Class for validating the 'save_workspace' input parameter of ReplayBG.
    """

    def __init__(self, save_workspace):
        self.save_workspace = save_workspace

    def validate(self):
        if not isinstance(self.save_workspace, bool):
            raise Exception("'save_workspace' input must be a boolean.'")


class BlueprintValidator:
    """
    Class for validating the 'blueprint' input parameter of ReplayBG.
    """

    def __init__(self, blueprint):
        self.blueprint = blueprint

    def validate(self):
        if not (self.blueprint == 'single-meal' or self.blueprint == 'multi-meal'):
            raise Exception("'blueprint' input must be 'single-meal' or 'multi-meal'.")


class SeedValidator:
    """
    Class for validating the 'seed' input parameter of ReplayBG.
    """

    def __init__(self, seed):
        self.seed = seed

    def validate(self):
        if not isinstance(self.seed, int):
            raise Exception("'seed' input must be an integer.'")


class SensorsValidator:
    """
    Class for validating the 'sensors' input parameter of ReplayBG.
    """

    def __init__(self, sensors):
        self.sensors = sensors

    def validate(self):
        if self.sensors is not None:
            if not isinstance(self.sensors, list):
                raise Exception("'sensors' input must be None or a list.'")


class U2SSValidator:
    """
    Class for validating the 'u2ss' input parameter of ReplayBG.
    """

    def __init__(self, u2ss):
        self.u2ss = u2ss

    def validate(self):
        if self.u2ss is not None:
            if not (isinstance(self.u2ss, float) or isinstance(self.u2ss, int)):
                raise Exception("'bw' input must be a number.'")


class VerboseValidator:
    """
    Class for validating the 'verbose' input parameter of ReplayBG.
    """

    def __init__(self, verbose):
        self.verbose = verbose

    def validate(self):
        if not isinstance(self.verbose, bool):
            raise Exception("'verbose' input must be a boolean.'")


class X0Validator:
    """
    Class for validating the 'x0' input parameter of ReplayBG.
    """

    def __init__(self, x0):
        self.x0 = x0

    def validate(self):
        if self.x0 is not None:
            if not isinstance(self.x0, list):
                raise Exception("'x0' input must be None or a list.'")


class YTSValidator:
    """
    Class for validating the 'yts' input parameter of ReplayBG.
    """

    def __init__(self, yts):
        self.yts = yts

    def validate(self):
        if not isinstance(self.yts, int):
            raise Exception("'yts' input must be an integer.'")


class SnackAbsorptionValidator:
    """
    Validates the 'snack_absorption' parameter.
    """

    def __init__(self, snack_absorption):
        self.snack_absorption = snack_absorption

    def validate(self):
        if self.snack_absorption is not None:
            if not isinstance(self.snack_absorption, float):
                raise Exception("'snack_absorption' input must be a float.'")
            if not (0 <= self.snack_absorption <= 1):
                raise Exception("'snack_absorption' input must be between 0 and 1.'")


class SnackAbsorptionDelayValidator:
    """
    Validates the 'snack_absorption_delay' parameter.
    """

    def __init__(self, snack_absorption_delay):
        self.snack_absorption_delay = snack_absorption_delay

    def validate(self):
        if self.snack_absorption_delay is not None:
            if not isinstance(self.snack_absorption_delay, int):
                raise Exception("'snack_absorption_delay' input must be a integer.'")
            if not (0 <= self.snack_absorption_delay <= 60):
                raise Exception("'snack_absorption_delay' input must be between 0 and 60.'")


class HypotreatmentAbsorptionValidator:
    """
    Validates the 'hypotreatment_absorption' parameter.
    """

    def __init__(self, hypotreatment_absorption):
        self.hypotreatment_absorption = hypotreatment_absorption

    def validate(self):
        if self.hypotreatment_absorption is not None:
            if not isinstance(self.hypotreatment_absorption, float):
                raise Exception("'hypotreatment_absorption' input must be a float.'")
            if not (0 <= self.hypotreatment_absorption <= 1):
                raise Exception("'hypotreatment_absorption' input must be between 0 and 1.'")
