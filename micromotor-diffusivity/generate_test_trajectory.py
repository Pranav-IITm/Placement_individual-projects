"""Generate synthetic particle trajectories for diffusivity analysis.

The trajectories are intentionally synthetic and are not experimental tumour data.
A heterogeneous medium is represented by spatially varying local diffusivity.
"""

from __future__ import annotations

import numpy as np


def generate_trajectory(
    n_steps: int = 5000,
    dt: float = 0.01,
    diffusion_coefficient: float = 1.0,
    seed: int | None = 42,
    heterogeneous: bool = False,
    slow_region_fraction: float = 0.35,
    slow_diffusion_factor: float = 0.25,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a 2-D Brownian trajectory.

    Parameters are dimensionless unless a physical unit system is supplied by the user.
    """
    if n_steps < 1 or dt <= 0 or diffusion_coefficient < 0:
        raise ValueError("n_steps must be positive and dt/D must be non-negative.")

    rng = np.random.default_rng(seed)
    positions = np.zeros((n_steps + 1, 2), dtype=float)
    local_D = np.full(n_steps, diffusion_coefficient, dtype=float)

    if heterogeneous:
        # Simple two-region medium: the particle experiences a slower region
        # after crossing a configurable fraction of the x-domain.
        boundary = np.quantile(np.linspace(-1, 1, n_steps + 1), slow_region_fraction)
        for i in range(n_steps):
            if positions[i, 0] > boundary:
                local_D[i] *= slow_diffusion_factor

    for i in range(n_steps):
        sigma = np.sqrt(2.0 * local_D[i] * dt)
        positions[i + 1] = positions[i] + rng.normal(0.0, sigma, size=2)

    time = np.arange(n_steps + 1) * dt
    return time, positions


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    t, trajectory = generate_trajectory(heterogeneous=False)
    plt.plot(trajectory[:, 0], trajectory[:, 1])
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Synthetic Brownian particle trajectory")
    plt.axis("equal")
    plt.grid(True)
    plt.show()
