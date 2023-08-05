from .time import (
    date_to_sidereal,
    date_to_jd,
    date_to_capital_t,
)
from .attitude import axis_rotation_matrices
from .math import (
    cosd,
    hat,
    sind,
    wrap_to_360,
    dms_to_rad,
    dot,
    stack_mat_mult,
    sph_to_cart,
    cart_to_sph,
    wrap_to_two_pi,
)
from .geodetic import geodetic_lat_to_geocentric, radius_at_geodetic_lat
from .constants import AstroConstants

from astropy.utils.iers import IERS_A_URL, IERS_A
from astropy.utils.data import download_file
import numpy as np
import datetime
import os

iers_provider = IERS_A.open(download_file(IERS_A_URL, cache=True))
nutation_coeffs = np.loadtxt(
    os.path.join(
        os.environ["SRCDIR"], "resources", "data", "nutation_coeffs.txt"
    )
)


def inclination_of_ecliptic(date: datetime.datetime) -> float:
    """Inclination of the ecliptic plane [rad]

    :param date: Date to evaluate at [utc]
    :type date: datetime.datetime
    :return: Inclination [rad]
    :rtype: float

    >>> date = datetime.datetime(2000, 12, 9, 13, 14, 15, tzinfo=datetime.timezone.utc)
    >>> i = inclination_of_ecliptic(date)
    >>> 0.4090906724834187
    """
    T = date_to_capital_t(date)
    epsilon = (
        dms_to_rad(23.43929111, 0, 0)
        - dms_to_rad(0, 0, 46.8150) * T
        - dms_to_rad(0, 0, 0.00059) * T**2
        + dms_to_rad(0, 0, 0.001813) * T**3
    )
    return epsilon


def eci_to_sun_ec(dates: np.ndarray[datetime.datetime]) -> np.ndarray:
    """Rotation matrix from Earth-centered inertial (ECI) to Sun-relative ECI

    :param dates: Dates to evaluate at
    :type dates: np.ndarray[datetime.datetime]
    :return: Stack of DCMs
    :rtype: np.ndarray
    """
    n = dates.size
    v1 = hat(sun(date_to_jd(dates)))
    ref = np.tile([0, 0, 1], (n, 1))
    v2 = hat(np.cross(v1, ref))
    v3 = np.cross(v1, v2)
    dcms = np.dstack((v1, v2, v3))
    return dcms


def eci_eq_to_eci_ec() -> np.ndarray:
    """Rotation matrix between equatorial and ecliptic Earth-centered inertial (ECI)

    :return: Rotation matrix
    :rtype: np.ndarray [3x3]
    """
    (r1, _, _) = axis_rotation_matrices()
    return r1(-AstroConstants.inclination_of_ecliptic)


def ecef_to_eci(date: datetime.datetime) -> np.ndarray:
    """Converts from Earth-centered, Earth-fixed (ECEF) coordinates to Earth- centered inertial (ECI). Does not account for precession, nutation, or polar motion.

    :param date: Time
    :type date: datetime.datetime [UTC]
    :return: Rotation matrix from ECEF to ECI
    :rtype: np.ndarray [3x3]
    """
    (_, _, r3) = axis_rotation_matrices()
    sid_time = date_to_sidereal(date)
    # Gets the current sidereal time
    gmst = (sid_time % 86400) / 86400 * 2 * np.pi
    # Gets the GMST hour angle
    return r3(
        -gmst
    )  # Gets the rotation matrix about the third body axis


def eci_to_ecef(date: datetime.datetime) -> np.ndarray:
    """Converts from Earth-centered inertial (ECI) to Earth-centered, Earth-fixed coordinates. Does not account for precession, nutation, or polar motion.

    :param date: Time
    :type date: datetime.datetime [UTC]
    :return: Rotation matrix from ECI to ECEF
    :rtype: np.ndarray [3x3]
    """
    return ecef_to_eci(date).T


