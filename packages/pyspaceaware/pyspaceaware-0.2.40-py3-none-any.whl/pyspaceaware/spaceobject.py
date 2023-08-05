import os
import numpy as np
import scipy
from typing import Tuple
import pyvista as pv

from .math import (
    close_egi,
    dot,
    hat,
    merge_clusters,
    remove_zero_rows,
    unique_rows,
    vecnorm,
)
from .sampling import rand_cone_vectors
from .lighting import Brdf
from .orbit import propagate_satnum_to_dates

from .attitude import quat_to_rv, quat_to_dcm


def set_model_directory(path: str) -> None:
    """Sets the 3D model path used by all tools and methods

    :param path: Absolute or relative (from cwd) path to the model folder
    :type path: str
    """
    if os.path.isabs(path):
        os.environ["MODELDIR"] = path
    else:
        os.environ["MODELDIR"] = os.path.join(os.getcwd(), path)


class SpaceObject:
    def __init__(
        self,
        obj_file: str = None,
        obj_vf: Tuple[np.ndarray, np.ndarray] = None,
        is_dual: bool = False,
        satnum: int = None,
    ):
        """Initializes an instance of Object from either a) a path to a *.obj file or b) vertex and face adjacency information

        :param obj_file: `*.obj` file to read in the `$MODELDIR` folder, defaults to None
        :type obj_file: str, optional
        :param obj_vf: Vertex and face triangle information, defaults to None
        :type obj_vf: Tuple[np.ndarray, np.ndarray], optional
        :param is_dual: Flag to prevent building dual's dual (leading to infinite recursion), defaults to False
        :type is_dual: bool, optional
        :param satnum: NORAD satellite number for SGP4 propgation, defaults to None
        :type satnum: int, optional
        """
        self.satnum = satnum
        if obj_file is not None:
            self._def_mode = "file"
            self.file_name = obj_file
            self.path = os.path.join(os.environ["MODELDIR"], obj_file)
            self._mesh = pv.read(self.path)
            self.f = self._mesh.faces.reshape(-1, 4)[:, 1:]
            self.v = self._mesh.points
        elif obj_vf is not None:
            self._def_mode = "vf"
            self.v = obj_vf[0]
            self.f = obj_vf[1]
            padded_f = np.hstack(
                (
                    3 * np.ones((self.f.shape[0], 1), dtype=np.int64),
                    self.f,
                )
            ).flatten()
            self._mesh = pv.PolyData(self.v, padded_f)
        else:
            ValueError("Either obj_path or obj_vf must be input")
        self.is_dual = is_dual
        self.build_properties()

        if self._def_mode == "vf":
            self.flip_normals()

        if self.satnum is not None:
            self.propagate = (
                lambda date_space: propagate_satnum_to_dates(
                    date_space, satnum, "teme"
                )
            )
        else:
            self.propagate = ValueError(
                "Satellite does not have a satnum!"
            )

    def build_properties(self):
        """Builds all relevant object properties for shape inversion or visualization"""
        self.vertices_on_each_face()
        self.compute_face_normals()
        self.compute_face_areas()
        self.unique_areas_and_normals()
        self.compute_face_centroids()
        self.compute_supports()
        self.compute_volume()
        self.get_egi()
        self.get_inner_vertices()
        self.compute_inertia_tensor()
        if not self.is_dual:
            self.get_dual()

    def is_convex(self, volume_tol: float = 1e-3) -> bool:
        convhull_f = scipy.spatial.ConvexHull(self.v).simplices
        convhull_obj = SpaceObject(obj_vf=(self.v, convhull_f))
        return np.abs(self.volume - convhull_obj.volume) < volume_tol

    def vertices_on_each_face(self):
        """Computes a np.ndarray Nx3x3 of vertices on each face"""
        self.fv = self.v[self.f]

    def get_face_vertices(self) -> Tuple[np.ndarray]:
        """Reshapes face vertices into tuple of all 1st vertices, 2nd vertices, 3rd vertices"""
        return (self.fv[:, 0, :], self.fv[:, 1, :], self.fv[:, 2, :])

    def compute_face_centroids(self):
        """Computes the centroids of each face by averaging vertices"""
        (v1, v2, v3) = self.get_face_vertices()
        self.face_centroids = (v1 + v2 + v3) / 3

    def compute_face_normals(self):
        """Computes the normals of each face"""
        (v1, v2, v3) = self.get_face_vertices()
        self.face_normals = hat(np.cross(v2 - v1, v3 - v1))

    def compute_face_areas(self):
        """Computes the area of each face"""
        (v1, v2, v3) = self.get_face_vertices()
        self.face_areas = (
            vecnorm(np.cross(v2 - v1, v3 - v1)).flatten() / 2
        )

    def compute_supports(self, trunc_limit: float = 1e-7):
        """Computes the support (perpendicular distance from plane containing face to origin)"""
        (v1, _, _) = self.get_face_vertices()
        self.supports = dot(
            v1[self.all_to_unique, :], self.unique_normals
        )
        self.supports[self.supports < trunc_limit] = trunc_limit

    def compute_volume(self):
        """Computes the volume via the supports and unique areas"""
        self.volume = (
            1
            / 3
            * np.sum(
                self.supports.flatten() * self.unique_areas.flatten()
            )
        )

    def unique_areas_and_normals(self):
        """Finds groups of unique normals and areas to save rows elsewhere"""
        (
            self.unique_normals,
            self.all_to_unique,
            self.unique_to_all,
        ) = unique_rows(
            self.face_normals, return_index=True, return_inverse=True
        )
        self.unique_areas = np.zeros((self.unique_normals.shape[0]))
        np.add.at(
            self.unique_areas, self.unique_to_all, self.face_areas
        )

    def get_egi(self):
        """Computes the Extended Gaussian Image (EGI)"""
        self.egi = (
            np.expand_dims(self.unique_areas, 1) * self.unique_normals
        )

    def get_dual(self):
        """Sets the dual object"""
        dual_v = self.unique_normals / self.supports
        dual_f = scipy.spatial.ConvexHull(dual_v).simplices
        self.dual = SpaceObject(obj_vf=(dual_v, dual_f), is_dual=True)

    def get_inner_vertices(self):
        """Computes which vertices are within the convex hull (not contained in any faces of the convex hull)"""
        nvert = self.v.shape[0]
        self.verts_within_convhull = np.setdiff1d(
            np.arange(0, nvert), np.unique(self.f)
        )

    def flip_normals(self):
        """For convex objects, flips any normal vectors pointing inside the object"""
        n_points_in = (
            dot(self.face_centroids, self.face_normals).flatten() < 0
        )
        if any(n_points_in):
            self.f[n_points_in, :] = np.array(
                [
                    self.f[n_points_in, 0],
                    self.f[n_points_in, 2],
                    self.f[n_points_in, 1],
                ]
            ).T
            self.build_properties()

    def render(
        self,
        pl: pv.Plotter,
        origin: np.ndarray = np.array([0, 0, 0]),
        scale: float = 1,
        quat: np.ndarray = np.array([[0, 0, 0, 1]]),
        **kwargs
    ):
        """Plots the object mesh using :py:mod:`pyvista`

        :param pl: Plotter to render object with
        :type pl: pv.Plotter
        """
        scalem = np.vstack(
            (
                np.hstack((np.eye(3) * scale, np.zeros((3, 1)))),
                [[0, 0, 0, 1]],
            )
        )
        rotm4 = np.vstack(
            (
                np.hstack((quat_to_dcm(quat).T, np.zeros((3, 1)))),
                [[0, 0, 0, 1]],
            )
        )
        rotm4[:3, 3] = origin
        mat4 = rotm4 @ scalem

        if "obj" in pl.actors:
            obj_actor = pl.actors["obj"]
        else:
            obj_actor = pl.add_mesh(self._mesh, name="obj", **kwargs)
        obj_actor.user_matrix = mat4

    def compute_convex_light_curve(
        self, brdf: Brdf, svb: np.ndarray, ovb: np.ndarray
    ) -> np.ndarray:
        """Computes the light curve of a covex object with a given BRDF :cite:t:`fan2020thesis`

        :param brdf: BRDF to render with
        :type brdf: Brdf
        :param svb: Sun unit vectors in the body frame
        :type svb: np.ndarray [nx1]
        :param ovb: Observer unit vectors in the body frame
        :type ovb: np.ndarray [nx1]
        :return: Observed irradiance at unit distance
        :rtype: np.ndarray [nx1]
        """
        g = brdf.compute_reflection_matrix(
            svb, ovb, self.unique_normals
        )
        return g @ self.unique_areas

    def rotate_by_quat(self, quat: np.ndarray) -> None:
        """Rotates the object's mesh by the given quaternion

        :param quat: Quaternion to apply to all vertices
        :type quat: np.ndarray [1x4]
        """
        rv = quat_to_rv(quat)
        theta = vecnorm(rv)[0][0]
        lam = hat(rv)[0]
        if theta == 0:
            lam = np.array([1.0, 0.0, 0.0])
        self._mesh.copy_from(
            self._mesh.rotate_vector(
                vector=lam, angle=np.rad2deg(theta)
            )
        )

    def compute_inertia_tensor(self):
        """Computes the body-frame inertia tensor of the object (`MatlabCentral <https://www.mathworks.com/matlabcentral/fileexchange/48913-rigid-body-parameters-of-closed-surface-meshes>`_)"""

        fn = 2 * np.expand_dims(self.face_areas, 1) * self.face_normals
        (v1, v2, v3) = self.get_face_vertices()
        (x1, y1, z1) = (v1[:, 0], v1[:, 1], v1[:, 2])
        (x2, y2, z2) = (v2[:, 0], v2[:, 1], v2[:, 2])
        (x3, y3, z3) = (v3[:, 0], v3[:, 1], v3[:, 2])
        m000 = self.volume
        if (
            m000 == 0
        ):  # Then the mesh has zero volume, this is waste of time
            return

        x_2 = ((x1 + x2) * (x2 + x3) + x1**2 + x3**2) / 12
        y_2 = ((y1 + y2) * (y2 + y3) + y1**2 + y3**2) / 12
        z_2 = ((z1 + z2) * (z2 + z3) + z1**2 + z3**2) / 12
        xy = (
            (x1 + x2 + x3) * (y1 + y2 + y3)
            + x1 * y1
            + x2 * y2
            + x3 * y3
        ) / 24
        xz = (
            (x1 + x2 + x3) * (z1 + z2 + z3)
            + x1 * z1
            + x2 * z2
            + x3 * z3
        ) / 24
        yz = (
            (y1 + y2 + y3) * (z1 + z2 + z3)
            + y1 * z1
            + y2 * z2
            + y3 * z3
        ) / 24
        m100 = np.sum(fn * np.array([x_2, 2 * xy, 2 * xz]).T) / 6
        m010 = np.sum(fn * np.array([2 * xy, y_2, 2 * yz]).T) / 6
        m001 = np.sum(fn * np.array([2 * xz, 2 * yz, z_2]).T) / 6
        # Second order moments (used to determine elements of the inertia tensor)
        x_3 = (
            (x1 + x2 + x3) * (x1**2 + x2**2 + x3**2)
            + x1 * x2 * x3
        ) / 20
        y_3 = (
            (y1 + y2 + y3) * (y1**2 + y2**2 + y3**2)
            + y1 * y2 * y3
        ) / 20
        z_3 = (
            (z1 + z2 + z3) * (z1**2 + z2**2 + z3**2)
            + z1 * z2 * z3
        ) / 20
        x_2y = (
            (3 * y1 + y2 + y3) * x1**2
            + (y1 + 3 * y2 + y3) * x2**2
            + (y1 + y2 + 3 * y3) * x3**2
            + (2 * y1 + 2 * y2 + y3) * x1 * x2
            + (2 * y1 + y2 + 2 * y3) * x1 * x3
            + (y1 + 2 * y2 + 2 * y3) * x2 * x3
        ) / 60
        x_2z = (
            (3 * z1 + z2 + z3) * x1**2
            + (z1 + 3 * z2 + z3) * x2**2
            + (z1 + z2 + 3 * z3) * x3**2
            + (2 * z1 + 2 * z2 + z3) * x1 * x2
            + (2 * z1 + z2 + 2 * z3) * x1 * x3
            + (z1 + 2 * z2 + 2 * z3) * x2 * x3
        ) / 60
        y_2x = (
            (3 * x1 + x2 + x3) * y1**2
            + (x1 + 3 * x2 + x3) * y2**2
            + (x1 + x2 + 3 * x3) * y3**2
            + (2 * x1 + 2 * x2 + x3) * y1 * y2
            + (2 * x1 + x2 + 2 * x3) * y1 * y3
            + (x1 + 2 * x2 + 2 * x3) * y2 * y3
        ) / 60
        y_2z = (
            (3 * z1 + z2 + z3) * y1**2
            + (z1 + 3 * z2 + z3) * y2**2
            + (z1 + z2 + 3 * z3) * y3**2
            + (2 * z1 + 2 * z2 + z3) * y1 * y2
            + (2 * z1 + z2 + 2 * z3) * y1 * y3
            + (z1 + 2 * z2 + 2 * z3) * y2 * y3
        ) / 60
        z_2y = (
            (3 * y1 + y2 + y3) * z1**2
            + (y1 + 3 * y2 + y3) * z2**2
            + (y1 + y2 + 3 * y3) * z3**2
            + (2 * y1 + 2 * y2 + y3) * z1 * z2
            + (2 * y1 + y2 + 2 * y3) * z1 * z3
            + (y1 + 2 * y2 + 2 * y3) * z2 * z3
        ) / 60
        z_2x = (
            (3 * x1 + x2 + x3) * z1**2
            + (x1 + 3 * x2 + x3) * z2**2
            + (x1 + x2 + 3 * x3) * z3**2
            + (2 * x1 + 2 * x2 + x3) * z1 * z2
            + (2 * x1 + x2 + 2 * x3) * z1 * z3
            + (x1 + 2 * x2 + 2 * x3) * z2 * z3
        ) / 60
        xyz = (
            (x1 + x2 + x3) * (y1 + y2 + y3) * (z1 + z2 + z3)
            - (y2 * z3 + y3 * z2 - 4 * y1 * z1) * x1 / 2
            - (y1 * z3 + y3 * z1 - 4 * y2 * z2) * x2 / 2
            - (y1 * z2 + y2 * z1 - 4 * y3 * z3) * x3 / 2
        ) / 60
        m110 = np.sum(fn * np.array([x_2y, y_2x, 2 * xyz]).T) / 6
        m101 = np.sum(fn * np.array([x_2z, 2 * xyz, z_2x]).T) / 6
        m011 = np.sum(fn * np.array([2 * xyz, y_2z, z_2y]).T) / 6
        m200 = np.sum(fn * np.array([x_3, 3 * x_2y, 3 * x_2z]).T) / 9
        m020 = np.sum(fn * np.array([3 * y_2x, y_3, 3 * y_2z]).T) / 9
        m002 = np.sum(fn * np.array([3 * z_2x, 3 * z_2y, z_3]).T) / 9

        # Inertia tensor
        Ixx = m020 + m002 - (m010**2 + m001**2) / m000
        Iyy = m200 + m002 - (m100**2 + m001**2) / m000
        Izz = m200 + m020 - (m100**2 + m010**2) / m000
        Ixy = m110 - m100 * m010 / m000
        Ixz = m101 - m100 * m001 / m000
        Iyz = m011 - m010 * m001 / m000
        self.itensor = np.array(
            [[Ixx, -Ixy, -Ixz], [-Ixy, Iyy, -Iyz], [-Ixz, -Iyz, Izz]]
        )
        self.itensor[np.abs(self.itensor) < 1e-7] = 0

        # Extracting principal axes and PMOIs
        (eig_vals, eig_vecs) = np.linalg.eig(self.itensor)
        eig_vecs[:, 2] = eig_vecs[:, 2] * np.linalg.det(eig_vecs)
        self.principal_itensor = np.diag(eig_vals)
        self.body_to_principal_axes = eig_vecs


