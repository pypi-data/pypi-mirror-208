"""Functions related to showing and saving animated plots of movies."""
from functools import partial
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter


def make_animation(
        movie: np.ndarray,
        frame_rate: float,
        cmap: str = "viridis",
        plot_text: bool = True,
        title: str | None = None,
        vmin: float | None = None,
        vmax: float | None = None,
) -> FuncAnimation:
    """Make an animated plot with a movie."""
    fig, ax = plt.subplots()
    fig.set_tight_layout(True)
    fig.set_size_inches(5, 5)
    if isinstance(title, str) and plot_text:
        fig.suptitle(title)

    update_func = partial(
        update_image,
        movie=movie,
        movie_cmap=cmap,
        frame_rate=frame_rate,
        plot_text=plot_text,
        ax=ax,
        vmin=vmin,
        vmax=vmax,
    )

    # save as mp4
    interval = 1 / frame_rate
    ani = FuncAnimation(fig, func=update_func, frames=movie.shape[0], interval=interval)
    return ani


def make_overlay_animation(
        movie: np.ndarray,
        frame_rate: float,
        movie_cmap: str,
        static_image: np.ndarray,
        static_cmap: str,
        plot_text: bool = True,
        title: str | None = None,
        vmin: float | None = None,
        vmax: float | None = None,
) -> FuncAnimation:
    """Create an animation of a movie overlayed over a static image."""
    fig, ax = plt.subplots()
    fig.set_tight_layout(True)
    fig.set_size_inches(5, 5)
    if isinstance(title, str) and plot_text:
        fig.suptitle(title)

    update_func = partial(
        update_image,
        movie=movie,
        movie_cmap=movie_cmap,
        frame_rate=frame_rate,
        plot_text=plot_text,
        ax=ax,
        static_image=static_image,
        static_cmap=static_cmap,
        vmin=vmin,
        vmax=vmax,
    )

    # save as mp4
    interval = 1 / frame_rate
    ani = FuncAnimation(fig, func=update_func, frames=movie.shape[0], interval=interval)
    return ani


def update_image(
        frame: int,
        movie: np.ndarray,
        ax: plt.Axes,
        movie_cmap: str,
        plot_text: bool,
        vmin: float | None = None,
        vmax: float | None = None,
        frame_rate: float | None = None,
        static_image: np.ndarray | None = None,
        static_cmap: str | None = None,
) -> None:
    """
    To be used as updating function with matplotlib.animation.FuncAnimation.
    Initialize with functools.partial.
    """
    ax.clear()
    ax.axis("off")
    if isinstance(static_image, np.ndarray):
        ax.imshow(static_image, cmap=static_cmap, origin="lower")
        ax.imshow(movie[frame, :, :], cmap=movie_cmap, origin="lower", alpha=0.5, vmin=vmin, vmax=vmax)
    else:
        ax.imshow(movie[frame, :, :], cmap=movie_cmap, origin="lower", vmin=vmin, vmax=vmax)

    if plot_text and frame_rate is not None:
        time = frame / frame_rate
        ax.set_title(f"Frame {frame} ({time:.3f}s)")


def write_animation_to_mp4(animation: FuncAnimation, file_path: Path, frame_rate: float) -> None:
    """Use FFMPegWriter to save an animation as a .mp4 file."""
    assert file_path.suffix == ".mp4"
    writer = FFMpegWriter(fps=frame_rate)
    animation.save(file_path, writer)
    print(f"{file_path} saved.")

