import numpy as np
from typing import Tuple, Union

from .attitude import rv_to_dcm
from .math import sph_to_cart, hat, dot, vecnorm


def rand_unit_vectors(num: int) -> np.ndarray:
    """Generates uniform random vectors on the unit sphere :math:`S^2`

    :param num: Number of unit vectors to generate
    :type num: int
    :return: Sampled unit vectors
    :rtype: np.ndarray [nx3]
    """
    return rand_cone_vectors(np.array([1, 0, 0]), np.pi, num)


def rand_cone_vectors(
    cone_axis: np.ndarray, cone_half_angle: float, num: int
) -> np.ndarray:
    """Generates uniform random unit vectors in a cone

    :param cone_axis: Axis of symmetry for the cone
    :type cone_axis: np.ndarray [1x3]
    :param cone_half_angle: Half-angle of the cone [rad]
    :type cone_half_angle: float
    :param num: Number of vectors to sample
    :type num: int
    :return: Sampled unit vectors
    :rtype: np.ndarray [nx3]
    """
    r1 = np.random.rand(num)
    r2 = np.random.rand(num)
    z = (1 - np.cos(cone_half_angle)) * r1 + np.cos(cone_half_angle)
    phi = 2 * np.pi * r2

    ref = hat(np.array([0, 0, 1]))
    cone_vec = np.transpose(
        np.array(
            [
                np.sqrt(1 - z**2) * np.cos(phi),
                np.sqrt(1 - z**2) * np.sin(phi),
                z,
            ]
        )
    )
    if all(ref != cone_axis):
        rot_vector = -np.cross(cone_axis, ref)
        rot_angle = np.arccos(dot(cone_axis, ref))
        rotm = rv_to_dcm(rot_vector * rot_angle)
    else:
        rotm = np.eye(3)
    return cone_vec @ rotm


def rand_point_in_shell(
    r_lims: Tuple[float, float], num: int
) -> np.ndarray:
    """Samples a random point in a solid spherical shell defined by `r_lims`

    :param r_lims: Minimum and maximum shell radii
    :type r_lims: Tuple[float, float]
    :param num: Number of points to sample
    :type num: int
    :return: Sampled points
    :rtype: np.ndarray [nx3]
    """
    (rmin, rmax) = r_lims
    v = np.zeros((num, 3))
    if (
        rmin == rmax
    ):  # Ok, we'll just return the sphere sampled unit vectors
        return rmin * rand_unit_vectors(num)
    while not all(vecnorm(v) > rmin):
        failed = (vecnorm(v) < rmin).flatten()
        nfailed = np.sum(failed)
        v[failed, :] = rmax * rand_point_in_ball(1, nfailed)
    return v


def rand_point_in_ball(
    r: Union[float, np.ndarray], num: int
) -> np.ndarray:
    """Samples random points in a solid ball

    :param r: Radius of the ball, or one unique radius per sample
    :type r: Union[float, np.ndarray]
    :param num: Number to sample
    :type num: int
    :raises ValueError: If the number of provided radii is not 1 or equal to `num`
    :return: Sampled points
    :rtype: np.ndarray [nx3]
    """
    v = rand_unit_vectors(num)
    ri = np.random.random((num, 1))
    if isinstance(r, int) or isinstance(r, float):
        return r * v * ri ** (1 / 3)
    if isinstance(r, np.ndarray):
        return np.reshape(r, (num, 1)) * v * ri ** (1 / 3)
    else:
        raise ValueError("r must be number or array of size num")


def spiral_sample_sphere(num: int) -> np.ndarray:
    """Generates relatively uniform samples on the unit sphere via Fibonacci sampling

    :param num: Number of vectors to sample
    :type num: int
    :return: Sampled unit vectors
    :rtype: np.ndarray [nx3]
    """
    gr = (1 + np.sqrt(5)) / 2  # golden ratio
    ga = 2 * np.pi * (1 - 1 / gr)  # golden angle

    i = np.arange(0, num)  # particle (i.e., point sample) index
    lat = np.arccos(1 - 2 * i / (num - 1))
    # latitude is defined so that particle index is proportional
    # to surface area between 0 and lat
    lon = i * ga  # position particles at even intervals along longitude

    return np.array(
        sph_to_cart(lon, lat - np.pi / 2, np.ones_like(lat))
    ).T
