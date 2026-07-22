from .animation import Animation
from .constants import CarConst
import numpy as np

class Cars(Animation):
    """Represents cars riding around a loop.

    Parameters
    ----------
    number_of_cars : int
        The quantity of running vehicles (must be > 0).
    v_initial : float
        Initial velocity reference for cars/limits.

    Raises
    ------
    ValueError
        If radius or number_of_cars are invalid.
    """

    def __init__(
            self,
            number_of_cars: int,
            v_initial: float,
            dt: float,
            name: str
) -> None:
        super().__init__(name=name, numc=number_of_cars, dt=dt)
        # Constructor Argument Validation
        if number_of_cars <= 0:
            raise ValueError("Number of cars must be a positive integer.")
        
        self._positions = np.linspace(0, 2 * np.pi, self.numc, endpoint=False) * self.r
        self._velocities = np.full(number_of_cars, v_initial)
        self.distance_reactions = np.random.normal(loc=CarConst.DISTANCE_REACTION, scale=0.1, size=self.numc)
        self.segment_reactions = np.random.normal(loc=CarConst.SEGMENT_REACTION, scale=0.01, size=self.numc)

    # ==========================================================================
    #     Properties and Setters
    # ==========================================================================
    @property
    def positions(self) -> np.ndarray:
        return self._positions
    @positions.setter
    def positions(self, positions: np.ndarray) -> None:
        """Takes the positions and keeps it in [0, 2*np.pi]."""
        if positions.ndim != 1:
            raise ValueError("Positions must be a 1D array.")
        self._positions = positions % self.length

    @property
    def velocities(self) -> np.ndarray:
        return self._velocities
    @velocities.setter
    def velocities(self, velocities: np.ndarray) -> None:
        if velocities.ndim != 1:
            raise ValueError("Velocities must be a 1D array.")
        self._velocities = velocities

    def minimum_distances(self) -> np.ndarray:
        """Updated minimum distance base on the current speed and reaction time."""
        return self.velocities * CarConst.REACTION_TIME

