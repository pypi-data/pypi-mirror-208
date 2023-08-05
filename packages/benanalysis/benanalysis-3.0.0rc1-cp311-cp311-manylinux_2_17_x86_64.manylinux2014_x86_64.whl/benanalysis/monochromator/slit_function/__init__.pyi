from __future__ import annotations
import benanalysis._benpy_core.monochromator.slit_function
import typing
import benanalysis._benpy_core

__all__ = [
    "uniform_fibres",
    "uniform_fibres_value"
]


def uniform_fibres(center_wavelength: float, bandwidth: float, points: int) -> benanalysis._benpy_core.Scan:
    """
    Returns the slit function (normalized to 1) formed by the perfect image of
    a uniform circular input fibre as it passes accross a circular exit fibre.
    Input and exit fibres have equal diameters.
    """
def uniform_fibres_value(center_wavelength: float, bandwidth: float, wavelength: float) -> float:
    """
    Returns the slit function value (normalized to 1) formed by the perfect image
    of a uniform circular input fibre as it passes accross a circular exit fibre.
    Input and exit fibres have equal diameters.
    """
