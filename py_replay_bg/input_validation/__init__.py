import pandas as pd


class ModalityValidator:
    """
    Class for validating the 'modality' input parameter of ReplayBG.
    """

    def __init__(self, modality):
        self.modality = modality

    def validate(self):
        if not (self.modality == 'identification' or self.modality == 'replay'):
            raise Exception("'modality' input must be 'identification' or 'replay'.")


class BWValidator:
    """
    Class for validating the 'bw' input parameter of ReplayBG.
    """

    def __init__(self, bw):
        self.bw = bw

    def validate(self):
        if not (isinstance(self.bw, float) or isinstance(self.bw, int)):
            raise Exception("'bw' input must be a number.'")


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


class ScenarioValidator:
    """
    Class for validating the 'scenario' input parameter of ReplayBG.
    """

    def __init__(self, scenario):
        self.scenario = scenario

    def validate(self):
        if not (self.scenario == 'single-meal' or self.scenario == 'multi-meal'):
            raise Exception("'scenario' input must be 'single-meal' or 'multi-meal'.")


class ExerciseValidator:
    """
    Class for validating the 'exercise' input parameter of ReplayBG.
    """

    def __init__(self, exercise):
        self.exercise = exercise

    def validate(self):
        if not isinstance(self.exercise, bool):
            raise Exception("'exercise' input must be a boolean.'")


class SaveNameValidator:
    """
    Class for validating the 'save_name' input parameter of ReplayBG.
    """

    def __init__(self, save_name):
        self.save_name = save_name

    def validate(self):
        if not isinstance(self.save_name, str):
            raise Exception("'save_name' input must be a string.'")


class DataValidator:
    """
    Class for validating the 'data' input parameter of ReplayBG.
    """

    def __init__(self, modality, data, scenario, exercise,
                 bolus_source, basal_source, cho_source):
        self.modality = modality
        self.data = data
        self.scenario = scenario
        self.exercise = exercise

        self.bolus_source = bolus_source
        self.basal_source = basal_source
        self.cho_source = cho_source

    def validate(self):

        if not isinstance(self.data, pd.DataFrame):
            raise Exception("'data' input must be a pandas.DataFrame.'")

        if not 't' in self.data:
            raise Exception("'data' must contain the 't' column.'")

        if self.modality == 'identification':

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

            if self.scenario == 'multi-meal':
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


class SaveSuffixValidator:
    """
    Class for validating the 'save_suffix' input parameter of ReplayBG.
    """

    def __init__(self, save_suffix):
        self.save_suffix = save_suffix

    def validate(self):
        if not isinstance(self.save_suffix, str):
            raise Exception("'save_suffix' input must be a string.'")


class YTSValidator:
    """
    Class for validating the 'yts' input parameter of ReplayBG.
    """

    def __init__(self, yts):
        self.yts = yts

    def validate(self):
        if not isinstance(self.yts, int):
            raise Exception("'yts' input must be an integer.'")


class GlucoseModelValidator:
    """
    Class for validating the 'glucose_model' input parameter of ReplayBG.
    """

    def __init__(self, glucose_model):
        self.glucose_model = glucose_model

    def validate(self):
        if not (self.glucose_model == 'BG' or self.glucose_model == 'IG'):
            raise Exception("'glucose_model' input must be 'BG' or 'IG'.")


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


class SeedValidator:
    """
    Class for validating the 'seed' input parameter of ReplayBG.
    """

    def __init__(self, seed):
        self.seed = seed

    def validate(self):
        if not isinstance(self.seed, int):
            raise Exception("'seed' input must be an integer.'")


class BolusSourceValidator:
    """
    Class for validating the 'bolus_source' input parameter of ReplayBG.
    """

    def __init__(self, bolus_source):
        self.bolus_source = bolus_source

    def validate(self):
        if not (self.bolus_source == 'data' or self.bolus_source == 'dss'):
            raise Exception("'bolus_source' input must be 'data' or 'dss'.")


class BasalSourceValidator:
    """
    Class for validating the 'basal_source' input parameter of ReplayBG.
    """

    def __init__(self, basal_source):
        self.basal_source = basal_source

    def validate(self):
        if not (self.basal_source == 'data' or self.basal_source == 'u2ss' or self.basal_source == 'dss'):
            raise Exception("'basal_source' input must be 'data', 'u2ss', or 'dss'.")


