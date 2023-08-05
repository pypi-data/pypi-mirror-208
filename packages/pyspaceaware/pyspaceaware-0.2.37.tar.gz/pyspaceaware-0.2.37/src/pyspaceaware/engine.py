import os
import numpy as np

from .lighting import Brdf


def run_engine(
    brdf: Brdf,
    model_file: str,
    svb: np.ndarray,
    ovb: np.ndarray,
    save_imgs: bool = False,
    output_dir: str = None,
    instance_count: int = 9,
) -> np.ndarray:
    """Runs the LightCurveEngine executable on the input model, observation geometry, and BRDF

    :param brdf: BRDF to use
    :type brdf: Brdf
    :param model_file: *.obj file to use
    :type model_file: str
    :param svb: Sun vectors in the object body frame
    :type svb: np.ndarray [nx3]
    :param ovb: Observer vectors in the object body frame
    :type ovb: np.ndarray [nx3]
    :param save_imgs: Flag to output rendered images to calling directory/out, defaults to False
    :type save_imgs: bool, optional
    :param output_dir: Directory to output images to, defaults to None
    :type output_dir: str, optional
    :param instance_count: Instances to render at once, leads to roughly linear performance improvement, defaults to 9
    :type instance_count: int, optional, ` 0 < instance_count <= 25`
    :return: Irradiance at unit distance in given geometries
    :rtype: np.ndarray [nx1]
    """
    assert (
        instance_count <= 25 and instance_count > 0
    ), "Engine runs with 0 < instance_count <= 25"
    assert (
        svb.shape[1] == 3 and ovb.shape[1] == 3
    ), "Engine requires n x 3 numpy arrays as input for sun and observer vectors"
    assert model_file[-4:] == ".obj", "Model file must be *.obj"
    lce_dir = os.environ["LCEDIR"]
    model_dir = os.environ["MODELDIR"]
    model_path = os.path.join(model_dir, model_file)

    cwd = os.getcwd()
    if output_dir is None:
        output_dir = os.path.join(cwd, "out")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    save_str = ""
    if save_imgs:
        save_str = "-s"

    brdf_ind = query_brdf_registry(brdf)
    results_file = "light_curve0.lcr"
    write_light_curve_command_file(svb, ovb)

    if not brdf.use_mtl:
        brdf_opt_str = (
            f"-b {brdf_ind} -D {brdf.cd} -S {brdf.cs} -N {brdf.n}"
        )
    else:
        brdf_opt_str = f"-M -b {brdf_ind}"

    opts_str = (
        f"-m {model_path} -i {instance_count} -c {svb.shape[0]}"
        f" -r {results_file} -x {output_dir} {save_str} {brdf_opt_str}"
    )
    run_str = f"{os.path.join(lce_dir, 'LightCurveEngine')} {opts_str}"
    print(f"Running Light Curve Engine: \n{run_str}\n")
    os.chdir(lce_dir)
    os.system(run_str)
    os.chdir(cwd)
    with open(f"{lce_dir}/{results_file}", "r") as f:
        lc_data = f.read().splitlines()
    return np.reshape(
        2 * np.array([float(x) for x in lc_data]), (len(lc_data), 1)
    )


def run_brdf_registry(name_or_all: str) -> int:
    """Finds the index of a BRDF name

    :param name_or_all: A BRDF name (e.g. 'phong') or 'all' to get a list of all registered BRDFs
    :type name_or_all: str
    :return: Index of BRDF as known by the `BRDFRegistry` executable
    :rtype: int
    """
    lce_dir = os.environ["LCEDIR"]
    brdf_registry_path = f"{lce_dir}/BRDFRegistry"
    return os.system(f"{brdf_registry_path} {name_or_all}") // 256


def print_all_registered_brdfs() -> None:
    """Prints all BRDFs registered in the `BRDFRegistry` executable"""
    run_brdf_registry("all")


def query_brdf_registry(brdf: Brdf) -> int:
    """Figures out if a `Brdf` is valid, and if it is, returns its registry index

    :param brdf: BRDF to check
    :type brdf: Brdf
    :return: Index of BRDF as known by the `BRDFRegistry` executable
    :rtype: int
    """
    brdf_ind = run_brdf_registry(brdf.name)
    assert brdf_ind < 200, "BRDF name not valid!"
    return brdf_ind


def write_light_curve_command_file(
    svb: np.array, ovb: np.array, command_file="light_curve0.lcc"
) -> None:
    """Writes the command file read by the `LightCurveEngine` executable

    :param svb: Sun vectors in the object body frame
    :type svb: np.array [nx3]
    :param ovb: Observer vectors in the object body frame
    :type ovb: np.array [nx3]
    :param command_file: Command file name read by `LightCurveEngine`, defaults to "light_curve0.lcc"
    :type command_file: str, optional
    """
    lce_dir = os.environ["LCEDIR"]

    with open(f"{lce_dir}/{command_file}", "w") as f:
        header = (
            f"Light Curve Command File\n"
            f"\nBegin header\n"
            f'{"Format".ljust(20)} {"SunXYZViewerXYZ".ljust(20)}\n'
            f'{"Reference Frame".ljust(20)} {"ObjectBody".ljust(20)}\n'
            f'{"Data Points".ljust(20)} {str(svb.shape[0]).ljust(20)}\n'
            f"End header\n\n"
        )

        vf = lambda v: (
            f"{str(np.round(v[0],6)).ljust(10)} "
            f"{str(np.round(v[1],6)).ljust(10)} "
            f"{str(np.round(v[2],6)).ljust(10)}"
        )

        data = (
            f"Begin data\n"
            + "".join([f"{vf(s)}{vf(o)}\n" for s, o in zip(svb, ovb)])
            + "End data"
        )

        f.write(header)
        f.write(data)
