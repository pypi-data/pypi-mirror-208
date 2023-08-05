import numpy as np
import scipy
from typing import Tuple
import datetime
import os
import pickle

from .math import (
    hat,
    dot,
    stack_mat_mult,
    dms_to_rad,
    vecnorm,
)
from .time import date_to_jd
from .coordinates import sun, moon, eci_to_sun_ec
from .constants import AstroConstants
from .lighting import apparent_magnitude_to_irradiance
from .math import sph_to_cart

_PROOF_RAW_SIGNAL_FACTOR = 23
_PROOF_MOON_FACTOR = 11.4
_PROOF_ZODIAC_FACTOR = 7.8
_STAR_CAT_DIR = os.path.join(os.environ["SRCDIR"], "resources", "data")


def sun_spectrum(lambdas: np.ndarray) -> np.ndarray:
    spec = np.loadtxt(
        os.path.join(
            os.environ["SRCDIR"],
            "resources",
            "data",
            "proof.sun",
        )
    )  # spec[0,:] in um, spec[:,1] in W/cm^2/um
    f = scipy.interpolate.interp1d(
        x=spec[:, 0] * 1e-6,
        y=spec[:, 1] * 1e10,
        fill_value=(0, 0),
        bounds_error=False,
        kind="linear",
    )
    return f(lambdas)


def proof_zero_mag_stellar_spectrum(lambdas: np.ndarray) -> np.ndarray:
    spec = np.loadtxt(
        os.path.join(
            os.environ["SRCDIR"],
            "resources",
            "data",
            "proof.ssz",
        )
    )  # spec[0,:] in um, spec[:,1] in W/cm^2/um
    f = scipy.interpolate.interp1d(
        x=spec[:, 0] * 1e-6,
        y=spec[:, 1] * 1e10,
        fill_value=(0, 0),
        bounds_error=False,
        kind="linear",
    )
    return f(lambdas)


def _zodiacal_light_signal(
    ecliptic_lat: np.ndarray,
    ecliptic_lon: np.ndarray,
    z_obs: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_gound_based: bool,
) -> np.ndarray:
    """Computes signal in CCD due to zodiacal light

    :param ecliptic_lat: Ecliptic latitude of observation [rad]
    :type ecliptic_lat: np.ndarray
    :param ecliptic_lon: Ecliptic longitude of observation [rad]
    :type ecliptic_lon: np.ndarray
    :param z_obs: Zenith angle of observation [rad]
    :type z_obs: np.ndarray
    :param t_int: Integration time [second]
    :type t_int: float
    :param scale: FOV per pixel (pixel scale) [arcsec]
    :type scale: float
    :param d: Diameter of aperture [m]
    :type d: float
    :return: Zodiacal light signal [e-/pixel]
    :rtype: np.ndarray
    """
    f_zod = _zodiacal_light(ecliptic_lat, ecliptic_lon)
    bint = (
        _zero_magnitude_signal(
            d=d, z_obs=z_obs, is_ground_based=is_gound_based
        )
        * _PROOF_ZODIAC_FACTOR
    )
    s_zod = (
        np.rad2deg(dms_to_rad(0, 0, scale)) ** 2
        * bint
        * t_int
        * f_zod
        * 1e-4
    )
    return s_zod


def moonlight_signal(
    dates: np.ndarray[datetime.datetime],
    look_dirs_eci_eq: np.ndarray,
    obs_pos_eci_eq: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_ground_based: bool = True,
) -> np.ndarray:
    """Mean signal on image background due to scattered moonlight

    :param dates: Dates to evaluate brightnesss at [utc]
    :type dates: np.ndarray[datetime.datetime]
    :param look_dirs_eci_eq: Look unit vectors in ecliptic Earth-centered inertial (ECI)
    :type look_dirs_eci_eq: np.ndarray
    :param obs_pos_eci_eq: Observer positions in ecliptic Earth-centered inertial (ECI) [km]
    :type obs_pos_eci_eq: np.ndarray
    :param t_int: Signal integration time [second]
    :type t_int: float
    :param scale: Pixel scale of CCD sensor [arcsec]
    :type scale: float
    :param d: Diameter of primary optics aperture
    :type d: float
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: Background signal due to moonlight [e-/pix]
    :rtype: np.ndarray
    """
    if not is_ground_based:
        return 0  # No atmosphere to scatter through
    zenith = hat(obs_pos_eci_eq)
    z_obs = np.arccos(dot(zenith, hat(look_dirs_eci_eq)))
    mv = moon(date_to_jd(dates))
    sv = sun(date_to_jd(dates))
    moon_to_obs = obs_pos_eci_eq - mv
    moon_to_sun = sv - mv
    obs_to_moon = -moon_to_obs
    phase_angle_moon = np.arccos(
        dot(hat(moon_to_sun), hat(moon_to_obs))
    )
    z_moon = np.arccos(dot(zenith, hat(obs_to_moon)))

    look_dir_on_horizon = (
        look_dirs_eci_eq - dot(look_dirs_eci_eq, zenith) * zenith
    )
    moon_on_horizon = mv - dot(mv, zenith) * hat(obs_pos_eci_eq)
    delta_az = np.arccos(
        dot(hat(look_dir_on_horizon), hat(moon_on_horizon))
    )

    sm = _moonlight_signal(
        phase_angle_moon=phase_angle_moon.flatten(),
        z_moon=z_moon.flatten(),
        z_obs=z_obs.flatten(),
        delta_az=delta_az.flatten(),
        t_int=t_int,
        scale=scale,
        d=d,
        is_ground_based=is_ground_based,
    )

    return sm


