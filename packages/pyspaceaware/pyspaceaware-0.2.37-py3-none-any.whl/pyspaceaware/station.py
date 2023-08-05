import numpy as np
from typing import Tuple
import datetime
import terrainman as tm

from .attitude import RbtfAttitude
from .time import siderial_hour_angle, date_to_jd
from .orbit import axis_rotation_matrices, quat_to_dcm
from .coordinates import (
    sun,
    moon,
    lla_to_eci,
    ecef_to_enu,
    lla_to_itrf,
    eci_to_ecef,
    enu_to_az_el,
)
from .background import (
    moonlight_signal,
    zodiacal_signal,
    airglow_signal,
    atmospherically_scattered_signal,
    integrated_starlight_signal,
    _raw_signal,
)
from .geodetic import geodetic_lat_to_geocentric
from .lighting import Brdf
from .engine import run_engine
from .math import hat, vecnorm, stack_mat_mult, dot, tand
from .constraints import ObserverConstraint
from .spaceobject import SpaceObject


class Station:
    def __init__(
        self,
        preset: str = "pogs",
        lat_deg: float = None,
        lon_deg: float = None,
        alt_km: float = None,
        name: str = None,
        use_terrain_data: bool = False,
    ):
        if preset.lower() == "pogs":
            self.name = "Purdue_Optical_Ground_Station"
            self.lat_geod_rad = 0.574213323906134
            self.lon_rad = -1.84190413727077
            self.alt_km = 2.22504
            self.telescope = Telescope(preset=preset)
        elif preset.lower() == "lmt":
            self.name = "ESA_Liquid_Mirror_Telescope"
            self.lat_geod_rad = np.deg2rad(32.9794)
            self.lon_rad = np.deg2rad(254.2666 - 180)
            self.alt_km = 2.772
            self.telescope = Telescope(preset=preset)
        elif preset.lower() == "sdt":
            self.name = "ESA_Space_Debris_Telescope"
            self.lat_geod_rad = np.deg2rad(28.1758)
            self.lon_rad = np.deg2rad(-16.3036)
            self.alt_km = 2.401
            self.telescope = Telescope(preset=preset)
        else:
            raise NotImplementedError(
                f"Station preset model '{preset}' not implemented!"
            )

        if lat_deg is not None:
            self.lat_geod_rad = np.deg2rad(lat_deg)
        if lon_deg is not None:
            self.lon_rad = np.deg2rad(lon_deg)
        if alt_km is not None:
            self.alt_km = alt_km
        if name is not None:
            self.name = name

        self.constraints: list[ObserverConstraint] = []

        self.lat_geoc_rad = geodetic_lat_to_geocentric(
            self.lat_geod_rad
        )
        self.lat_geod_deg, self.lon_deg = np.rad2deg(
            self.lat_geod_rad
        ), np.rad2deg(self.lon_rad)
        if use_terrain_data:
            tile = tm.TerrainDataHandler().load_tiles_containing(
                self.lat_geod_deg, self.lon_deg
            )
            self.alt_km = (
                tile.interpolate(self.lat_geod_deg, self.lon_deg) / 1e3
            )
        self.ecef = lla_to_itrf(
            self.lat_geod_rad, self.lon_rad, self.alt_km
        )

    def eci_at_dates(
        self, dates: np.ndarray[datetime.datetime] | datetime.datetime
    ) -> np.ndarray:
        return lla_to_eci(
            lat_geod=self.lat_geod_rad,
            lon=self.lon_rad,
            a=self.alt_km,
            date=dates,
        )

    def _ra_dec_to_az_el(self, date: datetime.datetime) -> np.ndarray:
        lha = siderial_hour_angle(self.lon_rad, date)
        # Computes the local hour angle [rad]
        (_, r2, r3) = axis_rotation_matrices()
        topo_eq_to_local_horizontal = r3(lha) @ r2(
            self.lat_geoc_rad - np.pi / 2
        )
        # Rotation matrix to go from topocentric equatorial (Ra, dec) to local horizon coordinates
        topo_eq_to_local_horizontal[1, :] *= -1
        # Applies S2 transformation, flips handedness of the coordinate system
        ra_dec_to_az_el = topo_eq_to_local_horizontal.T
        return ra_dec_to_az_el

    def az_el_to_eci(
        self, az: float, el: float, date: datetime.datetime
    ) -> np.ndarray:
        ra_dec_to_az_el = self._ra_dec_to_az_el(date)
        az_el_unit = np.array(
            [
                [np.cos(az) * np.cos(el)],
                [np.sin(az) * np.cos(el)],
                [np.sin(el)],
            ]
        )
        eci_unit = ra_dec_to_az_el.T @ az_el_unit
        return eci_unit.T

    def ra_dec_to_az_el(
        self, ra: float, dec: float, date: datetime.datetime
    ) -> Tuple[float, float]:
        ra_dec_to_az_el = self._ra_dec_to_az_el(date)
        ra_dec_unit = np.array(
            [
                [np.cos(ra) * np.cos(dec)],
                [np.sin(ra) * np.cos(dec)],
                [np.sin(dec)],
            ]
        )
        az_el_unit = ra_dec_to_az_el @ ra_dec_unit
        return enu_to_az_el(az_el_unit)

    def eci_to_az_el(
        self, dates: np.ndarray[datetime.datetime], r_eci: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        station_eci = self.eci_at_dates(dates)
        station_to_sat_hat_eci = hat(r_eci - station_eci)
        station_to_sat_hat_ecef = np.vstack(
            [
                (eci_to_ecef(d) @ rh.T).T
                for d, rh in zip(dates, station_to_sat_hat_eci)
            ]
        )
        station_to_sat_hat_enu = (
            ecef_to_enu(self.ecef) @ station_to_sat_hat_ecef.T
        ).T
        return enu_to_az_el(station_to_sat_hat_enu)

    def eval_constraints(
        self, **kwargs
    ) -> tuple[np.ndarray[bool], np.ndarray[bool]]:
        individual_constraints_satisfied = np.array(
            [
                cnstr.eval_fcn(**kwargs).flatten()
                for cnstr in self.constraints
            ]
        ).T
        all_constraints_satisfied = np.all(
            individual_constraints_satisfied, axis=1
        )
        return (
            all_constraints_satisfied,
            individual_constraints_satisfied,
        )

    def total_sky_brightness(
        self,
        dates: np.ndarray[datetime.datetime],
        look_dir_eci: np.ndarray,
        is_ground_based: bool = True,
    ) -> np.ndarray:
        obs_pos_eci_eq = self.eci_at_dates(dates)
        kwargs = {
            "look_dirs_eci_eq": look_dir_eci,
            "obs_pos_eci_eq": obs_pos_eci_eq,
            "t_int": self.telescope.integration_time,
            "scale": self.telescope.pixel_scale,
            "d": self.telescope.aperture_diameter,
            "is_ground_based": is_ground_based,
        }
        time_independent_signal = airglow_signal(
            **kwargs
        ) + atmospherically_scattered_signal(**kwargs)
        kwargs["dates"] = dates  # For time dependent signals
        time_dependent_signal = (
            moonlight_signal(**kwargs)
            + zodiacal_signal(**kwargs)
            + integrated_starlight_signal(**kwargs)
        )
        return time_independent_signal + time_dependent_signal

    def observe_light_curve(
        self,
        obj: SpaceObject,
        obj_attitude: RbtfAttitude,
        brdf: Brdf,
        dates: np.ndarray[datetime.datetime],
    ) -> np.ndarray:
        epsec_space = np.array(
            [(d - dates[0]).total_seconds() for d in dates]
        )
        (q, w) = obj_attitude.propagate(epsec_space)
        (r_sat, _) = obj.propagate(dates)

        r_station = self.eci_at_dates(dates)
        moon_vec = moon(date_to_jd(dates))
        ang_to_moon = np.arccos(
            dot(hat(moon_vec - r_station), hat(r_sat - r_station))
        ).flatten()

        sat_to_sun_inertial = sun(date_to_jd(dates))
        sat_to_station_inertial = r_station - r_sat
        rmag_station_to_sat = vecnorm(sat_to_station_inertial).flatten()
        z_obs = np.arccos(
            dot(hat(r_station), -hat(sat_to_station_inertial))
        )

        sat_to_sun_body = stack_mat_mult(
            quat_to_dcm(q), sat_to_sun_inertial
        )
        sat_to_obs_body = stack_mat_mult(
            quat_to_dcm(q), sat_to_station_inertial
        )

        lc_normalized = (
            run_engine(
                brdf,
                obj.file_name,
                hat(sat_to_sun_body),
                hat(sat_to_obs_body),
            ).flatten()
            * 10
        )  # [W] at one meter distance

        lc = (
            lc_normalized / (1e3 * rmag_station_to_sat) ** 2
        )  # Irradiance [w/m^2]

        sint = _raw_signal(
            self.telescope.aperture_diameter, z_obs, mode="sint"
        ).flatten()
        # [Ws/m^2], signal count per unit irradiance
        lc_clean = sint * lc

        background_mean = self.total_sky_brightness(
            dates, -hat(sat_to_station_inertial)
        ).flatten()  # [e-/pix]
        airy_disk_pixels = self.telescope.get_airy_disk_pixels(lc_clean)
        # Generating noise
        noise_lambda = (
            background_mean + self.telescope.count_readout_noise
        )
        noise_signal = np.zeros_like(noise_lambda)
        for i, (lam, p) in enumerate(
            zip(noise_lambda, airy_disk_pixels)
        ):
            noise_signal[i] = np.sum(
                np.random.poisson(lam=lam, size=(int(p),))
            )  # [e-]

        lc_noisy = (
            lc_clean + noise_signal - airy_disk_pixels * noise_lambda
        )
        snr = lc_clean / np.sqrt(lc_clean + noise_signal)

        (
            all_constraints_satisfied,
            individual_constraints_satisfied,
        ) = self.eval_constraints(
            dates=dates,
            target_pos_eci=r_sat,
            obs_pos_eci=r_station,
            look_dir_eci=-sat_to_station_inertial,
            lc=lc,
            snr=snr,
        )

        lc_noisy[
            np.logical_not(all_constraints_satisfied).flatten()
        ] = np.nan
        lc_clean[
            np.logical_not(all_constraints_satisfied).flatten()
        ] = np.nan
        return (
            lc_noisy,
            {
                "all_constraints_satisfied": all_constraints_satisfied,
                "individual_constraints_satisfied": individual_constraints_satisfied,
                "object_quat": q,
                "object_omega": w,
                "rmag_station_to_sat": rmag_station_to_sat,
                "object_pos_eci": r_sat,
                "station_pos_eci": r_station,
                "lc_normalized": lc_normalized,
                "noise_signal": noise_signal,
                "background_mean": background_mean,
                "sint": sint,
                "airy_disk_pixels": airy_disk_pixels,
                "obs_to_moon": ang_to_moon,
                "snr": snr,
                "lc_clean": lc_clean,
                "noise_lambda": noise_lambda,
            },
        )


class Telescope:
    def __init__(self, preset: str = None):
        self.count_readout_noise = 8  # Count
        if preset is not None:
            if preset.lower() == "pogs":
                self.fwhm = 1.5
                self.sensor_dimensions = 0.03690  # m
                self.f_number = 7.2
                self.aperture_diameter = 0.35560
                self.secondary_diameter = 0.1724660
                self.sensor_pixels = 4096
                self.pixel_size = (
                    self.sensor_dimensions / self.sensor_pixels
                )
                self.pixel_scale = 0.725447016117
                self.fov_deg = 0.8244251
                self.integration_time = 1  # seconds
            if preset.lower() == "lmt":
                # Liquid mirror telescope, Krag thesis
                self.sensor_dimensions = None
                self.f_number = None
                self.aperture_diameter = 3.0
                self.secondary_diameter = None
                self.sensor_pixels = 1250
                self.pixel_scale = 0.8
                self.fov_deg = 0.278
                self.integration_time = 0.033  # seconds
                self.fwhm = 1.56  # Pixels
                self.count_dark_noise = 0  # Count / s
                self.count_readout_noise = 8  # Count
                self.pixel_size = 20e-6  # m
            if preset.lower() == "sdt":
                # ESA Space Debris Telescope, Krag thesis
                self.sensor_dimensions = None
                self.f_number = None
                self.aperture_diameter = 1.016
                self.secondary_diameter = None
                self.sensor_pixels = 2048
                self.pixel_scale = 1.24
                self.fov_deg = 0.709
                self.integration_time = 2  # seconds
                self.fwhm = 1.21  # Pixels
                self.count_dark_noise = 0  # Count / s
                self.count_readout_noise = 8  # Count / s
                self.pixel_size = 28e-6  # m

        self.focal_length = (self.fov_deg * 3600 * self.pixel_size) / (
            2 * self.pixel_scale * tand(self.fov_deg / 2)
        )
        self.aperture_radius = self.aperture_diameter / 2
        self.aperture_area = np.pi * (self.aperture_radius) ** 2

    def get_airy_disk_pixels(
        self, s_obj: float, lam: float = 550e-9
    ) -> float:
        fwhm_sigma = self.fwhm / (2 * np.sqrt(2 * np.log(2)))  # Pixels
        area_of_gaussian = 0.838 * s_obj / (2 * np.pi * fwhm_sigma**2)
        return area_of_gaussian
