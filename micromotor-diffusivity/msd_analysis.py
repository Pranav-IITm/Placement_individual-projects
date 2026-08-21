"""Mean-square-displacement utilities for particle trajectories."""

from __future__ import annotations

import numpy as np


def calculate_msd(trajectory: np.ndarray, max_lag: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Calculate time-averaged MSD for a 2-D or N-D trajectory."""
    trajectory = np.asarray(trajectory, dtype=float)
    if trajectory.ndim != 2 or trajectory.shape[0] < 2:
        raise ValueError("trajectory must have shape (n_points, dimensions).")

    n = trajectory.shape[0]
    if max_lag is None:
        max_lag = n // 4
    max_lag = min(max_lag, n - 1)
    lags = np.arange(1, max_lag + 1)
    msd = np.empty(max_lag)

    for i, lag in enumerate(lags):
        displacement = trajectory[lag:] - trajectory[:-lag]
        msd[i] = np.mean(np.sum(displacement**2, axis=1))

    return lags, msd


def plot_msd(lags: np.ndarray, msd: np.ndarray, dt: float = 1.0) -> None:
    """Plot MSD against lag time."""
    import matplotlib.pyplot as plt

    plt.figure()
    plt.loglog(lags * dt, msd, marker="o", markersize=3)
    plt.xlabel("Lag time")
    plt.ylabel("MSD")
    plt.title("Mean-square displacement")
    plt.grid(True, which="both")
    plt.show()


if __name__ == "__main__":
    from generate_test_trajectory import generate_trajectory

    time, trajectory = generate_trajectory()
    lags, msd = calculate_msd(trajectory)
    plot_msd(lags, msd, dt=time[1] - time[0])
