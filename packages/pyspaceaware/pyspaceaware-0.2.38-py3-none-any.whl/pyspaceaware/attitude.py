import numpy as np
import scipy
from typing import Tuple, Callable, Any
from .math import (
    acosd,
    atan2d,
    dot,
    elliptic_pi_incomplete,
    hat,
    vecnorm,
)
from .constants import AstroConstants


class AttitudeRepresentation:
    _RV = {
        "name": "rv",
        "full_name": "rotation vector",
        "num_components": 3,
        "constraint_validator": lambda x: all(vecnorm(x) > 0),
        "constraint_msg": "Rotation vectors have a singularity at the origin, calculations will be inaccurate",
    }
    _QUAT = {
        "name": "quat",
        "full_name": "quaternion",
        "num_components": 4,
        "constraint_validator": lambda x: np.isclose(
            vecnorm(x).flatten(), np.ones((x.shape[0],))
        ),
        "constraint_msg": "Quaternions must have an L2 norm of 1 to represent an orientation, check your inputs",
    }
    _DCM = {
        "name": "dcm",
        "full_name": "direction cosine matrix",
        "num_components": 9,
        "constraint_validator": lambda x: np.isclose(
            np.linalg.det(x), 1.0
        )
        and np.isclose(np.linalg.inv(x), x.T).all(),
        "constraint_msg": "Direction cosine matrices must have det(A) == 1, inv(A) == transpose(A)",
    }
    _MRP = {
        "name": "mrp",
        "full_name": "modified Rodrigues parameter",
        "num_components": 3,
        "constraint_validator": lambda x: not np.isclose(
            vecnorm(mrp_to_rv(x)).flatten(),
            2 * np.pi * np.ones((x.shape[0],)),
        ),
        "constraint_msg": "Modified Rodrigues parameters have a singularity at theta = 2*pi",
    }

    _REGISTERED = [_RV, _QUAT, _DCM, _MRP]
    _REGISTERED_NAMES = [x["name"] for x in _REGISTERED]

    def __init__(self, repr_name: str, components: np.ndarray):
        assert repr_name in self._REGISTERED_NAMES, ValueError(
            f"{repr_name} not a registered attitude representation, options are: {self._REGISTERED_NAMES}"
        )
        i = np.argwhere(
            [n == repr_name for n in self._REGISTERED_NAMES]
        ).flatten()[0]
        self.current_repr = self._REGISTERED[i]
        self.name = self.current_repr["name"]
        self.full_name = self.current_repr["full_name"]
        self.num_components = self.current_repr["num_components"]
        self.constraint_validator = self.current_repr[
            "constraint_validator"
        ]
        self.constraint_msg = self.current_repr["constraint_msg"]

        assert components.size == self.num_components, ValueError(
            f"Attitude representation {self.name} must have {self.num_components} components, {components.size} components provided"
        )
        assert self.constraint_validator(components), ValueError(
            f"{self.constraint_msg}"
        )
        self.components = components

    def to(self, target_repr_name: str):
        """Converts the attitude in `self` to a new representation

        :param target_repr_name: Name of the target representation name
        :type target_repr_name: str
        :return: Coverted attitude representation
        :rtype: AttitudeRepresentation
        """
        assert target_repr_name in self._REGISTERED_NAMES, ValueError(
            f"{target_repr_name} not a registered attitude representation, options are: {self._REGISTERED_NAMES}"
        )
        if target_repr_name == self.name:
            return self
        fcn = globals()[f"{self.name}_to_{target_repr_name}"]
        return AttitudeRepresentation(
            target_repr_name, fcn(self.components)
        )

    def _match(self, other):
        """Converts the `other` attitude to match the representation of `self`

        :param other: Attitude representation to be changed
        :type other: AttitudeRepresentation
        :return: `other` in the representation of `self`
        :rtype: AttitudeRepresentation
        """
        return other.to(self.name)

    def __mul__(self, other):
        assert isinstance(other, AttitudeRepresentation), TypeError(
            f"Attitude representation can only be added to other attitude representations, not {type(other)}"
        )
        other = self._match(other)
        fcn = globals()[f"{self.name}_add"]
        return AttitudeRepresentation(
            self.name, fcn(self.components, other.components)
        )

    def __truediv__(self, other):
        assert isinstance(other, AttitudeRepresentation), TypeError(
            f"Attitude representation can only be divided by other attitude representations, not {type(other)}"
        )
        other = self._match(other)
        fcn = globals()[f"{self.name}_add"]
        return AttitudeRepresentation(
            self.name, fcn(self.inverse().components, other.components)
        )

    def inverse(self):
        """Returns the inverse of the attitude in the current representation via quaternions

        :return: Inverse of the current attitude
        :rtype: AttitudeRepresentation
        """
        temp_inv = AttitudeRepresentation(
            "quat", quat_inv(self.to("quat").components)
        )
        return temp_inv.to(self.name)

    def identity(self):
        """Returns the identity element of `SO3` as the current representation type, if possible

        :return: The identity element
        :rtype: AttitudeRepresentation
        """
        fcn = globals()[f"quat_to_{self.name}"]
        return AttitudeRepresentation(
            self.name, fcn(np.array([[0, 0, 0, 1.0]]))
        )

    def __pow__(self, n: int):
        if i == 0:
            return self.identity()
        self_to_the_n = self
        for i in range(n):
            self_to_the_n = self_to_the_n.__mul__(self_to_the_n)
        return self_to_the_n

    def __len__(self):
        return NotImplementedError("implement")

    def to_upper_hemisphere(self):
        """Transforms the attitude representation to the upper hemisphere of :math:`S^3` via quaternions

        :return: Upper hemisphere representation
        :rtype: AttitudeRepresentation
        """
        fcn = globals()[f"quat_to_{self.name}"]
        self_as_quat = self.to("quat")
        self.components = fcn(
            quat_upper_hemisphere(self_as_quat.components)
        )
        return self


