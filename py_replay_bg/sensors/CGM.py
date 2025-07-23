from abc import ABC, abstractmethod

import numpy as np


class CGM(ABC):
    """
    A class that represents a CGM sensor.

    Attributes
    ----------
    ts: int
        The sample time of the cgm sensor (min).
    t_offset: float
        The time offset of the cgm sensor (when new this is 0). This is used if a cgm sensor is shared between more
        replay runs.
    max_lifetime: float
        The maximum lifetime of the CGM sensor (in minutes).
    connected_at: int
        The time (minutes) at which the CGM sensor is connected (utility variable to manage sensor lifetime through multiple
        ReplayBG calls).

    Methods
    -------
    connect_new_cgm(connected_at):
        Connects a new CGM sensor by sampling new error parameters.
    measure(ig, t):
        Function that provides a CGM measure using the model of Vettoretti et al., Sensors, 2019.
    add_offset(to_add):
        Utility function that adds an offset to the sensor life. Used when the sensor object must be shared through
        multiple ReplayBG runs.
    """

    def __init__(self,
                 ):
        """
        Constructs all the necessary attributes for the CGM object.
        """

        self.ts = 5
        self.t_offset = 0

        self.connect_new_cgm()

        # Set max lifetime (minutes)
        self.max_lifetime = 1400 * 10
        self.connected_at = 0

    def connect_new_cgm(self, connected_at=0):
        """
        Connects a new CGM sensor by sampling new error parameters.

        Parameters
        ----------
        connected_at: int, optional, default = 0
            The time at which the CGM sensor is connected (utility variable to manage sensor lifetime through multiple
            ReplayBG calls).

        Returns
        -------
        None

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """

        # Set the offset (minutes)
        self.t_offset = 0

        # Set the connection time
        self.connected_at = connected_at

    @abstractmethod
    def measure(self, ig: float, past_ig: list[float], t):
        """
        Function that provides a CGM measure from the past interstitial glucose values.

        Parameters
        ----------
        ig: float
            The current interstitial glucose concentration (mg/dl).
        past_ig: list[float]
            The series of past interstitial glucose concentrations (mg/dl). The value of ig[-1] is the current interstitial glucose.
        t: float
            Current time in days from the start of CGM sensor.

        Returns
        -------
        cgm: float
            The CGM measurement at current time (mg/dl).

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """
        pass

    def add_offset(self,
                   to_add: float) -> None:
        """
        Utility function that adds an offset to the sensor life. Used when the sensor object must be shared through
        multiple ReplayBG runs.

        Parameters
        ----------
        to_add: float
            The offset to add to the sensor life.

        Returns
        -------
        None

        Raises
        ------
        None

        See Also
        --------
        None

        Examples
        --------
        None
        """
        self.t_offset += to_add
