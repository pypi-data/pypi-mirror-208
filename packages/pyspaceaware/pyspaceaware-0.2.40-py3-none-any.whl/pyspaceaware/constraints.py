import datetime
import numpy as np
import terrainman as tm
import scipy
import os
from typing import Tuple

from .constants import AstroConstants
from .time import date_to_jd
from .math import dot, hat, vecnorm, wrap_to_two_pi
from .coordinates import (
    moon,
    sun,
    lla_to_itrf,
    ecef_to_enu,
    lla_to_eci,
    az_el_to_enu,
)
from .profiling import tic, toc


class HorizonMask:
    _STORAGE_DIR = os.path.join(
        os.environ["SRCDIR"], "resources", "masks"
    )
    if not os.path.exists(_STORAGE_DIR):
        os.mkdir(_STORAGE_DIR)

    def __init__(
        self,
        station_lat_rad: float,
        station_lon_rad: float,
        station_name: str,
        terrain_res: int = 500,
        geodetic_degrees_limit: float = 1.0,
        station_m_above_terrain: float = 0,
        mask_resolution: int = 1000,
        iterations: int = 10,
        force_rebuild: bool = False,
    ) -> None:
        station_lat_deg, station_lon_deg = np.rad2deg(
            station_lat_rad
        ), np.rad2deg(station_lon_rad)
        (
            self.station_lat_deg,
            self.station_lon_deg,
            self.station_name,
        ) = (station_lat_deg, station_lon_deg, station_name)

        tdh = tm.TerrainDataHandler()
        self.tile = tdh.load_tiles_containing(
            self.station_lat_deg, self.station_lon_deg
        )

        station_terrain_alt_km = (
            self.tile.interpolate(
                self.station_lat_deg, self.station_lon_deg
            )
            / 1e3
        )
        self.station_ecef = lla_to_itrf(
            station_lat_rad,
            station_lon_rad,
            station_terrain_alt_km + station_m_above_terrain / 1e3,
        )
        self.station_enu = (
            ecef_to_enu(self.station_ecef) @ self.station_ecef.T
        ).T

        try:
            if force_rebuild:
                self._build_searcher(
                    geodetic_degrees_limit, terrain_res
                )
                self.build(mask_resolution, iterations)
                self._save()
            self._load()
        except FileNotFoundError as e:
            print("Mask does not exist for this station, building...")
            self._build_searcher(geodetic_degrees_limit, terrain_res)
            self.build(mask_resolution, iterations)
            self._save()
            self._load()
        # self.el = np.zeros_like(self.el)

    def _build_searcher(
        self, geodetic_degrees_limit: float, terrain_res: int
    ):
        enu_hat = np.array([[np.nan, np.nan, np.nan]])
        print("Collecting elevation data from terrain tile...")
        tic()
        for i in range(
            1, 100, 5
        ):  # Each iteration, halve radius and append
            deg_lim = geodetic_degrees_limit / i
            lat_space = (self.station_lat_deg + deg_lim) - np.linspace(
                0, 2 * deg_lim, terrain_res
            )
            lon_space = (self.station_lon_deg - deg_lim) + np.linspace(
                0, 2 * deg_lim, terrain_res
            )
            lat_grid, lon_grid = np.meshgrid(lat_space, lon_space)
            elev_grid_km = (
                self.tile.interpolate(lat_grid, lon_grid) / 1e3
            )
            ecef = lla_to_itrf(
                np.deg2rad(lat_grid), np.deg2rad(lon_grid), elev_grid_km
            )
            enu = (
                ecef_to_enu(self.station_ecef) @ ecef.T
            ).T - self.station_enu
            enu_hat = np.vstack((hat(enu), enu_hat))
        toc()

        include_idx = ~np.isnan(enu_hat[:, 0])
        self.searcher = scipy.spatial.KDTree(enu_hat[include_idx, :])

    def terrain_grids(
        self,
        terrain_res: int = 3000,
        geodetic_degrees_limit: float = 1.0,
    ) -> dict:
        lat_space = (
            self.station_lat_deg + geodetic_degrees_limit
        ) - np.linspace(0, 2 * geodetic_degrees_limit, terrain_res)
        lon_space = (
            self.station_lon_deg - geodetic_degrees_limit
        ) + np.linspace(0, 2 * geodetic_degrees_limit, terrain_res)
        lat_grid, lon_grid = np.meshgrid(lat_space, lon_space)
        elev_grid_km = self.tile.interpolate(lat_grid, lon_grid) / 1e3
        ecef = lla_to_itrf(
            np.deg2rad(lat_grid), np.deg2rad(lon_grid), elev_grid_km
        )
        enu = (
            ecef_to_enu(self.station_ecef) @ ecef.T
        ).T - self.station_enu
        return {
            "x_enu_grid": enu[:, 0].reshape(lat_grid.shape),
            "y_enu_grid": enu[:, 1].reshape(lat_grid.shape),
            "z_enu_grid": enu[:, 2].reshape(lat_grid.shape),
            "lat_grid": lat_grid,
            "lon_grid": lon_grid,
            "elev_grid_km": elev_grid_km,
        }

    def interpolate(self, az: np.ndarray) -> np.ndarray:
        """Interpoaltes elevation linearly between mask points

        :param az: Queried azimuths [rad]
        :type az: np.ndarray
        :return: Interpolated elevations [rad]
        :rtype: np.ndarray
        """
        az_data = np.concatenate(([0], self.az))
        el_data = np.concatenate(([self.el[0]], self.el))
        f = scipy.interpolate.interp1d(
            x=az_data,
            y=el_data,
            kind="linear",
        )
        return f(az)

    def _save_fpath(self) -> str:
        return os.path.join(
            self._STORAGE_DIR, f"{self.station_name}.hzm"
        )

    def _save(self):
        with open(self._save_fpath(), "w") as f:
            f.write(
                f"# Horizon mask file for station {self.station_name}\n# Local azimuth [rad], local elevation [rad]\n"
            )
            f.writelines(
                [f"{az} {el}\n" for az, el in zip(self.az, self.el)]
            )

    def _load(self) -> Tuple[np.ndarray, np.ndarray]:
        """Loads saved mask file

        :return: Azimuth [rad], Elevation [rad] of mask
        :rtype: Tuple[np.ndarray, np.ndarray]
        """
        x = np.loadtxt(self._save_fpath())
        self.az, self.el = x[:, 0], x[:, 1]

    def build(self, mask_resolution: int, iterations: int):
        az_ray = np.linspace(0, 2 * np.pi, mask_resolution)
        el_ray = np.ones_like(az_ray) * np.pi / 4

        hit_horizon = np.zeros(el_ray.shape, dtype=bool)
        print("Computing horizon azimuth/elevation pairs")
        tic()
        for i in range(iterations):
            rays = az_el_to_enu(az_ray, el_ray)
            _, cindx = self.searcher.query(rays, k=1)
            closest_to_rays = self.searcher.data[cindx, :]
            ang_to_closest = np.arccos(
                dot(closest_to_rays, rays)
            ).flatten()
            ang_difference_to_neighbor = (
                np.roll(el_ray, 1) + np.roll(el_ray, -1) - 2 * el_ray
            )
            update_down = (ang_to_closest > 0.01) & ~hit_horizon
            update_up = ~update_down & hit_horizon
            el_ray[update_down] += -ang_to_closest[update_down] / 2
            el_ray[update_up] += (
                ang_difference_to_neighbor[update_up] / 4
            )
            el_ray[el_ray < 0] = 0.0  # Prevents negative elevations
            hit_horizon = (~update_down & ~hit_horizon) | hit_horizon
        toc()
        self.az = az_ray
        self.el = el_ray


