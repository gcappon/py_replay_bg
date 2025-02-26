from typing import Callable, Dict

import numpy as np
import pandas as pd

from py_replay_bg.environment import Environment
from py_replay_bg.model.t1d_model_single_meal import T1DModelSingleMeal
from py_replay_bg.model.t1d_model_multi_meal import T1DModelMultiMeal

from py_replay_bg.dss import DSS
from py_replay_bg.dss.default_dss_handlers import default_meal_generator_handler, standard_bolus_calculator_handler, \
    default_basal_handler, ada_hypotreatments_handler, corrects_above_250_handler

from py_replay_bg.data import ReplayBGData

from py_replay_bg.twinning.mcmc import MCMC
from py_replay_bg.twinning.map import MAP
from py_replay_bg.replay import Replayer
from py_replay_bg.visualizer import Visualizer

from py_replay_bg.input_validation.input_validator_init import InputValidatorInit
from py_replay_bg.input_validation.input_validator_twin import InputValidatorTwin
from py_replay_bg.input_validation.input_validator_replay import InputValidatorReplay

import os

import pickle


class ReplayBG:
    """
    Core class of ReplayBG.

    ...
    Attributes
    ----------
    environment: Environment
        An object that represents the hyperparameters to be used by ReplayBG.

    Methods
    -------
    twin(data, bw, save_name, twinning_method, n_steps, save_chains, u2ss, x0, previous_data_name, parallelize,
        n_processes)
        Runs ReplayBG twinning procedure.
    replay(data, bw, save_name, u2ss, x0, previous_data_name, twinning_method, bolus_source, basal_source,
        cho_source, meal_generator_handler, meal_generator_handler_params,
        bolus_calculator_handler, bolus_calculator_handler_params, basal_handler, basal_handler_params,
        enable_hypotreatments, hypotreatments_handler, hypotreatments_handler_params,
        enable_correction_boluses,  correction_boluses_handler, correction_boluses_handler_params,
        save_suffix, save_workspace, n_replay, sensors)
        Runs ReplayBG according to the chosen modality.
    """

    def __init__(self, save_folder: str, blueprint: str = 'single_meal',
                 yts: int = 5, exercise: bool = False,
                 seed: int = 1,
                 plot_mode: bool = True, verbose: bool = True
                 ):
        """
        Constructs all the necessary attributes for the ReplayBG object.

        Parameters
        ----------
        save_folder : str
            A string defining the folder that will contain the results of the twinning procedure and the replay
            simulations.
        blueprint: str, {'single-meal', 'multi-meal'}
            A string that specifies the blueprint to be used to create the digital twin.

        yts: int, optional, default : 5
            An integer that specifies the data sample time (in minutes).
        exercise: boolean, optional, default : False
            A boolean that specifies whether to simulate exercise or not.
        seed: int, optional, default: 1
            An integer that specifies the random seed. For reproducibility.

        plot_mode : boolean, optional, default : True
            A boolean that specifies whether to show the plot of the results or not.
        verbose : boolean, optional, default : True
            A boolean that specifies the verbosity of ReplayBG.

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

        References
        --------
        Cappon et al., "ReplayBG: a methodology to identify a personalized model from type 1 diabetes data and simulate
        glucose concentrations to assess alternative therapies", IEEE Transactions on Biomedical Engineering, 2023.
        """

        # Validate input
        InputValidatorInit(
            save_folder=save_folder,
            blueprint=blueprint,
            yts=yts,
            exercise=exercise,
            seed=seed,
            plot_mode=plot_mode,
            verbose=verbose,
        ).validate()

        # Initialize the environment parameters
        self.environment = Environment(blueprint=blueprint, save_folder=save_folder,
                                       yts=yts, exercise=exercise,
                                       seed=seed,
                                       plot_mode=plot_mode, verbose=verbose)

    def twin(self, data: pd.DataFrame, bw: float, save_name: str,
             twinning_method: str = 'mcmc',
             extended: bool = False, find_start_guess_first: bool = False,
             n_steps: int = 50000, save_chains: bool = False,
             u2ss: float | None = None, x0: np.ndarray | None = None, previous_data_name: str | None = None,
             parallelize: bool = False, n_processes: int | None = None,
    ) -> None:
        """
        Runs ReplayBG twinning procedure.

        Parameters
        ----------
        data: pd.DataFrame
            Pandas dataframe which contains the data to be used by the tool.
        bw: float
            The patient's body weight.
        save_name : str
            A string used to label, thus identify, each output file and result.


        u2ss : float, optional, default : None
            The steady state of the basal insulin infusion.
        x0 : list, optional, default : None
            The initial model conditions.
        previous_data_name : str, optional, default : None
            The name of the previous data portion. This is used to correcly "transfer" the initial model conditions to
            the current portion of data.

        twinning_method : str, {'mcmc', 'map'}, optional, default : 'mcmc'
            The method to be used to twin the model.

        extended : bool, optional, default : False
            A flag indicating whether to use the "extended" model for twinning
        find_start_guess_first : bool, optional, default : False
            A flag indicating whether to find the start guess using MAP before twinning.

        n_steps: int, optional, default : 50000
            Number of steps to use for the main chain. This is ignored if twinning_method is 'map'.
        save_chains: bool, optional, default : False
            A flag that specifies whether to save additional results of the mcmc twinning method. This is ignored if
            `twinning_method` is `'map'`.

        parallelize : boolean, optional, default : False
            A boolean that specifies whether to parallelize the twinning process.
        n_processes : int, optional, default : None
            The number of processes to be spawn if `parallelize` is `True`. If None, the number of CPU cores is used.

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
        InputValidatorTwin(
                 data=data,
                 bw=bw,
                 save_name=save_name,
                 twinning_method=twinning_method,
                 n_steps=n_steps,
                 save_chains=save_chains,
                 u2ss=u2ss,
                 x0=x0,
                 previous_data_name=previous_data_name,
                 parallelize=parallelize,
                 n_processes=n_processes,
                 blueprint=self.environment.blueprint,
                 exercise=self.environment.exercise,
                 extended=extended,
                 find_start_guess_first=find_start_guess_first,
                 ).validate()

        if self.environment.verbose:
            print('Creating the digital twin using ' + twinning_method.upper())

        # If we are twinning, override initial conditions of glucose if they are not None. This allows to avoid
        # "jumps" of glucose values during twinning.
        if x0 is not None:
            idx = np.where(data.glucose.isnull().values == False)[0][0]
            x0[0] = data.glucose.values[idx]
            x0[-1] = data.glucose.values[idx]

        # Initialize model
        if self.environment.blueprint == 'single-meal':
            model = T1DModelSingleMeal(data=data, bw=bw, u2ss=u2ss, x0=x0,
                                       previous_data_name=previous_data_name,
                                       twinning_method=twinning_method,
                                       environment=self.environment,
                                       is_twin=True)
        else:
            model = T1DModelMultiMeal(data=data, bw=bw, u2ss=u2ss, x0=x0,
                                      previous_data_name=previous_data_name,
                                      twinning_method=twinning_method,
                                      environment=self.environment,
                                      is_twin=True, extended=extended)

        # Unpack data to optimize performance during simulation
        rbg_data = ReplayBGData(data=data, model=model, environment=self.environment)

        # Initialize start_guess
        start_guess = None

        # Initialize twinner
        if twinning_method == 'mcmc':
            twinner = MCMC(n_steps=n_steps,
                              save_chains=save_chains,
                              callback_ncheck=1000,
                              parallelize=parallelize,
                              n_processes=n_processes,
                              )
        else:
            twinner = MAP(max_iter=100000,
                             parallelize=parallelize,
                             n_processes=n_processes
                             )

        # Find the start guess if requested
        if find_start_guess_first:

            if self.environment.verbose:
                print('Looking for start guess')

            start_guesser = MAP(max_iter=100000,
                          parallelize=parallelize,
                          n_processes=n_processes
                          )

            # Run twinning procedure for finding the start guess.
            start_guess = start_guesser.twin(rbg_data=rbg_data,
                                       model=model,
                                       save_name=save_name,
                                       environment=self.environment,
                                       for_start_guess=True)

            if self.environment.verbose:
                print('Running actual twinning')

        # Run twinning procedure
        twinner.twin(rbg_data=rbg_data,
                     model=model,
                     save_name=save_name,
                     environment=self.environment,
                     start_guess=start_guess)

    def replay(self,
               data: pd.DataFrame,
               bw: float,
               save_name: str,
               x0: np.ndarray | None = None,
               previous_data_name: str | None  = None,
               twinning_method: str = 'mcmc',
               bolus_source: str = 'data',
               basal_source: str = 'data',
               cho_source: str = 'data',
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
               save_suffix: str = '',
               save_workspace: bool = False,
               n_replay: int = 1000,
               sensors: list | None = None
               ) -> Dict:
        """
        Runs ReplayBG according to the chosen modality.

        Parameters
        ----------
        data : pd.DataFrame
                Pandas dataframe which contains the data to be used by the tool.
        bw : float
            The patient's body weight.
        save_name : str
        A string used to label, thus identify, each output file and result.

        x0: list
            The initial model state.
        previous_data_name: str
            The name of the previous portion of data. To be used to initialize the initial conditions.

        twinning_method : str
            The method used to twin the model.

        bolus_source : string, {'data', or 'dss'}
            A string defining whether to use, during replay, the insulin bolus data contained in the 'data' timetable
            (if 'data'), or the boluses generated by the bolus calculator implemented via the provided
            'bolusCalculatorHandler' function.
        basal_source : string, {'data', 'u2ss', or 'dss'}
            A string defining whether to use, during replay, the insulin basal data contained in the 'data' timetable
            (if 'data'), or the basal generated by the controller implemented via the provided
            'basalControllerHandler' function (if 'dss'), or fixed to the average basal rate used during
            twinning (if 'u2ss').
        cho_source : string, {'data', 'generated'}
            A string defining whether to use, during replay, the CHO data contained in the 'data' timetable (if 'data'),
            or the CHO generated by the meal generator implemented via the provided 'mealGeneratorHandler' function.

        meal_generator_handler: Callable, optional, default : default_meal_generator_handler
            A callback function that implements a meal generator to be used during the replay of a given scenario.
        meal_generator_handler_params: dict, optional, default : None
            A dictionary that contains the parameters to pass to the meal_generator_handler function.
        bolus_calculator_handler: Callable, optional, default : standard_bolus_calculator_handler
            A callback function that implements a bolus calculator to be used during the replay of a given scenario.
        bolus_calculator_handler_params: dict, optional, default : None
            A dictionary that contains the parameters to pass to the bolusCalculatorHandler function. It also serves
            as memory area for the bolusCalculatorHandler function.
        basal_handler: Callable, optional, default : default_basal_handler
            A callback function that implements a basal controller to be used during the replay of a given scenario.
        basal_handler_params: dict, optional, default : None
            A dictionary that contains the parameters to pass to the basalHandler function. It also serves as memory
            area for the basalHandler function.
        enable_hypotreatments: boolean
            A flag that specifies whether to enable hypotreatments during the replay of a given scenario.
        hypotreatments_handler: Callable, optional, default : ada_hypotreatments_handler
            A callback function that implements a hypotreatment strategy during the replay of a given scenario.
        hypotreatments_handler_params: dict, optional, default : None
            A dictionary that contains the parameters to pass to the hypoTreatmentsHandler function. It also serves
            as memory area for the hypoTreatmentsHandler function.
        enable_correction_boluses: boolean
            A flag that specifies whether to enable correction boluses during the replay of a given scenario.
        correction_boluses_handler: Callable, optional, default : corrects_above_250_handler
            A callback function that implements a corrective bolus strategy during the replay of a given scenario.
        correction_boluses_handler_params: dict, optional, default : None
            A dictionary that contains the parameters to pass to the correctionBolusesHandler function. It also serves
            as memory area for the correctionBolusesHandler function.

        save_suffix : string
            A string to be attached as suffix to the resulting output files' name.
        save_workspace: bool
            A flag that specifies whether to save the resulting workspace.

        n_replay: int, {1, 10, 100, 1000}, optional, default: 1000
            The number of Monte Carlo replays to be performed. Ignored if twinning_method is 'map'.
        sensors: list[Sensors], optional, default: None
            The sensors to be used in each of the replay simulations.

        Returns
        -------
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
        # Validate inputs
        InputValidatorReplay(
            data=data,
            bw=bw,
            save_name=save_name,
            x0=x0,
            previous_data_name=previous_data_name,
            twinning_method=twinning_method,
            bolus_source=bolus_source,
            basal_source=basal_source,
            cho_source=cho_source,
            meal_generator_handler=meal_generator_handler,
            meal_generator_handler_params=meal_generator_handler_params,
            bolus_calculator_handler=bolus_calculator_handler,
            bolus_calculator_handler_params=bolus_calculator_handler_params,
            basal_handler=basal_handler,
            basal_handler_params=basal_handler_params,
            enable_hypotreatments=enable_hypotreatments,
            hypotreatments_handler=hypotreatments_handler,
            hypotreatments_handler_params=hypotreatments_handler_params,
            enable_correction_boluses=enable_correction_boluses,
            correction_boluses_handler=correction_boluses_handler,
            correction_boluses_handler_params=correction_boluses_handler_params,
            save_suffix=save_suffix,
            save_workspace=save_workspace,
            n_replay=n_replay,
            sensors=sensors,
            exercise=self.environment.exercise,
            blueprint=self.environment.blueprint,
        ).validate()

        if self.environment.verbose:
            print('Running replay simulation')

        # Load model parameters
        if self.environment.verbose:
            print('Loading twinned model parameter realizations...')

        with open(os.path.join(self.environment.replay_bg_path, 'results', twinning_method,
                               twinning_method + '_' + save_name + '.pkl'), 'rb') as file:
            twinning_results = pickle.load(file)
        draws = twinning_results['draws']
        u2ss = twinning_results['u2ss']

        if self.environment.blueprint == 'single-meal':
            model = T1DModelSingleMeal(data=data, bw=bw, u2ss=u2ss, x0=x0,
                                       previous_data_name=previous_data_name,
                                       twinning_method=twinning_method,
                                       environment=self.environment,
                                       is_twin=False)
        else:
            model = T1DModelMultiMeal(data=data, bw=bw, u2ss=u2ss, x0=x0,
                                      previous_data_name=previous_data_name,
                                      twinning_method=twinning_method,
                                      environment=self.environment,
                                      is_twin=False)

        # Initialize DSS
        dss = DSS(bw=bw,
                  meal_generator_handler=meal_generator_handler,
                  meal_generator_handler_params=meal_generator_handler_params,
                  bolus_calculator_handler=bolus_calculator_handler,
                  bolus_calculator_handler_params=bolus_calculator_handler_params,
                  basal_handler=basal_handler, basal_handler_params=basal_handler_params,
                  enable_hypotreatments=enable_hypotreatments, hypotreatments_handler=hypotreatments_handler,
                  hypotreatments_handler_params=hypotreatments_handler_params,
                  enable_correction_boluses=enable_correction_boluses,
                  correction_boluses_handler=correction_boluses_handler,
                  correction_boluses_handler_params=correction_boluses_handler_params)

        # Unpack data to optimize performance
        rbg_data = ReplayBGData(data=data, model=model,
                                environment=self.environment,
                                bolus_source=bolus_source, basal_source=basal_source, cho_source=cho_source)

        # Run replay
        if self.environment.verbose:
            print('Replaying scenario...')
        replayer = Replayer(
            rbg_data=rbg_data,
            draws=draws,
            u2ss=u2ss,
            n_replay=n_replay,
            sensors=sensors,
            environment=self.environment,
            model=model,
            dss=dss,
            twinning_method=twinning_method)
        replay_results = replayer.replay_scenario()

        # Plot results if plot_mode is enabled
        if self.environment.plot_mode:
            if self.environment.verbose:
                print('Plotting results...')
            Visualizer().plot_replay_results(replay_results=replay_results)

        # Save results
        if save_workspace:
            if self.environment.verbose:
                print('Saving results in ' + os.path.join(self.environment.replay_bg_path, 'results', 'workspaces',
                                                          save_name + save_suffix + '.pkl'))

            with open(os.path.join(self.environment.replay_bg_path, 'results', 'workspaces',
                                   save_name + save_suffix + '.pkl'),
                      'wb') as file:
                pickle.dump(replay_results, file)

        return replay_results
