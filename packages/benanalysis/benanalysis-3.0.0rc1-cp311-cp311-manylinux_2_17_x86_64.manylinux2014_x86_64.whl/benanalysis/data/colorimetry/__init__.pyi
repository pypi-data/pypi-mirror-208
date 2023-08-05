from __future__ import annotations
import benanalysis._benpy_core.data.colorimetry
import typing
import benanalysis._benpy_core

__all__ = [
    "ANSI_Z80_3_2015_green_signal_transmittance",
    "ANSI_Z80_3_2015_red_signal_transmittance",
    "ANSI_Z80_3_2015_yellow_signal_transmittance",
    "ISO8980_3_incandescent_blue",
    "ISO8980_3_incandescent_green",
    "ISO8980_3_incandescent_red",
    "ISO8980_3_incandescent_yellow",
    "ISO8980_3_led_blue",
    "ISO8980_3_led_green",
    "ISO8980_3_led_red",
    "ISO8980_3_led_yellow",
    "aphake_hazard",
    "blue_light_hazard",
    "cie_1931_standard_observer_x",
    "cie_1931_standard_observer_y",
    "cie_1931_standard_observer_z",
    "cie_1964_standard_observer_x",
    "cie_1964_standard_observer_y",
    "cie_1964_standard_observer_z",
    "cie_illuminant_a",
    "cie_illuminant_c",
    "cie_illuminant_d65",
    "relative_spectral_effectiveness",
    "solar_spectral_irradiance"
]


def ANSI_Z80_3_2015_green_signal_transmittance() -> benanalysis._benpy_core.Scan:
    """
    Transmittance of the green traffic signal lens specified in ANSI Z80.3-2015
    """
def ANSI_Z80_3_2015_red_signal_transmittance() -> benanalysis._benpy_core.Scan:
    """
    Transmittance of the red traffic signal lens specified in ANSI Z80.3-2015
    """
def ANSI_Z80_3_2015_yellow_signal_transmittance() -> benanalysis._benpy_core.Scan:
    """
    Transmittance of the yellow traffic signal lens specified in ANSI Z80.3-2015
    """
def ISO8980_3_incandescent_blue() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by incandescent signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Blue Signal
    """
def ISO8980_3_incandescent_green() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by incandescent signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Green Signal
    """
def ISO8980_3_incandescent_red() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by incandescent signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Red Signal
    """
def ISO8980_3_incandescent_yellow() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by incandescent signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Yellow Signal
    """
def ISO8980_3_led_blue() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by LED signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Blue Signal
    """
def ISO8980_3_led_green() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by LED signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Green Signal
    """
def ISO8980_3_led_red() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by LED signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Red Signal
    """
def ISO8980_3_led_yellow() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral distribution of radiation emitted by LED signal lights,
    ESignal(λ), weighted by the spectral luminous efficiency function of the average
    human eye for daylight vision, V(λ), as specified in ISO 11664-1.
    Yellow Signal
    """
def aphake_hazard() -> benanalysis._benpy_core.Scan:
    """
    Aphake hazard function A(λ)
    """
def blue_light_hazard() -> benanalysis._benpy_core.Scan:
    """
    Blue-light hazard function B(λ)
    380nm to 500nm steps 5nm
    """
def cie_1931_standard_observer_x() -> benanalysis._benpy_core.Scan:
    """
    CIE 1931 standard colorimetric observer (CIE 1931 2° Standard Observer)
    Color Matching Function x
    """
def cie_1931_standard_observer_y() -> benanalysis._benpy_core.Scan:
    """
    CIE 1931 standard colorimetric observer (CIE 1931 2° Standard Observer)
    Color Matching Function y
    """
def cie_1931_standard_observer_z() -> benanalysis._benpy_core.Scan:
    """
    CIE 1931 standard colorimetric observer (CIE 1931 2° Standard Observer)
    Color Matching Function z
    """
def cie_1964_standard_observer_x() -> benanalysis._benpy_core.Scan:
    """
    CIE 1964 standard colorimetric observer (CIE 1964 10° Standard Observer)
    Color Matching Function x
    """
def cie_1964_standard_observer_y() -> benanalysis._benpy_core.Scan:
    """
    CIE 1964 standard colorimetric observer (CIE 1964 10° Standard Observer)
    Color Matching Function y
    """
def cie_1964_standard_observer_z() -> benanalysis._benpy_core.Scan:
    """
    CIE 1964 standard colorimetric observer (CIE 1964 10° Standard Observer)
    Color Matching Function z
    """
def cie_illuminant_a() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral power distribution of CIE Standard Illuminant A
    """
def cie_illuminant_c() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral power distribution of CIE Standard Illuminant C
    """
def cie_illuminant_d65() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral power distribution of CIE Standard Illuminant D65
    """
def relative_spectral_effectiveness() -> benanalysis._benpy_core.Scan:
    """
    Relative spectral effectiveness function S(λ)
    280nm to 400nm steps 5nm
    see: The International commission on non-ionizing radiation protection (ICNIRP).
    Guidelines on limits of exposure to ultraviolet radiation of wavelengths between
    180 nm and 400 nm (incoherent optical radiation).
    Health Phys. 2004, 87 (2) pp. 171-186
    """
def solar_spectral_irradiance() -> benanalysis._benpy_core.Scan:
    """
    Solar Spectral Irradiance (mW m-2 nm-1)
    250nm to 500nm steps 5nm
    """