def build_dual(normals: np.array, supports: np.array) -> SpaceObject:
    """Computes the polyhedral dual of the set of normals and supports

    :param normals: Outward-facing normal vectors
    :type normals: np.array [nx3]
    :param supports: Support of each face (see :py:meth:`get_supports`)
    :type supports: np.array [nx1]
    :return: Dual object defined by the normals and supports
    :rtype: SpaceObject
    """
    dual_v = normals / supports
    dual_f = scipy.spatial.ConvexHull(dual_v).simplices
    return SpaceObject(obj_vf=(dual_v, dual_f), is_dual=True)


def construct_from_egi_and_supports(
    egi: np.array, support: np.array
) -> SpaceObject:
    """Constructs an object from an input Extended Gaussian Image (EGI) and support set

    :param egi: EGI of the object
    :type egi: np.array [nx3]
    :param support: Supports of each face in the EGI
    :type support: np.array [nx1]
    :return: Resulting convex object, with potentially fewer faces than the original EGI depending on supports selected
    :rtype: SpaceObject
    """
    dual_obj = build_dual(hat(egi), np.expand_dims(support, axis=1))
    b = np.ones((dual_obj.f.shape[0], 3, 1))
    rec_obj_verts = np.reshape(
        np.linalg.solve(dual_obj.fv, b), (dual_obj.f.shape[0], 3)
    )
    rec_obj_faces = scipy.spatial.ConvexHull(rec_obj_verts).simplices
    rec_obj = SpaceObject(obj_vf=(rec_obj_verts, rec_obj_faces))
    return (rec_obj, dual_obj)