def _moonlight_signal(
    phase_angle_moon: np.ndarray,
    z_moon: np.ndarray,
    z_obs: np.ndarray,
    delta_az: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_ground_based: bool = True,
) -> np.ndarray:
    """Signal on CCD sensor due to moonlight

    :param phase_angle_moon: Angle between Earth and Sun as seen from the Moon
    :type phase_angle_moon: np.ndarray
    :param z_moon: Zenith angle of the Moon at the observer [rad]
    :type z_moon: np.ndarray
    :param z_obs: Zenith angle of the observation [rad]
    :type z_obs: np.ndarray
    :param delta_az: Difference in azimuth between Moon and observation [rad]
    :type delta_az: np.ndarray
    :param t_int: integration time [second]
    :type t_int: float
    :param scale: FOV per pixel [arcsec]
    :type scale: float
    :param d: Diameter of aperture [m]
    :type d: float
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: Signal on CCD [e-/pixel]
    :rtype: np.ndarray
    """
    f_mt = _moon_brightness(phase_angle_moon, z_moon, z_obs, delta_az)
    sint = (
        _raw_signal(
            d, z_obs, mode="sint", is_ground_based=is_ground_based
        )
        * _PROOF_MOON_FACTOR
    )
    f_corr = AstroConstants.sun_irradiance_vacuum / sun_spectrum(550e-9)
    return sint * dms_to_rad(0, 0, scale) ** 2 * f_corr * f_mt * t_int


def _zero_magnitude_signal(
    d: float,
    z_obs: np.ndarray,
    lambda_lims: Tuple[float] = (1e-8, 1e-6),
    is_ground_based: bool = True,
) -> np.ndarray:
    """Computes CCD response per second for a zero-magnitude star

    :param d: Diameter of aperture [m]
    :type d: float
    :param z_obs: Zenith angle of observation [rad]
    :type z_obs: np.ndarray
    :param lambda_lims: Wavelength integration limits [m], defaults to (1e-8, 1e-6)
    :type lambda_lims: Tuple[float], optional
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: Expected CCD response due to a zero-magnitude star [count/second]
    :rtype: np.ndarray
    """
    lambdas = np.linspace(lambda_lims[0], lambda_lims[1], int(1e2))
    (gz, gl) = np.meshgrid(z_obs, lambdas)
    strint = proof_zero_mag_stellar_spectrum(
        gl
    )  # Approximately same as STRINT TODO: cite Krag thesis
    atmos_trans = _atmospheric_transmission(lambdas=gl, zenith_angle=gz)
    qe = _quantum_efficiency(gl)
    if is_ground_based:
        integrand_num = strint * atmos_trans * qe * gl
    else:
        integrand_num = strint * qe * gl
    denom = (
        AstroConstants.planck_constant
        * AstroConstants.speed_of_light_vacuum
    )
    integral = np.trapz(integrand_num, gl, axis=0)
    bint = np.pi / 4 * d**2 * integral / denom
    return bint


