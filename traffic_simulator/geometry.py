import numpy as np

def distance(positions: np.ndarray, length: float  ) -> np.ndarray:
    """Calculate directional spatial differences (gaps) between successive cars.

    Parameters
    ----------
    positions : np.ndarray
        Sorted circular positions of cars.
    length : float
        Length of the track.

    Returns
    -------
    np.ndarray
        Angular distances to the car ahead (accounting for circular wrap-around).
    """
    switched_positions = np.concatenate((positions[1:], np.array([positions[0]])), axis=None)
    diffs = switched_positions - positions
    diffs = np.where(diffs < 0, length + diffs, diffs)

    return diffs

def position(positions: np.ndarray, segment_positions: np.ndarray) -> np.ndarray:
    """Calculates a segment in which car currently is.

    Parameters
    __________
    positions : np.ndarray
        Current positions of cars.
    segment_positions : np.ndarray
        Ends of segments.

    Returns
    _______
    np.ndarray
        An array of number of segments in which every car is.
    """
    return np.array([len(segment_positions[segment_positions < car]) for car in positions])