import numpy as np

from .math import hat, rdot, dot

_SUPPORTED_BRDFS = ["phong", "diffuse"]


def brdf_diffuse(cd: np.ndarray) -> np.ndarray:
    """Bidirectional Reflectance Distribution Function (BRDF) reflectance for a diffuse surface

    :param cd: Coefficients of diffuse reflection for each face
    :type cd: np.ndarray
    :return: Fraction of incident light reflected towards observer
    :rtype: np.ndarray
    """
    return cd / np.pi


def brdf_phong(
    L: np.ndarray,
    O: np.ndarray,
    N: np.ndarray,
    cd: np.ndarray,
    cs: np.ndarray,
    n: np.ndarray,
) -> np.ndarray:
    """Bidirectional Reflectance Distribution Function (BRDF) reflectance for the Phong model

    :param L: Unit vector illumination directions
    :type L: np.ndarray [nx3]
    :param O: Unit vector observation directions
    :type O: np.ndarray [nx3]
    :param N: Unit vector surface normals
    :type N: np.ndarray [nx3]
    :param cd: Coefficients of diffuse reflection for each face
    :type cd: np.ndarray [nx1]
    :param cs: Coefficients of specular reflection for each face
    :type cs: np.ndarray [nx1]
    :param n: Specular exponents for each face
    :type n: np.ndarray [nx1]
    :return: Fraction of incident light reflected towards observer
    :rtype: np.ndarray [nx1]
    """
    NdL = rdot(N, L)
    R = hat(2 * dot(N, L) * N - L)
    fd = brdf_diffuse(cd)
    fs = cs * (n + 1) / (2 * np.pi) * rdot(R, O) ** n / NdL
    fs[
        NdL <= 0
    ] = 0.0  # To account for beyond horizon NdL div by zero above
    return fd + fs


class Brdf:
    def __init__(
        self,
        name: str,
        cd: float = None,
        cs: float = None,
        n: int = None,
    ):
        """Class for representing Bidirectional Reflectance Distribution Functions (BRDFs)

        :param name: BRDF to use, must be a registered name
        :type name: str
        :param cd: Coefficient of diffuse reflection, defaults to None if .mtl file should be used
        :type cd: float, optional
        :param cs: Coefficient of specula reflection, defaults to None if .mtl file should be used
        :type cs: float, optional
        :param n: Specular exponent, defaults to None if .mtl file should be used
        :type n: int, optional
        """
        self.name = name
        self.cd = cd
        self.cs = cs
        self.n = n
        self.use_mtl = False
        if self.cd is None and self.cs is None and self.n is None:
            self.use_mtl = True
        self.validate()

    def validate(self):
        """Decides if a BRDF is valid

        :raises: `ValueError` if energy conservation/other violations are made
        """
        if not self.use_mtl:
            assert self.cd != 0 or self.cs != 0, ValueError(
                "your BRDF is boring"
            )
            assert self.cd >= 0 and self.cs >= 0, ValueError(
                "cd and cs must be >= 0 for energy conservation"
            )
            assert self.cd + self.cs <= 1, ValueError(
                "cd + cs must be <= 1 for energy conservation"
            )
            if self.n is None:
                assert (
                    self.name == "diffuse"
                ), "specular exponent 'n' kwarg required"
            if self.n is not None:
                assert self.n > 0, ValueError(
                    "n > 0 for a physical brdf"
                )
        assert self.name in _SUPPORTED_BRDFS, ValueError(
            "only 'phong' supported as BRDF name"
        )

    def eval(
        self, L: np.ndarray, O: np.ndarray, N: np.ndarray
    ) -> np.ndarray:
        """Evaluates the BRDF with the given observation and illumination geometry

        :param L: Unit vector illumination directions
        :type L: np.ndarray [nx3]
        :param O: Unit vector observation directions
        :type O: np.ndarray [nx3]
        :param N: Unit vector surface normals
        :type N: np.ndarray [nx3]
        :return: Fraction of incident irradiance reflected towards observer
        :rtype: np.ndarray [nx1]
        """
        if self.name == "phong":
            return brdf_phong(L, O, N, self.cd, self.cs, self.n)
        elif self.name == "diffuse":
            return np.tile(brdf_diffuse(self.cd), (L.shape[0], 1))

    def eval_normalized_brightness(
        self, L: np.ndarray, O: np.ndarray, N: np.ndarray
    ) -> np.ndarray:
        """Computes the observed irradiance at a unit distance for this BRDF

        :param L: Unit vector illumination directions
        :type L: np.ndarray [nx3]
        :param O: Unit vector observation directions
        :type O: np.ndarray [nx3]
        :param N: Unit vector surface normals
        :type N: np.ndarray [nx3]
        :return: Fraction of incident irradiance reflected towards observer at unit distance
        :rtype: np.ndarray [nx1]
        """
        fr = self.eval(L, O, N)
        lc = fr * rdot(N, O) * rdot(N, L)
        return lc

    def compute_reflection_matrix(
        self, L: np.array, O: np.array, N: np.array
    ) -> np.ndarray:
        """Computes the reflection matrix for the EGI estimation stage of shape inversion
        (or for convex shape light curve simulation)

        :param L: Unit vector illumination directions
        :type L: np.array [nx3]
        :param O: Unit vector observation directions
        :type O: np.array [nx3]
        :param N: Unit vector surface normals
        :type N: np.array [mx3]
        :return: Reflection matrix, (i,j) entry is normalized irradiance per unit area for facet j at time i
        :rtype: np.ndarray [nxm]
        """
        assert L.shape[0] == O.shape[0], ValueError(
            "Size of illumination vectors must match observer vectors"
        )
        geom_count = L.shape[0]
        normal_count = N.shape[0]
        [v1_grid, v2_grid] = np.meshgrid(
            np.arange(0, geom_count), np.arange(0, normal_count)
        )
        # Grid of values for each time and facet
        ov_all = O[
            v1_grid.flatten(), :
        ]  # Column vector of all observer vectors
        sv_all = L[
            v1_grid.flatten(), :
        ]  # Column vector of all sun vectors
        nv_all = N[
            v2_grid.flatten(), :
        ]  # Column vector of all normal vectors

        lc_all = self.eval_normalized_brightness(sv_all, ov_all, nv_all)
        return np.reshape(lc_all, (geom_count, normal_count), order="F")


def apparent_magnitude_to_irradiance(m: np.ndarray) -> np.ndarray:
    """Computes irradiance [W/m^2] from apparent magnitude (assumed same spectrum as sunlight)

    :param m: Apparent magnitude
    :type m: np.ndarray
    :return: Irradiance [W/m^2]
    :rtype: np.ndarray
    """
    return (2.518021002e-8) * 10 ** (-0.4 * m)


def irradiance_to_apparent_magnitude(E: np.ndarray) -> np.ndarray:
    """Computes apparent magnitude from irradiance [W/m^2] (assumed same spectrum as sunlight)

    :param m: Irradiance [W/m^2]
    :type m: np.ndarray
    :return: Apparent magnitude
    :rtype: np.ndarray
    """
    return -2.5 * np.log10(E / 2.518021002e-8)
