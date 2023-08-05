#!/usr/bin/env python
import argparse
import numpy as np
import lal
import lalsimulation as LS
import click
from typing import Tuple


def MECO_freq(m_total: float, q: float, chi1z: float, chi2z: float) -> float:
    """Compute an estimate of the MECO frequency. Uses IMRPhenomX
    functions.

    Args:
        m_total (float): Total mass in solar masses
        q (float): Mass ratio >=1
        chi1z (float): Dimensionless spin of primary
        chi2z (float): Dimensionless spin of secondary

    Returns:
        float: MECO frequency in Hz
    """
    eta = q / (1.0 + q) ** 2
    fmeco_tmp = LS.SimIMRPhenomXfMECO(eta, chi1z, chi2z)
    fmeco = LS.SimIMRPhenomXUtilsMftoHz(fmeco_tmp, m_total)
    return fmeco


def estimate_seglen(
    fLow: float,
    m_total_min: float,
    safety_factor: float = 0.03,
    q: float = 5.0,
    chi1z: float = 0.99,
    chi2z: float = 0.99,
) -> Tuple[float]:
    """Estimate the required segment length. By default uses the SEOBNRv4ROM
    function + some additional esimtate of the length of the ringdown. Assumes
    a 0.4 second roll-on plus 2 second pad.
    Also cross checks with IMRPhenomXAS.

    Args:
        fLow (float): The starting frequency to use for the length estimate
        m_total_min (float): The total mass to use for length estimate
        safety_factor (float, optional): Safety factor. Defaults to 0.03.
        q (float, optional): Mass ratio >=1 to use of length estimate. Defaults to 5.0.
        chi1z (float, optional): Dimensionless spin of the primary. Defaults to 0.99.
        chi2z (float, optional): Dimensionsless spin of secondary. Defaults to 0.99.

    Returns:
        tuple: (length with no padding, length with padding, next power of 2)
    """
    m1 = m_total_min * q / (1.0 + q) * lal.MSUN_SI
    m2 = m_total_min * 1.0 / (1.0 + q) * lal.MSUN_SI
    # Longest signal - aligned maximal spins
    s = LS.SimInspiralFinalBlackHoleSpinBound(chi1z, chi2z)
    tmerge = LS.SimInspiralMergeTimeBound(m1, m2) + LS.SimInspiralRingdownTimeBound(
        m1 + m2, s
    )
    wf_len = LS.SimIMRSEOBNRv4ROMTimeOfFrequency(fLow, m1, m2, chi1z, chi2z)
    wf_len_xas = LS.SimIMRPhenomXASDuration(m1, m2, chi1z, chi2z, fLow)

    # Check if SEOB and PhenomX prediction for duration differ more than 20%
    if np.abs(wf_len - wf_len_xas) / wf_len > 0.2:
        print(
            f"Warning: different waveform length estimation between SEOBNRv4={wf_len}s and IMRPhenomXAS={wf_len_xas}. Using longest one."
        )
        if wf_len_xas > wf_len:
            wf_len = wf_len_xas

    wf_len += tmerge
    # Make the waveform slightly longer just for safety
    safe_len = wf_len * (1.0 + safety_factor)
    full_len = safe_len + 2 + 0.4  # Padding and roll-on
    seglen = 2 ** (np.floor(np.log2(full_len)) + 1)  # Next power  of 2
    return safe_len, full_len, seglen


def next_power_of_2(x):
    return 1 if x == 0 else 2 ** (x - 1).bit_length()


def Get_freqQNM_SEOBNRv4HM_SI_units(
    q: float, mtot: float, chi1z: float, chi2z: float, lm: Tuple[int]
) -> float:
    """Compute the QNM frequency in Hz for the given binary and lm mode.
    Uses SEOBNRv4 functions

    Args:
        q (float): Mass ratio >=1
        mtot (float): Total mass in solar masses
        chi1z (float): Dimensionless spin of primary
        chi2z (float): Dimensionless spin of secondary
        lm (Tuple[int]): (ell,m) of the mode

    Returns:
        float: real part of the QNM frequency in Hz
    """

    # It first computes the QNM omega in geometric units and then it rescale it with the total mass
    M = 100.0  # will be ignored
    Ms = M * lal.MTSUN_SI
    m1 = M * q / (1 + q)
    m2 = M * 1 / (1 + q)
    complexQNM = lal.CreateCOMPLEX16Vector(1)
    LS.SimIMREOBGenerateQNMFreqV2(
        complexQNM,
        m1,
        m2,
        np.array([0.0, 0.0, chi1z]),
        np.array([0.0, 0.0, chi2z]),
        lm[0],
        lm[1],
        1,
        LS.SEOBNRv4,
    )
    return Ms * np.real(complexQNM.data[0]) / (lal.MTSUN_SI * mtot * 2.0 * np.pi)


