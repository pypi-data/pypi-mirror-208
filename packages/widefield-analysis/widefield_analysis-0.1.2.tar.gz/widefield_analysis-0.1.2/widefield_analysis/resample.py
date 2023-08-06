"""Resample movies e.g. by downsizing."""

import numpy as np
from skimage.transform import downscale_local_mean
from tqdm import tqdm


def downsize_movie_with_local_mean(movie: np.ndarray, factor: int) -> np.ndarray:
    """Downsize each frame using skimage.transform.downscale_local_mean."""
    n_frames, x, y = movie.shape
    new_x = int(np.rint(x / factor))
    new_y = int(np.rint(y / factor))
    downsized_movie = np.zeros((n_frames, new_x, new_y))
    print("Downsizing movie.")
    for i_frame in tqdm(range(n_frames)):
        original_frame = movie[i_frame, :, :]
        smaller_frame = downscale_local_mean(original_frame, (factor, factor))
        downsized_movie[i_frame, :, :] = smaller_frame
    return downsized_movie