def moon(jd: np.ndarray) -> np.ndarray:
    """Translation of Vallado's MATLAB method of the same name, approximates the position of the Moon.

    :param jd: Julian dates
    :type jd: np.ndarray [nx1]
    :return: Approximate vector to Moon from Earth center [km]
    :rtype: np.ndarray [nx3]
    """
    jd = np.array([jd]).flatten()
    ttdb = (jd - 2451545.0) / 36525.0

    eclplong = wrap_to_360(
        218.32
        + 481267.8813 * ttdb
        + 6.29 * sind(134.9 + 477198.85 * ttdb)
        - 1.27 * sind(259.2 - 413335.38 * ttdb)
        + 0.66 * sind(235.7 + 890534.23 * ttdb)
        + 0.21 * sind(269.9 + 954397.70 * ttdb)
        - 0.19 * sind(357.5 + 35999.05 * ttdb)
        - 0.11 * sind(186.6 + 966404.05 * ttdb)
    )

    eclplat = wrap_to_360(
        5.13 * sind(93.3 + 483202.03 * ttdb)
        + 0.28 * sind(228.2 + 960400.87 * ttdb)
        - 0.28 * sind(318.3 + 6003.18 * ttdb)
        - 0.17 * sind(217.6 - 407332.20 * ttdb)
    )

    hzparal = wrap_to_360(
        0.9508
        + 0.0518 * cosd(134.9 + 477198.85 * ttdb)
        + 0.0095 * cosd(259.2 - 413335.38 * ttdb)
        + 0.0078 * cosd(235.7 + 890534.23 * ttdb)
        + 0.0028 * cosd(269.9 + 954397.70 * ttdb)
    )

    obliquity = 23.439291 - 0.0130042 * ttdb
    magr = 1.0 / sind(hzparal)
    # ------------- calculate moon position vector ----------------
    rmoon = np.empty((jd.shape[0], 3), dtype=np.float64)
    rmoon[:, 0] = magr * cosd(eclplat) * cosd(eclplong)
    rmoon[:, 1] = magr * (
        cosd(obliquity) * cosd(eclplat) * sind(eclplong)
        - sind(obliquity) * sind(eclplat)
    )
    rmoon[:, 2] = magr * (
        sind(obliquity) * cosd(eclplat) * sind(eclplong)
        + cosd(obliquity) * sind(eclplat)
    )
    return rmoon * AstroConstants.earth_r_eq


def sun(jd: np.ndarray) -> np.ndarray:
    """Translation of Vallado's MATLAB method of the same name, approximating the position of the sun.

    :param jd: Julian days
    :type jd: np.ndarray [nx1]
    :return: Approximate vector to the Sun from Earth center [km]
    :rtype: np.ndarray [nx3]
    """
    jd = np.array([jd]).flatten()
    tut1 = (jd - 2451545.0) / 36525.0
    meanlong = (280.460 + 36000.77 * tut1) % 360.0
    meananomaly = np.deg2rad((357.5277233 + 35999.05034 * tut1) % 360.0)
    meananomaly = np.array(
        [m if m > 0 else m + 2 * np.pi for m in meananomaly]
    )
    # if meananomaly < 0: meananomaly += 2*np.pi
    eclplong = np.deg2rad(
        (
            meanlong
            + 1.914666471 * np.sin(meananomaly)
            + 0.019994643 * np.sin(2 * meananomaly)
        )
        % 360.0
    )
    obliquity = np.deg2rad(23.439291 - 0.0130042 * tut1)
    magr = (
        1.000140612
        - 0.016708617 * np.cos(meananomaly)
        - 0.000139589 * np.cos(2.0 * meananomaly)
    )
    # in AU
    rsun = np.empty((jd.shape[0], 3))
    rsun[:, 0] = magr * np.cos(eclplong)
    rsun[:, 1] = magr * np.cos(obliquity) * np.sin(eclplong)
    rsun[:, 2] = magr * np.sin(obliquity) * np.sin(eclplong)
    return rsun * AstroConstants.au_to_km


iers_provider = IERS_A.open(download_file(IERS_A_URL, cache=True))


