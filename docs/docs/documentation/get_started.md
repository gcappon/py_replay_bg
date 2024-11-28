---
sidebar: auto
---
# Get started

## Installation

**ReplayBG** can be installed via pypi by simply 

```python
pip install py-replay-bg
```

### Requirements

* Python >= 3.11
* List of python packages in `requirements.txt`

## Preparation: imports, setup, and data loading 

First of all import the core modules:
```python
import os
import numpy as np
import pandas as pd

from multiprocessing import freeze_support
```

Here, `os` will be used to manage the filesystem, `numpy` and `pandas` to manipulate and manage the data to be used, and
`multiprocessing.freeze_support` to enable multiprocessing functionalities and run the twinning procedure in a faster,
parallelized way. 

Then, we will import the necessary ReplayBG modules:
```python
from py_replay_bg.py_replay_bg import ReplayBG
from py_replay_bg.visualizer import Visualizer
from py_replay_bg.analyzer import Analyzer
```

Here, `ReplayBG` is the core ReplayBG object, while `Analyzer` and `Visualizer` are utility objects that will be used to
respectively analyze and visualize the results that we will produce with ReplayBG.

Next steps consist of setting up some variables that will be used by ReplayBG environment. 
First of all, we will run the twinning procedure in a parallelized way so let's start with:
```python
if __name__ == '__main__':
    freeze_support()
```

Then, we will set the verbosity of ReplayBG:
```python
    verbose = True
```
This means that while we will run ReplayBG, we will see some informative messages to follow what the tool is doing. 
```python
    plot_mode = False
```
This means that while we will run ReplayBG, plots will not be generated automatically. 
 
Then, we need to decide what model to use for twinning the data at hand. 
```python
    blueprint = 'multi-meal'
    save_folder = os.path.join(os.path.abspath(''),'..','..','..')
    parallelize = True
```

Now, let's load some data to play with. In this example, we will use the data in `example/data/multi-meal_data.csv` 
which contains a day data of a patient with T1D whose body weight is `100` kg:

```python
data = pd.read_csv(os.path.join(os.path.abspath(''),'..', 'data', 'multi-meal_example.csv'))
data.t = pd.to_datetime(data['t'])
```

Be careful, data in PyReplayBG must be provided in a `.csv.` file that must follow some strict requirements. For more info
on data requirements in `PyReplayBG` see the [Data Requirements](./data_requirements) 
section.

## Step 1. Identify the model (AKA fits your data)

The first step of PyReplayBG consists of twinning its model (i.e., the digital twinning procedure). This can be done
with:

```python
modality = 'identification' # set modality as 'identification'
bw = 100 # set the patient body weight
blueprint = 'multi-meal' # set the type of blueprint (can be single-meal or multi-meal)
save_name = 'test_multi_meal' # set a save name
n_steps = 2500 # set the number of steps that will be used for identification (for multi-meal it should be at least 100k)
save_folder = os.path.abspath('') # set the results folder to the current folder

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, blueprint=blueprint, save_name=save_name, save_folder=save_folder, n_steps=n_steps)

# Run it
rbg.run(data=data, bw=bw)
```

The above code, creates and runs an instance of PyReplayBG in `identification` modality, i.e., the necessary mode used 
to run step 1. 

Results of step 1 will be save in a `results` folder whose path is specified by the `save_folder` parameter.
Particularly, the `results` folder contains the following subfolders:
* `draws`: contains the identified parameters.
* `mcmc_chains`: contains the raw chains of the Markov Chain Monte Carlo procedure if `save_chains` is `True` (by 
default it is `False` since it would require a lot of storage)
* `workspaces`: contains the overall simulation results.

At the hand of the procedure a plot will be produced (if `plot_mode` is `True`) showing the overall results. 

::: warning
`save_name` is very important. It will uniquely identify the set of identified parameters for the given data. This means
that if one wants to run step 2 (see below) over those data, the same `save_name` must be used in both steps.
:::

## Step 2. Replay

Once identified, it is possible to start replay the data and test alternative insulin/cho therapies. 

If one wants to simply replay the fitted data just run:

```python
modality = 'replay' # change modality as 'replay'

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, blueprint=blueprint, save_name=save_name, save_folder=save_folder)

# Run it
rbg.run(data=data, bw=bw)
```

Another example could be test "waht happens if I reduce the bolus insulin by 30%?". To know the answer run:
```python
modality = 'replay' # change modality as 'replay'

# Replay with less insulin
data.bolus = data.bolus * .7 # Reduce insulin boluses by 30%

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, blueprint=blueprint, save_name=save_name, save_folder=save_folder)

# Run it
rbg.run(data=data, bw=bw)
```
## Full example

A `.py` file with the full code of the quick start example can be found in `example/code/quick-start.py`.

```python


if __name__ == '__main__':
    freeze_support()

    # Set verbosity
    verbose = True
    plot_mode = False

    # Set the number of steps for MCMC
    n_steps = 5000  # 5k is for testing. In production, this should be >= 50k

    # Set other parameters for twinning
    blueprint = 'multi-meal'
    save_folder = os.path.join(os.path.abspath(''),'..','..','..')
    parallelize = True

    # load patient_info
    patient_info = pd.read_csv(os.path.join(os.path.abspath(''), '..', 'data', 'patient_info.csv'))
    p = np.where(patient_info['patient'] == 1)[0][0]
    # Set bw and u2ss
    bw = float(patient_info.bw.values[p])
    u2ss = float(patient_info.u2ss.values[p])

    # Instantiate ReplayBG
    rbg = ReplayBG(blueprint=blueprint, save_folder=save_folder,
                   yts=5, exercise=False,
                   seed=1,
                   verbose=verbose, plot_mode=plot_mode)

    # Load data and set save_name
    data = pd.read_csv(os.path.join(os.path.abspath(''), '..', 'data', 'data_day_1.csv'))
    data.t = pd.to_datetime(data['t'])
    save_name = 'data_day_1'

    print("Twinning " + save_name)

    # Step 1. Run twinning procedure
    rbg.twin(data=data, bw=bw, save_name=save_name,
             twinning_method='mcmc',
             parallelize=parallelize,
             n_steps=n_steps,
             u2ss=u2ss)

    # Step 2a. Replay the twin with the same input data to get the initial conditions for the subsequent day
    replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                                twinning_method='mcmc',
                                save_workspace=True,
                                u2ss=u2ss,
                                save_suffix='_step_2a')

    # Visualize results and compare with the original glucose data
    Visualizer.plot_replay_results(replay_results, data=data)
    # Analyze results
    analysis = Analyzer.analyze_replay_results(replay_results, data=data)
    # Print, for example, the fit MARD and the average glucose
    print('Fit MARD: %.2f %%' % analysis['median']['twin']['mard'])
    print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])

    # Step 2b. Replay the twin with different input data (-30% bolus insulin) to experiment how glucose changes
    data.bolus = data.bolus * .7
    replay_results = rbg.replay(data=data, bw=bw, save_name=save_name,
                                twinning_method='mcmc',
                                save_workspace=True,
                                u2ss=u2ss,
                                save_suffix='_step_2b')

    # Visualize results
    Visualizer.plot_replay_results(replay_results)
    # Analyze results
    analysis = Analyzer.analyze_replay_results(replay_results)

    # Print, for example, the average glucose
    print('Mean glucose: %.2f mg/dl' % analysis['median']['glucose']['variability']['mean_glucose'])

```