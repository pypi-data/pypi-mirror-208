import numpy as np
import os
import pyvista as pv
from pyvista import examples
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Callable

from .constants import AstroConstants
from .math import hat
from .spaceobject import SpaceObject
from .coordinates import ecef_to_eci
from .attitude import axis_rotation_matrices


def render_video(
    pre_render_fcn: Callable,
    render_fcn: Callable,
    post_render_fcn: Callable,
    frame_count: int,
    fname: str = None,
    framerate: int = 60,
    quality: int = 9,
    background_color: str = "white",
) -> None:
    """Renders a video given callables each stage of the recording

    :param pre_render_fcn: Called once before the first frame
    :type pre_render_fcn: Callable(pl: pv.Plotter)
    :param render_fcn: Called each frame
    :type render_fcn: Callable(pl: pv.Plotter, i: int)
    :param post_render_fcn: Called after each frame, before the next (only needed for niche effects)
    :type post_render_fcn: Callable(pl: pv.Plotter, i: int)
    :param frame_count: Number of frames to render
    :type frame_count: int
    :param fname: File name to save as, defaults to None
    :type fname: str, optional
    :param framerate: Frame rate of movie [frames/second], defaults to 60
    :type framerate: int, optional
    :param quality: Quality of movie file, defaults to 9, less than 10
    :type quality: int, optional
    :param background_color: Background color of plot window, defaults to "white"
    :type background_color: str, optional
    """
    pl = pv.Plotter()
    if fname is not None:
        pl.open_movie(
            f"out/{fname}", framerate=framerate, quality=quality
        )
    pl.set_background(background_color)
    pre_render_fcn(pl)
    pl._on_first_render_request()
    pl.render()
    for i in range(frame_count):
        render_fcn(pl, i)
        if fname is not None:
            pl.write_frame()
        else:
            pl.update()
        post_render_fcn(pl, i)
    pl.close()


def vis_attitude_motion(
    obj: SpaceObject,
    quat: np.ndarray,
    fname: str = None,
    framerate: int = 60,
    quality: int = 9,
    background_color: str = "white",
) -> None:
    """Visualizes attitude motion in terms of quaternions, applied to a 3D model

    :param obj: Object to visualize orientations with
    :type obj: SpaceObject
    :param quat: Orientation history
    :type quat: np.ndarray [nx4]
    :param fname: File name to save movie to, defaults to `None`. If `None`, no video saved
    :type fname: str, optional
    :param framerate: Frame rate of movie [frames/second], defaults to 60
    :type framerate: int, optional
    :param quality: Quality of movie file, defaults to 9, less than 10
    :type quality: int, optional
    :param background_color: Background color of plot window, defaults to "white"
    :type background_color: str, optional
    """
    pl = pv.Plotter()
    if fname is not None:
        pl.open_movie(
            f"out/{fname}", framerate=framerate, quality=quality
        )
    pl.set_background(background_color)
    pl.add_mesh(obj._mesh)
    o_obj = obj._mesh.copy()
    pl._on_first_render_request()
    pl.render()
    for i in range(quat.shape[0]):
        obj.rotate_by_quat(quat[i, :])
        if fname is not None:
            pl.write_frame()
        else:
            pl.update()
        obj._mesh.copy_from(o_obj)
    pl.close()


def two_sphere(
    pl: pv.Plotter, radius: float = 1.0, opacity: float = 0.3, **kwargs
):
    """Plots a sphere :math:`S^2` in :math:`R^3`

    :param pl: Plotter to add sphere to
    :type pl: pv.Plotter
    :param radius: Radius of sphere mesh, defaults to 1.0
    :type radius: float, optional
    :param opacity: Opacity of sphere mesh, defaults to 0.3
    :type opacity: float, optional
    """
    sphere = pv.Sphere(
        radius=radius,
        theta_resolution=120,
        phi_resolution=120,
        start_theta=270.001,
        end_theta=270,
    )
    pl.add_mesh(sphere, opacity=opacity, **kwargs)


