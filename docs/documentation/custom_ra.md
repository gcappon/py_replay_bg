---
sidebar: heading
---

# Custom Rate of Appearance (Ra) Model

The Rate of Appearance (Ra) model is a crucial component in glucose metabolism simulations, representing the rate at which glucose enters the bloodstream after carbohydrate ingestion. In ReplayBG, users can implement custom Ra models to better simulate specific physiological responses.

## Model abstract class
The Ra model is implemented as an abstract class `CustomRaBase`, which defines the interface for all Ra model implementations. This class can be extended by specific Ra model implementations.

The interface of the abstract class includes the following method:
- `simulate_forcing_ra(self, time: np.ndarray, time_index: int) -> float:`: Simulates the Rate of Appearance at a given time index. It takes as input the time array and the current time index, returning the Ra value in mg/kg/min.
- `get_events(self)-> np.ndarray`: Returns the array of events (e.g., meal times and quantities) that influence the Ra simulation.

::: warning
The model shoud inherit from `CustomRaBase` and implement the required methods. 
:::

::: tip REMARK
The Ra model should output values in **mg/kg/min** to ensure compatibility with the ReplayBG framework.
All the logic of equations, states and parameters should be implemented within the custom class.
:::

## How to set the Ra Model to use during replays
The replay method of the `ReplayBG` class accepts a `custom_ra` parameter, which can be set to an instance of the custom Ra model to be used.

```python
import MyCustomRaModel
custom_ra = MyCustomRaModel(params)
results = rbg.replay(..., custom_ra=custom_ra)
```

## Example of custom Ra Model reproducing the snack model of ReplayBG

This example shows how to use a custom Ra model in a ReplayBG simulation. The example uses a simple Ra model that simulates a snack ingestion event.
The full example is available in the `examples` folder of the ReplayBG repository.

```python
from py_replay_bg.replay.custom_ra import CustomRaBase

class CustomRa(CustomRaBase):
    
    def __init__(self, CHO, k_empt, k_abs, f=1.0, beta=0, bw=70.0):
        super().__init__()
        self.dt = 1.0  # time step in minutes
        self.CHO = CHO * 1000 / bw  # np.array of CHO at each timestamp converted to mg/(kg*min)
        self.k_empt = k_empt
        self.k_abs = k_abs
        self.f = f
        self.beta = int(beta)  # delay in number of time steps
        self.Q_sto1 = 0.0
        self.Q_sto2 = 0.0
        self.Q_gut = 0.0
        self.bw = bw  # body weight in kg

    def simulate_forcing_ra(self, time: np.ndarray, time_index: int) -> float:
        # Apply delay (beta) in indices
        cho_idx = (time_index - self.beta)
        CHO_input = self.CHO[cho_idx - 1] if cho_idx >= 0 else 0.0

        dQ_sto1 = -self.k_empt * self.Q_sto1 + CHO_input
        dQ_sto2 = self.k_empt * self.Q_sto1 - self.k_empt * self.Q_sto2
        dQ_gut = self.k_empt * self.Q_sto2 - self.k_abs * self.Q_gut

        self.Q_sto1 += dQ_sto1 * self.dt
        self.Q_sto2 += dQ_sto2 * self.dt
        self.Q_gut += dQ_gut * self.dt

        Ra = self.f * self.k_abs * self.Q_gut
        return Ra

    def get_events(self):
        return self.CHO
```