def gtod_to_itrf(date: datetime.datetime) -> np.ndarray:
    """Rotation matrix from Greenwich True of Date (GTOD) to the Internation Terrestrial Reference Frame (ITRF)

    :param date: Date to evaluate at [utc]
    :type date: datetime.datetime
    :return: Rotation matrix
    :rtype: np.ndarray [3x3]
    """
    r1, r2, r3 = axis_rotation_matrices()
    x_p, y_p = iers_provider.pm_xy(date_to_jd(date))
    x_p, y_p = dms_to_rad(0, 0, x_p.value), dms_to_rad(0, 0, y_p.value)
    Pi = r2(-x_p) @ r1(-y_p)
    return Pi


def tod_to_gtod(date: datetime.datetime) -> np.ndarray:
    """Rotation matrix from True of Date (TOD) to Greenwich True of Date (GTOD)

    :param date: Date to evaluate at [utc]
    :type date: datetime.datetime
    :return: Rotation matrix
    :rtype: np.ndarray [3x3]
    """
    r1, r2, r3 = axis_rotation_matrices()
    stime = date_to_sidereal(date)
    gmst = (
        (stime % AstroConstants.earth_sec_in_day)
        / AstroConstants.earth_sec_in_day
        * 2
        * np.pi
    )
    Theta = r3(gmst)
    return Theta


def mod_to_tod(date: datetime.datetime) -> np.ndarray:
    """Rotation matrix from Mean of Date (MOD) to True of Date (TOD), accounts for nutation

    :param date: Date to evaluate at [utc]
    :type date: datetime.datetime
    :return: Rotation matrix
    :rtype: np.ndarray [3x3]
    """
    T = date_to_capital_t(date)
    r1, r2, r3 = axis_rotation_matrices()
    l = (
        dms_to_rad(134, 57, 46.733)
        + dms_to_rad(477198, 52, 02.633) * T
        + dms_to_rad(0, 0, 31.310) * T**2
        + dms_to_rad(0, 0, 0.064) * T**3
    )
    lprime = (
        dms_to_rad(357, 31, 39.804)
        + dms_to_rad(35999, 3, 01.244) * T
        - dms_to_rad(0, 0, 0.577) * T**2
        - dms_to_rad(0, 0, 0.012) * T**3
    )
    F = (
        dms_to_rad(93, 16, 18.877)
        + dms_to_rad(483202, 1, 03.137) * T
        - dms_to_rad(0, 0, 13.257) * T**2
        + dms_to_rad(0, 0, 0.011) * T**3
    )
    D = (
        dms_to_rad(297, 51, 01.307)
        + dms_to_rad(445267, 6, 41.328) * T
        - dms_to_rad(0, 0, 6.891) * T**2
        + dms_to_rad(0, 0, 0.019) * T**3
    )
    Omega = (
        dms_to_rad(125, 2, 40.280)
        - dms_to_rad(1934, 8, 10.539) * T
        + dms_to_rad(0, 0, 7.455) * T**2
        + dms_to_rad(0, 0, 0.008) * T**3
    )

    pl = nutation_coeffs[:, 1]
    plprime = nutation_coeffs[:, 2]
    pf = nutation_coeffs[:, 3]
    pd = nutation_coeffs[:, 4]
    pomega = nutation_coeffs[:, 5]
    deltaPsi_i = np.deg2rad(
        (nutation_coeffs[:, 6] + T * nutation_coeffs[:, 7]) / 3600e4
    )
    # Computes the change in the equinox
    deltaepsilon_i = np.deg2rad(
        (nutation_coeffs[:, 8] + T * nutation_coeffs[:, 9]) / 3600e4
    )
    # Computes the change in the ecliptic

    phi_i = pl * l + plprime * lprime + pf * F + pd * D + pomega * Omega
    # Series form of phi

    deltaPsi = np.sum(deltaPsi_i * np.sin(phi_i))
    deltaepsilon = np.sum(deltaepsilon_i * np.cos(phi_i))
    epsilon = inclination_of_ecliptic(date)
    # The nominal inclination of the ecliptic at this time
    N = r1(-epsilon - deltaepsilon) @ r3(-deltaPsi) @ r1(epsilon)
    return N


