from typing import List, Union
import numpy as np
from .road import Road
from .constants import PartIndex

class Parts(Road):
    
    def __init__(self,
            name: str,
            radius: float,
            number_of_parts: int,
            number_of_cars: int,
            v_initial: float,
    ) -> None:
        """Represents cars riding around a loop.

        Parameters
        ----------
        name : str
            Name of the track.
        radius : float
            The physical radius of the circular track (must be positive).
        number_of_parts : int
            The quantity of parts (must be > 0).
        number_of_cars : int
            The quantity of running vehicles (must be > 0).
        v_initial : float
            Initial velocity reference for cars/limits.

        Raises
        ------
        ValueError
            If radius or number_of_cars are invalid.
        ValueError
            If radius or number_of_parts are invalid.
        """
        super().__init__(
            name=name,
            radius=radius,
            number_of_cars=number_of_cars,
            v_initial=v_initial
            )
        
        if number_of_parts <= 0:
            raise ValueError("Number of parts (sectors) must be a positive integer.")
        
        self.nump: int = number_of_parts
        self._parts = self.init_parts(nump=number_of_parts, v_0=v_initial)
        
    # =======================================================================================
    #    Propertys
    # =======================================================================================
    @property
    def parts(self) -> np.ndarray:
        """Get sectors tracking data array."""
        return self._parts

    @parts.setter
    def parts(self, new_parts_data: np.ndarray) -> None:
        """Set sector profiles."""
        self._parts = new_parts_data
        
    # ========================================================================================
    #    Initialization Functions
    # ========================================================================================
    def init_parts(self, nump: int, v_0: float) -> np.ndarray:
        """Set up track physical sector segments.

        Parameters
        ----------
        nump : int
            Number of parts.
        v_0 : float
            Initial velocity limit.

        Returns
        -------
        np.ndarray
            Data structure tracking segment ranges and speed limits.
        """
        parts = np.zeros((2, nump))
        parts[PartIndex.ZONES] = np.linspace(0, 2 * np.pi, nump, endpoint=False)
        parts[PartIndex.MAX_SPEEDS] = np.full(nump, v_0)
        
        return parts
        
    

