#!/usr/bin/env python3
"""Generate synthetic .hdf5 files with the layout expected by the GUI tools.

The data are artificial (Gaussian peaks on a noisy CCD-like image with a
curved dispersion) and contain no real beamline measurements. They are meant
for trying out the interface and for taking screenshots.

Usage:
    python examples/make_synthetic_data.py            # writes to ./examples/data
    python examples/make_synthetic_data.py my_folder  # writes to ./my_folder
"""

import os
import sys

import numpy as np

N_ROWS, N_COLS = 200, 1024


def gaussian(x, amp, mean, sigma):
    return amp * np.exp(-(x - mean) ** 2 / (2 * sigma**2))


def build_dataset(peaks, rng):
    """Return a dict with the datasets read by the GUI tools."""
    x = np.arange(N_COLS)
    rows = np.arange(N_ROWS)

    # Parabolic distortion of the peak position along the image rows
    curvature = 0.0006 * (rows - N_ROWS / 2) ** 2

    raw = np.zeros((N_ROWS, N_COLS))
    corrected = np.zeros((N_ROWS, N_COLS))
    for r in rows:
        for amp, pos, sigma in peaks:
            raw[r] += gaussian(x, amp, pos + curvature[r], sigma)
            corrected[r] += gaussian(x, amp, pos, sigma)
    raw += rng.poisson(5, raw.shape)
    corrected += rng.poisson(5, corrected.shape)

    return {
        "spectraImage": raw,
        "spectraCurveCorrectedNAccImage": corrected,
        "spectraCorrectedNAccImage": corrected,
        "baseAcc": raw.sum(axis=0),
        "curveCorrectedAcc": corrected.sum(axis=0),
        "correctedAcc": corrected.sum(axis=0),
    }


def main(out_dir):
    import h5py  # imported here so the data builder can be reused without it

    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng(42)

    # Three "scans" with the same elastic-line-like peaks shifted slightly,
    # so that several files can be overlaid in the Energy Calibration tool.
    for i, shift in enumerate([0, 40, 80]):
        peaks = [(60, 300 + shift, 5), (40, 520 + shift, 6), (25, 740 + shift, 7)]
        data = build_dataset(peaks, rng)
        path = os.path.join(out_dir, f"synthetic_scan_{i + 1}.hdf5")
        with h5py.File(path, "w") as f:
            for name, values in data.items():
                f.create_dataset(name, data=values)
        print("written", path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join("examples", "data"))
