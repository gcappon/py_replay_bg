from py_replay_bg.sensors import CGM


class FakeCGM(CGM):
    def __init__(self):
        super().__init__()
        self.max_lifetime = 10

    def measure(self, ig: float, past_ig: list[float], t):
        return ig * 2

    def connect_new_cgm(self, connected_at=0):
        super().connect_new_cgm()
        print(f"New CGM sensor connected at {connected_at}")