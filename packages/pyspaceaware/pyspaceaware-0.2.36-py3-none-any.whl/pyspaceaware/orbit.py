import numpy as np
import scipy
import datetime
from typing import Callable, Tuple
from sgp4.api import Satrec, SatrecArray
import os

from .constants import AstroConstants
from .attitude import (
    axis_rotation_matrices,
    quat_kinematics,
    rigid_rotation_dynamics,
    quat_to_dcm,
)
from .coordinates import sun, ecef_to_eci
from .math import (
    acosd,
    atand,
    cosd,
    sind,
    stack_mat_mult,
    tand,
    wrap_to_360,
)
from .time import date_to_jd


def integrate_orbit_and_attitude(
    r0: np.ndarray,
    v0: np.ndarray,
    q0: np.ndarray,
    w0: np.ndarray,
    itensor: np.ndarray,
    teval: np.ndarray,
    orbit_perturbations: Callable = lambda t, y: np.zeros(3),
    external_torque: Callable = lambda t, y: np.zeros(3),
    internal_torque: Callable = lambda t, y: np.zeros(3),
    int_tol: float = 1e-13,
) -> np.ndarray:
    fun = lambda t, y: np.concatenate(
        (
            two_body_dynamics(y[0:6])
            + np.concatenate(
                ([0, 0, 0], orbit_perturbations(t, y[0:6]))
            ),
            np.concatenate(
                (
                    quat_kinematics(y[6:10], y[10:13]),
                    rigid_rotation_dynamics(
                        t,
                        y[10:13],
                        itensor,
                        lambda t: external_torque(
                            t, quat_to_dcm(y[6:10]).T @ y[0:3]
                        ),
                    ),
                )
            ),
        )
    )
    y0 = np.concatenate(
        (r0.flatten(), v0.flatten(), q0.flatten(), w0.flatten())
    )
    tspan = [np.min(teval), np.max(teval)]
    ode_res = scipy.integrate.solve_ivp(
        fun, tspan, y0, t_eval=teval, rtol=int_tol, atol=int_tol
    )
    ode_res = ode_res.y.T
    return (
        ode_res[:, 0:3],
        ode_res[:, 3:6],
        ode_res[:, 6:10],
        ode_res[:, 10:13],
    )


def integrate_orbit_dynamics(
    rv0: np.ndarray,
    perturbations: Callable,
    teval: np.ndarray,
    int_tol: float = 1e-13,
) -> np.ndarray:
    """Integration for orbital dynamics with perturbations

    :param rv0: Initial position and velocity state in Earth-centered inertial coordinates
    :type rv0: np.ndarray [1x6]
    :param perturbations: Accelerations applied to the body due to perturbing forces
    :type perturbations: Callable -> np.ndarray [1x6], [km/s^2]
    :param teval: Times to return integrated trajectory at [EpSec]
    :type teval: np.ndarray [nx1]
    :param int_tol: Integration rtol and atols for RK45, defaults to 1e-13
    :type int_tol: float, optional
    :return: Integrated orbit state in ECI in position and velocity
    :rtype: np.ndarray [nx3]
    """
    fun = lambda t, y: two_body_dynamics(y) + np.concatenate(
        ([0, 0, 0], perturbations(t, y))
    )
    tspan = [np.min(teval), np.max(teval)]
    ode_res = scipy.integrate.solve_ivp(
        fun, tspan, rv0, t_eval=teval, rtol=int_tol, atol=int_tol
    )
    return ode_res.y.T


def sun_acceleration(rv: np.ndarray, jd: np.ndarray) -> np.ndarray:
    """Approximate 3rd body acceleration due to the Sun

    :param rv: Position and velocity state in Earth-centered inertial coordinates
    :type rv: np.ndarray [nx3]
    :param jd: Julian date to evaluate at
    :type jd: np.ndarray [nx3]
    :return: Acceleration due to the sun [m/s^2]
    :rtype: np.ndarray [nx3]
    """
    earth_to_sun = sun(jd).flatten() * AstroConstants.au_to_km
    sat_to_sun = earth_to_sun - rv[0:3]
    return -AstroConstants.sun_mu * (
        earth_to_sun / np.linalg.norm(earth_to_sun) ** 3
        - sat_to_sun / np.linalg.norm(sat_to_sun) ** 3
    )


def two_body_dynamics(rv: np.ndarray) -> np.ndarray:
    """Relative two-body dynamics for orbits

    :param rv: Position [:3] [km] and velocity [3:] [km/s] of the satellite
    :type rv: np.ndarray [6,]
    :return: Time derivative of position and velocity states
    :rtype: np.ndarray [6,]
    """
    rvdot = np.empty(rv.shape)
    rvdot[:3] = rv[3:]
    rvdot[3:] = (
        -AstroConstants.earth_mu * rv[:3] / np.linalg.norm(rv[:3]) ** 3
    )
    return rvdot


def j2_acceleration(rvec: np.ndarray) -> np.ndarray:
    """Acceleration due to the J2 perturbation (Earth oblateness)

    :param rvec: Position vector of the satellite [km]
    :type rvec: np.ndarray [1x3]
    :return: Acceleration due to J2 [km/s^2]
    :rtype: np.ndarray [1x3]
    """
    re = AstroConstants.earth_r_eq
    mu = AstroConstants.earth_mu
    j2 = AstroConstants.earth_j2
    r = np.linalg.norm(rvec)
    (x_eci, y_eci, z_eci) = rvec  # ECI positions
    return (
        -3
        / 2
        * j2
        * (mu / r**2)
        * (re / r) ** 2
        * np.array(
            [
                (1 - 5 * (z_eci / r) ** 2) * x_eci / r,
                (1 - 5 * (z_eci / r) ** 2) * y_eci / r,
                (3 - 5 * (z_eci / r) ** 2) * z_eci / r,
            ]
        )
    )


