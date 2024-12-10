---
sidebar: auto
---

# The ReplayBG Object

The `ReplayBG` object is the core, key, object to instatiate when starting to work with the ReplayBG framework.

Its constructor is formally defined as:

```python
from py_replay_bg.py_replay_bg import ReplayBG

ReplayBG(save_folder: str, blueprint: str = 'single_meal',
    yts: int = 5, exercise: bool = False,
    seed: int = 1,
    plot_mode: bool = True, verbose: bool = True)
```

## Input parameters 

Let's inspect and describe each input parameter.

- `save_folder`: a string defining the folder that will contain the results of the twinning procedure and the replay 
simulations. This parameter is mandatory. More information on how to set it can be found in 
[The _results/_ Folder](./results_folder.md) page. 
- `blueprint`, optional, `{'single-meal', 'multi-meal'}`, default: `'single-meal'`: a string that specifies the blueprint to be used to create 
the digital twin. More information on how to set it can be found in [Choosing Blueprint](./choosing_blueprint.md) page. 
- `yts`, optional, default: `5` : an integer that specifies the data sample time (in minutes).
- `exercise`, optional, default: `False`: a boolean that specifies whether to simulate exercise or not.
- `seed`, optional, default: `1`: an integer that specifies the random seed. For reproducibility.
- `plot_mode`, optional, default: `True`: a boolean that specifies whether to show the plot of the results or not. More 
information on how to visualize the results of ReplayBG can be found in 
[Visualizing Replay Results](./visualizing_replay_results.md) page. 
- `verbose`, optional, default: `True`: a boolean that specifies the verbosity of ReplayBG.



