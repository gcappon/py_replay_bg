from py_replay_bg.sensors.CGM import CGM


class Sensors:
    """
    A class that represents the sensors to be used by ReplayBG.

    ...
    Attributes
    ----------
    cgm: CGM
        The CGM sensor used to measure the interstitial glucose during simulations.

    Methods
    -------
    None
    """

    def __init__(self, cgm: CGM):
        """
        Constructs all the necessary attributes for the Sensors object.

        Parameters
        ----------
        cgm: CGM
            The CGM sensor used to measure the interstitial glucose during simulations.
        """
        self.cgm = cgm