def optimize_egi(
    lc: np.ndarray,
    svb: np.ndarray,
    ovb: np.ndarray,
    brdf: Brdf,
    num_candidates: int = int(1e3),
    merge_iter: int = 1,
    merge_angle: float = np.pi / 10,
) -> np.ndarray:
    """Optimizes an Extended Gaussian Image (EGI) to fit observed irradiances :cite:p:`robinson2022`

    :param lc: Unit irradiance light curve
    :type lc: np.ndarray [nx1]
    :param svb: Sun unit vectors in the body frame for each observation
    :type svb: np.ndarray [nx3]
    :param ovb: Observer unit vectors in the body frame
    :type ovb: np.ndarray [nx3]
    :param brdf: BRDF to use
    :type brdf: Brdf
    :param num_candidates: Number of candidate normal vectors to fit, defaults to int(1e3)
    :type num_candidates: int, optional
    :param merge_iter: Number of iterations for the merging step, defaults to 1
    :type merge_iter: int, optional
    :param merge_angle: Angle between vectors to merge by, defaults to np.pi/10
    :type merge_angle: float, optional
    :return: Optimized EGI
    :rtype: np.ndarray
    """
    normal_candidates = rand_cone_vectors(
        np.array([0, 0, 1]), np.pi, num_candidates
    )
    g_candidates = brdf.compute_reflection_matrix(
        svb, ovb, normal_candidates
    )
    a_candidates = np.expand_dims(
        scipy.optimize.nnls(g_candidates, lc.flatten())[0], axis=1
    )
    egi_candidate = normal_candidates * a_candidates
    egi_candidate = remove_zero_rows(egi_candidate)
    egi_candidate = merge_clusters(
        egi_candidate, merge_angle, miter=merge_iter
    )
    return close_egi(egi_candidate)