def coe_to_rv(
    a: float,
    e: float,
    i: float,
    Om: float,
    om: float,
    ma: float,
    mu: float = AstroConstants.earth_mu,
) -> np.array:
    """Converts classical (Keplerian) orbital elements to position/velocity state

    :param a: Semi-major axis of the orbit [km]
    :type a: float
    :param e: Eccentricity
    :type e: float
    :param i: Inclination
    :type i: float
    :param Om: Right Ascension of the Ascending Node (RAAN) [deg]
    :type Om: float
    :param om: Argument of periapsis [deg]
    :type om: float
    :param ma: Mean anomaly [deg]
    :type ma: float
    :param mu: Gravitational parameter of central body, defaults to AstroConstants.earth_mu [km^3/s^2]
    :type mu: float, optional
    :return: ECI state vector in position/velocity
    :rtype: np.array [1x6]
    """
    efun = lambda ea: np.deg2rad(ma) - np.deg2rad(ea) + e * sind(ea)
    ea = scipy.optimize.fsolve(efun, ma)  # Eccentric anomaly
    ta = wrap_to_360(
        2 * atand(tand(ea / 2) * np.sqrt((1 + e) / (1 - e)))
    )  # True anomaly
    ta = float(ta)  # TODO: accept vector arguments
    p = a * (1 - e**2)  # Semi-latus rectum
    h = np.sqrt(p * mu)  # Angular momentum
    r = p / (1 + e * cosd(ta))  # Position magnitude
    v = np.sqrt(mu * (2 / r - 1 / a))  # Velocity magnitude
    isasc = 2 * (ta < 180) - 1  # 1 if asc, -1 if not
    y = isasc * acosd(
        h / (r * v)
    )  # Flight path angle above/below local horizon
    r_rth = r * np.array([1, 0, 0])  # Rotating frame position
    v_rth = v * np.array(
        [sind(y), cosd(y), 0]
    )  # Rotating frame velocity

    (R1, _, R3) = axis_rotation_matrices()  # Getting basic DCMs
    D_i2r = (
        R3(np.deg2rad(ta + om)) @ R1(np.deg2rad(i)) @ R3(np.deg2rad(Om))
    )
    # DCM from inertial to rotating frame
    r_i = np.transpose(D_i2r) @ r_rth  # Rotating rv to inertial space
    v_i = np.transpose(D_i2r) @ v_rth
    return (r_i, v_i)


def propagate_catalog_to_dates(
    dates: datetime.datetime, cat_preset: str = "all"
) -> Tuple[np.ndarray, np.ndarray]:
    """Propgates a satellite catalog to an array of dates

    :param dates: Array of datetimes [UTC]
    :type dates: datetime.datetime [nx1]
    :param cat_preset: Catalog preset, defaults to "all"
    :type cat_preset: str, optional
    :return: Position [km] and velocity [km/s] in TEME
    :rtype: Tuple[np.ndarray [nx3], np.ndarray [nx3]]
    """
    jds = np.array([date_to_jd(d) for d in dates])
    sats = []
    cat_path = os.path.join(
        os.environ["SRCDIR"], "tle", f"tle_latest_{cat_preset}.cat"
    )
    with open(cat_path, "r") as f:
        for i, line in enumerate(f):
            if not i % 2:
                s = line
            else:
                t = line
                sats.append(Satrec.twoline2rv(s, t))

    sat_coll = SatrecArray(sats)
    (jdays, jfracs) = np.modf(jds)
    e, r, v = sat_coll.sgp4(jdays, jfracs)
    return (r, v)


def propagate_satnum_to_dates(
    dates: datetime.datetime, satnum: int, target_frame: str = "teme"
) -> Tuple[np.ndarray, np.ndarray]:
    """Propagates a satellite number to the given UTC datetimes

    :param dates: Array of datetimes [UTC]
    :type dates: datetime.datetime [nx1]
    :param satnum: NORAD satellite number
    :type satnum: int
    :param target_frame: Reference frame to propagate in, defaults to "teme"
    :type target_frame: str, optional
    :return: Position [km] and velocity [km/s] in the target reference frame
    :rtype: Tuple[np.ndarray [nx3], np.ndarray [nx3]]
    """
    jds = date_to_jd(dates)
    (jdays, jfracs) = np.modf(jds)
    cat_path = os.path.join(
        os.environ["SRCDIR"], "tle", "tle_latest_all.cat"
    )
    with open(cat_path, "r") as f:
        for i, line in enumerate(f):
            if not i % 2:
                s = line
            else:
                t = line
                sr = Satrec.twoline2rv(s, t)
                if sr.satnum == satnum:
                    _, r_teme, v_teme = sr.sgp4_array(jdays, jfracs)
                    break

    if target_frame == "teme":
        return (r_teme, v_teme)
    elif target_frame == "ecef":
        rot = np.dstack([ecef_to_eci(d).T for d in dates])

    r_rot = stack_mat_mult(rot, r_teme)
    v_rot = stack_mat_mult(rot, v_teme)
    return (r_rot, v_rot)