def _raw_signal(
    d: float,
    z_obs: np.ndarray,
    mode: str,
    lambda_lims: Tuple = (1e-8, 1e-6),
    is_ground_based: bool = True,
) -> np.ndarray:
    """Computes raw signals for background model TODO: cite Krag thesis

    :param d: Diameter of telescope aperture [m]
    :type d: float
    :param z_obs: Zenith angle of observation [rad]
    :type z_obs: np.ndarray
    :param mode: Signal to compute, either "aint" for airglow or "sint" for the object signal
    :type mode: str
    :param lambda_lims: Wavelength limits to integrate over [m], defaults to (1e-8, 1e-6)
    :type lambda_lims: Tuple, optional
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: Raw signal, if `mode="sint"` [m^2/(Ws)], if `mode="aint"` [1/s/sterad]
    :rtype: np.ndarray
    """
    lambdas = np.linspace(lambda_lims[0], lambda_lims[1], int(1e2))
    (gz, gl) = np.meshgrid(z_obs, lambdas)
    atmos_trans = (
        _atmospheric_transmission(lambdas=gl, zenith_angle=gz)
        if is_ground_based
        else 1
    )
    qe = _quantum_efficiency(gl)
    if mode == "sint":
        sun_spec = sun_spectrum(gl)
        integrand_num = (
            sun_spec * atmos_trans * qe * gl * _PROOF_RAW_SIGNAL_FACTOR
        )
        denom = (
            AstroConstants.planck_constant
            * AstroConstants.sun_irradiance_vacuum
            * AstroConstants.speed_of_light_vacuum
        )
    if mode == "aint":
        airglow_spec = _airglow_radiance(gl)
        integrand_num = (
            airglow_spec
            * atmos_trans
            * qe
            * gl
            * _PROOF_RAW_SIGNAL_FACTOR
        )
        denom = (
            AstroConstants.planck_constant
            * AstroConstants.speed_of_light_vacuum
        )
    integral = np.trapz(integrand_num, gl, axis=0)
    signal = np.pi / 4 * d**2 * integral / denom
    return signal


def _atmospheric_transmission(
    lambdas: np.ndarray,
    zenith_angle: np.ndarray,
    terrain_elev: float = 0.1,
) -> np.ndarray:
    """Calculates atmospheric transmission fraction as described in TODO: cite Krag thesis

    :param lambdas: Wavelengths to sample [m]
    :type lambdas: np.ndarray
    :param zenith_angle: Angle from point of interest to local zenith [rad]
    :type zenith_angle: np.ndarray
    :param terrain_elev: Elevation to stop at to avoid numerical errors in the Van Rijhn factor [rad]
    :type terrain_elev: float
    :return: Atmospheric transimssion fraction [nondim]
    :rtype: np.ndarray
    """
    atmos_transmission = np.zeros_like(lambdas)
    calc_zeniths = zenith_angle < (
        np.pi / 2 - terrain_elev
    )  # Don't calculate if below terrain height
    atmos_transmission[calc_zeniths] = np.exp(
        -_atmospheric_extinction(lambdas[calc_zeniths])
        / np.cos(zenith_angle[calc_zeniths])
    )
    return atmos_transmission


def _quantum_efficiency(lambdas: np.ndarray) -> np.ndarray:
    """Computes quantum efficiency for a representative CCD sensor TODO: cite Krag thesis

    :param lambdas: Sample wavelengths [m]
    :type lambdas: np.ndarray
    :return: Quantum efficiency [electrons/photon]
    :rtype: np.ndarray
    """
    data_lambda = np.arange(400, 1051, 50) * 1e-9  # [m]
    data_qe = np.array(
        [
            0,
            0.05,
            0.12,
            0.17,
            0.23,
            0.3,
            0.36,
            0.34,
            0.3,
            0.26,
            0.2,
            0.12,
            0.04,
            0,
        ]
    )
    f_qe = scipy.interpolate.interp1d(
        data_lambda,
        data_qe,
        kind="linear",
        bounds_error=False,
        fill_value=(0, 0),
    )
    return f_qe(lambdas)


def _atmospheric_extinction(lambdas: np.ndarray) -> np.ndarray:
    """Calculates atmospheric extinction coefficient as described in TODO: cite Krag thesis

    :param lambdas: Wavelengths to sample [m]
    :type lambdas: np.ndarray
    :return: Atmospheric extinction coefficient [nondim]
    :rtype: np.ndarray
    """
    data_lambda = 1e-6 * np.array(
        [
            0,
            0.32,
            0.34,
            0.36,
            0.38,
            0.40,
            0.45,
            0.50,
            0.55,
            0.60,
            0.65,
            0.70,
            0.80,
            1000,
        ]
    )
    data_ext = np.array(
        [
            5,
            0.96,
            0.54,
            0.42,
            0.34,
            0.27,
            0.17,
            0.13,
            0.11,
            0.11,
            0.07,
            0.05,
            0.03,
            0.0,
        ]
    )
    f = scipy.interpolate.interp1d(
        data_lambda,
        data_ext,
        kind="linear",
        bounds_error=False,
        fill_value=(5, 0),
    )
    # 5 added by me as data_ext[0] to get exponential falloff similar to TODO: Krag thesis
    return f(lambdas)


