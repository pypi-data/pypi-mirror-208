class AstroConstants:
    """Collection of astrodynamically-relevant constants"""

    earth_mu = 3.9860044e5  # [km^3/s^2] Earth gravitational parameter
    sun_mu = 1.327124400e11  # [km^3/s^2] Sun gravitational parameter
    earth_r_eq = 6378.14  # [km] Earth equatorial radius
    earth_r_mean = 6371.0087714  # [km] Earth mean radius
    earth_j2 = 1.08262668e-3  # [nondim] Coefficient of the Earth 2,0 zonal harmonic
    earth_f = 1.0 / 298.257223563  # [nondim] Flattening coefficient
    earth_sec_in_day = 86400  # [seconds] Seconds in a day
    earth_angular_velocity = 7.29211585530e-05  # [rad/s] Angular velocity of Earth about its axis
    au_to_km = 1.496e8  # Astronomical Units to km
    sun_irradiance_vacuum = 1361  # [W/m^2] mean irradiance of Sun, not accounting for atmospheric loss
    sun_magnitude = -26.832  # [nondim] Absolute magnitude of Sun
    sun_solid_angle = 6.794e-5  # [rad^2]
    lunar_month_days = 29.530588853  # [days] Length of lunar month
    moon_solid_angle = 6.418e-5  # [rad^2]
    inclination_of_ecliptic = 0.408407  # [rad]
    planck_constant = 6.62607015e-34  # [m^2 kg/s]
    speed_of_light_vacuum = 2.99792458e8  # [m/s]
    sun_radius_km = 696340.0  # km