class RbtfAttitude:
    """Class for rigid body torque free attitude propatation
    using accelerated semi-analytical solution with elliptic integrals
    """

    def __init__(
        self, w0: np.ndarray, q0: np.ndarray, itensor: np.ndarray
    ):
        self.w0, self.q0, self.itensor = w0, q0, itensor

    def propagate(self, epsec_space) -> np.ndarray:
        """Propagates attitude forward to all epoch seconds"""
        return propagate_attitude_torque_free(
            self.q0, self.w0, self.itensor, epsec_space
        )


def integrate_rigid_attitude_dynamics(
    q0: np.ndarray,
    omega0: np.ndarray,
    itensor: np.ndarray,
    teval: np.ndarray,
    body_torque: Callable = lambda t, y: np.zeros(3),
    int_tol: float = 1e-13,
) -> Tuple[np.ndarray, np.ndarray]:
    """Integration for rigid body rotational dynamics

    :param q0: Initial quaternion from inertial to body frame
    :type q0: np.ndarray [1x4]
    :param omega0: Initial angular velocity vector of body relative to inertial space [rad/s]
    :type omega0: np.ndarray [1x3]
    :param itensor: Principal inertia tensor [kg m^2]
    :type itensor: np.ndarray [3x3]
    :param teval: Times to return integrated trajectory at [second]
    :type teval: np.ndarray [nx1]
    :param body_torque: Body torques function `f(t,y) -> [3,]` [Nm], defaults to `np.zeros(3)`
    :type body_torque: Callable, optional
    :param int_tol: Integration rtol and atol for RK45, defaults to 1e-13
    :type int_tol: float, optional
    :return: Integrated quaternions [nx4]; integrated angular velocities [nx3]
    :rtype: Tuple[np.ndarray, np.ndarray]
    """
    fun = lambda t, y: np.concatenate(
        (
            quat_kinematics(y[:4], y[4:]),
            rigid_rotation_dynamics(
                t, y[4:], itensor, lambda t: body_torque(t, y[0:4])
            ),
        )
    )
    tspan = [np.min(teval), np.max(teval)]
    y0 = np.concatenate((q0, omega0))
    ode_res = scipy.integrate.solve_ivp(
        fun, tspan, y0, t_eval=teval, rtol=int_tol, atol=int_tol
    )
    return (ode_res.y.T[:, :4], ode_res.y.T[::, 4:])


def rigid_rotation_dynamics(
    t: float,
    w: np.ndarray,
    itensor: np.ndarray,
    torque: Callable = None,
) -> np.ndarray:
    """Rigid body rotational dynamics (Euler's equations of motion)

    :param t: Current integration time [seconds]
    :type t: float
    :param w: Angular velocity vector of body relative to inertial space [rad/s]
    :type w: np.ndarray [1x3]
    :param itensor: Inertia tensor in principal axes, should be diagonal [kg m^2]
    :type itensor: np.ndarray [3x3]
    :param torque: Torque applied to the body due to external forces [N m], defaults to None
    :type torque: Callable, optional
    :return: Angular acceleration vector [rad/s^2]
    :rtype: np.ndarray [1x3]
    """
    dwdt = np.zeros((3,))
    (ix, iy, iz) = np.diag(itensor)
    (wx, wy, wz) = w
    if torque is not None:
        (mx, my, mz) = torque(t)
    else:
        (mx, my, mz) = (0, 0, 0)

    dwdt[0] = -1 / ix * (iz - iy) * wy * wz + mx / ix
    dwdt[1] = -1 / iy * (ix - iz) * wz * wx + my / iy
    dwdt[2] = -1 / iz * (iy - ix) * wx * wy + mz / iz

    return dwdt


def gravity_gradient_torque(
    itensor: np.ndarray,
    rvec: np.ndarray,
    mu: float = AstroConstants.earth_mu,
) -> np.ndarray:
    """Computes gravity gradient torque in the body frame

    :param itensor: Inertia tensor in body axes [kg m^2]
    :type itensor: np.ndarray [3x3]
    :param rvec: Position vector of body [km]
    :type rvec: np.ndarray [1x3]
    :param mu: Gravitational parameter of central body, defaults to AstroConstants.earth_mu
    :type mu: float, optional
    :return: Gravity gradient torque in body frame [N m]
    :rtype: np.ndarray [1x3]
    """
    rmag = np.linalg.norm(rvec)
    # Distance from central body COM to satellite COM
    return (
        3
        * mu
        / rmag**5
        * np.cross(rvec.flatten(), (itensor @ rvec).flatten())
        / 1e3
    )
    # Torque applied to body [Nm]