def _zodiacal_light(
    ecliptic_lat: np.ndarray, ecliptic_lon: np.ndarray
) -> np.ndarray:
    """Computes zodiacal light at a given ecliptic latitude and longitude

    :param ecliptic_lat: Latitude of observation in ecliptic ECI coordinates [rad]
    :type ecliptic_lat: np.ndarray
    :param ecliptic_lon: Longitude of observation in ecliptic ECI coordinates [rad]
    :type ecliptic_lon: np.ndarray
    :return: Zodiacal light in units :math:`S^10`, defined as "The equivalent number of tenth magnitude (visual) stars of solar spectral type per square degree." [`source <https://link.springer.com/chapter/10.1007/3-540-07615-8_450>`_]
    :rtype: np.ndarray
    """
    data_values = (
        1e2
        * np.array(
            [
                [2.58, 2.12, 1.83, 1.59, 1.41, 1.27, 1.17, 1.10, 1.03],
                [2.11, 1.94, 1.74, 1.53, 1.37, 1.27, 1.20, 1.12, 1.05],
                [2.07, 1.85, 1.68, 1.52, 1.37, 1.28, 1.20, 1.12, 1.05],
                [2.39, 2.17, 1.96, 1.77, 1.61, 1.46, 1.32, 1.20, 1.08],
                [2.77, 2.47, 2.20, 1.96, 1.75, 1.56, 1.39, 1.23, 1.11],
                [3.65, 3.12, 2.58, 2.19, 1.90, 1.66, 1.46, 1.27, 1.11],
                [5.35, 4.18, 3.30, 2.58, 2.04, 1.65, 1.37, 1.18, 1.06],
                [6.30, 4.55, 3.39, 2.70, 2.12, 1.66, 1.37, 1.20, 1.07],
                [7.56, 5.12, 3.58, 2.82, 2.29, 1.83, 1.47, 1.24, 1.07],
                [9.39, 6.03, 4.03, 2.90, 2.27, 1.85, 1.49, 1.24, 1.08],
                [
                    1.19e1,
                    6.96,
                    4.42,
                    3.04,
                    2.33,
                    1.89,
                    1.50,
                    1.24,
                    1.07,
                ],
                [
                    1.49e1,
                    8.25,
                    5.12,
                    3.31,
                    2.40,
                    1.86,
                    1.49,
                    1.26,
                    1.11,
                ],
                [
                    2.01e1,
                    1.15e1,
                    6.35,
                    3.63,
                    2.24,
                    1.71,
                    1.37,
                    1.18,
                    1.07,
                ],
                [
                    2.94e1,
                    1.55e1,
                    8.00,
                    4.17,
                    2.41,
                    1.80,
                    1.41,
                    1.20,
                    1.06,
                ],
                [
                    4.66e1,
                    1.82e1,
                    9.32,
                    4.91,
                    2.46,
                    1.83,
                    1.44,
                    1.21,
                    1.08,
                ],
                [
                    7.69e1,
                    2.14e1,
                    1.07e1,
                    5.42,
                    2.52,
                    1.86,
                    1.45,
                    1.21,
                    1.08,
                ],
                [
                    1.51e2,
                    2.76e1,
                    1.12e1,
                    5.92,
                    2.65,
                    1.90,
                    1.45,
                    1.21,
                    1.08,
                ],
                [
                    3.65e2,
                    2.72e1,
                    1.39e1,
                    6.55,
                    2.90,
                    1.99,
                    1.45,
                    1.21,
                    1.08,
                ],
                [
                    1.76e3,
                    5.63e1,
                    1.70e1,
                    7.24,
                    3.15,
                    2.09,
                    1.46,
                    1.21,
                    1.08,
                ],
                [
                    1.63e6,
                    1.99e2,
                    2.29e1,
                    7.94,
                    4.03,
                    2.52,
                    1.50,
                    1.21,
                    1.08,
                ],
            ]
        ).T
    )
    data_ecliptic_lat = np.deg2rad(np.arange(0, 81, 10))
    data_ecliptic_lon = np.deg2rad(
        np.array(
            [
                180,
                160,
                140,
                120,
                100,
                80,
                65,
                60,
                55,
                50,
                45,
                40,
                35,
                30,
                25,
                20,
                15,
                10,
                5,
                0,
            ]
        )
    )
    return scipy.interpolate.interpn(
        points=(data_ecliptic_lat, data_ecliptic_lon),
        values=data_values,
        xi=(np.abs(ecliptic_lat), np.abs(ecliptic_lon)),
        method="linear",
        fill_value=100 * 0.98,
        bounds_error=False,
    )


