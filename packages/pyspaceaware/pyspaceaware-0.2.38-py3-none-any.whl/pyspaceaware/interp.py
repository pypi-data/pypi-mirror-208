import numpy as np
import scipy
import os
import pickle

from .math import cart_to_sph, sph_to_cart
from .engine import run_engine
from .lighting import Brdf
from .spaceobject import SpaceObject


class InterpBrightnessModel:
    """Interpolates brightness by evaluating full non-convex rendered brightness in 4D rectilinear grid of azimuth and elevation to parameterize the observer and lighting directions"""

    def __init__(
        self,
        model_name: str = None,
        brdf: Brdf = None,
        path: str = None,
        use_engine: bool = True,
        method: str = "linear",
    ):
        self.method = method
        self.use_engine = use_engine
        if model_name is not None and brdf is not None:
            self.model_name = model_name
            self.brdf = brdf
        elif path is not None:
            self.load_from_file(path)
        self.get_file_name = (
            lambda: f"{self.model_name[:-4]}_{self.brdf.name}_cd_{self.brdf.cd}_cs_{self.brdf.cs}_n_{self.brdf.n}_{self.method}_ord_{self.order}.pkl"
        )

    def _f_engine(
        self,
        laz: np.ndarray,
        lel: np.ndarray,
        oaz: np.ndarray,
        oel: np.ndarray,
    ) -> np.ndarray:
        """True brightness function, evaluates using the LightCurveEngine renderer

        :param laz: Lighting azimuth in the body frame [rad]
        :type laz: np.ndarray
        :param lel: Lighting elevation in the body frame [rad]
        :type lel: np.ndarray
        :param oaz: Observer azimuth in the body frame [rad]
        :type oaz: np.ndarray
        :param oel: Observer elevation in the body frame [rad]
        :type oel: np.ndarray
        :return: Unit distance irradiance in given observation geometry [W/m^2]
        :rtype: np.ndarray
        """
        (x1, y1, z1) = sph_to_cart(laz, lel, lel * 0 + 1)
        L = np.vstack((x1, y1, z1)).T
        (x2, y2, z2) = sph_to_cart(oaz, oel, oel * 0 + 1)
        O = np.vstack((x2, y2, z2)).T
        if self.use_engine:
            nper = 1e4
            runcount = int(np.ceil(L.shape[0] / nper))
            lc = []
            for i in range(runcount):
                lower_ind = int(i * nper)
                upper_ind = min(int((i + 1) * nper), L.shape[0])
                inds = list(range(lower_ind, upper_ind))
                lc.append(
                    run_engine(
                        self.brdf,
                        self.model_name,
                        L[inds, :],
                        O[inds, :],
                    )
                )
            return np.vstack(lc)
        else:
            obj = SpaceObject(self.model_name)
            lc = obj.compute_convex_light_curve(self.brdf, L, O)
            return np.reshape(lc, (lc.size, 1))

    def build_from_engine(self, dimn: int = 10) -> None:
        """Builds the interpolated model, enables ``self.eval(points)`` after completion

        :param dimn: Size of each linear dimension, defaults to 10
        :type dimn: int, optional
        """
        assert dimn > 0 and isinstance(
            dimn, int
        ), "Model order must be a positive integer"
        self.order = dimn
        saz, sel = np.linspace(-np.pi, np.pi, dimn), np.linspace(
            -np.pi / 2, np.pi / 2, dimn
        )
        self.grid_pts = (saz, sel, saz, sel)
        (gaz1, gel1, gaz2, gel2) = np.meshgrid(
            saz, sel, saz, sel, indexing="ij"
        )
        lc = self._f_engine(
            gaz1.flatten(),
            gel1.flatten(),
            gaz2.flatten(),
            gel2.flatten(),
        )
        self.data = np.reshape(lc, gaz1.shape)
        self.make_interpolator()

    def save_to_file(self, directory: str = "") -> None:
        """Saves the model to the directory provided

        :param directory: Directory to save model in, defaults to ""
        :type directory: str, optional
        """
        path = os.path.join(
            directory,
            self.get_file_name(),
        )
        with open(path, "wb") as f:
            grids_as_list = tuple([g.tolist() for g in self.grid_pts])
            save_data = {
                "data": self.data.tolist(),
                "grid_pts": grids_as_list,
                "brdf": {
                    "name": self.brdf.name,
                    "cd": self.brdf.cd,
                    "cs": self.brdf.cs,
                    "n": self.brdf.n,
                },
                "model_name": self.model_name,
            }
            pickle.dump(save_data, f)

    def load_from_file(self, path: str) -> None:
        """Loads and builds the interpolator from a saved pickle file containing the brightness data and interpolator grids

        :param path: Path to the pickle file containing the saved data
        :type path: str
        """
        with open(path, "rb") as f:
            d = pickle.load(f)
        self.data = np.array(d["data"])
        self.grid_pts = tuple([np.array(g) for g in d["grid_pts"]])
        self.brdf = Brdf(
            name=d["brdf"]["name"],
            cd=d["brdf"]["cd"],
            cs=d["brdf"]["cs"],
            n=d["brdf"]["n"],
        )
        self.model_name = d["model_name"]
        self.order = self.grid_pts[0].shape[0]
        self.make_interpolator()

    def make_interpolator(self) -> None:
        """Builds the interpolator"""
        self.interp = scipy.interpolate.RegularGridInterpolator(
            self.grid_pts, self.data, method=self.method
        )
        self.is_built = True

    def eval(self, L: np.ndarray, O: np.ndarray) -> np.ndarray:
        """Evaluates the brightness model with the given observer and sun unit vectors in the body frame

        :param L: Sun vector in body frame, length irrelevant
        :type L: np.ndarray [nx3]
        :param O: Observer vector in body frame, length irrelevant
        :type O: np.ndarray [nx3]
        :raises AttributeError: If the model has not been built yet
        :return: Interpolated normalized irradiances [W/m^2]
        :rtype: np.ndarray [nx1]
        """
        if self.is_built:
            (az1, el1, _) = cart_to_sph(L[:, 0], L[:, 1], L[:, 2])
            (az2, el2, _) = cart_to_sph(O[:, 0], O[:, 1], O[:, 2])
            return self.interp((az1, el1, az2, el2))
        else:
            raise AttributeError("Interpolator not available")
