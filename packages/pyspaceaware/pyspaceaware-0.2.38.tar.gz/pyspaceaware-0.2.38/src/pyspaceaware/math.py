import numpy as np
from scipy.special import elliprf, elliprj
from typing import Tuple


def dms_to_rad(
    deg: np.ndarray, min: np.ndarray, sec: np.ndarray
) -> np.ndarray:
    """Converts from degrees, arcminutes, and arcseconds to radians

    :param deg: Degrees
    :type deg: np.ndarray
    :param min: Arcminutes
    :type min: np.ndarray
    :param sec: Arcseconds
    :type sec: np.ndarray
    :return: Radians
    :rtype: np.ndarray
    """
    return np.deg2rad(deg + min / 60 + sec / 3600)


def tilde(v: np.ndarray) -> np.ndarray:
    """Matrix cross product operator such that :math:`v \\times x = \\left[\\tilde{v}\right]x`

    :param v: Vector to operate on
    :type v: np.ndarray [nx3]
    :return: Cross product matrices
    :rtype: np.ndarray [3x3xn]
    """
    nv = v.shape[0]
    v1_deep = np.reshape(v[:, 0], (1, 1, nv))
    v2_deep = np.reshape(v[:, 1], (1, 1, nv))
    v3_deep = np.reshape(v[:, 2], (1, 1, nv))
    z = 0 * v1_deep

    mat_cp = np.array(
        [
            [z, -v3_deep, v2_deep],
            [v3_deep, z, -v1_deep],
            [-v2_deep, v1_deep, z],
        ]
    ).squeeze()
    return mat_cp


def look_at_matrix(
    eye: np.ndarray, target: np.ndarray, up: np.ndarray
) -> np.ndarray:
    """Look matrix for a camera placed at `eye`, looking at `target`, with up vector `up`. Transforms from world frame coordinates to camera frame coordinates. `Source <https://www.geertarien.com/blog/2017/07/30/breakdown-of-the-lookAt-function-in-OpenGL/>`_

    :param eye: Location of camera origin in world coordinates
    :type eye: np.ndarray [1x3]
    :param target: Location of camera target in world coordinates
    :type target: np.ndarray [1x3]
    :param up: Up vector constraining the vertical camera axis
    :type up: np.ndarray [1x3]
    :return: Look matrix :math:`V` such that :math:`V[x \: 1]^T` transforms the vector :math:`x` into camera coordinates :math:`\\frac{V[x \: 1]_{1:3}^T}{V[x \: 1]_{4}^T}`
    :rtype: np.ndarray [4x4]
    """
    result = np.zeros((4, 4))
    vz = hat(eye - target)
    vx = hat(np.cross(up, vz))
    vy = np.cross(vz, vx)

    result[:3, :3] = np.array([vx, vy, vz])
    result[:, 3] = np.array(
        (-dot(vx, eye), -dot(vy, eye), -dot(vz, eye), [1.0])
    ).flatten()
    return result


def perspective_projection_matrix(
    fov_deg: float, aspect: float, near: float, far: float
) -> np.ndarray:
    """Transforms from camera coordinates to image plane coordinates for a perspective camera

    :param fov_deg: Field of view [deg]
    :type fov_deg: float
    :param aspect: Aspect ratio of camera: the ratio of the horizontal to vertical fields of view
    :type aspect: float
    :param near: Near plane distance from camera origin, avoid going much below 0.01 to avoid numerical issues at 0
    :type near: float
    :param far: Far plane distance from camera origin
    :type far: float
    :return: Projection matrix :math:`P` such that :math:`P[x \: 1]^T` transforms the vector :math:`x` into image coordinates :math:`\\frac{P[x \: 1]_{1:3}^T}{P[x \: 1]_{4}^T}`
    :rtype: np.ndarray [4x4]
    """
    result = np.zeros((4, 4))
    top = near * tand(fov_deg * 0.5)
    bottom = -top
    right = top * aspect
    left = -right

    rl = right - left
    tb = top - bottom
    fn = far - near

    result[0, 0] = (near * 2.0) / rl
    result[1, 1] = (near * 2.0) / tb
    result[0, 2] = (right + left) / rl
    result[1, 2] = (top + bottom) / tb
    result[2, 2] = -(far + near) / fn
    result[3, 2] = -1.0
    result[2, 3] = -(far * near * 2.0) / fn
    return result