def _moon_mie_scattering(
    z_moon: np.ndarray, z_obs: np.ndarray, delta_az: np.ndarray
) -> np.ndarray:
    """Computes Mie scattered moonlight

    :param z_moon: Angle from zenith for the Moon from the observer [rad]
    :type z_moon: np.ndarray
    :param z_obs: Angle of the observation from zenith [rad]
    :type z_obs: np.ndarray
    :param delta_az: Angle on horizon between the observation and Moon [rad]
    :type delta_az: np.ndarray
    :return: Mie scattered light radiance :math:`[10^{-10}W/(cm^2\cdot steradian \cdot \mu m)]`
    :rtype: np.ndarray
    """
    psi1, psi2 = np.deg2rad(15), np.deg2rad(50)
    f_rs = _moon_rayleigh_scattering(z_moon, z_obs, delta_az)
    psi = np.arccos(
        np.cos(z_moon) * np.cos(z_obs)
        + np.sin(z_moon) * np.sin(z_obs) * np.cos(delta_az)
    )
    # Angle between moon and observation directions
    f_ms = (
        75
        * (np.exp(-psi / psi1) + 0.015 * np.exp(-(np.pi - psi) / psi2))
        * f_rs
    )
    return f_ms


def _moon_rayleigh_scattering(
    z_moon: np.ndarray, z_obs: np.ndarray, delta_az: np.ndarray
) -> np.ndarray:
    """Computes Rayleigh scattered moonlight

    :param z_moon: Angle from zenith for the Moon from the observer [rad]
    :type z_moon: np.ndarray
    :param z_obs: Angle of the observation from zenith [rad]
    :type z_obs: np.ndarray
    :param delta_az: Angle on horizon between the observation and Moon [rad]
    :type delta_az: np.ndarray
    :return: Brightness of the Moon due to Rayleigh scattering :math:`[10^{-10}W/(cm^2\cdot ster \cdot \mu m)] = [W/(m \cdot ster \cdot m)]`
    :rtype: np.ndarray
    """
    data_radiance_z_moon0 = np.array(
        [
            [22, 22, 22, 22, 22],
            [22, 22, 22, 22, 22],
            [22, 22, 22, 22, 22],
            [22, 22, 22, 22, 22],
            [23, 23, 23, 23, 23],
            [24, 24, 24, 24, 24],
            [27, 27, 27, 27, 27],
            [34, 34, 34, 34, 34],
            [55, 55, 55, 55, 58],
        ]
    )

    data_radiance_z_moon30 = np.array(
        [
            [19, 19, 19, 19, 19],
            [21, 20, 19, 18, 18],
            [23, 22, 19, 17, 17],
            [25, 23, 20, 17, 16],
            [28, 25, 21, 17, 16],
            [31, 28, 22, 18, 18],
            [37, 33, 25, 22, 22],
            [47, 41, 33, 30, 31],
            [72, 65, 54, 54, 58],
        ]
    )

    data_radiance_z_moon60 = np.array(
        [
            [13, 13, 13, 13, 13],
            [15, 14, 13, 12, 12],
            [18, 16, 14, 12, 12],
            [21, 18, 14, 12, 12],
            [25, 21, 16, 14, 14],
            [31, 26, 18, 17, 18],
            [39, 32, 22, 22, 25],
            [54, 43, 29, 33, 40],
            [89, 71, 50, 61, 76],
        ]
    )

    data_radiance_z_moon75 = np.array(
        [
            [10, 10, 10, 10, 10],
            [11, 11, 10, 9.7, 9.6],
            [13, 12, 10, 9.9, 10],
            [16, 14, 11, 11, 11],
            [20, 17, 12, 13, 14],
            [25, 20, 15, 16, 18],
            [33, 26, 18, 21, 26],
            [48, 37, 25, 32, 40],
            [82, 63, 43, 58, 75],
        ]
    )
    data_radiance = np.dstack(
        (
            data_radiance_z_moon0,
            data_radiance_z_moon30,
            data_radiance_z_moon60,
            data_radiance_z_moon75,
        )
    )

    data_z_obs = np.deg2rad(
        np.arange(0, 81, 10)
    )  # Obseravtion angle from zenith, [rad]
    data_delta_az = np.deg2rad(
        np.arange(0, 181, 45)
    )  # Relative azimuth difference between moon and observation [rad]
    data_z_moon = np.deg2rad(
        np.array([0, 30, 60, 75])
    )  # Zenith angle of the mooon [rad]
    return scipy.interpolate.interpn(
        points=(data_z_obs, data_delta_az, data_z_moon),
        values=data_radiance,
        xi=(z_obs, delta_az, z_moon),
        bounds_error=False,
        fill_value=0,
        method="linear",
    )