# def plot_sun(pl: pv.Plotter, date: datetime.datetime, sf: float = 1e3):
#     sun_pos = sun(date_to_jd(date))[0] / sf
#     pl.camera.clipping_range = (10, vecnorm(sun_pos))
#     if "sun" in pl.actors:
#         sun_mesh = pl.actors["sun"]
#         sun_mesh.position = sun_pos
#     else:
#         pl.add_mesh(
#             pv.Sphere(
#                 center=sun_pos,
#                 radius=10 * AstroConstants.sun_radius_km / sf,
#                 theta_resolution=200,
#                 phi_resolution=200,
#             ),
#             color="yellow",
#             emissive=True,
#             style="points_gaussian",
#             name="sun",
#         )

# def plot_basis(pl: pv.Plotter, quat: np.ndarray, scale: float = 1,
#                origin: np.ndarray = np.array([0,0,0])):
#     arrow_kwargs = {
#         "tip_length": 0.2,
#         "tip_resolution": 50,
#         "shaft_radius": 0.03,
#         "shaft_resolution": 50,
#         "scale": scale,
#     }
#     plot_kwargs = {"show_scalar_bar": False}

#     pl.add_mesh(
#         pv.Arrow(r[[i], :], v1[[i], :], **arrow_kwargs), name="arr_v1", **plot_kwargs
#     )
#     pl.add_mesh(
#         pv.Arrow(r[[i], :], v2[[i], :], **arrow_kwargs), name="arr_v2", **plot_kwargs
#     )
#     pl.add_mesh(
#         pv.Arrow(r[[i], :], v3[[i], :], **arrow_kwargs), name="arr_v3", **plot_kwargs
#     )


def plot_earth(
    pl: pv.Plotter,
    mode: str = "eci",
    date: datetime.datetime = None,
    stars: bool = False,
) -> pv.PolyData:
    """Plots the Earth as a sphere in [km]

    :param pl: Plotter to add the Earth to
    :type pl: pv.Plotter
    :return: Generated spherical mesh
    :rtype: pv.PolyData
    """
    assert mode in ["eci", "ecef"], "Mode must be 'eci' or 'ecef'"
    (_, _, r3) = axis_rotation_matrices()
    rotm = r3(np.pi / 2)
    if mode == "eci":
        rotm = rotm @ ecef_to_eci(date)
    rotm4 = np.vstack(
        (np.hstack((rotm, np.zeros((3, 1)))), [[0, 0, 0, 1]])
    )

    if "earth" in pl.actors:
        earth_actor = pl.actors["earth"]
    else:
        a = (
            AstroConstants.earth_r_eq
        )  # Semi-major axis of Earth ellipsoid
        b = a * (1 - AstroConstants.earth_f)  # Semi-minor axis
        res = 200
        earth = pv.ParametricEllipsoid(
            a,
            a,
            b,
            u_res=res,
            v_res=res,
            w_res=res,
            min_u=-np.pi / 2 + 0.00001,
            max_u=3 * np.pi / 2 - 0.00001,
        )
        sph_hat_pts = hat(earth.points)
        earth.active_t_coords = np.zeros((earth.points.shape[0], 2))
        earth.active_t_coords[:, 0] = 0.5 + np.arctan2(
            -sph_hat_pts[:, 0], sph_hat_pts[:, 1]
        ) / (2 * np.pi)
        earth.active_t_coords[:, 1] = (
            0.5 + np.arcsin(sph_hat_pts[:, 2]) / np.pi
        )

        tex_path = os.path.join(
            os.environ["SRCDIR"],
            "resources",
            "textures",
            "earth_tex.jpg",
        )
        etex = pv.Texture(tex_path)
        earth_actor = pl.add_mesh(
            earth, texture=etex, smooth_shading=True, name="earth"
        )
        pl.set_background("black")  # Because obviously, space and stuff
        if stars:
            cubemap = examples.download_cubemap_space_4k()
            pl.add_actor(cubemap.to_skybox())

    earth_actor.user_matrix = rotm4


def scatter3(pl: pv.Plotter, v: np.ndarray, **kwargs) -> pv.PolyData:
    """Replicates MATLAB scatter3() with ``pyvista`` backend

    :param pl: Plotter object to add points to
    :type pl: pv.Plotter
    :param v: Vector to scatter
    :type v: np.ndarray [nx3]
    :param **kwargs: Additional arguments passed to ``pl.add_mesh``
    :return: Handle to plotted data
    :rtype: pv.PolyData
    """
    assert 3 in v.shape, TypeError(
        "scatter3 requires a 3xn or nx3 input vector"
    )
    if v.shape[0] == 3:
        v = np.transpose(v)

    pc = pv.PolyData(v)
    pl.add_mesh(pc, render_points_as_spheres=True, **kwargs)
    return pc