def sind(x: np.ndarray) -> np.ndarray:
    """Computes :math:`\\sin(x)` with :math:`x` in degrees

    :param x: Input [deg]
    :type x: np.ndarray
    :return: :math:`\\sin(x)`
    :rtype: np.ndarray
    """
    return np.sin(np.deg2rad(x))


def cosd(x: np.ndarray) -> np.ndarray:
    """Computes :math:`\\cos(x)` with :math:`x` in degrees

    :param x: Input [deg]
    :type x: np.ndarray
    :return: :math:`\\cos(x)`
    :rtype: np.ndarray
    """
    return np.cos(np.deg2rad(x))


def tand(x: np.ndarray) -> np.ndarray:
    """Computes :math:`\\tan(x)` with :math:`x` in degrees

    :param x: Input [deg]
    :type x: np.ndarray
    :return: :math:`\\tan(x)`
    :rtype: np.ndarray
    """
    return np.tan(np.deg2rad(x))


def acosd(x: np.ndarray) -> np.ndarray:
    """Computes :math:`\\cos^{-1}(x)` with :math:`x` in degrees

    :param x: Input [deg]
    :type x: np.ndarray
    :return: :math:`\\cos^{-1}(x)`
    :rtype: np.ndarray
    """
    return np.rad2deg(np.arccos(x))


def atand(x: np.ndarray) -> np.ndarray:
    """Computes :math:`\\tan^{-1}(x)` with :math:`x` in degrees

    :param x: Input [deg]
    :type x: np.ndarray
    :return: :math:`\\tan^{-1}(x)`
    :rtype: np.ndarray
    """
    return np.rad2deg(np.arctan(x))