def get_volume(h: np.ndarray, egi: np.ndarray) -> float:
    """Computes the volume of the polytope represented by the supports and EGI input

    :param h: Support vector
    :type h: np.ndarray [nx1]
    :param egi: Extended Gaussian image to reconstruct from
    :type egi: np.ndarray [nx3]
    :return: Volume of the reconstructed convex polytope
    :rtype: float
    """
    (p, _) = construct_from_egi_and_supports(egi=egi, support=h)
    return p.volume


def little_fun(h: np.ndarray, egi: np.ndarray) -> float:
    """Little's objective function for support vector optimization :cite:t:`little1983`

    :param h: Supports vector
    :type h: np.ndarray [nx1]
    :param egi: Extended Gaussian image to reconstruct from
    :type egi: np.ndarray [nx3]
    :return: Objective function value :math:`f=(h \cdot a)`
    :rtype: float
    """
    v = dot(h, vecnorm(egi).flatten())[0]
    print(h)
    return v


def optimize_supports_little(egi: np.ndarray) -> np.ndarray:
    """Optimizes a support vector to construct the polytope with the given Extended Gaussian Image (EGI) :cite:t:`little1983`

    :param egi: EGI to find supports for, convergence only possible if the sum of rows is zero. See :meth:`close_egi`
    :type egi: np.ndarray [nx3]
    :return: Optimal set of supports
    :rtype: np.ndarray [nx1]
    """
    jac = lambda h: vecnorm(egi).flatten()
    hess = lambda h: np.zeros(egi[:, 0].size)
    cons = {
        "type": "eq",
        "fun": lambda h: get_volume(h, egi) - 1,
        "keep_feasible": True,
    }
    res = scipy.optimize.minimize(
        lambda h: little_fun(h, egi),
        np.ones(egi.shape[0]) / np.sum(vecnorm(egi)),
        method="trust-constr",
        constraints=cons,
        jac=jac,
        options={"disp": True, "gtol": 1e-3},
        bounds=[(0, None) for i in range(egi.shape[0])],
    )

    (rec_obj_unit, _) = construct_from_egi_and_supports(
        egi=egi, support=res.x
    )
    h_opt = (
        np.sqrt(
            np.sum(vecnorm(egi)) / np.sum(vecnorm(rec_obj_unit.egi))
        )
        * res.x
    )
    return h_opt
