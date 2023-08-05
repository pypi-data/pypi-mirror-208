import datetime
import numpy as np
from typing import Any, Tuple

from .math import wrap_to_two_pi
from .constants import AstroConstants


def days(num: float):
    return datetime.timedelta(days=num)


def hours(num: float):
    return datetime.timedelta(hours=num)


def minutes(num: float):
    return datetime.timedelta(minutes=num)


def seconds(num: float):
    return datetime.timedelta(seconds=num)


def date_to_capital_t(date: datetime.datetime) -> np.ndarray:
    """Besselian years as used in the STM text TODO: cite STM notes

    :param date: Date to evaluate at [utc]
    :type date: datetime.datetime
    :return: Besselian years [yr]
    :rtype: np.ndarray
    """
    jd = date_to_jd(date)
    TT_MINUS_UTC = 64.148
    jd_tt = jd + TT_MINUS_UTC / AstroConstants.earth_sec_in_day
    T = (jd_tt - 2451545.0) / 36525.0
    return T


def beginning_of_day(
    dates: np.ndarray[datetime.datetime],
) -> np.ndarray[datetime.datetime]:
    """Finds the beginning of the day for given datetime array

    :param dates: Date array (UTC)
    :type dates: np.ndarray[datetime.datetime] [nx1]
    :return: Beginning of day for each date (UTC)
    :rtype: np.ndarray[datetime.datetime] [nx1]
    """
    return_naked = False
    if isinstance(dates, datetime.datetime):
        dates = np.array([dates])
        return_naked = True

    bod_arr = np.array(
        [
            datetime.datetime(
                d.year, d.month, d.day, 0, 0, 0, 0, tzinfo=d.tzinfo
            )
            for d in dates
        ]
    )

    if return_naked:
        return bod_arr[0]
    else:
        return bod_arr


def date_to_ut(date: datetime.datetime) -> float:
    """Converts a datetime object to Universal Time (UT)

    :param date: Date object (UTC)
    :type date: datetime.datetime
    :return: UT at input date [hr]
    :rtype: float
    """

    min_year = np.min([d.year for d in np.array(date).flatten()])
    assert min_year > 1582, ValueError("date must be after 1582")
    bod = beginning_of_day(date)
    # Generates the datetime object at the beginning of the day
    univ_delta = date - bod
    # Calculates the decimal hours since the beginning of the day
    if hasattr(univ_delta, "__iter__"):
        return np.array(
            [dt.total_seconds() / 3600 for dt in univ_delta]
        )
    else:
        return univ_delta.total_seconds() / 3600


def date_to_jd(dates: np.ndarray[datetime.datetime]) -> float:
    """Converts datetime to Julian date

    :param dates: Date objects to compute the Julian date (UTC)
    :type dates: np.ndarray[datetime.datetime]
    :return: Julian date of input dates
    :rtype: float
    :tests:
    >>> date_to_jd(datetime.datetime(year=2000, month=12, day=9, hour=12, minute=30, second=10, tzinfo=datetime.timezone.utc))
    2451888.020949074...

    """
    return_float = False
    if isinstance(dates, datetime.datetime):
        return_float = True

    dates = np.array([dates]).flatten()
    jds = np.zeros(dates.shape, dtype=np.float64)
    for i, date in enumerate(dates):
        ut = date_to_ut(date)
        if date.month <= 2:  # If the month is Jan or Feb
            y = date.year - 1
            m = date.month + 12
        elif date.month > 2:  # If the month is after Feb
            y = date.year
            m = date.month

        B = np.floor(y / 400) - np.floor(
            y / 100
        )  # Account for leap years
        jds[i] = (
            np.floor(365.25 * y)
            + np.floor(30.6001 * (m + 1))
            + B
            + 1720996.5
            + date.day
            + ut / 24
        )
    if return_float:
        return jds[0]
    else:
        return jds.flatten()


def date_to_sidereal(date: datetime.datetime) -> float:
    """Converts a datetime to sidereal time

    :param date: Date objects (UTC)
    :type date: datetime.datetime
    :return: Sidereal times [seconds]
    :rtype: float
    :tests:
    >>> date_to_sidereal(datetime.datetime(year=2000, month=12, day=9, hour=12, minute=30, second=10, tzinfo=datetime.timezone.utc))
    150263.545124541...

    """
    beginning_of_day = datetime.datetime(
        date.year,
        date.month,
        date.day,
        00,
        00,
        00,
        00,
        tzinfo=datetime.timezone.utc,
    )
    ut = date_to_ut(date)
    jd0 = date_to_jd(beginning_of_day)
    jd = date_to_jd(date)

    T0 = (
        jd0 - 2451545
    ) / 36525  # Time since Jan 1 2000, 12h UT to beginning of day
    T1 = (jd - 2451545) / 36525  # Time since Jan 1 2000, 12h UT to now

    sidereal_beginning_of_day = (
        24110.54841
        + 8640184.812866 * T0
        + 0.093104 * T1**2
        - 0.0000062 * T1**3
    )
    # Sidereal time at the beginning of the julian date day

    # Computes the exact sidereal time, accounting for the extra 4 mins/day
    return sidereal_beginning_of_day + 1.0027279093 * ut * 3600


def siderial_hour_angle(
    obs_lon_rad: float, date: datetime.datetime
) -> float:
    s_time = date_to_sidereal(
        date
    )  # Computes exact siderial time at greenwich
    gmst = s_time % 86400  # current siderial time at greenwich [s]
    gmst_frac = gmst / 86400  # Fraction of a siderial day at greenwich
    hour_gmst = gmst_frac * 24  # Hours of siderial time at greenwich
    greenwich_hour_angle = hour_gmst / 24 * 2 * np.pi
    # Hour angle at this time at greenwich
    lmst = hour_gmst + np.rad2deg(obs_lon_rad) * 1 / 15
    # Computes local siderial time [hr]
    local_hour_angle = wrap_to_two_pi(lmst / 24 * 2 * np.pi)
    # Computes local hour angle in [rad]
    return local_hour_angle


def jd_now() -> float:
    """Computes the Julian date at evaluation time

    :return: Current Julian date [days]
    :rtype: float
    """
    return date_to_jd(now())


def now() -> datetime.datetime:
    """Current ``datetime.datetime`` object

    :return: Current UTC date object at runtime
    :rtype: datetime.datetime
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)


def date_linspace(
    date_start: datetime.datetime,
    date_stop: datetime.datetime,
    num: int,
) -> Tuple[np.ndarray[datetime.datetime], np.ndarray[np.float64]]:
    """Computes a linspace of datetime objects

    :param date_start: Date to start at (UTC)
    :type date_start: datetime.datetime
    :param date_stop: Date to stop at (UTC)
    :type date_stop: datetime.datetime
    :param num: Number of samples to make
    :type num: int
    :return: Sampled linspace of datetimes (UTC)
    :rtype: Tuple[np.ndarray[datetime.datetime], np.ndarray[np.float64]]
    """
    if num == 1:
        return np.array([date_start])
    delta_seconds = (date_stop - date_start).total_seconds() / (
        int(num) - 1
    )
    date_space = np.array(
        [
            date_start + datetime.timedelta(seconds=n * delta_seconds)
            for n in range(int(num))
        ]
    )
    epsec_space = np.array(
        [(d - date_start).total_seconds() for d in date_space]
    )
    return (date_space, epsec_space)


## DOCTESTING
if __name__ == "__main__":
    import doctest

    # doctest.run_docstring_examples(date_to_jd, globals(), verbose=True, optionflags=doctest.ELLIPSIS)
    doctest.testmod(optionflags=doctest.ELLIPSIS, verbose=True)