def j2000_to_mod(date: datetime.datetime) -> np.ndarray:
    """Rotation matrix from J2000 to Mean of Date (MOD), accounts for precession

    :param date: Date to evaluate at [utc]
    :type date: datetime.datetime
    :return: Rotation matrix
    :rtype: np.ndarray [3x3]
    """
    r1, r2, r3 = axis_rotation_matrices()
    T = date_to_capital_t(date)

    zeta = dms_to_rad(
        0, 0, 2306.2181 * T + 0.30188 * T**2 + 0.017998 * T**3
    )
    theta = dms_to_rad(
        0, 0, 2004.3109 * T - 0.42665 * T**2 - 0.041833 * T**3
    )
    z = zeta + dms_to_rad(0, 0, 0.79280 * T**2 + 0.000205 * T**3)
    P = r3(z) @ r2(-theta) @ r3(zeta)
    return P.T


class EarthFixedFrame:
    """Handles transformations between various Earth-centered reference frames"""

    _FRAMES = ["itrf", "gtod", "tod", "mod", "j2000"]

    def __init__(self, home: str, to: str):
        assert (
            home.lower() != to.lower()
        ), f"Home and To frmes must be different"
        assert (
            home.lower() in self._FRAMES
        ), f"Frame {home} not in {self._FRAMES}"
        assert (
            to.lower() in self._FRAMES
        ), f"Frame {to} not in {self._FRAMES}"
        self.home, self.to = home, to
        self.get_functions()

    def eval(self, date: datetime.datetime) -> np.ndarray:
        """Evaluates the frame transformation at a given time

        :param date: Date to evaluate [utc]
        :type date: datetime.datetime
        :return: DCM from home frame to target frame
        :rtype: np.ndarray [3x3]
        """
        dcm = np.eye(3)
        for f in self.fcns:
            dcm = dcm @ f(date)
        return dcm.T if self.transpose_flag else dcm

    def get_functions(self):
        """Gets the functions required to transform between the requested frames"""
        _FRAME_FCNS = [
            f"{self._FRAMES[i+1]}_to_{self._FRAMES[i]}"
            for i in range(len(self._FRAMES) - 1)
        ]
        _home_ind, _to_ind = self._FRAMES.index(
            self.home
        ), self._FRAMES.index(self.to)
        self.transpose_flag = _home_ind < _to_ind
        if (
            not self.transpose_flag
        ):  # Then we need to compute the reverse and transpose
            compose_fcns = [
                _FRAME_FCNS[i] for i in range(_to_ind, _home_ind)
            ]
        else:  # We can compute in order
            compose_fcns = [
                _FRAME_FCNS[i] for i in range(_home_ind, _to_ind)
            ]
        self.fcns = [globals()[f] for f in list(reversed(compose_fcns))]


def ecef_to_enu(enu_origin_in_ecef: np.ndarray) -> np.ndarray:
    """Rotation matrix from Earth-centered, Earth-fixed (ECEF) coordinates to East, North, Up (ENU) coordinates

    :param enu_origin_in_ecef: ENU origin point in ECEF coordinates [km]
    :type enu_origin_in_ecef: np.ndarray [1x3]
    :return: Rotation matrix at that ECEF point
    :rtype: np.ndarray [3x3]
    """
    local_up_ecef = hat(enu_origin_in_ecef).reshape((1, 3))
    local_north_ecef = (
        np.array([[0, 0, 1]])
        - dot(local_up_ecef, np.array([[0, 0, 1]])) * local_up_ecef
    )
    local_east_ecef = -np.cross(local_up_ecef, local_north_ecef)
    return np.vstack((local_east_ecef, local_north_ecef, local_up_ecef))


