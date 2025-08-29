---
sidebar: heading
---

# The CGM error model

The CGM error model is a key component of the ReplayBG framework, and it is designed to simulate the errors associated with
these devices.

## Model abstract class

The CGM error model is implemented as an abstract class `CGM`, which defines the interface for
all CGM error models. This class can be extended by specific CGM error model implementations.

The constructor of the abstract class defines the following attributes:

- `ts`: The sample time of the cgm sensor in minutes (default: 5).
- `max_lifetime`: The maximum lifetime of the CGM sensor in minutes (default: 1440).

The abstract class defines the following methods:

- `connect_new_cgm(connected_at: int=0)`: Connects a new CGM device, setting the time at which it is connected. Used
  internally to reset state across multiple replays.
- `add_offset(to_add: float)`: Adjusts the model's internal offset. Rarely needs overriding.
- `measure(ig: float, past_ig: list[float], t: float)`:  Function that provides a CGM measure from the past interstitial
  glucose values. It takes as input the interstitial glucose values `ig`, all the past interstitial glucose values
  `past_ig`, and the relative time `t` in days since the startup of the sensor.

## Default CGM error model

The default CGM error model available in ReplayBG is the Vettoretti19CGM model as published in Vettoretti et al., Sensors,
2019, which is a factory-calibrated device with a lifespan of 10 days and a sample time of 5 minutes.

Model equations are:

$
\begin{cases}
IG_S(t) = (a_0 + a_1 \cdot t + a_2 \cdot t^2) \cdot IG(t) + b_0 \\
CGM(t) = IG_S(t) + v(t)
\end{cases}
$

with $a_0$, $a_1$, $a_2$, and $b_0$ (min$^{-1}$) model coefficients; and $v(t) \sim N(0, \epsilon_v)$ random white
noise. Particularly, in order to mimic real CGM systems, $CGM(t)$ is saturated between 40 and 400 mg/dL.

## How to choose the CGM error model to use during replays

The replay method of the `ReplayBG` class accepts a `sensor_cgm` parameter, which can be set to the class of the CGM to
be used.
```python
import MyCustomCGM
results = rbg.replay(..., sensor_cgm=MyCustomCGM)
```
If no `sensor_cgm` is provided, the default CGM error model (Vettoretti19CGM) is used.

### Example of use

This example shows how to use a custom CGM error model in a ReplayBG simulation. The example uses a fake CGM model
that doubles the interstitial glucose values for demonstration purposes. The sensor has a maximum lifetime of 10
minutes.

The full example is available in the `example/code/` folder in the `fake_CGM.py` and `replay_map_fakecgm.py` files.

```
class FakeCGM(CGM):
    def __init__(self):
        super().__init__()
        self.max_lifetime = 10

    def measure(self, ig: float, past_ig: list[float], t):
        return ig * 2

    def connect_new_cgm(self, connected_at=0):
        super().connect_new_cgm()
        print(f"New CGM sensor connected at {connected_at}")
        
def main():
  ...
  # Replay the twin with the same input data used for twinning
  replay_results = rbg.replay(..., sensor_cgm=FakeCGM)
  ...
```