class CHOSourceValidator:
    """
    Class for validating the 'cho_source' input parameter of ReplayBG.
    """

    def __init__(self, cho_source):
        self.cho_source = cho_source

    def validate(self):
        if not (self.cho_source == 'data' or self.cho_source == 'generated'):
            raise Exception("'cho_source' input must be 'data' or 'generated'.")


class CGMModelValidator:
    """
    Class for validating the 'cgm_model' input parameter of ReplayBG.
    """

    def __init__(self, cgm_model):
        self.cgm_model = cgm_model

    def validate(self):
        if not (self.cgm_model == 'CGM' or self.cgm_model == 'IG'):
            raise Exception("'cgm_model' input must be 'CGM' or 'IG'.")


class X0Validator:
    """
    Class for validating the 'X0' input parameter of ReplayBG.
    """

    def __init__(self, X0):
        self.X0 = X0

    def validate(self):
        if self.X0 is not None:
            if not isinstance(self.X0, list):
                raise Exception("'X0' input must be None or a list.'")


class NStepsValidator:
    """
    Class for validating the 'n_steps' input parameter of ReplayBG.
    """

    def __init__(self, n_steps):
        self.n_steps = n_steps

    def validate(self):
        if not isinstance(self.n_steps, int):
            raise Exception("'n_steps' input must be an integer.'")


class SaveChainsValidator:
    """
    Class for validating the 'save_chains' input parameter of ReplayBG.
    """

    def __init__(self, save_chains):
        self.save_chains = save_chains

    def validate(self):
        if not isinstance(self.save_chains, bool):
            raise Exception("'save_chains' input must be a boolean.'")


class AnalyzeResultsValidator:
    """
    Class for validating the 'analyze_results' input parameter of ReplayBG.
    """

    def __init__(self, analyze_results):
        self.analyze_results = analyze_results

    def validate(self):
        if not isinstance(self.analyze_results, bool):
            raise Exception("'analyze_results' input must be a boolean.'")


class CRValidator:
    """
    Class for validating the 'CR' input parameter of ReplayBG.
    """

    def __init__(self, CR):
        self.CR = CR

    def validate(self):
        if not (isinstance(self.CR, float) or isinstance(self.CR, int)):
            raise Exception("'CR' input must be a number.'")


class CFValidator:
    """
    Class for validating the 'CF' input parameter of ReplayBG.
    """

    def __init__(self, CF):
        self.CF = CF

    def validate(self):
        if not (isinstance(self.CF, float) or isinstance(self.CF, int)):
            raise Exception("'CF' input must be a number.'")


class GTValidator:
    """
    Class for validating the 'GT' input parameter of ReplayBG.
    """

    def __init__(self, GT):
        self.GT = GT

    def validate(self):
        if not (isinstance(self.GT, float) or isinstance(self.GT, int)):
            raise Exception("'GT' input must be a number.'")


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
        if not isinstance(self.meal_generator_handler_params, dict):
            raise Exception("'meal_generator_handler_params' input must be a dict.'")


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
        if not isinstance(self.bolus_calculator_handler_params, dict):
            raise Exception("'bolus_calculator_handler_params' input must be a dict.'")


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
        if not isinstance(self.basal_handler_params, dict):
            raise Exception("'basal_handler_params' input must be a dict.'")


class EnableHypotreatmentsValidator:
    """
    Class for validating the 'enable_hypotreatments' input parameter of ReplayBG.
    """

    def __init__(self, enable_hypotreatments):
        self.enable_hypotreatments = enable_hypotreatments

    def validate(self):
        if not isinstance(self.enable_hypotreatments, bool):
            raise Exception("'enable_hypotreatments' input must be a boolean.'")


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
        if not isinstance(self.hypotreatments_handler_params, dict):
            raise Exception("'hypotreatments_handler_params' input must be a dict.'")


