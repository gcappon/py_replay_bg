from py_replay_bg.input_validation import *


class InputValidatorInit:
    """
    Class for validating the input of ReplayBG __init__ method.

    ...
    Attributes
    ----------
    blueprint: str, {'single-meal', 'multi-meal'}
            A string that specifies the blueprint to be used to create the digital twin.
    save_folder : str
        A string defining the folder that will contain the results.

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

    Methods
    -------
    validate():
        Run the input validation process.
    """

    def __init__(self,
                 save_folder: str,
                 blueprint: str,
                 yts: int,
                 exercise: bool,
                 seed: int,
                 plot_mode: bool,
                 verbose: bool,
                 ):
        self.save_folder = save_folder
        self.blueprint = blueprint
        self.yts = yts
        self.exercise = exercise
        self.seed = seed
        self.plot_mode = plot_mode
        self.verbose = verbose

    def validate(self):
        """
        Run the input validation process.
        """

        # Validate the 'save_folder' input
        SaveFolderValidator(save_folder=self.save_folder).validate()

        # Validate the 'blueprint' input
        BlueprintValidator(blueprint=self.blueprint).validate()

        # Validate the 'yts' input
        YTSValidator(yts=self.yts).validate()

        # Validate the 'exercise' input
        ExerciseValidator(exercise=self.exercise).validate()

        # Validate the 'seed' input
        SeedValidator(seed=self.seed).validate()

        # Validate the 'plot_mode' input
        PlotModeValidator(plot_mode=self.plot_mode).validate()

        # Validate the 'verbose' input
        VerboseValidator(verbose=self.verbose).validate()