def quat_kinematics(q: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Kinematic differential equations for quaternion time evolution

    :param q: Current quaternion from inertial to body
    :type q: np.ndarray [1x4]
    :param w: Current angular velocity in body frame [rad/s]
    :type w: np.ndarray [1x3]
    :return: Time derivative of input quaternion
    :rtype: np.ndarray [1x3]
    """
    return (
        1
        / 2
        * np.array(
            [
                [q[3], -q[2], q[1], q[0]],
                [q[2], q[3], -q[0], q[1]],
                [-q[1], q[0], q[3], q[2]],
                [-q[0], -q[1], -q[2], q[3]],
            ]
        )
        @ np.concatenate((w, [0]))
    )


def quat_ang(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """Angle between two quaternion arrays

    :param q1: Quaternion array
    :type q1: np.ndarray [nx4]
    :param q2: Quaternion array
    :type q2: np.ndarray [nx4]
    :return: Angle between quaternion arrays [rad]
    :rtype: np.ndarray [nx1]
    """
    return 2 * np.arccos(dot(q1, q2))


def mrp_add(s1: np.ndarray, s2: np.ndarray) -> np.ndarray:
    """Adds modified Rodrigues parameters (see quat_add)

    :param s1: Modified Rodrigues parameter array
    :type s1: np.ndarray [nx3]
    :param s2: Modified Rodrigues parameter array
    :type s2: np.ndarray [nx3]
    :return: Modified Rodrigues parameter array
    :rtype: np.ndarray [nx3]
    """
    return quat_to_mrp(quat_add(mrp_to_quat(s1), mrp_to_quat(s2)))


def rv_add(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    """Adds rotation vectors (see quat_add)

    :param p1: Rotation vector array
    :type p1: np.ndarray [nx3]
    :param p2: Rotation vector array
    :type p2: np.ndarray [nx3]
    :return: Rotation vector array
    :rtype: np.ndarray [nx3]
    """
    return quat_to_rv(quat_add(rv_to_quat(p1), rv_to_quat(p2)))


def quat_add(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """Adds (multiplies) quaternions together such that quat_add(inv_quat(q1), q2) gives the rotation between q1 and q2

    :param q1: Quaternion array
    :type q1: np.ndarray [nx4]
    :param q2: Quaternion array
    :type q2: np.ndarray [nx4]
    :return: Quaternion array
    :rtype: np.ndarray [nx4]
    """
    if q1.size == 4 and q2.size == 4:
        (q1, q2) = (np.reshape(q1, (1, 4)), np.reshape(q2, (1, 4)))
    elif q1.size == 4 and q2.shape[0] > 1:
        q1 = np.tile(q1, (q2.shape[0], 1))
    elif q1.shape[0] > 1 and q2.size == 4:
        q2 = np.tile(q2, (q1.shape[0], 1))

    nquats = q1.shape[0]
    q1d = np.reshape(q1, (nquats, 4, 1))
    q2dmat = np.array(
        [
            [q2[:, 3], q2[:, 2], -q2[:, 1], q2[:, 0]],
            [-q2[:, 2], q2[:, 3], q2[:, 0], q2[:, 1]],
            [q2[:, 1], -q2[:, 0], q2[:, 3], q2[:, 2]],
            [-q2[:, 0], -q2[:, 1], -q2[:, 2], q2[:, 3]],
        ]
    )
    q12 = np.matmul(np.moveaxis(q2dmat, 2, 0), q1d)
    q12 = np.reshape(q12, (nquats, 4))
    return q12


def mrp_to_rv(s: np.ndarray) -> np.ndarray:
    """Converts modified Rodrigues parameters to rotation vectors

    :param s: Modified Rodrigues parameter array
    :type s: np.ndarray [nx3]
    :return: Rotation vector array
    :rtype: np.ndarray [nx3]
    """
    return quat_to_rv(mrp_to_quat(s))


def mrp_to_dcm(s: np.ndarray) -> np.ndarray:
    """Converts modified Rodrigues parameters to direction cosine matrices

    :param s: Modified Rodrigues parameter array
    :type s: np.ndarray [nx3]
    :return: Direction cosine matrix array
    :rtype: np.ndarray [3x3xn]
    """
    return quat_to_dcm(mrp_to_quat(s))


def mrp_to_quat(s: np.ndarray) -> np.ndarray:
    """Converts modified Rodrigues parameters to quaternions

    :param s: Modified Rodrigues parameter array
    :type s: np.ndarray [nx3]
    :return: Quaternion array
    :rtype: np.ndarray [nx4]
    """
    s2 = np.sum(s * s, axis=1, keepdims=True)
    return np.hstack((2 * s / (1 + s2), (1 - s2) / (1 + s2)))


def quat_to_mrp(q: np.ndarray) -> np.ndarray:
    """Converts quaternions to modified Rodrigues parameters

    :param q: Quaternion array
    :type q: np.ndarray [nx4]
    :return: Modified Rodrigues parameter array
    :rtype: np.ndarray [nx3]
    """
    return q[:, 0:3] / (q[:, [3]] + 1)


def rv_to_mrp(p: np.ndarray) -> np.ndarray:
    """Converts rotation vectors to modified Rodrigues parameters via quaternions

    :param p: Rotation vector array
    :type p: np.ndarray [nx3]
    :return: Quaternion array
    :rtype: np.ndarray [nx4]
    """
    return quat_to_mrp(rv_to_quat(p))


def dcm_to_mrp(c: np.ndarray) -> np.ndarray:
    """Converts direction cosine matrices to modified Rodrigues parameters via quaternions

    :param c: Direction cosine matrix array
    :type c: np.ndarray [3x3xn]
    :return: MRP array
    :rtype: np.ndarray [nx3]
    """
    return quat_to_mrp(dcm_to_quat(c))


def rv_to_dcm(p: np.ndarray) -> np.ndarray:
    """Converts rotation vectors to direction cosine matrices

    :param p: Rotation vector array
    :type p: np.ndarray [nx3]
    :return: Direction cosine matrix array
    :rtype: np.ndarray [3x3xn]
    """
    return quat_to_dcm(rv_to_quat(p))


def quat_to_dcm(q: np.ndarray) -> np.ndarray:
    """Converts quaternions to direction cosine matrices

    :param q: Quaternion array
    :type q: np.ndarray [nx4]
    :return: Direction cosine matrix array
    :rtype: np.ndarray [3x3xn]
    """
    if q.ndim == 1:
        q = np.reshape(q, (1, 4))
    C = np.empty((3, 3, q.shape[0]))
    C[0, 0, :] = 1 - 2 * q[:, 1] ** 2 - 2 * q[:, 2] ** 2
    C[0, 1, :] = 2 * (q[:, 0] * q[:, 1] + q[:, 2] * q[:, 3])
    C[0, 2, :] = 2 * (q[:, 0] * q[:, 2] - q[:, 1] * q[:, 3])
    C[1, 0, :] = 2 * (q[:, 0] * q[:, 1] - q[:, 2] * q[:, 3])
    C[1, 1, :] = 1 - 2 * q[:, 0] ** 2 - 2 * q[:, 2] ** 2
    C[1, 2, :] = 2 * (q[:, 1] * q[:, 2] + q[:, 0] * q[:, 3])
    C[2, 0, :] = 2 * (q[:, 0] * q[:, 2] + q[:, 1] * q[:, 3])
    C[2, 1, :] = 2 * (q[:, 1] * q[:, 2] - q[:, 0] * q[:, 3])
    C[2, 2, :] = 1 - 2 * q[:, 0] ** 2 - 2 * q[:, 1] ** 2
    return np.squeeze(C)


def quat_to_rv(q: np.ndarray) -> np.ndarray:
    """Converts quaternions to rotation vectors

    :param q: Quaternion array
    :type q: np.ndarray [nx4]
    :return: Rotation vector array
    :rtype: np.ndarray [nx3]
    """
    if q.size == 4:
        q = np.reshape(q, (1, 4))
    theta, lam = 2 * np.arccos(q[:, [3]]), hat(q[:, 0:3])
    lam[
        np.isnan(lam[:, 0]), :
    ] = 0.0  # Accounting for origin singularity
    return theta * lam


def rv_to_quat(p: np.ndarray) -> np.ndarray:
    """Converts rotation vectors to quaternions

    :param p: Rotation vector array
    :type p: np.ndarray [nx3]
    :return: Quaternion array
    :rtype: np.ndarray [nx4]
    """
    theta, lam = vecnorm(p), hat(p)
    q = np.hstack((lam * np.sin(theta / 2), np.cos(theta / 2)))
    return q


def axis_rotation_matrices() -> Tuple[Callable, Callable, Callable]:
    """Rotation matrices about body axes

    :return: Callables for body axis rotations around (x, y, z) rotation angles in [rad]
    :rtype: Tuple[Callable, Callable, Callable]
    """
    r1 = lambda t: np.array(
        [
            [np.ones_like(t), np.zeros_like(t), np.zeros_like(t)],
            [np.zeros_like(t), np.cos(t), np.sin(t)],
            [np.zeros_like(t), -np.sin(t), np.cos(t)],
        ]
    )

    r2 = lambda t: np.array(
        [
            [np.cos(t), np.zeros_like(t), -np.sin(t)],
            [np.zeros_like(t), np.ones_like(t), np.zeros_like(t)],
            [np.sin(t), np.zeros_like(t), np.cos(t)],
        ]
    )

    r3 = lambda t: np.array(
        [
            [np.cos(t), np.sin(t), np.zeros_like(t)],
            [-np.sin(t), np.cos(t), np.zeros_like(t)],
            [np.zeros_like(t), np.zeros_like(t), np.ones_like(t)],
        ]
    )

    return (r1, r2, r3)


def quat_inv(q: np.ndarray) -> np.ndarray:
    """Finds the quaternion inverse (conjugate for unit quaternions)

    :param q: Input quaternion array
    :type q: np.ndarray [nx4]
    :return: Inverse quaternion array
    :rtype: np.ndarray [nx4]
    """
    if q.size == 4:
        q = np.reshape(q, (1, 4))
    qinv = -q
    qinv[:, 3] = -qinv[:, 3]
    return qinv


def quat_upper_hemisphere(q: np.ndarray) -> np.ndarray:
    """Transforms any quaternions in q to the upper hemisphere of S^3 such that `q[:,3] > 0`

    :param q: Quaternion array
    :type q: np.ndarray [nx4]
    :return: Transformed quaternion array
    :rtype: np.ndarray [nx4]
    """
    q[q[:, 3] < 0, :] = -q[q[:, 3] < 0, :]
    return q


def dcm_to_ea313(dcm: np.ndarray) -> np.ndarray:
    """Finds the Euler angle (3-1-3) body frame sequence corresponding to the input direction cosine matrices

    :param dcm: DCM array
    :type dcm: np.ndarray [3x3xn]
    :return: Euler angle array
    :rtype: np.ndarray [nx3]
    """
    eas = np.zeros((dcm.shape[2], 3))
    eas[:, 0] = atan2d(dcm[2, 0, :], -dcm[2, 1, :])
    eas[:, 1] = acosd(dcm[2, 2, :])
    eas[:, 2] = atan2d(dcm[0, 2, :], dcm[1, 2, :])
    return eas


def ea_to_dcm(
    seq: Tuple[int, int, int],
    a1: np.ndarray,
    a2: np.ndarray,
    a3: np.ndarray,
) -> np.ndarray:
    """Converts Euler angle (EA) sequence to DCMs

    :param seq: Axes to rotate about, ex: (1,2,3) gives 1-2-3 sequence
    :type seq: Tuple[int, int, int]
    :param a1: First rotation angle
    :type a1: np.ndarray [nx1]
    :param a2: Second rotation angle
    :type a2: np.ndarray [nx1]
    :param a3: Third rotation angle
    :type a3: np.ndarray [nx1]
    :return: Computed DCMs
    :rtype: np.ndarray [3x3xn]
    """
    assert all(seq < 4) and all(seq > 0), ValueError(
        "Euler angle sequence axes must be 1, 2, or 3"
    )
    rs = axis_rotation_matrices()
    r3 = rs[seq[0] - 1](a3)
    r2 = rs[seq[1] - 1](a2)
    r1 = rs[seq[2] - 1](a1)
    dcms = np.moveaxis(
        np.moveaxis(r1, -1, 0)
        @ np.moveaxis(r2, -1, 0)
        @ np.moveaxis(r3, -1, 0),
        0,
        -1,
    )
    return dcms


def dcm_to_rv(c: np.ndarray) -> np.ndarray:
    """Converts DCMs to rotation vectors by way of quaternions

    :param c: Input DCM array
    :type c: np.ndarray [3x3xn]
    :return: Computed rotation vectors
    :rtype: np.ndarray [nx3]
    """
    return quat_to_rv(dcm_to_quat(c))


def dcm_to_quat(c: np.ndarray) -> np.ndarray:
    """Converts DCMs to quaternions using Sheppard's method

    :param c: Input DCM array
    :type c: np.ndarray [3x3xn]
    :return: Computed quaternions
    :rtype: np.ndarray [nx4]
    """
    tr = np.trace(c, axis1=0, axis2=1)
    if c.ndim == 2:
        n = 1
        c = np.reshape(c, (3, 3, 1))
    elif c.ndim == 3:
        n = c.shape[2]

    e1_sq = 1 / 4 * (1 + 2 * c[0, 0, :] - tr)  # finds e1^2
    e2_sq = 1 / 4 * (1 + 2 * c[1, 1, :] - tr)  # finds e2^2
    e3_sq = 1 / 4 * (1 + 2 * c[2, 2, :] - tr)  # finds e3^2
    e4_sq = 1 / 4 * (1 + tr.flatten())  # finds e4^2

    q = np.zeros((c.shape[2], 4))
    test_vals = np.reshape((e1_sq, e2_sq, e3_sq, e4_sq), (4, n)).T
    # combines all values together

    best = np.argmax(test_vals, axis=1)
    (b1, b2, b3, b4) = (best == 0, best == 1, best == 2, best == 3)

    q[b1, 0] = np.sqrt(e1_sq[b1])
    q[b1, 1] = (c[0, 1, b1] + c[1, 0, b1]) / (4 * q[b1, 0])
    q[b1, 2] = (c[2, 0, b1] + c[0, 2, b1]) / (4 * q[b1, 0])
    q[b1, 3] = (c[1, 2, b1] - c[2, 1, b1]) / (4 * q[b1, 0])

    q[b2, 1] = np.sqrt(e2_sq[b2])
    q[b2, 0] = (c[0, 1, b2] + c[1, 0, b2]) / (4 * q[b2, 1])
    q[b2, 2] = (c[1, 2, b2] + c[2, 1, b2]) / (4 * q[b2, 1])
    q[b2, 3] = (c[2, 0, b2] - c[0, 2, b2]) / (4 * q[b2, 1])

    q[b3, 2] = np.sqrt(e3_sq[b3])
    q[b3, 0] = (c[2, 0, b3] + c[0, 2, b3]) / (4 * q[b3, 2])
    q[b3, 1] = (c[1, 2, b3] + c[2, 1, b3]) / (4 * q[b3, 2])
    q[b3, 3] = (c[0, 1, b3] - c[1, 0, b3]) / (4 * q[b3, 2])

    q[b4, 3] = np.sqrt(e4_sq[b4])
    q[b4, 0] = (c[1, 2, b4] - c[2, 1, b4]) / (4 * q[b4, 3])
    q[b4, 1] = (c[2, 0, b4] - c[0, 2, b4]) / (4 * q[b4, 3])
    q[b4, 2] = (c[0, 1, b4] - c[1, 0, b4]) / (4 * q[b4, 3])

    return q


def _analytic_torque_free_attitude(
    quat0: np.ndarray,
    omega: np.ndarray,
    itensor: np.ndarray,
    teval: np.ndarray,
    ksquared: float,
    tau0: float,
    tau_dot: float,
    is_sam: bool,
    itensor_org_factor: int = 1,
    itensor_inv_inds: list = [0, 1, 2],
) -> np.ndarray:
    """Analytically propagates orientation under torque-free rigid-body motion

    :param quat0: Quaternion from the body frame to inertial at initial time step
    :type quat0: np.ndarray [4x1]
    :param omega: Body angular velocities at each point in `teval` [rad/s]
    :type omega: np.ndarray [nx3]
    :param itensor: Principal inertia tensor satisfying `itensor[0,0] <= itensor[1,1] <= itensor[2,2]` [kg m^2]
    :type itensor: np.ndarray [3x3]
    :param teval: Times to output attitude soliution at, `teval[0]` corresponds to `quat0` and `omega[0,:]`
    :type teval: np.ndarray [nx1]
    :param ksquared: :math:`k^2` parameter from the angular velocity propagation
    :type ksquared: float
    :param tau0: Initial value of :math:`\tau` from the angular velocity propagation
    :type tau0: float
    :param tau_dot: Rate of change of :math:`\tau` from the angular velocity propagation
    :type tau_dot: float
    :param is_sam: Indicates the rotation mode. 0 = long-axis mode (LAM), 1 = short-axis mode (SAM)
    :type is_sam: bool
    :param itensor_org_factor: Indicates if an even or odd number of flips was required to reorganize the inertia tensor, defaults to 1
    :type itensor_org_factor: int, optional
    :param itensor_inv_inds: Inverse mapping from the user's inertia tensor to the one used here, defaults to [0, 1, 2]
    :type itensor_inv_inds: list, optional
    :return: Propagated quaternions at each time in `teval`
    :rtype: np.ndarray [nx1]
    """
    # Compute angular momentum vector and direction
    hvec = (itensor @ omega.T).T
    hmag = np.linalg.norm(hvec[0, :])
    hhat = hat(hvec[0, :])

    # separate itensor components
    (ix, iy, iz) = np.diag(itensor)

    # separate out the angular velocity components
    (wx, wy, wz) = (omega[:, 0], omega[:, 1], omega[:, 2])

    # get initial nutation angle
    if is_sam:
        theta0 = np.arccos(hhat[2])
    else:
        theta0 = np.arccos(hhat[0])

    (cT, sT, cT2, sT2) = (
        np.cos(theta0),
        np.sin(theta0),
        np.cos(theta0 / 2),
        np.sin(theta0 / 2),
    )

    # get initial spin angle
    if is_sam:
        psi0 = np.arctan2(hhat[0] / sT, hhat[1] / sT)
    else:
        psi0 = np.arctan2(hhat[2] / sT, -hhat[1] / sT)

    (cS, sS) = (np.cos(psi0), np.sin(psi0))
    (cS2, sS2) = (np.cos(psi0 / 2), np.sin(psi0 / 2))

    # get initial precession angle
    A = (cT + 1) * cT2 * cS2 + sT * sT2 * (cS * cS2 + sS * sS2)
    B = -(cT + 1) * cT2 * sS2 + sT * sT2 * (cS * sS2 - sS * cS2)
    C = np.sqrt(2 * (cT + 1))

    ti = np.real((B - np.sqrt(A**2 + B**2 - C**2 + 0j)) / (A + C))
    phi0 = 4 * np.arctan(ti)

    # compute the nutation and spin angles at each time step
    if is_sam:
        theta = np.arccos(iz * wz / hmag)
        psi = np.arctan2(ix * wx, iy * wy)
    else:
        theta = np.arccos(ix * wx / hmag)
        psi = np.arctan2(iz * wz, -iy * wy)

    # get Lambda value used to compute phi
    if is_sam:
        phi_denom = -iz * (ix - iy) / (ix * (iy - iz))
    else:
        phi_denom = -ix * (iz - iy) / (iz * (iy - ix))

    (_, _, _, amp0) = scipy.special.ellipj(tau0, ksquared)
    phi_lambda = -elliptic_pi_incomplete(phi_denom, amp0, ksquared)

    # compute the precession angles
    t = itensor_org_factor * (teval - teval[0])
    (_, _, _, ampt) = scipy.special.ellipj(tau_dot * t + tau0, ksquared)
    phi_pi = elliptic_pi_incomplete(phi_denom, ampt, ksquared)

    if is_sam:
        phi = (
            phi0
            + hmag / iz * t
            + hmag
            * (iz - ix)
            / (tau_dot * ix * iz)
            * (phi_pi + phi_lambda)
        )
    else:
        phi = (
            hmag / ix * t
            + phi0
            + hmag
            * (ix - iz)
            / (tau_dot * ix * iz)
            * (phi_pi + phi_lambda)
        )

    quat_r = _quat_r_from_eas(hhat, phi, theta, psi, is_sam).T
    quat_r[:, [0, 1, 2]] = quat_r[:, itensor_inv_inds]
    if itensor_org_factor == 1:
        quat_r = quat_inv(quat_r)
    # Compute the quaternions corresponding to the Euler angles
    quat_bi = quat_add(quat0, quat_r)
    return quat_bi


def _quat_r_from_eas(
    hhat: np.ndarray,
    phi: np.ndarray,
    theta: np.ndarray,
    psi: np.ndarray,
    is_sam: bool,
) -> np.ndarray:
    """Computes quaternion for attitude solution from Euler angle sequence

    :param hhat: Inertial angular momentum direction
    :type hhat: np.ndarray [1x3]
    :param phi: Spin angle [rad]
    :type phi: np.ndarray [nx1]
    :param theta: Nutation angle [rad]
    :type theta: np.ndarray [nx1]
    :param psi: Precession angle [rad]
    :type psi: np.ndarray [nx1]
    :param is_sam: Whether the rotation is short axis mode (SAM)
    :type is_sam: bool
    :return: Computed quaternions
    :rtype: np.ndarray [nx4]
    """
    (hx, hy, hz) = hhat
    (st2, ct2) = (np.sin(theta / 2), np.cos(theta / 2))
    (sm, sp, cm, cp) = (
        np.sin((phi - psi) / 2),
        np.sin((phi + psi) / 2),
        np.cos((phi - psi) / 2),
        np.cos((phi + psi) / 2),
    )

    if is_sam:
        return (
            1
            / np.sqrt(2 * (hz + 1))
            * np.array(
                [
                    -(hz + 1) * st2 * cm - ct2 * (hx * sp - hy * cp),
                    -(hz + 1) * st2 * sm - ct2 * (hx * cp + hy * sp),
                    -(hz + 1) * ct2 * sp + st2 * (hx * cm + hy * sm),
                    (hz + 1) * ct2 * cp + st2 * (hy * cm - hx * sm),
                ]
            )
        )
    else:
        return (
            1
            / np.sqrt(2 * (hx + 1))
            * np.array(
                [
                    -(hx + 1) * ct2 * sp + st2 * (hz * cm - hy * sm),
                    (hx + 1) * st2 * sm + ct2 * (hz * cp - hy * sp),
                    -(hx + 1) * st2 * cm - ct2 * (hy * cp + hz * sp),
                    (hx + 1) * ct2 * cp - st2 * (hy * cm + hz * sm),
                ]
            )
        )


def _analytic_torque_free_angular_velocity(
    omega0: np.ndarray,
    itensor: np.ndarray,
    teval: np.ndarray,
    itensor_org_factor: int = 1,
) -> Tuple[np.ndarray, float, float, float, bool]:
    """Analytically propogates angular velocity assuming no torque is being applied

    :param omega0: Initial angular velocity in body frame [rad/s]
    :type omega0: np.ndarray [3x1]
    :param itensor: Principal moments of inertia satisfying `i[3,3] < i[2,2] < i[1,1]` [kg m^2]
    :type itensor: np.ndarray [3x1]
    :param teval: Times to compute angular velocity for after initial state time [seconds]
    :type teval: np.ndarray [nx1]
    :param itensor_org_factor: If inertia tensor was reorganized with an even or odd number of flips, defaults to 1
    :type itensor_org_factor: int, optional
    :return: Angular velocity [rad/s]; :math:`k^2` term of elliptic integral, :math:`\tau_0`, :math:`\dot{\tau}`; short-axis model (SAM) flag
    :rtype: Tuple[np.ndarray [3x1], float, float, float, bool]
    """
    (wx0, wy0, wz0) = omega0  # Break up initial angular velocity
    # Angular momentum
    hvec = itensor @ omega0
    hmag = np.linalg.norm(hvec)

    # Rotational kinetic energy
    T = 0.5 * omega0.T @ itensor @ omega0

    idyn = hmag**2 / (2 * T)  # Dynamic moment of inertia
    we = 2 * T / hmag  # Effective angular velocity

    (ix, iy, iz) = np.diag(itensor)

    if idyn == iy:
        ValueError("Edge Case! Needs to be implemented")
    elif idyn < iy:  # For long axis mode rotation
        is_sam = False
        (ix, iz) = (iz, ix)
        (wx0, wz0) = (wz0, wx0)
    else:
        is_sam = True

    ibig_neg = 2 * int(wz0 > 0) - 1  # 1 if not negative, -1 else

    tau_dot = we * np.sqrt(
        idyn * (idyn - ix) * (iz - iy) / (ix * iy * iz)
    )
    ksquared = (iy - ix) * (iz - idyn) / ((iz - iy) * (idyn - ix))
    cos_phi = np.sqrt(ix * (iz - ix) / (idyn * (iz - idyn))) * wx0 / we
    sin_phi = np.sqrt(iy * (iz - iy) / (idyn * (iz - idyn))) * wy0 / we

    psi = ibig_neg * np.arctan2(sin_phi, cos_phi)
    tau0 = scipy.special.ellipkinc(psi, ksquared)
    tau = itensor_org_factor * tau_dot * (teval - teval[0]) + tau0
    (sn, cn, dn, _) = scipy.special.ellipj(tau, ksquared)

    wx = we * np.sqrt(idyn * (iz - idyn) / (ix * (iz - ix))) * cn
    wy = (
        ibig_neg
        * we
        * np.sqrt(idyn * (iz - idyn) / (iy * (iz - iy)))
        * sn
    )
    wz = (
        ibig_neg
        * we
        * np.sqrt(idyn * (idyn - ix) / (iz * (iz - ix)))
        * dn
    )

    if not is_sam:
        (wz, wx) = (wx, wz)

    omega = np.reshape((wx, wy, wz), (3, wx.size)).T
    return (omega, ksquared, tau0, tau_dot, is_sam)


def propagate_attitude_torque_free(
    quat0: np.ndarray,
    omega0: np.ndarray,
    itensor: np.ndarray,
    teval: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Computes torque free motion for a arbitrary inertia tensor using elliptic integrals and Jacobi elliptic functions

    :param quat0: Initial orientation as quaternion
    :type quat0: np.ndarray [1x4]
    :param omega0: Initial angular velocity [rad/s]
    :type omega0: np.ndarray [1x3]
    :param itensor: Inertia tensor in principal axes [kg m^2]
    :type itensor: np.ndarray [3x3]
    :param teval: Times to evaluate at past initial state [second]
    :type teval: np.ndarray [nx1]
    :return: Orientation of body over time as a quaternion and body frame angular velocity
    :rtype: Tuple[np.ndarray [nx4], np.ndarray [nx3]]
    """
    is_spherical_itensor = np.unique(np.diag(itensor)).size == 1
    is_single_axis = (
        vecnorm(hat(omega0) - np.array([[1, 0, 0]])) < 1e-14
        or vecnorm(hat(omega0) - np.array([[0, 1, 0]])) < 1e-14
        or vecnorm(hat(omega0) - np.array([[0, 0, 1]])) < 1e-14
    )
    is_inertially_fixed = vecnorm(omega0)[0] == 0

    # Checking for single-axis rotation cases
    if is_spherical_itensor or is_single_axis:
        # If spherically symmetric
        t = teval - teval[0]
        omega = np.tile(omega0, (teval.size, 1))
        quat_from_initial = rv_to_quat(np.expand_dims(t, 1) * omega)
        quat = quat_add(
            np.tile(quat0, (teval.size, 1)), quat_from_initial
        )
        return (quat, omega)
    if is_inertially_fixed:
        omega = np.tile(omega0, (teval.size, 1))
        quat = np.tile(quat0, (teval.size, 1))
        return (quat, omega)

    itensor_inds = np.argsort(np.diag(itensor))
    itensor_inv_inds = np.argsort(itensor_inds)
    moved_inds = np.argwhere(itensor_inds != [0, 1, 2]).flatten()
    itensor_org_factor = (
        2 * (moved_inds.size % 2 or moved_inds.size == 0) - 1
    )
    # Figures out how itensor should be organized to satisfy Ix <= Iy <= Iz
    itensor = np.diag(np.diag(itensor)[itensor_inds])
    omega0 = omega0[itensor_inds]

    (
        omega,
        ksquared,
        tau0,
        tau_dot,
        is_sam,
    ) = _analytic_torque_free_angular_velocity(
        omega0, itensor, teval, itensor_org_factor
    )
    quat = _analytic_torque_free_attitude(
        quat0=quat0,
        omega=omega,
        itensor=itensor,
        teval=teval,
        ksquared=ksquared,
        tau0=tau0,
        tau_dot=tau_dot,
        is_sam=is_sam,
        itensor_inv_inds=itensor_inv_inds,
        itensor_org_factor=itensor_org_factor,
    )

    omega = omega[:, itensor_inv_inds]
    # Reorganizes the inertia tensor to the user's input order

    return (quat, omega)


def rand_quaternions(num: int) -> np.ndarray:
    """Generates uniform random vectors on :math:`S^3` (interpreted as unit quaternions)

    :param num: Number of unit vectors to generate
    :type num: int
    :return: Sampled quaternions
    :rtype: np.ndarray [nx4]
    """
    u, v, w = (
        np.random.rand(num),
        np.random.rand(num),
        np.random.rand(num),
    )
    return np.array(
        [
            np.sqrt(1 - u) * np.sin(2 * np.pi * v),
            np.sqrt(1 - u) * np.cos(2 * np.pi * v),
            np.sqrt(u) * np.sin(2 * np.pi * w),
            np.sqrt(u) * np.cos(2 * np.pi * w),
        ]
    ).T
