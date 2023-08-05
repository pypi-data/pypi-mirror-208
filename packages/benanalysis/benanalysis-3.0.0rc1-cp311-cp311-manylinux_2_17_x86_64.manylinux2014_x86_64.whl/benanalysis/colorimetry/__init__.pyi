from __future__ import annotations
import benanalysis._benpy_core.colorimetry
import typing
import benanalysis._benpy_core

__all__ = [
    "ANSI_Z80_3_tau_signal",
    "ANSI_Z80_3_tau_spectral_min",
    "ANSI_Z80_3_tau_uva",
    "ANSI_Z80_3_tau_uvb",
    "ANSI_Z80_3_tau_v",
    "ASNZS1067_2016_tau_suva",
    "CIELAB",
    "CIELAB_f",
    "CIELAB_tristimulus_values",
    "CIEXYZ",
    "CIE_tristimulus_values",
    "ISO12311_tau_sb",
    "ISO8980_3_tau_signal_incandescent",
    "ISO8980_3_tau_signal_led",
    "ISO8980_3_tau_suva",
    "ISO8980_3_tau_suvb",
    "ISO8980_3_tau_uva",
    "ISO8980_3_tau_v",
    "Observer",
    "RYG",
    "RYGB",
    "f1_prime",
    "f2"
]


class CIELAB():
    """
    CIE 1976 (L*, a*, b*) color space (CIELAB) coordinates
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, L_star: float, a_star: float, b_star: float) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def L_star(self) -> float:
        """
        :type: float
        """
    @L_star.setter
    def L_star(self, arg0: float) -> None:
        pass
    @property
    def a_star(self) -> float:
        """
        :type: float
        """
    @a_star.setter
    def a_star(self, arg0: float) -> None:
        pass
    @property
    def b_star(self) -> float:
        """
        :type: float
        """
    @b_star.setter
    def b_star(self, arg0: float) -> None:
        pass
    pass
class CIEXYZ():
    """
    CIE 1931 (X, Y, Z) color space (CIEXYZ) coordinates
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, X: float, Y: float, Z: float) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def X(self) -> float:
        """
        :type: float
        """
    @X.setter
    def X(self, arg0: float) -> None:
        pass
    @property
    def Y(self) -> float:
        """
        :type: float
        """
    @Y.setter
    def Y(self, arg0: float) -> None:
        pass
    @property
    def Z(self) -> float:
        """
        :type: float
        """
    @Z.setter
    def Z(self, arg0: float) -> None:
        pass
    pass
class Observer():
    """
    Observer struct
    """
    def __init__(self, x: benanalysis._benpy_core.Scan, y: benanalysis._benpy_core.Scan, z: benanalysis._benpy_core.Scan) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def x(self) -> benanalysis._benpy_core.Scan:
        """
        :type: benanalysis._benpy_core.Scan
        """
    @property
    def y(self) -> benanalysis._benpy_core.Scan:
        """
        :type: benanalysis._benpy_core.Scan
        """
    @property
    def z(self) -> benanalysis._benpy_core.Scan:
        """
        :type: benanalysis._benpy_core.Scan
        """
    pass
class RYG():
    """
    Red, Yellow, Green coordinates
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, red: float, yellow: float, green: float) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def green(self) -> float:
        """
        :type: float
        """
    @green.setter
    def green(self, arg0: float) -> None:
        pass
    @property
    def red(self) -> float:
        """
        :type: float
        """
    @red.setter
    def red(self, arg0: float) -> None:
        pass
    @property
    def yellow(self) -> float:
        """
        :type: float
        """
    @yellow.setter
    def yellow(self, arg0: float) -> None:
        pass
    pass
class RYGB():
    """
    Red, Yellow, Green, Blue coordinates
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, red: float, yellow: float, green: float, blue: float) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def blue(self) -> float:
        """
        :type: float
        """
    @blue.setter
    def blue(self, arg0: float) -> None:
        pass
    @property
    def green(self) -> float:
        """
        :type: float
        """
    @green.setter
    def green(self, arg0: float) -> None:
        pass
    @property
    def red(self) -> float:
        """
        :type: float
        """
    @red.setter
    def red(self, arg0: float) -> None:
        pass
    @property
    def yellow(self) -> float:
        """
        :type: float
        """
    @yellow.setter
    def yellow(self, arg0: float) -> None:
        pass
    pass