def atan2d(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Four quadrant inverse tangent :math:`\\tan^{-1}(y/x)` with inputs in degrees

    :param x: Input [deg]
    :type x: np.ndarray
    :return: :math:`\\tan^{-1}(y/x)`
    :rtype: np.ndarray
    """
    return np.rad2deg(np.arctan2(y, x))


def hat(v: np.ndarray) -> np.ndarray:
    """Normalizes input np.ndarray nx3 such that each row is unit length. If a row is ``[0,0,0]```, ``hat()`` returns it unchanged

    :param v: Input vectors
    :type v: np.ndarray [nx3]
    :return: Unit vectors
    :rtype: np.ndarray [nx3]
    """
    vm = vecnorm(v)
    vm[vm == 0] = 1.0  # Such that hat([0,0,0]) = [0,0,0]
    return v / vm


def vecnorm(v: np.ndarray) -> np.ndarray:
    """Takes the :math:`L_2` norm of the rows of ``v``

    :param v: Input vector
    :type v: np.ndarray [nxm]
    :return: Norm of each row
    :rtype: np.ndarray [nx1]
    """
    axis = v.ndim - 1
    return np.linalg.norm(v, axis=axis, keepdims=True)


def dot(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """Euclidean dot product between corresponding rows of ``v1`` and ``v2``

    :param v1: First input vector
    :type v1: np.ndarray [nxm]
    :param v2: Second input vector
    :type v2: np.ndarray [nxm]
    :return: Dot products of corresponding rows
    :rtype: np.ndarray [nx1]
    """
    axis = v1.ndim - 1
    return np.sum(v1 * v2, axis=axis, keepdims=True)


def rdot(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """Rectified dot product, where ``0 if dot(v1,v2) < 0 else dot(v1,v2)``

    :param v1: First input vector
    :type v1: np.ndarray [nxm]
    :param v2: Second input vector
    :type v2: np.ndarray [nxm]
    :return: Positive dot product of ``v1`` rows with ``v2``` rows
    :rtype: np.ndarray [nx1]
    """
    d = dot(v1, v2)
    d[d < 0] = 0
    return d

    """"""


def cart_to_sph(
    x: np.ndarray, y: np.ndarray, z: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Converts from Cartesian ``(x,y,z)`` to spherical ``(azimuth, elevation, range)``

    :param x: Cartesian x
    :type x: np.ndarray
    :param y: Cartesian y
    :type y: np.ndarray
    :param z: Cartesian z
    :type z: np.ndarray
    :return: ``(azimuth, elevation, range)`` angles in [rad]
    :rtype: Tuple[np.ndarray, np.ndarray, np.ndarray]
    """
    hxy = np.hypot(x, y)
    r = np.hypot(hxy, z)
    el = np.arctan2(z, hxy)
    az = np.arctan2(y, x)
    return az, el, r


def sph_to_cart(
    az: np.ndarray, el: np.ndarray, r: np.ndarray = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Converts from spherical ``(azimuth, elevation, range)`` to Cartesian ``(x, y, z)``

    :param az: Azimuth [rad]
    :type az: np.ndarray
    :param el: Elevation [rad]
    :type el: np.ndarray
    :param r: Range, if not provided assumed to be 1
    :type r: np.ndarray, defaults to None
    :return: Cartesian ``(x, y, z)``
    :rtype: Tuple[np.ndarray, np.ndarray, np.ndarray]
    """
    if r is None:
        r = 0 * el + 1
    rcos_theta = r * np.cos(el)
    x = rcos_theta * np.cos(az)
    y = rcos_theta * np.sin(az)
    z = r * np.sin(el)
    return x, y, z

    """Replicates MATLAB's wrapTo360() functionality"""


def wrap_to_360(lon: np.ndarray) -> np.ndarray:
    """Wraps angular quantities to their remainder on ``[0, 360]``

    :param lon: Angle to wrap [deg]
    :type lon: np.ndarray
    :return: Wrapped angle [deg]
    :rtype: np.ndarray
    """
    lon %= 360
    return lon


def wrap_to_two_pi(lon: np.ndarray) -> np.ndarray:
    """Wraps angular quantities to their remainder on ``[0, 2pi]``

    :param lon: Angle to wrap [rad]
    :type lon: np.ndarray
    :return: Wrapped angle [rad]
    :rtype: np.ndarray
    """
    return np.deg2rad(wrap_to_360(np.rad2deg(lon)))


def angle_between_deg(a1: np.ndarray, a2: np.ndarray) -> np.ndarray:
    """Given two angular quantities, finds smallest angle between their unit circle vectors, ex: ``f(50, 40) -> 10``, ``f(-30, 20) = 50``

    :param a1: First angle [deg]
    :type a1: np.ndarray
    :param a2: Second angle [deg]
    :type a2: np.ndarray
    :return: Smallest angle difference [deg]
    :rtype: np.ndarray
    """

    m1 = wrap_to_360(a1 - a2)
    m2 = wrap_to_360(a2 - a1)
    mina = np.empty_like(a1)
    mina[m1 < m2] = m1[m1 < m2]
    mina[m2 < m1] = m2[m2 < m1]
    return mina


def angle_between_rad(a1: np.ndarray, a2: np.ndarray) -> np.ndarray:
    """Given two angular quantities, finds smallest angle between their unit circle vectors, see ``angle_between_deg``

    :param a1: First angle [rad]
    :type a1: np.ndarray
    :param a2: Second angle [rad]
    :type a2: np.ndarray
    :return: Smallest angle difference [rad]
    :rtype: np.ndarray
    """
    return np.deg2rad(angle_between_deg(np.rad2deg(a1), np.rad2deg(a2)))


def unique_rows(v: np.ndarray, **kwargs) -> np.ndarray:
    """Extracts unique rows from the input 2D array

    :param v: Input vector
    :type v: np.ndarray [nxm]
    :param **kwargs: Additional arguments to pass to ``np.unique()``
    :return: Unique rows of ``v``
    :rtype: np.ndarray [n-k x m], ``k>=0``
    """
    return np.unique(np.round(v, decimals=6), axis=0, **kwargs)


def merge_clusters(
    v: np.ndarray, atol: float, miter: int = 3
) -> np.ndarray:
    """Merges clusters of vectors in :math:`R^3` within an angle tolerance by addition

    :param v: Array of row vectors to merge
    :type v: np.ndarray [nx3]
    :param atol: Angle between vectors to merge by [rad]
    :type atol: float
    :param miter: Merge iterations, defaults to 3
    :type miter: int, optional
    :return: Merged vectors
    :rtype: np.ndarray [mx3], ``m <= n``
    """
    n = v.shape[0]
    for i in range(miter):
        vh = hat(v)
        vm = np.empty((0, 3))
        merged_inds = np.array([])
        for i in range(n):
            ang_to_others = np.arccos(
                dot(np.tile(vh[i, :], (n, 1)), vh)
            ).flatten()
            cluster_inds = np.argwhere(ang_to_others < atol).flatten()
            unmerged_cluster_inds = np.setdiff1d(
                cluster_inds, merged_inds
            )
            vm = np.append(
                vm,
                [np.sum(v[unmerged_cluster_inds, :], axis=0)],
                axis=0,
            )
            merged_inds = np.append(merged_inds, unmerged_cluster_inds)
        v = vm

    zero_row_inds = np.argwhere(
        (vecnorm(v) < 1e-12).flatten()
    ).flatten()
    v = np.delete(v, zero_row_inds, axis=0)
    return unique_rows(v)


def points_to_planes(
    pt: np.ndarray, plane_n: np.ndarray, support: np.ndarray
) -> np.ndarray:
    """Computes distance from a set of points to a set of planes

    :param pt: Array of points in R^3
    :type pt: np.ndarray [nx3]
    :param plane_n: Normal vectors of planes
    :type plane_n: np.ndarray [nx3]
    :param support: Distance from each plane to the origin
    :type support: np.ndarray [nx1]
    :return: Distance from points to planes
    :rtype: np.ndarray [nx1]
    """
    return dot(pt, plane_n) + support


def close_egi(egi: np.ndarray) -> np.ndarray:
    """Enforces closure condition by adding mean closure error to each row :cite:p:`robinson2022`

    :param egi: Extended Gaussian Image (EGI)
    :type egi: np.ndarray [nx3]
    :return: Shifted EGI such that the sum of rows is zero
    :rtype: np.ndarray [nx3]
    """
    return egi - np.sum(egi, axis=0) / egi.shape[0]


def remove_zero_rows(v: np.ndarray) -> np.ndarray:
    """Removes all rows from the 2D array `v` that have a norm of zero

    :param v: Array to operate on
    :type v: np.ndarray [nxm]
    :return: Copy of `v` with zero rows removed
    :rtype: np.ndarray [n-k x m]
    """
    return np.delete(v, vecnorm(v).flatten() == 0, axis=0)


def elliptic_pi_complete(
    n: np.ndarray, ksquared: np.ndarray
) -> np.ndarray:
    """Computes the complete elliptic integral of the third kind based on Carlson symmetric forms :math:`R_f, R_j`

    :param n: :math:`n` parameter of the integral
    :type n: np.ndarray [mx1]
    :param ksquared: :math:`k^2` parameter of the integral
    :type ksquared: np.ndarray [mx1]
    :return: :math:`\pi(n, \phi, k^2)`
    :rtype: np.ndarray [mx1]
    """
    return elliprf(0, 1 - ksquared, 1) + 1 / 3 * n * elliprj(
        0, 1 - ksquared, 1, 1 - n
    )


def elliptic_pi_incomplete(
    n: np.ndarray, phi: np.ndarray, ksquared: np.ndarray
) -> np.ndarray:
    """Computes the incomplete elliptic integral of the third kind based on Carlson symmetric forms :math:`R_f, R_j`

    :param n: :math:`n` parameter of the integral
    :type n: np.ndarray [nx1]
    :param phi: :math:`\phi`
    :type phi: np.ndarray [nx1]
    :param ksquared: :math:`k^2` parameter of the integral
    :type ksquared: np.ndarray [nx1]
    :return: :math:`\Pi(n, \phi, k^2)`
    :rtype: np.ndarray [nx1]
    """
    c = np.floor((phi + np.pi / 2) / np.pi)
    phi_shifted = phi - c * np.pi
    onemk2_sin2phi = 1 - ksquared * np.sin(phi_shifted) ** 2
    cos2phi = np.cos(phi_shifted) ** 2
    sin3phi = np.sin(phi_shifted) ** 3
    n_sin2phi = n * np.sin(phi_shifted) ** 2

    periodic_portion = 2 * c * elliptic_pi_complete(n, ksquared)

    return (
        np.sin(phi_shifted) * elliprf(cos2phi, onemk2_sin2phi, 1)
        + 1
        / 3
        * n
        * sin3phi
        * elliprj(cos2phi, onemk2_sin2phi, 1, 1 - n_sin2phi)
        + periodic_portion
    )


def stack_mat_mult(mats: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Multiplies each row in v by each page of mats

    :param mats: Matrices to multiply by
    :type mats: np.ndarray [mxmxn]
    :param v: Vectors to be multiplied
    :type v: np.ndarray [nxm]
    :return: Multiplied product obeying ``result[i, :] = mats[i,:,:] @ v[i, :].T``
    :rtype: np.ndarray [nxm]
    """
    (n, m) = v.shape
    if mats.shape[0] == mats.shape[1]:
        mats = np.moveaxis(mats, -1, 0)

    assert mats.shape[0] == n, "Matrix dimensions to not match vector!"
    v_deep = np.reshape(v, (n, m, 1))
    return np.squeeze(mats @ v_deep)