class EnableCorrectionBolusesValidator:
    """
    Class for validating the 'enable_correction_boluses' input parameter of ReplayBG.
    """

    def __init__(self, enable_correction_boluses):
        self.enable_correction_boluses = enable_correction_boluses

    def validate(self):
        if not isinstance(self.enable_correction_boluses, bool):
            raise Exception("'enable_correction_boluses' input must be a boolean.'")


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
        if not isinstance(self.correction_boluses_handler_params, dict):
            raise Exception("'correction_boluses_handler_params' input must be a dict.'")


class ParallelizeValidator:
    """
    Class for validating the 'parallelize' input parameter of ReplayBG.
    """

    def __init__(self, parallelize):
        self.parallelize = parallelize

    def validate(self):
        if not isinstance(self.parallelize, bool):
            raise Exception("'parallelize' input must be a boolean.'")


class PlotModeValidator:
    """
    Class for validating the 'plot_mode' input parameter of ReplayBG.
    """

    def __init__(self, plot_mode):
        self.plot_mode = plot_mode

    def validate(self):
        if not isinstance(self.plot_mode, bool):
            raise Exception("'plot_mode' input must be a boolean.'")


class VerboseValidator:
    """
    Class for validating the 'verbose' input parameter of ReplayBG.
    """

    def __init__(self, verbose):
        self.verbose = verbose

    def validate(self):
        if not isinstance(self.verbose, bool):
            raise Exception("'verbose' input must be a boolean.'")