def _moon_phase_fraction(moon_phase_angle: np.ndarray) -> np.ndarray:
    """Computes the brightness fraction at a given lunar phase angle
    :param moon_phase_angle: Angle between Earth and Sun from the perspective of the Moon [rad]
    :type moon_phase_angle: np.ndarray
    :return: Fraction of full Moon radiance at observer [nondim]
    :rtype: np.ndarray
    """
    data_lunar_phase = np.deg2rad(np.arange(0, 181, 10))
    data_normalized_brightness = np.array(
        [
            1.00,
            0.809,
            0.685,
            0.483,
            0.377,
            0.288,
            0.225,
            0.172,
            0.127,
            0.089,
            0.061,
            0.041,
            0.077,
            0.017,
            0.009,
            0.004,
            0.001,
            0.0,
            0.0,
        ]
    )

    f = scipy.interpolate.interp1d(
        data_lunar_phase, data_normalized_brightness, kind="linear"
    )
    return f(moon_phase_angle)


def _moon_brightness(
    phase_angle_moon: np.ndarray,
    z_moon: np.ndarray,
    z_obs: np.ndarray,
    delta_az: np.ndarray,
) -> np.ndarray:
    """Computes the brightness of the moon in given observation conditions

    :param phase_angle_moon: Angle between Sun and Earth from the perspective of the Moon [rad]
    :type phase_angle_moon: np.ndarray
    :param z_moon: Angle from zenith for the Moon from the observer [rad]
    :type z_moon: np.ndarray
    :param z_obs: Angle of the observation from zenith [rad]
    :type z_obs: np.ndarray
    :param delta_az: Angle on horizon between the observation and Moon [rad]
    :type delta_az: np.ndarray
    :return: Brightness of the Moon in :math:`[10^{-10}W/(cm^2\cdot steradian \cdot \mu m)]
    :rtype: np.ndarray
    """
    f_theta = _moon_phase_fraction(phase_angle_moon)
    f_rs = _moon_rayleigh_scattering(z_moon, z_obs, delta_az)
    f_ms = _moon_mie_scattering(z_moon, z_obs, delta_az)
    f_mt = f_theta * (f_ms + f_rs)
    return f_mt


