import numpy as np

from .constants import AstroConstants


def geodetic_lat_to_geocentric(lat_geod: np.ndarray) -> np.ndarray:
    """Converts geodetic latitude to geocentric latitude

    :param lat_geod: Geodetic latitudes [rad]
    :type lat_geod: np.ndarray
    :return: Geocentric latitudes [rad]
    :rtype: np.ndarray
    """
    return np.arctan(
        (1 - AstroConstants.earth_f) ** 2 * np.tan(lat_geod)
    )


def radius_at_geodetic_lat(lat_geodetic: np.ndarray) -> np.ndarray:
    """Earth's radius at the given geodetic latitude

    :param lat_geodetic: Geodetic latitudes [rad]
    :type lat_geodetic: np.ndarray
    :return: Earth radius at given latitudes [km]
    :rtype: np.ndarray
    """
    return (
        AstroConstants.earth_r_eq
        - 21.38 * np.sin(geodetic_lat_to_geocentric(lat_geodetic)) ** 2
    )