class ObserverConstraint:
    pass


class HorizonMaskConstraint(ObserverConstraint):
    def __init__(self, station) -> None:
        horizon_mask = HorizonMask(
            station.lat_geod_rad, station.lon_rad, station.name
        )
        self.eval_fcn = lambda **kwargs: _horizon(
            **kwargs, horizon_mask=horizon_mask, station=station
        )


class SnrConstraint(ObserverConstraint):
    def __init__(self, min_snr: float) -> None:
        self.eval_fcn = lambda **kwargs: _snr(
            **kwargs, snr_limit=min_snr
        )


class ElevationConstraint(ObserverConstraint):
    def __init__(self, min_angle_deg: float) -> None:
        self.eval_fcn = lambda **kwargs: _observer_elevation(
            **kwargs, min_elevation_rad=np.deg2rad(min_angle_deg)
        )


class VisualMagnitudeConstraint(ObserverConstraint):
    def __init__(self, max_visual_magnitude: float) -> None:
        self.eval_fcn = lambda **kwargs: _observer_visual_magnitude(
            **kwargs, maximum_visual_magnitude=max_visual_magnitude
        )


class MoonExclusionConstraint(ObserverConstraint):
    def __init__(self, min_angle_deg: float) -> None:
        self.eval_fcn = lambda **kwargs: _observer_moon_exclusion(
            **kwargs,
            moon_exclusion_angle_min_rad=np.deg2rad(min_angle_deg),
        )


