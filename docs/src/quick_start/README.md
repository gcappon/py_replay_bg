---
sidebar: auto
---
# Quick Start

## Installation

**PyReplayBG** can be installed via pypi by simply 

```python
pip install py-replay-bg
```

## Preparation: import and get data to play with 

First of all import the necessary modules. 

```python
import os
import pandas as pd
from py_replay_bg.py_replay_bg import ReplayBG
```

Now, let's load some data to play with. In this example, we will use the data in `example/data/multi-meal_data.csv` 
which contains a day data of a patient with T1D whose body weight is `100` kg:

```python
data = pd.read_csv(os.path.join(os.path.abspath(''),'..', 'data', 'multi-meal_example.csv'))
data.t = pd.to_datetime(data['t'])
```

Be careful, data in PyReplayBG must be provided in a `.csv.` file that must follow some strict requirements. For more info
on data requirements in `PyReplayBG` see the [Data Requirements](../data_requirements/README.md) 
section.

## Step 1. Identify the model (AKA fits your data)

The first step of PyReplayBG consists of identifying its model (i.e., the digital twinning procedure). This can be done
with:

```python
modality = 'identification' # set modality as 'identification'
bw = 100 # set the patient body weight
scenario = 'multi-meal' # set the type of scenario corresponding to the data at hand (can be single-meal or multi-meal)
save_name = 'test_multi_meal' # set a save name
n_steps = 2500 # set the number of steps that will be used for identification (for multi-meal it should be at least 100k)
save_folder = os.path.abspath('') # set the results folder to the current folder

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder, n_steps=n_steps)

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
rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder)

# Run it
rbg.run(data=data, bw=bw)
```

Another example could be test "waht happens if I reduce the bolus insulin by 30%?". To know the answer run:
```python
modality = 'replay' # change modality as 'replay'

# Replay with less insulin
data.bolus = data.bolus * .7 # Reduce insulin boluses by 30%

# Instantiate ReplayBG
rbg = ReplayBG(modality=modality, data=data, bw=bw, scenario=scenario, save_name=save_name, save_folder=save_folder)

# Run it
rbg.run(data=data, bw=bw)
```
## Full example

A `.py` file with the full code of the quick start example can be found in `example/code/quick-start.py`.