def min_sampling_rate_EOB(
    mtot: float,
    q: float = 2.0,
    chi1z: float = 0.5,
    chi2z: float = 0.5,
    HM: bool = False,
    ell_max: int = 3,
):
    """Compute the sampling rate needed

    Args:
        mtot (float): Total mass in solar masses
        q (float, optional): Mass ratio >=. Defaults to 2.0.
        chi1z (float, optional): Dimensionless spin of primary. Defaults to 0.5.
        chi2z (float, optional): Dimensionless spin of secondary. Defaults to 0.5.
        HM (bool, optional): Use higher modes?. Defaults to False.
        ell_max (int, optional): Which (l,m) to use to estimate QNM frequency. Defaults to 3.

    Returns:
        Union[float,float]: Sampling rate, next power of 2
    """
    # mtot must be in solar masses
    if HM:
        fmax = Get_freqQNM_SEOBNRv4HM_SI_units(
            q, mtot, chi1z, chi2z, (ell_max, ell_max)
        )
    else:
        fmax = Get_freqQNM_SEOBNRv4HM_SI_units(q, mtot, chi1z, chi2z, (2, 2))

    return 2 * fmax, next_power_of_2(int(2 * fmax))


def max_mass(freq):
    """Given a starting frequency in Hz, return the maximum total mass allowed"""
    return 10.5 ** (-1.5) / freq / lal.PI / lal.MTSUN_SI


def max_freq(m_total, fudge=0.99):
    """Given a maximum total mass return the largest possible starting frequency allowed"""
    mTScaled = m_total * lal.MTSUN_SI
    return fudge * 10.5 ** (-1.5) / (lal.PI * mTScaled)


def get_amp_order(m_total, f_low=20.0, HM=False, m_HM=3):
    """Given the maximum total mass and the desired f_low to be used in likelihood,
    return the appropriate amp_order"""
    m_freq = max_freq(m_total)
    if f_low < m_freq:
        m_freq = 1 * f_low
    # Check if the minimum frequency is determined by the generation  of the waveform or higher modes being present at the requested frequency
    hm_dominated = False
    if HM:
        # If we have HM turned on, then check if the desired mode is present at f_low
        # That is the starting frequency is a factor of m/2 lower than the f_low
        f_HM = f_low / (m_HM / 2)
        if f_HM < m_freq:
            m_freq = f_HM
            hm_dominated = True

    amp_order_tmp = 2 * f_low / m_freq - 2
    try:
        amp_order = np.array([int(np.ceil(x)) for x in amp_order_tmp])
        # We don't need to start any earlier because m_freq>f_min
        idx = np.where(amp_order < 0)[0]
        if len(idx) > 0:
            amp_order[idx] = 0
    except TypeError:
        amp_order = int(np.ceil(amp_order_tmp))
        if amp_order < 0:
            amp_order = 0
    return amp_order, m_freq, hm_dominated


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--m_total_min",
        required=True,
        type=float,
        help="Minimum total mass (solar masses)",
    )
    p.add_argument(
        "--m_total_max",
        required=True,
        type=float,
        help="Maximum total mass (solar masses)",
    )
    p.add_argument(
        "--f_low",
        default=20,
        type=float,
        help="The f_low to be used in the likelihood (Hz)",
    )
    p.add_argument(
        "--f_ref", default=20, type=float, help="The reference frequency to use (Hz)"
    )
    p.add_argument(
        "--HM",
        action="store_true",
        help="Run the checks taking into account higher modes",
    )
    p.add_argument(
        "--estimate_seglen",
        action="store_true",
        help="Try to estimate the seglen such that the template will fit in it, taking into account the amp_order",
    )
    p.add_argument(
        "--mass_ratio",
        type=float,
        help="The mass ratio to use for estimating the seglen",
        default=5.0,
    )

    p.add_argument(
        "--ell_max",
        type=int,
        help="Max ell for Nyquist check when HM enabled",
        default=3,
    )
    args = p.parse_args()
    amp_order, freq, hm_dominated = get_amp_order(
        args.m_total_max, args.f_low, HM=args.HM, m_HM=args.ell_max,
    )

    # Print summary
    click.echo("#" * 30 + " SUMMARY " + 30 * "#")
    click.echo("Input parameters")
    click.echo("--" * 20)

    if args.HM:

        print(
            "Compute the EOB settings with m_total_min={},m_total_max={}, f_low={} and higher modes taken into account".format(
                args.m_total_min, args.m_total_max, args.f_low
            )
        )
        if hm_dominated:
            print(
                f"The maximum starting (2,2) mode frequency allowed with amp_order=0 is {freq} to allow modes with ell={args.ell_max} in band at f_low={args.f_low}"
            )

        else:
            print(
                "The maximum starting (2,2) mode frequency allowed with amp_order=0 is {} to allow waveform to be generated".format(
                    freq
                )
            )
    else:
        print(
            "Compute the EOB settings with m_total_min={},m_total_max={},f_low={}".format(
                args.m_total_min, args.m_total_max, args.f_low
            )
        )

        print(
            "The maximum starting (2,2) mode frequency allowed with amp_order=0 is {} to allow waveform to be generated ".format(
                freq
            )
        )
    print("Use amp_order={}".format(amp_order))
    srate_min, srate_min_next_pow_2 = min_sampling_rate_EOB(
        args.m_total_min, HM=args.HM, ell_max=args.ell_max
    )
    print(
        "The minimum sampling rate to use is {}, the next power of two is {}".format(
            srate_min, srate_min_next_pow_2
        )
    )
    if args.estimate_seglen:
        wf_length, length_estimate, seglen = estimate_seglen(
            args.f_low, args.m_total_min, q=args.mass_ratio
        )
        print(
            "Estimated length of waveform starting at fLow={}: {} sec".format(
                args.f_low, wf_length
            )
        )
        print(
            "Total length,including 2 sec padding + 0.4 sec tapering: {} sec".format(
                length_estimate
            )
        )
        print("Recommended seglen: {} sec".format(seglen))