class ObserverEclipseConstraint(ObserverConstraint):
    def __init__(self, station) -> None:
        self.eval_fcn = (
            lambda **kwargs: _observer_eclipsed_geodetic_surface(
                lat_geod=station.lat_geod_rad,
                lon_rad=station.lon_rad,
                **kwargs,
            )
        )


class TargetIlluminatedConstraint(ObserverConstraint):
    def __init__(self) -> None:
        self.eval_fcn = (
            lambda **kwargs: ~_observer_eclipsed_geocentric_eci(
                **kwargs
            )
        )


def _horizon(
    look_dir_eci: np.ndarray,
    horizon_mask: HorizonMask,
    dates: np.ndarray[datetime.datetime],
    station,
    **kwargs,
) -> np.ndarray[bool]:
    (a, h) = station.eci_to_az_el(
        dates, look_dir_eci + station.eci_at_dates(dates)
    )
    terrain_el_at_az = horizon_mask.interpolate(wrap_to_two_pi(a))
    return h > terrain_el_at_az


def _snr(
    snr: np.ndarray, snr_limit: float, **kwargs
) -> np.ndarray[bool]:
    return snr > snr_limit


def _observer_eclipsed_geodetic_surface(
    lat_geod: float,
    lon_rad: float,
    dates: np.ndarray[datetime.datetime],
    **kwargs,
) -> np.ndarray:
    """Computes whether a geodetic latitude/longitude is eclipsed at times

    Args:
        lat_geod (float) [rad]: Geodetic latitude of station
        lon_rad (float) [rad]: Longitude of the station
        dates (datetime.datetime nx1) [utc]: Dates to check

    Returns:
        np.ndarray[bool] nx1: Is the station eclipsed at the times?

    """
    station_eci = lla_to_eci(
        lat_geod=lat_geod, lon=lon_rad, a=0, date=dates
    )
    return _observer_eclipsed_geocentric_eci(station_eci, dates)


def _observer_eclipsed_geocentric_eci(
    target_pos_eci: np.ndarray,
    dates: np.ndarray[datetime.datetime],
    **kwargs,
) -> np.ndarray:
    """Computes whether a geocentric position in Earth-Centered Inertial
    coordinates is in eclipse at given dates

    Args:
        target_pos_eci (np.ndarray nx3): Positions to check in ECI
        dates (np.ndarray[datetime.datetime] nx1) [utc]: Dates to propagate to

    Returns:
        float: Volume of the reconstructed convex polytope

    """
    rmag = vecnorm(target_pos_eci)
    sun_eci = sun(date_to_jd(dates))
    ha_arg = np.min(
        np.hstack(
            (AstroConstants.earth_r_eq / rmag, np.ones_like(rmag))
        ),
        axis=1,
        keepdims=True,
    )
    earth_half_angle = np.arcsin(ha_arg)
    sun_half_angle = np.arccos(dot(hat(sun_eci), hat(target_pos_eci)))
    return earth_half_angle > sun_half_angle


def _observer_moon_exclusion(
    look_dir_eci: np.ndarray,
    dates: np.ndarray[datetime.datetime],
    moon_exclusion_angle_min_rad: float,
    **kwargs,
) -> np.ndarray:
    moon_eci = moon(date_to_jd(dates))
    angle_look_to_moon = np.arccos(
        dot(hat(look_dir_eci), hat(moon_eci))
    )
    return angle_look_to_moon > moon_exclusion_angle_min_rad


def _observer_elevation(
    obs_pos_eci: np.ndarray,
    look_dir_eci: np.ndarray,
    min_elevation_rad: float,
    **kwargs,
) -> np.ndarray:
    angle_horizon_to_look = (
        np.arccos(dot(hat(obs_pos_eci), hat(look_dir_eci))) - np.pi / 2
    )
    return angle_horizon_to_look < min_elevation_rad


def _observer_visual_magnitude(
    lc: np.ndarray, maximum_visual_magnitude: float, **kwargs
) -> np.ndarray[bool]:
    lc[lc == 0] = np.nan
    vm = AstroConstants.sun_magnitude - 2.5 * np.log10(
        lc / AstroConstants.sun_irradiance_vacuum
    )
    return vm < maximum_visual_magnitude
