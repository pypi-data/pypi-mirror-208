import numpy as np
from scipy.ndimage import gaussian_filter
from tqdm import tqdm


def smooth_spatially(raw_movie: np.ndarray, sigma: float) -> np.ndarray:
    """Apply gaussian kernel convolution to each frame separately."""
    smoothed_movie = np.zeros_like(raw_movie)
    n_frames = raw_movie.shape[0]
    for i_frame in tqdm(range(n_frames)):
        smoothed_frame = gaussian_filter(raw_movie[i_frame, :, :], sigma=sigma)
        smoothed_movie[i_frame, :, :] = smoothed_frame
    return smoothed_movie


def smooth_temporally(movie: np.ndarray, sigma: float) -> np.ndarray:
    raise NotImplementedError()


def smooth_all_dimensions(movie: np.ndarray, sigma: float) -> np.ndarray:
    """Apply gaussian kernel convolution along all dimensions of a movie."""
    movie = gaussian_filter(movie, sigma=sigma)
    return movie