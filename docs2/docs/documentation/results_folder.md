---
sidebar: auto
---

# The _results/_ folder

All results of ReplayBG, i.e., both model parameters obtained via twinning procedure and replayed
glucose traces of a given scenario, will be saved in a folder named `results/`.

## Choosing the path of _results/_

When creating the ReplayBG object, user must decide the location of `results/`.
To do that, specify a custom location, relative to current `<WORKING_DIRECTORY>`
using the `save_folder` parameter of the `ReplayBG` object builder. For example, 
to put `results/` in `<WORKING_DIRECTORY>/custom/path/location/`, simply: 

```python
rbg = ReplayBG(save_folder=os.path.join('custom', 'path', 'location'), ...)
```

This means that if the user wants to put `results/` just in `<WORKING_DIRECTORY>`
he/she must use:

```python
rbg = ReplayBG(save_folder=os.path.join(''), ...)
```

## What's inside

The `results/` folder is organized as follows: 

```
results/
|--- mcmc/
|--- map/
|--- workspaces/
```

where the `mcmc/` and `map/` subfolders contains the model parameters obtained via
MCMC-based and MAP-based twinning procedures, respectively; and the `workspaces/` folder
contains the results of the replayed scenarios simulated when the `rbg.replay()` method 
is called.

::: tip REMEMBER
Results of the replayed scenarios are saved in the `workspace/` subfolder only if the 
`save_workspace` parameter of `rbg.replay()` is set to `True`: 
```python
rbg.replay(save_workspace=True, ...)
```
If not set, being its default value `False`, nothing will be saved. 
:::