def equatorial_dir_to_ecliptic_azel(
    dates: np.ndarray[datetime.datetime], look_dirs_eci_eq: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    eq_to_ec = eci_to_sun_ec(dates)
    look_dirs_eci_ec = stack_mat_mult(eq_to_ec, look_dirs_eci_eq)
    ec_az = np.arctan2(look_dirs_eci_ec[:, 1], look_dirs_eci_ec[:, 0])
    ec_el = np.arctan2(
        look_dirs_eci_ec[:, 2],
        vecnorm(look_dirs_eci_ec[:, :2]).flatten(),
    )
    return (ec_az, ec_el)


def zodiacal_signal(
    dates: np.ndarray[datetime.datetime],
    look_dirs_eci_eq: np.ndarray,
    obs_pos_eci_eq: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_ground_based: bool = True,
) -> np.ndarray:
    """_summary_

    :param dates: _description_
    :type dates: np.ndarray[datetime.datetime]
    :param look_dirs_eci_eq: _description_
    :type look_dirs_eci_eq: np.ndarray
    :param obs_pos_eci_eq: _description_
    :type obs_pos_eci_eq: np.ndarray
    :param t_int: _description_
    :type t_int: float
    :param scale: _description_
    :type scale: float
    :param d: _description_
    :type d: float
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: _description_
    :rtype: np.ndarray
    """
    z_obs = np.arccos(dot(hat(obs_pos_eci_eq), hat(look_dirs_eci_eq)))
    (ec_az, ec_el) = equatorial_dir_to_ecliptic_azel(
        dates, look_dirs_eci_eq
    )
    return _zodiacal_light_signal(
        ec_el, ec_az, z_obs, t_int, scale, d, is_ground_based
    )


def _save_patched_catalog(vmag_limit: int = 10) -> None:
    """Saves a patched star catalog generated for a given visual magnitude limit using the Tycho 2 star catalog

    :param vmag_limit: Brightest magnitude to integrate into patched catalog
    :type vmag_limit: int, defaults to 10
    """
    fpath = os.path.join(
        _STAR_CAT_DIR, f"m0_patched_v_geq_{vmag_limit}.pkl"
    )
    if os.path.exists(fpath):
        return
    t2 = scipy.io.loadmat(
        os.path.join(
            os.environ["SRCDIR"],
            "resources",
            "data",
            "Tycho_2_fullcatalog.mat",
        )
    )
    tycho2 = t2["Tycho2_full"][0][0]
    starxyz = tycho2[0].T
    vmag = tycho2[-1].T
    irrads = apparent_magnitude_to_irradiance(vmag)

    az_range, el_range = np.arange(360), np.arange(-90, 90)
    (g_az, g_el) = np.meshgrid(
        az_range,
        el_range,
    )
    look_eci = np.vstack(
        sph_to_cart(
            np.deg2rad(g_az.flatten()), np.deg2rad(g_el.flatten())
        )
    ).T
    star_kdt = scipy.spatial.KDTree(
        data=starxyz[vmag.flatten() > vmag_limit, :]
    )

    m0_per_deg2 = np.zeros_like(look_eci[:, [0]])
    irrad_of_m0 = apparent_magnitude_to_irradiance(0)
    kdt_stars = star_kdt.query_ball_point(look_eci, np.pi / 180)
    m0_per_deg2 = (
        np.array([np.sum(irrads[irs]) for irs in kdt_stars])
        / irrad_of_m0
    )
    m0_per_deg2 = m0_per_deg2.reshape((180, 360), order="C")
    cat_dict = {
        "az_data": az_range,
        "el_data": el_range,
        "m0_per_deg2": m0_per_deg2,
        "look_eci": look_eci,
        "vmag_limit": vmag_limit,
    }
    cat_dict_list = {
        k: (v if v is not np.ndarray else v.tolist())
        for k, v in cat_dict.items()
    }
    with open(fpath, "wb") as f:
        pickle.dump(cat_dict_list, f)


def load_patched_catalog(vmag_limit: int) -> dict:
    """Loads a patched star catalog generated for a given visual magnitude limit

    :param vmag_limit: Brightest magnitude to integrate into patched catalog
    :type vmag_limit: int
    :return: Catalog dictionary
    :rtype: dict
    """
    fpath = os.path.join(
        _STAR_CAT_DIR, f"m0_patched_v_geq_{vmag_limit}.pkl"
    )
    with open(fpath, "rb") as f:
        cat_dict = pickle.load(f)
    return {
        k: (v if v is not list else np.array(v))
        for k, v in cat_dict.items()
    }


def _catalog_starlight_signal(
    ecliptic_lat: np.ndarray, ecliptic_lon: np.ndarray
) -> np.ndarray:
    vmag_limit = 10
    _save_patched_catalog(vmag_limit)
    cat = load_patched_catalog(vmag_limit)
    return scipy.interpolate.interpn(
        points=(np.deg2rad(cat["el_data"]), np.deg2rad(cat["az_data"])),
        values=cat["m0_per_deg2"],
        xi=(ecliptic_lat, ecliptic_lon),
        method="linear",
        fill_value=0,
        bounds_error=False,
    )


def integrated_starlight_signal(
    dates: np.ndarray[datetime.datetime],
    look_dirs_eci_eq: np.ndarray,
    obs_pos_eci_eq: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_ground_based: bool = True,
) -> np.ndarray:
    z_obs = np.arccos(dot(hat(obs_pos_eci_eq), hat(look_dirs_eci_eq)))
    (ec_az, ec_el) = equatorial_dir_to_ecliptic_azel(
        dates, look_dirs_eci_eq
    )
    ec_az += np.pi
    return _integrated_starlight_signal(
        ecliptic_lat=ec_el,
        ecliptic_lon=ec_az,
        z_obs=z_obs,
        t_int=t_int,
        scale=scale,
        d=d,
        is_ground_based=is_ground_based,
    )


def _integrated_starlight_signal(
    ecliptic_lat: np.ndarray,
    ecliptic_lon: np.ndarray,
    z_obs: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_ground_based: bool = True,
) -> np.ndarray:
    """Computes signal in CCD due to integrated starlight

    :param ecliptic_lat: Ecliptic latitude of observation [rad]
    :type ecliptic_lat: np.ndarray
    :param ecliptic_lon: Ecliptic longitude of observation [rad]
    :type ecliptic_lon: np.ndarray
    :param z_obs: Zenith angle of observation [rad]
    :type z_obs: np.ndarray
    :param t_int: Integration time [second]
    :type t_int: float
    :param scale: FOV per pixel (pixel scale) [arcsec]
    :type scale: float
    :param d: Diameter of aperture [m]
    :type d: float
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: Starlight signal [e-/pixel]
    :rtype: np.ndarray
    """
    f_star = _catalog_starlight_signal(
        ecliptic_lat, ecliptic_lon
    )  # Units [0th magnitude stars / deg^2]
    bint = _zero_magnitude_signal(
        d=d, z_obs=z_obs, is_ground_based=is_ground_based
    )
    s_star = (
        np.rad2deg(dms_to_rad(0, 0, scale)) ** 2 * bint * t_int * f_star
    )
    return s_star


def _airglow_radiance(lambdas: np.ndarray) -> np.ndarray:
    """Computes spectral radiances due to airglow TODO: cite [73]

    :param lambdas: Wavelengths to interpolate [m]
    :type lambdas: np.ndarray
    :return: Spectral radiances [W/m^2/m/ster]
    :rtype: np.ndarray
    """
    lambda_data = np.arange(0.32, 0.81, 0.02) * 1e-6
    zenith_airglow_radiance_data = np.array(
        [
            2.50,
            2.50,
            1.50,
            1.00,
            0.20,
            0.46,
            0.54,
            0.62,
            0.69,
            0.82,
            0.94,
            0.94,
            4.30,
            1.90,
            1.80,
            3.20,
            3.10,
            0.94,
            0.41,
            0.89,
            6.00,
            0.84,
            3.90,
            4.90,
            10.0,
        ]
    )
    f = scipy.interpolate.interp1d(
        x=lambda_data,
        y=zenith_airglow_radiance_data,
        kind="linear",
        fill_value=0,
        bounds_error=False,
    )
    return f(lambdas)


def airglow_signal(
    look_dirs_eci_eq: np.ndarray,
    obs_pos_eci_eq: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_ground_based: bool = True,
) -> np.ndarray:
    """Signal on CCD sensor due to airglow

    :param look_dirs_eci_eq: Look unit vectors in ecliptic Earth-centered inertial (ECI)
    :type look_dirs_eci_eq: np.ndarray
    :param obs_pos_eci_eq: Observer positions in ecliptic Earth-centered inertial (ECI) [km]
    :type obs_pos_eci_eq: np.ndarray
    :param t_int: integration time [second]
    :type t_int: float
    :param scale: FOV per pixel [arcsec]
    :type scale: float
    :param d: Diameter of aperture [m]
    :type d: float
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: Signal on CCD [e-/pixel]
    :rtype: np.ndarray
    """
    if not is_ground_based:
        return 0  # No atmosphere to scatter through
    z_obs = np.arccos(
        dot(look_dirs_eci_eq, hat(obs_pos_eci_eq))
    ).flatten()
    aint = _raw_signal(
        d, z_obs, mode="aint", is_ground_based=is_ground_based
    )
    f_van_rhijn = 1 / np.cos(z_obs)
    return aint * dms_to_rad(0, 0, scale) ** 2 * t_int * f_van_rhijn


def atmospherically_scattered_signal(
    look_dirs_eci_eq: np.ndarray,
    obs_pos_eci_eq: np.ndarray,
    t_int: float,
    scale: float,
    d: float,
    is_ground_based: bool = True,
) -> np.ndarray:
    """Signal on CCD sensor due to atmospherically scattered light (not from Sun or Moon)

    :param look_dirs_eci_eq: Look unit vectors in ecliptic Earth-centered inertial (ECI)
    :type look_dirs_eci_eq: np.ndarray
    :param obs_pos_eci_eq: Observer positions in ecliptic Earth-centered inertial (ECI) [km]
    :type obs_pos_eci_eq: np.ndarray
    :param t_int: integration time [second]
    :type t_int: float
    :param scale: FOV per pixel [arcsec]
    :type scale: float
    :param d: Diameter of aperture [m]
    :type d: float
    :param is_ground_based: Whether the station taking the observation is ground or space based
    :type is_ground_based: bool
    :return: Signal on CCD [e-/pixel]
    :rtype: np.ndarray
    """
    if not is_ground_based:
        return 0  # No atmosphere to scatter through
    z_obs = np.arccos(
        dot(look_dirs_eci_eq, hat(obs_pos_eci_eq))
    ).flatten()
    sint = _raw_signal(
        d, z_obs, mode="sint", is_ground_based=is_ground_based
    )
    f_van_rhijn = 1 / np.cos(z_obs)
    z_rad = 3.5e-1  # Expected radiation at zenith, W/m^2/m/ster
    f_corr = AstroConstants.sun_irradiance_vacuum / sun_spectrum(550e-9)
    return (
        z_rad
        * sint
        * f_corr
        * dms_to_rad(0, 0, scale) ** 2
        * t_int
        * f_van_rhijn
    )
