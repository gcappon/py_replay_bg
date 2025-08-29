import numpy as np
from py_replay_bg.sensors import CGM


class FakeCGM(CGM):
    def __init__(self):
        super().__init__()
        self.max_lifetime = 10  # This sensor only lasts 10 minutes

    def measure(self, ig: float, past_ig: list[float], t):
        # Fake sensor that just doubles the ig value
        # return ig * 2

        # Fake sensor that averages the last 10 ig values (10 minutes) plus some noise
        return np.nanmean(past_ig[-10:]) + np.random.uniform(-10,
                                                             10)

    def connect_new_cgm(self, connected_at=0):
        super().connect_new_cgm()
        print(f"New CGM sensor connected at {connected_at}")  # Just to show that this method is called