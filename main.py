#!/usr/bin/env python3
"""Launcher for the RIXS beamline GUI tools.

Opens a small main window from which the two tools can be started:
  - Spectra Analyser
  - Energy Calibration
"""

import tkinter as tk

from rixs_gui.spectra_analyser import graphs_analyser
from rixs_gui.energy_calibration import energy_calibration


def main():
    root = tk.Tk()
    root.title("RIXS Beamline Tools")
    root.geometry("320x180+300+300")

    tk.Label(root, text="RIXS Beamline Tools", font=("Helvetica", 16, "bold")).pack(pady=(20, 10))

    tk.Button(
        root, text="Spectra Analyser", width=24,
        command=lambda: graphs_analyser(root),
    ).pack(pady=5)

    tk.Button(
        root, text="Energy Calibration", width=24,
        command=lambda: energy_calibration(root),
    ).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
