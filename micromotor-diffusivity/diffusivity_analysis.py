"""Estimate effective diffusivity from particle trajectories."""

from __future__ import annotations

import numpy as np

from msd_analysis import calculate_msd


def estimate_diffusivity(lags: np.ndarray, msd: np.ndarray, dt: float, dimensions: int = 2, fit_fraction: float = 0.5) -> tuple[float, np.ndarray]:
    """Estimate D from MSD = 2*d*D*t using a linear fit over early data."""
    if dt <= 0 or dimensions < 1:
        raise ValueError("dt must be positive and dimensions must be >= 1.")
    n_fit = max(2, int(len(lags) * fit_fraction))
    time = lags[:n_fit] * dt
    slope, intercept = np.polyfit(time, msd[:n_fit], 1)
    D = slope / (2.0 * dimensions)
    return float(D), np.array([slope, intercept])


def analyze_trajectory(trajectory: np.ndarray, dt: float, label: str = "condition") -> dict:
    lags, msd = calculate_msd(trajectory)
    D, fit = estimate_diffusivity(lags, msd, dt)
    return {"label": label, "lags": lags, "msd": msd, "diffusivity": D, "fit": fit}


def compare_conditions(conditions: dict[str, np.ndarray], dt: float) -> dict[str, dict]:
    """Analyze multiple trajectories, e.g. homogeneous vs heterogeneous media."""
    return {name: analyze_trajectory(traj, dt, name) for name, traj in conditions.items()}


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from generate_test_trajectory import generate_trajectory

    dt = 0.01
    _, homogeneous = generate_trajectory(dt=dt, diffusion_coefficient=1.0, heterogeneous=False, seed=1)
    _, heterogeneous = generate_trajectory(dt=dt, diffusion_coefficient=1.0, heterogeneous=True, seed=1)

    results = compare_conditions({"homogeneous": homogeneous, "heterogeneous": heterogeneous}, dt)

    plt.figure()
    for name, result in results.items():
        plt.loglog(result["lags"] * dt, result["msd"], label=f"{name}: D={result['diffusivity']:.3g}")
    plt.xlabel("Lag time")
    plt.ylabel("MSD")
    plt.title("Effective diffusivity comparison")
    plt.legend()
    plt.grid(True, which="both")
    plt.show()
