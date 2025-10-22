from abc import abstractmethod, ABC

import numpy as np


class CustomRaBase(ABC):

    @abstractmethod
    def simulate_forcing_ra(self, time: np.ndarray, time_index: int) -> float:
        """
        This method should be implemented by subclasses to provide the logic for simulating the custom forcing RA at each time step.
        IMPORTANT: This method should maintain the internal state of the object, as it will be called iteratively during the replay simulation.

        Parameters
        ----------
        time: np.ndarray
            An array vector as long the simulation length containing the time corresponding to the current step (hours) up
            to time_index. The values after time_index should be ignored.
        time_index: int
            The index corresponding to the current step of the replay simulation.

        Returns
        -------
        current_ra: float
            The value of the current RA to be used in the replay simulation (in mg/(kg*min).
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @abstractmethod
    def get_events(self)-> np.ndarray:
        """
        Returns a list of events that have generated the forcing RA. By default, it returns an empty list.
        CHO events should be in mg/(kg*min).

        Returns
        -------
        events: list
            A list of events.
        """
        return np.array([])