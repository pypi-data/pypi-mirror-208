import asyncio
import os
import spacetrack.operators as op
from spacetrack.aio import AsyncSpaceTrackClient
from spacetrack import SpaceTrackClient
from typing import Union


def get_spacetrack_client(
    is_async: bool = False,
) -> Union[SpaceTrackClient, AsyncSpaceTrackClient]:
    """Gets client for the Space-Track API

    :param is_async: Whether the produced client operates asynchronously, defaults to False
    :type is_async: bool, optional
    :return: Client used to execute Space-Track API requests
    :rtype: Union[SpaceTrackClient, AsyncSpaceTrackClient]
    """
    (user, pword) = (
        os.environ["SPACETRACK_USERNAME"],
        os.environ["SPACETRACK_PASSWORD"],
    )
    if is_async:
        return AsyncSpaceTrackClient(identity=user, password=pword)
    else:
        return SpaceTrackClient(identity=user, password=pword)


async def download_latest_tles(
    preset: str = "all", epoch_tol_days: int = 30
) -> None:
    """Downloads TLE catalog from Space-Track

    :param preset: Preset TLE set, either "all", "leo", or "geo", defaults to "all"
    :type preset: str, optional
    :param epoch_tol_days: Oldest TLE to consider, defaults to 30
    :type epoch_tol_days: int, optional
    """
    st = get_spacetrack_client(is_async=True)
    save_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "tle"
    )
    cat_path = os.path.join(save_dir, f"tle_latest_{preset}.cat")
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    async with st:
        if preset.lower() == "geo":
            data = await st.tle_latest(
                iter_lines=True,
                ordinal=1,
                epoch=f">now-{epoch_tol_days}",
                mean_motion=op.inclusive_range(0.99, 1.01),
                eccentricity=op.less_than(0.01),
                format="tle",
            )
        elif preset.lower() == "leo":
            data = await st.tle_latest(
                iter_lines=True,
                ordinal=1,
                epoch=f">now-{epoch_tol_days}",
                semimajor_axis=op.less_than(8378),
                format="tle",
            )
        elif preset.lower() == "all":
            data = await st.tle_latest(
                iter_lines=True,
                ordinal=1,
                epoch=f">now-{epoch_tol_days}",
                format="tle",
            )

        with open(cat_path, "w+") as fp:
            async for line in data:
                fp.write(line + "\n")


def download_catalog_tles(preset: str = "all") -> None:
    """Downloads catalog TLEs for a given preset

    :param preset: Preset TLE set, either "all", "leo", or "geo", defaults to "all"
    :type preset: str, optional
    """
    print(f"Downloading TLE catalog for preset '{preset}'")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(download_latest_tles(preset=preset))
    print(f"Finished downloading TLE catalog for preset '{preset}'")


def download_catalogs():
    """Downloads all preset catalogs"""
    download_catalog_tles("leo")
    download_catalog_tles("geo")
    download_catalog_tles("all")
