"""Bentham Instruments spectral analysis package."""
from __future__ import annotations
import benanalysis._benpy_core
import typing

__all__ = [
    "Interpolation",
    "Scan",
    "colorimetry",
    "data",
    "log",
    "log10",
    "monochromator",
    "utils"
]


class Interpolation():
    """
    Members:

      NONE

      AKIMA

      CUBIC

      LINEAR

      POLYNOMIAL
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    AKIMA: benanalysis._benpy_core.Interpolation # value = <Interpolation.AKIMA: 1>
    CUBIC: benanalysis._benpy_core.Interpolation # value = <Interpolation.CUBIC: 2>
    LINEAR: benanalysis._benpy_core.Interpolation # value = <Interpolation.LINEAR: 3>
    NONE: benanalysis._benpy_core.Interpolation # value = <Interpolation.NONE: 0>
    POLYNOMIAL: benanalysis._benpy_core.Interpolation # value = <Interpolation.POLYNOMIAL: 4>
    __members__: dict # value = {'NONE': <Interpolation.NONE: 0>, 'AKIMA': <Interpolation.AKIMA: 1>, 'CUBIC': <Interpolation.CUBIC: 2>, 'LINEAR': <Interpolation.LINEAR: 3>, 'POLYNOMIAL': <Interpolation.POLYNOMIAL: 4>}
    pass
class Scan():
    """
    Class to manipulate spectral data consisting of wavelength and value pairs.


    Usage:
    >>> scan1 = Scan() # create empty scan object
    >>> scan1 = Scan(epsilon=0.001) # ... with wavelength float comparison epsilon
    >>> scan1 = Scan(interpolation=SplineType.LINEAR) # ... allowing interpolation
    >>> scan1[400] = 1.1  # start assigning values to wavelengths
    >>> print(scan1[400]) # and retrieving them
    1.1
    >>> scan2 = benpy.Scan([400,405,410,415,420],[1,2,3,4,5],  # initialise with list or numpy arrays
    ...   epsilon=0.001, interpolation=benpy.SplineType.AKIMA)
    >>> scan2(402) # call with one value to interpolate
    2.4
    >>> scan2(402,415) # call with one value to integrate
    35.1
    >>> scan3 = log10(scan1+1) * scan2  # do complex maths
    Scan(400→420[5], epsilon=0.001, interpolation=AKIMA)
    >>> scan3.to_numpy()
    [[4.00000000e+02 4.05000000e+02 4.10000000e+02 4.15000000e+02
      4.20000000e+02]
     [9.06190583e-02 2.27644692e-01 3.62476233e-01 4.88559067e-01
      6.05519368e-01]]
    """
    @typing.overload
    def __add__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __add__(self, arg0: float) -> Scan: ...
    @typing.overload
    def __call__(self, wavelength: float) -> float: 
        """
        Indirect access to the data to allow interpolation. Note does not
        extrapolate or throw, returns zero if wavelength is out of bounds.



        The numerical integral result of the interpolated function over
        the range [wavelength_from, wavelength_to].
        """
    @typing.overload
    def __call__(self, wavelength_from: float, wavelength_to: float) -> float: ...
    def __eq__(self, arg0: Scan) -> bool: ...
    def __getitem__(self, arg0: float) -> float: ...
    @typing.overload
    def __iadd__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __iadd__(self, arg0: float) -> Scan: ...
    @typing.overload
    def __imul__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __imul__(self, arg0: float) -> Scan: ...
    @typing.overload
    def __init__(self, epsilon: float = 1e-20, interpolation: Interpolation = Interpolation.NONE) -> None: 
        """
        Initialise an empty Scan, storing epsilon and interpolation.

        Initialise a scan with lists of wavelength and values, wavelength epsilon, and interpolation type
        """
    @typing.overload
    def __init__(self, wavelength_array: typing.List[float], value_array: typing.List[float], epsilon: float = 1e-20, interpolation: Interpolation = Interpolation.NONE) -> None: ...
    @typing.overload
    def __isub__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __isub__(self, arg0: float) -> Scan: ...
    def __iter__(self) -> typing.Iterator: ...
    @typing.overload
    def __itruediv__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __itruediv__(self, arg0: float) -> Scan: ...
    @typing.overload
    def __mul__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __mul__(self, arg0: float) -> Scan: ...
    def __neg__(self) -> Scan: ...
    @typing.overload
    def __pow__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __pow__(self, arg0: float) -> Scan: ...
    def __radd__(self, arg0: float) -> Scan: ...
    def __repr__(self) -> str: ...
    def __rmul__(self, arg0: float) -> Scan: ...
    def __rpow__(self, arg0: float) -> Scan: ...
    def __rsub__(self, arg0: float) -> Scan: ...
    def __rtruediv__(self, arg0: float) -> Scan: ...
    def __setitem__(self, arg0: float, arg1: float) -> None: ...
    def __str__(self) -> str: ...
    @typing.overload
    def __sub__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __sub__(self, arg0: float) -> Scan: ...
    @typing.overload
    def __truediv__(self, arg0: Scan) -> Scan: ...
    @typing.overload
    def __truediv__(self, arg0: float) -> Scan: ...
    def add(self, wavelength: float, value: float) -> None: 
        """
        Add a wavelength, value point to the scan.
        """
    def init_spline(self) -> None: 
        """
        Initialise the spline with the current interpolation type.
        """
    def is_interpolated(self) -> bool: 
        """
        Returns whether or not the scan uses interpolation (a SplineType other than NONE).
        """
    def items(self) -> typing.Iterator: ...
    def populate_from_csv(self, file_path: str) -> None: 
        """
        Populate from csv (or general char delimited) file.
        """
    def to_lists(self) -> typing.List[typing.List[float]]: 
        """
        Convert Scan object to a pair of lists
        """
    def to_numpy(self) -> numpy.ndarray[numpy.float64]: 
        """
        Convert Scan object to a 2D numpy array where index 0 and 1 are arrays of wavelengths and values respectively
        """
    def values(self) -> typing.List[float]: 
        """
        return the values from the scan object
        """
    def wavelengths(self) -> typing.List[float]: 
        """
        return the wavelengths from the scan object
        """
    @property
    def epsilon(self) -> float:
        """
        :type: float
        """
    @epsilon.setter
    def epsilon(self, arg1: float) -> None:
        pass
    @property
    def interpolation(self) -> Interpolation:
        """
        :type: Interpolation
        """
    @interpolation.setter
    def interpolation(self, arg1: Interpolation) -> None:
        pass
    __hash__ = None
    pass
@typing.overload
def log(arg0: Scan) -> Scan:
    """
    Compute natural logarithm of a scan.

    Compute logarithm base [Scan] of a Scan

    Compute logarithm base [float] of a [Scan]

    Compute logarithm base [Scan] of a [float]
    """
@typing.overload
def log(arg0: Scan, arg1: Scan) -> Scan:
    pass
@typing.overload
def log(arg0: Scan, arg1: float) -> Scan:
    pass
@typing.overload
def log(arg0: float, arg1: Scan) -> Scan:
    pass
def log10(arg0: Scan) -> Scan:
    """
    Compute logarithm base 10 of a scan.
    """