def ANSI_Z80_3_tau_signal(trans: benanalysis._benpy_core.Scan) -> RYG:
    """
    Returns the luminous transmittance of the lens for the spectral radiant power distribution of the incandescent traffic signal light.
    """
def ANSI_Z80_3_tau_spectral_min(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the minimum of the spectral transmittance tau(lambda) of the lens between 475nm and 650nm.
    """
def ANSI_Z80_3_tau_uva(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the mean UV-A transmittance (tau_UVA). The mean transmittance between 315 nm and 380 nm.
    """
def ANSI_Z80_3_tau_uvb(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the mean UV-B transmittance (tau_UVB). The mean transmittance between 280 nm and 315 nm.
    """
def ANSI_Z80_3_tau_v(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the luminous transmittance (tau_V). The ratio of the luminous flux transmitted by the lens or filter to the incident luminous flux.
    """
def ASNZS1067_2016_tau_suva(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the solar UV-A transmittance (tau_SUVA). The mean of the spectral transmittance between 315 nm and 400 nm weighted by the solar radiation distribution Es(λ) at sea level, for air mass 2, and the relative spectral effectiveness function for UV radiation S(λ).
    """
def CIELAB_f(t: float) -> float:
    """
    Non-linear function used in the forward transformation from the CIEXYZ color space to the CIELAB.
    """
def CIELAB_tristimulus_values(scan: benanalysis._benpy_core.Scan, white_point_reference: benanalysis._benpy_core.Scan, observer: Observer) -> CIELAB:
    """
    Returns the CIE 1976 (L*, a*, b*) color space coordinates for a given spectrum given a specific observer and white point reference.
    """
def CIE_tristimulus_values(scan: benanalysis._benpy_core.Scan, observer: Observer) -> CIEXYZ:
    """
    Calculate the CIE Tristimulus Values for a given observer and spectrum.

    Args:
        scan (Scan): A scan object containing the spectrum data.
        observer (Observer): An observer object containing color matching functions.

    Returns:
        CIEXYZ: A CIEXYZ object containing the calculated CIE Tristimulus Values.
    """
def ISO12311_tau_sb(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the solar blue-light transmittance tau_sb. Solar blue-light transmittance is the result of the mean of the spectral transmittance between 380 nm and 500 nm and appropriate weighting functions.
    """
def ISO8980_3_tau_signal_incandescent(trans: benanalysis._benpy_core.Scan) -> RYGB:
    """
    Returns the luminous transmittance of the lens for the spectral radiant power distribution of the incandescent traffic signal light.
    """
def ISO8980_3_tau_signal_led(trans: benanalysis._benpy_core.Scan) -> RYGB:
    """
    Returns the luminous transmittance of the lens for the spectral radiant power distribution of the LED traffic signal light.
    """
def ISO8980_3_tau_suva(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the solar UV-A transmittance (tau_SUVA). The mean of the spectral transmittance between 315 nm and 380 nm weighted by the solar radiation distribution Es(λ) at sea level, for air mass 2, and the relative spectral effectiveness function for UV radiation S(λ).
    """
def ISO8980_3_tau_suvb(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the solar UV-B transmittance (tau_SUVB). The mean of the spectral transmittance between 280 nm and 315 nm weighted by the solar radiation distribution Es(λ) at sea level, for air mass 2, and the relative spectral effectiveness function for UV radiation S(λ).
    """
def ISO8980_3_tau_uva(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the mean UV-A transmittance (tau_UVA). The mean transmittance between 315 nm and 380 nm.
    """
def ISO8980_3_tau_v(trans: benanalysis._benpy_core.Scan) -> float:
    """
    Returns the luminous transmittancev (tau_V). The ratio of the luminous flux transmitted by the lens or filter to the incident luminous flux.
    """
def f1_prime(scan: benanalysis._benpy_core.Scan) -> float:
    """
    The integral parameter f1' describes the quality of the spectral match between a specified spectrum and the CIE 1931 standard colorimetric observer (CIE 1931 2° Standard Observer) Color Matching Function y.
    """
def f2(Y_0: benanalysis._benpy_core.Scan, Y_pi_2: benanalysis._benpy_core.Scan) -> float:
    """
    f2 is the deviation in directional response to the incident radiation of a photometer with a plane input window measuring planar illuminances.
    """
