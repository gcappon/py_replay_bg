from typing import Callable, Dict

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
    meal_generator_handler: Callable
        A callback function that implements a meal generator to be used during the replay of a given scenario.
    meal_generator_handler_params: dict
        A mutable dictionary that contains the parameters to pass to the meal_generator_handler function.
    bolus_calculator_handler: Callable
        A callback function that implements a bolus calculator to be used during the replay of a given scenario.
    bolus_calculator_handler_params: dict
        A mutable dictionary that contains the parameters to pass to the bolusCalculatorHandler function. It also
        serves as memory area for the bolusCalculatorHandler function.
    basal_handler: Callable
        A callback function that implements a basal controller to be used during the replay of a given scenario.
    basal_handler_params: dict
        A mutable dictionary that contains the parameters to pass to the basalHandler function. It also serves as
        memory area for the basalHandler function.
    enable_hypotreatments: boolean
        A flag that specifies whether to enable hypotreatments during the replay of a given scenario.
    hypotreatments_handler: Callable
        A callback function that implements a hypotreatment strategy during the replay of a given scenario.
    hypotreatments_handler_params: dict
        A mutable dictionary that contains the parameters to pass to the hypoTreatmentsHandler function. It also
        serves as memory area for the hypoTreatmentsHandler function.
    enable_correction_boluses: boolean
        A flag that specifies whether to enable correction boluses during the replay of a given scenario.
    correction_boluses_handler: Callable
        A callback function that implements a corrective bolusing strategy during the replay of a given scenario.
    correction_boluses_handler_params: dict
        A mutable dictionary that contains the parameters to pass to the correctionBolusesHandler function. It also
        serves as memory area for the correctionBolusesHandler function.

    Methods
    -------
    None
    """

    def __init__(self,
                 bw: float,
                 meal_generator_handler: Callable = default_meal_generator_handler,
                 meal_generator_handler_params: Dict | None = None,
                 bolus_calculator_handler: Callable = standard_bolus_calculator_handler,
                 bolus_calculator_handler_params: Dict | None = None,
                 basal_handler: Callable = default_basal_handler,
                 basal_handler_params: Dict | None = None,
                 enable_hypotreatments: bool = False,
                 hypotreatments_handler: Callable = ada_hypotreatments_handler,
                 hypotreatments_handler_params: Dict | None = None,
                 enable_correction_boluses: bool = False,
                 correction_boluses_handler: Callable = corrects_above_250_handler,
                 correction_boluses_handler_params: Dict | None = None,
                 ):
        """
        Constructs all the necessary attributes for the DSS object.

        Parameters
        ----------
        bw: double
            The patient's body weight.
        meal_generator_handler: Callable, optional, default : default_meal_generator_handler
            A callback function that implements a meal generator to be used during the replay of a given scenario.
        meal_generator_handler_params: dict, optional, default : None
            A mutable dictionary that contains the parameters to pass to the meal_generator_handler function.
        bolus_calculator_handler: Callable, optional, default : standard_bolus_calculator_handler
            A callback function that implements a bolus calculator to be used during the replay of a given scenario.
        bolus_calculator_handler_params: dict, optional, default : None
            A mutable dictionary that contains the parameters to pass to the bolusCalculatorHandler function. It also
            serves as memory area for the bolusCalculatorHandler function.
        basal_handler: function, Callable, default : default_basal_handler
            A callback function that implements a basal controller to be used during the replay of a given scenario.
        basal_handler_params: dict, optional, default : None
            A mutable dictionary that contains the parameters to pass to the basalHandler function. It also serves as
            memory area for the basalHandler function.
        enable_hypotreatments: boolean, optional, default : False
            A flag that specifies whether to enable hypotreatments during the replay of a given scenario.
        hypotreatments_handler: Callable, optional, default : ada_hypotreatments_handler
            A callback function that implements a hypotreatment strategy during the replay of a given scenario.
        hypotreatments_handler_params: dict, optional, default : None
            A mutable dictionary that contains the parameters to pass to the hypoTreatmentsHandler function. It also
            serves as memory area for the hypoTreatmentsHandler function.
        enable_correction_boluses: boolean, optional, default : False
            A flag that specifies whether to enable correction boluses during the replay of a given scenario.
        correction_boluses_handler: Callable, optional, default : corrects_above_250_handler
            A callback function that implements a corrective bolusing strategy during the replay of a given scenario.
        correction_boluses_handler_params: dict, optional, default : None
            A mutable dictionary that contains the parameters to pass to the correctionBolusesHandler function.
            It also serves as memory area for the correctionBolusesHandler function.
        """

        # Patient's body weight
        self.bw = bw

        # Meal Generator module parameters
        self.meal_generator_handler = meal_generator_handler
        self.meal_generator_handler_params = meal_generator_handler_params if meal_generator_handler_params is not None else {}

        # Bolus Calculator module parameters
        self.bolus_calculator_handler = bolus_calculator_handler
        self.bolus_calculator_handler_params = bolus_calculator_handler_params if bolus_calculator_handler_params is not None else {}

        # Basal module parameters
        self.basal_handler = basal_handler
        self.basal_handler_params = basal_handler_params if basal_handler_params is not None else {}

        # Hypotreatment module parameters
        self.enable_hypotreatments = enable_hypotreatments
        self.hypotreatments_handler = hypotreatments_handler
        self.hypotreatments_handler_params = hypotreatments_handler_params if hypotreatments_handler_params is not None else {}

        # Correction bolus module parameters
        self.enable_correction_boluses = enable_correction_boluses
        self.correction_boluses_handler = correction_boluses_handler
        self.correction_boluses_handler_params = correction_boluses_handler_params if correction_boluses_handler_params is not None else {}
