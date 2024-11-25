import pandas as pd
import numpy as np

from py_replay_bg.input_validation import *


class InputValidatorTwin:
    """
    Class for validating the input of ReplayBG twin method.

    ...
    Attributes
    ----------
    data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
    bw: float
        The patient's body weight.
    save_name : str
        A string used to label, thus identify, each output file and result.


    u2ss : float
        The steady state of the basal insulin infusion.
    x0 : np.ndarray
        The initial model conditions.
    previous_data_name : str
        The name of the previous data portion. This is used to correctly "transfer" the initial model conditions to
        the current portion of data.

    twinning_method : str
        The method to be used to twin the model.

    n_steps: int
        Number of steps to use for the main chain. This is ignored if modality is 'replay'.
    save_chains: bool, optional, default : False
        A flag that specifies whether to save the resulting mcmc chains and copula samplers.

    parallelize : boolean
        A boolean that specifies whether to parallelize the twinning process.
    n_processes : int, optional, default : None
        The number of processes to be spawn if `parallelize` is `True`. If None, the number of CPU cores is used.

    blueprint: str
            A string that specifies the blueprint to be used to create the digital twin.
    exercise: bool
        A boolean that specifies whether to use exercise model or not.

    Methods
    -------
    validate():
        Run the input validation process.
    """

    def __init__(self,
                 data: pd.DataFrame,
                 bw: float,
                 save_name: str,
                 twinning_method: str,
                 n_steps: int,
                 save_chains: bool,
                 u2ss: float | None,
                 x0: np.ndarray | None,
                 previous_data_name: str | None,
                 parallelize: bool,
                 n_processes: int | None,
                 blueprint: str,
                 exercise: bool
                 ):
        self.data = data
        self.bw = bw
        self.save_name = save_name
        self.twinning_method = twinning_method
        self.n_steps = n_steps
        self.save_chains = save_chains
        self.u2ss = u2ss
        self.x0 = x0
        self.previous_data_name = previous_data_name
        self.parallelize = parallelize
        self.n_processes = n_processes
        self.blueprint = blueprint
        self.exercise = exercise

    def validate(self):
        """
        Run the input validation process.
        """

        # Validate the 'data' input
        DataValidator(modality='twin', data=self.data, blueprint=self.blueprint, exercise=self.exercise,
                      bolus_source='data', basal_source='data', cho_source='data').validate()

        # Validate the 'bw' input
        BWValidator(bw=self.bw).validate()

        # Validate the 'save_name' input
        SaveNameValidator(save_name=self.save_name).validate()

        # Validate the 'twinning_method' input
        TwinningMethodValidator(twinning_method=self.twinning_method).validate()

        # Validate the 'n_steps' input
        NStepsValidator(n_steps=self.n_steps).validate()

        # Validate the 'u2ss' input
        U2SSValidator(u2ss=self.u2ss).validate()

        # Validate the 'save_name' input
        X0Validator(x0=self.x0).validate()

        # Validate the 'previous_data_name' input
        PreviousDataNameValidator(previous_data_name=self.previous_data_name).validate()

        # Validate the 'parallelize' input
        ParallelizeValidator(parallelize=self.parallelize).validate()

        # Validate the 'n_processes' input
        NProcessesValidator(n_processes=self.n_processes).validate()
