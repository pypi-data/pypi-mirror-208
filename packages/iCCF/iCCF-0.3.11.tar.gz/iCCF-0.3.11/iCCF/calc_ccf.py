import numpy as np
from scipy.interpolate import interp1d
from .utils import doppler_shift_wave


def calculate_ccf(wa: np.ndarray, sa: np.ndarray, wb: np.ndarray,
                  sb: np.ndarray, rvarray: np.ndarray,
                  normalize_by_median: bool = True) -> np.ndarray:

    if normalize_by_median:
        sa /= np.median(sa)
        sb /= np.median(sb)

    ccf = np.zeros_like(rvarray)
    f = interp1d(wa, sa, bounds_error=False, fill_value=0.0)

    for i, rv in enumerate(rvarray):
        # doppler shift the wavelength array
        wa_new = doppler_shift_wave(wa, rv)
        # interpolate to the new wavelengths
        sa_new = f(wa_new)
        # correlate shifted sa with sb
        ccf[i] = np.correlate(sa_new, sb)

    return ccf
