"""Bandpass filter widefield movies."""

import numpy as np
from scipy import signal


def apply_bandpass_filter(movie: np.ndarray, frame_rate: float, start_freq: float, end_freq: float, filter_order: int = 1) -> np.ndarray:
    """Apply bandpass filter to movie."""
    butterworth_filter = signal.butter(
        N=filter_order,
        Wn=[start_freq, end_freq],
        output="sos",
        btype="bandpass",
        fs=frame_rate,
    )
    filtered_movie = signal.sosfilt(butterworth_filter, movie, axis=0)
    return filtered_movie


def remove_high_frequencies(movie: np.ndarray, frame_rate: float, cutoff_freq: float, filter_order: int = 1) -> np.ndarray:
    """Remove high frequencies from movie."""
    butterworth_filter = signal.butter(
        N=filter_order,
        Wn=cutoff_freq,
        output="sos",
        btype="lowpass",
        fs=frame_rate,
    )
    filtered_movie = signal.sosfilt(butterworth_filter, movie, axis=0)
    return filtered_movie


def remove_low_frequencies(movie: np.ndarray, frame_rate: float, cutoff_freq: float, filter_order: int = 1) -> np.ndarray:
    """Remove low frequencies from movie."""
    butterworth_filter = signal.butter(
        N=filter_order,
        Wn=cutoff_freq,
        output="sos",
        btype="highpass",
        fs=frame_rate,
    )
    filtered_movie = signal.sosfilt(butterworth_filter, movie, axis=0)
    return filtered_movie
