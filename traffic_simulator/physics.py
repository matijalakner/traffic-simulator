from typing import Optional, Tuple
import numpy as np

def sign(arr1, arr2):
    return np.where(arr1>arr2, 1, -1)

def reactor(arr1, arr2):
    return np.where(arr1>arr2, 1, -1) * (1 - np.e**((arr2 - arr1)/(arr1 + arr2)))

def distance_acceleration(
        s_diff: np.ndarray,
        s_min: np.ndarray,  
        alpha: np.ndarray,
        sensitivity: float=2.5,
) -> np.ndarray:
    """Calculate the vehicle's acceleration contribution based on car-following behavior.

    Parameters
    ----------
    s_diff : np.ndarray
        Distances between vehicles.
    s_min : np.ndarray
        Minimum safe distance threshold between vehicles.
    alpha : np.ndarray
        Sensitivity coefficient for speed-to-distance coupling.
    sensitivity:
        how sensible is the driver on the distance of the car ahead.
    Returns
    -------
    np.ndarray
        Acceleration component derived from interactions with leading vehicles.
    """
    return np.where(s_diff < sensitivity*s_min, alpha /(- reactor(s_diff, s_min)), 0)
    
def sector_acceleration(
        cars: np.ndarray,
        sectors: np.ndarray,
        sector_positions: np.ndarray,
        beta: np.ndarray,
) -> np.ndarray:
    """Calculate the acceleration contribution based on sector speed limit compliance.

    Parameters
    ----------
    cars : np.ndarray
        Car data(s_car, v_car).
    sectors : np.ndarray
        Sector data(s_sect, len_sect, v_sect).
    sector_positions : np.ndarray
        Sector of cars.
    beta : np.ndarray
        Sensitivity coefficient for matching sector target speeds.

    Returns
    -------
    np.ndarray
        Acceleration component derived from the sector speed adjustment.
    """
    [s_sect, len_sect, v_sect] = sectors
    switched_v_sect = np.concatenate((v_sect[1:], np.array([v_sect[0]])), axis=None)

    [s_car, v_car] = cars
    coeff = ((s_sect[sector_positions] - s_car) / len_sect[sector_positions])

    v_ratio = (switched_v_sect[sector_positions] - v_sect[sector_positions]) / (v_sect[sector_positions] + switched_v_sect[sector_positions])
    next_coeff = 1 - coeff
    
    acc = beta * (coeff * reactor(v_sect[sector_positions], v_car) + v_ratio * next_coeff * reactor(switched_v_sect[sector_positions], v_car))
    
    return acc
    
def calculate_acceleration(
        acc_sect: np.ndarray,
        acc_car: np.ndarray,
) -> np.ndarray: 
    """Blend sector and car-following acceleration weights safely using dynamic proximity.

    Parameters
    ----------
    acc_sect : np.ndarray
        Acceleration component based on sector speed compliance.
    acc_car : np.ndarray
        Acceleration component based on car-following behavior.

    Returns
    -------
    np.ndarray
        Combined net acceleration for each vehicle.
    """
    
    acc = acc_sect + acc_car
    
    return acc
    
def ei_v(
        vel: np.ndarray,
        acc: np.ndarray,
        dt: float = 0.1
) -> np.ndarray:
    """Compute updated velocities using basic Euler integration.

    Parameters
    ----------
    vel : np.ndarray
        Current velocities.
    acc : np.ndarray
        Accelerations.
    dt : float, optional
        Time-step interval, by default 0.1.

    Returns
    -------
    np.ndarray
        Updated velocity states.
    """
    return vel + acc * dt
   
def ei_s(
        pos: np.ndarray,
        vel: np.ndarray,
        acc: np.ndarray,
        dt: float = 0.1
) -> np.ndarray:
    """Compute circular positions mapping trajectory steps.

    Parameters
    ----------
    pos : np.ndarray
        Current positions (radians).
    vel : np.ndarray
        Velocities.
    acc : np.ndarray
        Accelerations.
    dt : float, optional
        Time-step interval, by default 0.1.

    Returns
    -------
    np.ndarray
        Updated polar coordinates on the track ring.
    """
    return pos + vel * dt + 0.5 * acc * (dt ** 2)