class InputValidator:
    """
    Class for validating the input of ReplayBG

    ...
    Attributes
    ----------
    (same as ReplayBG)

    Methods
    -------
    validate():
        Run the input validation process.
    """

    def __init__(self, modality, data, bw, u2ss, scenario, save_name, save_suffix,
                 yts, glucose_model, pathology, exercise, seed,
                 bolus_source, basal_source, cho_source,
                 cgm_model,
                 X0,
                 n_steps, save_chains, analyze_results,
                 CR, CF, GT,
                 meal_generator_handler, meal_generator_handler_params,
                 bolus_calculator_handler, bolus_calculator_handler_params,
                 basal_handler, basal_handler_params,
                 enable_hypotreatments, hypotreatments_handler, hypotreatments_handler_params,
                 enable_correction_boluses, correction_boluses_handler, correction_boluses_handler_params,
                 parallelize, plot_mode, verbose):
        self.modality = modality
        self.data = data
        self.bw = bw
        self.u2ss = u2ss
        self.scenario = scenario
        self.save_name = save_name
        self.save_suffix = save_suffix

        self.yts = yts
        self.glucose_model = glucose_model
        self.pathology = pathology
        self.exercise = exercise
        self.seed = seed

        self.bolus_source = bolus_source
        self.basal_source = basal_source
        self.cho_source = cho_source

        self.cgm_model = cgm_model

        self.X0 = X0

        self.n_steps = n_steps
        self.save_chains = save_chains
        self.analyze_results = analyze_results

        self.CR = CR
        self.CF = CF
        self.GT = GT

        self.meal_generator_handler = meal_generator_handler
        self.meal_generator_handler_params = meal_generator_handler_params
        self.bolus_calculator_handler = bolus_calculator_handler
        self.bolus_calculator_handler_params = bolus_calculator_handler_params
        self.basal_handler = basal_handler
        self.basal_handler_params = basal_handler_params

        self.enable_hypotreatments = enable_hypotreatments
        self.hypotreatments_handler = hypotreatments_handler
        self.hypotreatments_handler_params = hypotreatments_handler_params
        self.enable_correction_boluses = enable_correction_boluses
        self.correction_boluses_handler = correction_boluses_handler
        self.correction_boluses_handler_params = correction_boluses_handler_params

        self.parallelize = parallelize
        self.plot_mode = plot_mode
        self.verbose = verbose

    def validate(self):
        # Validate the 'modality' input
        ModalityValidator(modality=self.modality).validate()

        # Validate the 'bw' input
        BWValidator(bw=self.bw).validate()

        # Validate the 'u2ss' input
        U2SSValidator(u2ss=self.u2ss).validate()

        # Validate the 'scenario' input
        ScenarioValidator(scenario=self.scenario).validate()

        # Validate the 'save_name' input
        SaveNameValidator(save_name=self.save_name).validate()

        # Validate the 'exercise' input
        ExerciseValidator(exercise=self.exercise).validate()

        # Validate the 'save_suffix' input
        SaveSuffixValidator(save_suffix=self.save_suffix).validate()

        # Validate the 'bolus_source' input
        BolusSourceValidator(bolus_source=self.bolus_source).validate()

        # Validate the 'basal_source' input
        BasalSourceValidator(basal_source=self.basal_source).validate()

        # Validate the 'bolus_source' input
        CHOSourceValidator(cho_source=self.cho_source).validate()

        # Validate the 'data' input
        DataValidator(modality=self.modality, data=self.data, scenario=self.scenario, exercise=self.exercise,
                      bolus_source=self.bolus_source, basal_source=self.basal_source,
                      cho_source=self.cho_source).validate()

        # Validate the 'yts' input
        YTSValidator(yts=self.yts).validate()

        # Validate the 'glucose_model' input
        GlucoseModelValidator(glucose_model=self.glucose_model).validate()

        # Validate the 'pathology' input
        PathologyValidator(pathology=self.pathology).validate()

        # Validate the 'seed' input
        SeedValidator(seed=self.seed).validate()

        # Validate the 'cgm_model' input
        CGMModelValidator(cgm_model=self.cgm_model).validate()

        # Validate the 'X0' input
        X0Validator(X0=self.X0).validate()

        # Validate the 'n_steps' input
        NStepsValidator(n_steps=self.n_steps).validate()

        # Validate the 'save_chains' input
        SaveChainsValidator(save_chains=self.save_chains).validate()

        # Validate the 'analyze_results' input
        AnalyzeResultsValidator(analyze_results=self.analyze_results).validate()

        # Validate the 'CR' input
        CRValidator(CR=self.CR).validate()

        # Validate the 'CF' input
        CFValidator(CF=self.CF).validate()

        # Validate the 'GT' input
        GTValidator(GT=self.GT).validate()

        # Validate the 'meal_generator_handler' input
        MealGeneratorHandlerValidator(meal_generator_handler=self.meal_generator_handler).validate()

        # Validate the 'meal_generator_handler_params' input
        MealGeneratorHandlerParamsValidator(meal_generator_handler_params=self.meal_generator_handler_params).validate()

        # Validate the 'bolus_calculator_handler' input
        BolusCalculatorHandlerValidator(bolus_calculator_handler=self.bolus_calculator_handler).validate()

        # Validate the 'bolus_calculator_handler_params' input
        BolusCalculatorHandlerParamsValidator(
            bolus_calculator_handler_params=self.bolus_calculator_handler_params).validate()

        # Validate the 'basal_handler' input
        BasalHandlerValidator(basal_handler=self.basal_handler).validate()

        # Validate the 'basal_handler_params' input
        BasalHandlerParamsValidator(basal_handler_params=self.basal_handler_params).validate()

        # Validate the 'enable_hypotreatments' input
        EnableHypotreatmentsValidator(enable_hypotreatments=self.enable_hypotreatments).validate()

        # Validate the 'hypotreatments_handler' input
        HypotreatmentsHandlerValidator(hypotreatments_handler=self.hypotreatments_handler).validate()

        # Validate the 'hypotreatments_handler_params' input
        HypotreatmentsHandlerParamsValidator(
            hypotreatments_handler_params=self.hypotreatments_handler_params).validate()

        # Validate the 'enable_correction_boluses' input
        EnableCorrectionBolusesValidator(enable_correction_boluses=self.enable_correction_boluses).validate()

        # Validate the 'correction_boluses_handler' input
        CorrectionBolusesHandlerValidator(correction_boluses_handler=self.correction_boluses_handler).validate()

        # Validate the 'hypotreatments_handler_params' input
        CorrectionBolusesHandlerParamsValidator(
            correction_boluses_handler_params=self.correction_boluses_handler_params).validate()

        # Validate the 'parallelize' input
        ParallelizeValidator(parallelize=self.parallelize).validate()

        # Validate the 'plot_mode' input
        PlotModeValidator(plot_mode=self.plot_mode).validate()

        # Validate the 'verbose' input
        VerboseValidator(verbose=self.verbose).validate()
