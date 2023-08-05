from __future__ import annotations
import benanalysis._benpy_core.utils
import typing
import benanalysis._benpy_core

__all__ = [
    "find_key",
    "find_peak",
    "find_peaks",
    "peak_width"
]


def find_key(scan: benanalysis._benpy_core.Scan, lo: float, hi: float, value: float) -> float:
    """
    The value to search for. 
    """
def find_peak(scan: benanalysis._benpy_core.Scan) -> float:
    """
    The scan to find the peak of.
    """
def find_peaks(scan: benanalysis._benpy_core.Scan) -> benanalysis._benpy_core.Scan:
    """
    The scan to find the peaks of.
    """
def peak_width(scan: benanalysis._benpy_core.Scan, height: float) -> float:
    """
    The height as a fraction of max
    """
