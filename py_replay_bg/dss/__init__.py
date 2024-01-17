from py_replay_bg.dss.default_dss_handlers import default_meal_generator_handler, standard_bolus_calculator_handler, \
    default_basal_handler, ada_hypotreatments_handler, corrects_above_250_handler


class DSS:
    """
    A class that represents the hyperparameters of the integrated decision support system.

    ...
    Attributes
    ----------
    bw: double
        The patient's body weight.
    CR: double
        The carbohydrate-to-insulin ratio of the patient in g/U to be used by the integrated decision support system.
    CF: double
        The correction factor of the patient in mg/dl/U to be used by the integrated decision support system.
    GT: double
        The target glucose value in mg/dl to be used by the decsion support system modules.
    meal_generator_handler: function
        A callback function that implements a meal generator to be used during the replay of a given scenario.
    meal_generator_handler_params: dict
        A dictionary that contains the parameters to pass to the meal_generator_handler function.
    bolus_calculator_handler: function
        A callback function that implements a bolus calculator to be used during the replay of a given scenario.
    bolus_calculator_handler_params: dict
        A dictionary that contains the parameters to pass to the bolusCalculatorHandler function. It also serves as memory
        area for the bolusCalculatorHandler function.
    basal_handler: function
        A callback function that implements a basal controller to be used during the replay of a given scenario.
    basal_handler_params: dict
        A dictionary that contains the parameters to pass to the basalHandler function. It also serves as memory area for the basalHandler function.
    enable_hypotreatments: boolean
        A flag that specifies whether to enable hypotreatments during the replay of a given scenario.
    hypotreatments_handler: function
        A callback function that implements an hypotreatment strategy during the replay of a given scenario.
    hypotreatments_handler_params: dict
        A dictionary that contains the parameters to pass to the hypoTreatmentsHandler function. It also serves as memory
        area for the hypoTreatmentsHandler function.
    enable_correction_boluses: boolean
        A flag that specifies whether to enable correction boluses during the replay of a given scenario.
    correction_boluses_handler: function
        A callback function that implements a corrective bolusing strategy during the replay of a given scenario.
    correction_boluses_handler_params: dict
        A dictionary that contains the parameters to pass to the correctionBolusesHandler function. It also serves as memory
        area for the correctionBolusesHandler function.

    Methods
    -------
    None
    """

    def __init__(self, bw, CR=10, CF=40, GT=120,
                 meal_generator_handler=default_meal_generator_handler, meal_generator_handler_params={},
                 bolus_calculator_handler=standard_bolus_calculator_handler, bolus_calculator_handler_params={},
                 basal_handler=default_basal_handler, basal_handler_params={},
                 enable_hypotreatments=False, hypotreatments_handler=ada_hypotreatments_handler,
                 hypotreatments_handler_params={},
                 enable_correction_boluses=False, correction_boluses_handler=corrects_above_250_handler,
                 correction_boluses_handler_params={}):
        """
        Constructs all the necessary attributes for the DSS object.

        Parameters
        ----------
        bw: double
            The patient's body weight.
        CR: double, optional, default : 10
            The carbohydrate-to-insulin ratio of the patient in g/U to be used by the integrated decision support system.
        CF: double, optional, default : 40
            The correction factor of the patient in mg/dl/U to be used by the integrated decision support system.
        GT: double, optional, default : 120
            The target glucose value in mg/dl to be used by the decision support system modules.
        meal_generator_handler: function, optional, default : default_meal_generator_handler
            A callback function that implements a meal generator to be used during the replay of a given scenario.
        meal_generator_handler_params: dict, optional, default : {}
            A dictionary that contains the parameters to pass to the meal_generator_handler function.
        bolus_calculator_handler: function, optional, default : standard_bolus_calculator_handler
            A callback function that implements a bolus calculator to be used during the replay of a given scenario.
        bolus_calculator_handler_params: dict, optional, default : {}
            A dictionary that contains the parameters to pass to the bolusCalculatorHandler function. It also serves as memory
            area for the bolusCalculatorHandler function.
        basal_handler: function, optional, default : default_basal_handler
            A callback function that implements a basal controller to be used during the replay of a given scenario.
        basal_handler_params: dict, optional, default : {}
            A dictionary that contains the parameters to pass to the basalHandler function. It also serves as memory area for the basalHandler function.
        enable_hypotreatments: boolean, optional, default : False
            A flag that specifies whether to enable hypotreatments during the replay of a given scenario.
        hypotreatments_handler: function, optional, default : ada_hypotreatments_handler
            A callback function that implements an hypotreatment strategy during the replay of a given scenario.
        hypotreatments_handler_params: dict, optional, default : {}
            A dictionary that contains the parameters to pass to the hypoTreatmentsHandler function. It also serves as memory
            area for the hypoTreatmentsHandler function.
        enable_correction_boluses: boolean, optional, default : False
            A flag that specifies whether to enable correction boluses during the replay of a given scenario.
        correction_boluses_handler: function, optional, default : corrects_above_250_handler
            A callback function that implements a corrective bolusing strategy during the replay of a given scenario.
        correction_boluses_handler_params: dict, optional, default : {}
            A dictionary that contains the parameters to pass to the correctionBolusesHandler function. It also serves as memory
            area for the correctionBolusesHandler function.
        """

        # Patient's body weight
        self.bw = bw

        # Patient therapy parameters
        self.GT = GT
        self.CR = CR
        self.CF = CF

        # Meal Generator module parameters
        self.meal_generator_handler = meal_generator_handler
        self.meal_generator_handler_params = meal_generator_handler_params

        # Bolus Calculator module parameters
        self.bolus_calculator_handler = bolus_calculator_handler
        self.bolus_calculator_handler_params = bolus_calculator_handler_params

        # Basal module parameters
        self.basal_handler = basal_handler
        self.basal_handler_params = basal_handler_params

        # Hypotreatment module parameters
        self.enable_hypotreatments = enable_hypotreatments
        self.hypotreatments_handler = hypotreatments_handler
        self.hypotreatments_handler_params = hypotreatments_handler_params

        # Correction bolus module parameters
        self.enable_correction_boluses = enable_correction_boluses
        self.correction_boluses_handler = correction_boluses_handler
        self.correction_boluses_handler_params = correction_boluses_handler_params