def enu_to_ecef(
    r_enu: np.ndarray, enu_origin_in_ecef: np.ndarray
) -> np.ndarray:
    """Transforms from local East, North, Up (ENU) coordinates to Earth-centered, Earth-fixed (ECEF) coordinates

    :param r_enu: Point in ENU coordinates [km]
    :type r_enu: np.ndarray [nx3]
    :param enu_origin_in_ecef: ECEF location of the origin to the local ENU coordinate system [km]
    :type enu_origin_in_ecef: np.ndarray [1x3]
    :return: Rotation matrix
    :rtype: np.ndarray [3x3]
    """
    rotm_to_enu = ecef_to_enu(enu_origin_in_ecef)
    enu_origin_enu = (
        rotm_to_enu @ enu_origin_in_ecef.reshape((3, 1))
    ).T
    r_enu_rel_earth_center = r_enu + enu_origin_enu
    r_ecef_rel_earth_center = (
        rotm_to_enu.T @ r_enu_rel_earth_center.T
    ).T
    return r_ecef_rel_earth_center


def lla_to_eci(
    lat_geod: float,
    lon: float,
    a: float,
    date: np.ndarray[datetime.datetime],
) -> np.ndarray:
    """Converts latitude, longitude, altitude (LLA) to Earth-centered inertial (ECI) coordinates

    :param lat_geod: Geodetic latitudes [rad]
    :type lat_geod: float
    :param lon: Longitudes [rad]
    :type lon: float
    :param a: Altitudes above the WGS84 ellipsoid [km]
    :type a: float
    :param date: Date to evaluate conversion [UTC]
    :type date: np.ndarray[datetime.datetime] [nx1]
    :return: ECI positions for each LLA triplet [km]
    :rtype:  np.ndarray [nx3]
    """
    r_itrf = lla_to_itrf(lat_geod, lon, a)
    date = np.array([date]).flatten()

    if date.size > 1:
        sidereal_rot = np.dstack([ecef_to_eci(d) for d in date])
        return stack_mat_mult(
            sidereal_rot, np.tile(r_itrf, (date.size, 1))
        )
    else:
        sidereal_rot = ecef_to_eci(date[0])
        return np.reshape(sidereal_rot @ r_itrf.T, (1, 3))


def lla_to_itrf(
    lat_geod: np.ndarray, lon: np.ndarray, a: np.ndarray
) -> np.ndarray:
    """Converts from latitude, longitude, altitude (LLA) to the International Terrestrial Reference Frame (ITRF)

    :param lat_geod: Geodetic latitudes [rad]
    :type lat_geod: np.ndarray [nx1]
    :param lon: Longitudes [rad]
    :type lon: np.ndarray [nx1]
    :param a: Altitudes above the WGS84 ellipsoid [km]
    :type a: np.ndarray [nx1]
    :return: ITRF positions for each LLA triplet [km]
    :rtype: np.array [nx3]
    """
    nrow = lat_geod.size if hasattr(lat_geod, "size") else 1
    lat_geoc = geodetic_lat_to_geocentric(lat_geod)
    # Transforms geodetic latitude into geocentric

    r_earth_at_lat = radius_at_geodetic_lat(lat_geod)
    # Computes the radius of the earth at the given geodetic latitude
    r_topo = r_earth_at_lat + a
    # Computes the altitude of the observer at this point [km]

    (x_itrf, y_itrf, z_itrf) = sph_to_cart(lon, lat_geoc, r_topo)
    return np.array((x_itrf, y_itrf, z_itrf)).reshape((3, nrow)).T


def enu_to_az_el(r_enu: np.ndarray) -> np.ndarray:
    (theta, phi, _) = cart_to_sph(r_enu[:, 0], r_enu[:, 1], r_enu[:, 2])
    return (wrap_to_two_pi(np.pi / 2 - theta), phi)


def az_el_to_enu(az: np.ndarray, el: np.ndarray):
    r_hat_enu = np.vstack(sph_to_cart(-az + np.pi / 2, el)).T
    return r_hat_enu