def plot3(pl: pv.Plotter, v: np.ndarray, **kwargs) -> pv.PolyData:
    """Replicates MATLAB plot3() with pyvista backend, please use densely scattered points to avoid confusing splines

    :param pl: Plotter object to add line to
    :type pl: pv.Plotter
    :param v: Vector to plot
    :type v: np.ndarray [nx3]
    :param **kwargs: Additional arguments passed to ``pl.add_mesh``
    :return: Plotted spline
    :rtype: pv.PolyData
    """
    assert 3 in v.shape, TypeError(
        "plot3 requires a 3xn or nx3 input vector"
    )
    if v.shape[0] == 3:
        v = np.transpose(v)

    spline = pv.Spline(v, v.shape[0])
    pl.add_mesh(spline, render_lines_as_tubes=True, **kwargs)
    return spline


def texit(
    title: str,
    xlabel: str,
    ylabel: str,
    legend: list[str] = None,
    axis_label_font_size: int = 12,
    title_font_size: int = 15,
):
    """All my prefered plot formatting, all in one place

    :param title: Title string
    :type title: str
    :param xlabel: X-axis label
    :type xlabel: str
    :param ylabel: Y-axis label
    :type ylabel: str
    """
    plt.title(title, fontsize=title_font_size)
    plt.xlabel(xlabel, fontsize=axis_label_font_size)
    plt.ylabel(ylabel, fontsize=axis_label_font_size)
    if legend is not None:
        plt.legend(legend)


def show_and_copy(ch: pv.Chart2D) -> None:
    """Shows and copies a pyvista plot to the clipboard using ffmpeg

    :param ch: Chart object to copy
    :type ch: pv.Chart2D
    """
    im_arr = ch.show(screenshot=True, off_screen=True)
    from PIL import Image

    im = Image.fromarray(im_arr)
    imf = "imtemp.png"
    im.save(imf)

    cp_cmd = (
        f"osascript -e 'on run argv'"
        f" -e 'set the clipboard to "
        f"(read POSIX file (POSIX path of first "
        f"item of argv) as JPEG picture)' "
        f"-e 'end run' {os.getcwd()}/{imf}"
    )

    os.system(cp_cmd)
    os.remove(imf)
    ch.show()


def plot_basis(
    pl,
    dcm: np.ndarray,
    labels: str | list[str] = None,
    origin: np.ndarray = np.array([0, 0, 0]),
    scale: float = 1,
    color: str = "tan",
):
    if labels is str:
        labels = [labels for i in range(3)]
    for i, direction in enumerate(dcm.T):
        if labels is not None:
            plot_arrow(
                pl,
                origin,
                direction,
                scale=scale,
                color=color,
                label=labels[i],
            )
        else:
            plot_arrow(pl, origin, direction, scale=scale, color=color)


def plot_angle_between(
    pl: pv.Plotter,
    v1: np.ndarray,
    v2: np.ndarray,
    center: np.ndarray,
    dist: float = 1.0,
    linewidth: float = 10.0,
):
    v1h, v2h = hat(v1), hat(v2)
    p1 = v1h * dist + center
    p2 = v2h * dist + center
    arc = pv.CircularArc(p1.flatten(), p2.flatten(), center.flatten())
    pl.add_mesh(arc, color="k", line_width=linewidth)


def plot_arrow(
    pl: pv.Plotter,
    origin: np.ndarray,
    direction: np.ndarray,
    scale: float = 1,
    color: str = "tan",
    label: str = None,
    shape_opacity: float = 0.0,
) -> None:
    arrow_kwargs = {
        "tip_length": 0.2,
        "tip_resolution": 50,
        "shaft_radius": 0.03,
        "shaft_resolution": 50,
        "scale": scale,
    }
    plot_kwargs = {"show_scalar_bar": False}
    label_kwargs = {
        "always_visible": True,
        "show_points": False,
        "font_size": 36,
        "shape_color": "white",
        "margin": 0,
        "shape_opacity": shape_opacity,
    }
    pl.add_mesh(
        pv.Arrow(origin, direction, **arrow_kwargs),
        **plot_kwargs,
        color=color,
    )
    if label is not None:
        pl.add_point_labels(
            origin + direction * scale,
            [label],
            **label_kwargs,
        )
