#!/usr/bin/env python3

import numpy as np
import os
import pytest
import lal
import lalsimulation as lalsim


from peconfigurator.get_settings import (
    get_amp_order,
    estimate_seglen,
    min_sampling_rate_EOB,
    next_power_of_2,
)


def manual_qnm_frequency(m1, m2, s1z, s2z, ell, m):
    """Get the (ell,m) mode QNM frequency in SI units.
    Stolen from LALSimIMRPhenomXHM_qnm.c
    """
    eta = m1 * m2 / (m1 + m2) ** 2
    finalDimlessSpin = lalsim.SimIMRPhenomXFinalSpin2017(eta, s1z, s2z)
    erad = lalsim.SimIMRPhenomXErad2017(eta, s1z, s2z)
    x2 = finalDimlessSpin * finalDimlessSpin
    x3 = x2 * finalDimlessSpin
    x4 = x2 * x2
    x5 = x3 * x2
    x6 = x3 * x3
    if ell == 2 and m == 2:
        fring_tmp = lalsim.SimIMRPhenomXfring22(finalDimlessSpin)
    if ell == 3 and m == 3:
        fring_tmp = (
            0.09540436245212061
            - 0.22799517865876945 * finalDimlessSpin
            + 0.13402916709362475 * x2
            + 0.03343753057911253 * x3
            - 0.030848060170259615 * x4
            - 0.006756504382964637 * x5
            + 0.0027301732074159835 * x6
        ) / (
            1
            - 2.7265947806178334 * finalDimlessSpin
            + 2.144070539525238 * x2
            - 0.4706873667569393 * x4
            + 0.05321818246993958 * x6
        )
    if ell == 4 and m == 4:
        fring_tmp = (
            0.1287821193485683
            - 0.21224284094693793 * finalDimlessSpin
            + 0.0710926778043916 * x2
            + 0.015487322972031054 * x3
            - 0.002795401084713644 * x4
            + 0.000045483523029172406 * x5
            + 0.00034775290179000503 * x6
        ) / (
            1
            - 1.9931645124693607 * finalDimlessSpin
            + 1.0593147376898773 * x2
            - 0.06378640753152783 * x4
        )
    res = lalsim.SimIMRPhenomXUtilsMftoHz(fring_tmp, m1 + m2) / (1.0 - erad)
    return res


def manual_seglen(m1, m2, chi1z, chi2z, flow):
    """Compute the seglen by the following procedure:
    1. Actually evolve SEOBNRv4_opt in time domain
    2. Check that the seglen that we return is strictly greater than what
    we got in step 1.
    """
    distance = 400 * 1e6 * lal.PC_SI
    iota = 0.0
    phi = 0.0
    delta_t = 1.0 / 16384
    hp, hc = lalsim.SimInspiralChooseTDWaveform(
        m1 * lal.MSUN_SI,
        m2 * lal.MSUN_SI,
        0.0,
        0.0,
        chi1z,
        0.0,
        0.0,
        chi2z,
        distance,
        iota,
        phi,
        0.0,
        0.0,
        0.0,
        delta_t,
        flow,
        flow,
        lal.CreateDict(),
        lalsim.GetApproximantFromString("SEOBNRv4_opt"),
    )
    duration = len(hp.data.data) * delta_t
    with_rollon = duration + 2.4
    seglen = 2 ** (np.floor(np.log2(with_rollon)) + 1)  # Next power  of 2
    return duration, with_rollon, seglen


@pytest.mark.parametrize(
    "m_total,HM,m_HM,expected",
    [
        (20, True, 2, [0, 20.0]),
        (20, False, 2, [0, 20.0]),
        (20, True, 3, [1, 13.333333333]),
        (20, True, 4, [2, 10]),
        (20, True, 5, [3, 8]),
        (100, True, 2, [1, 18.994]),
        (100, True, 3, [1, 13.3333333]),
        (200, True, 2, [3, 9.497]),
        (200, True, 3, [3, 9.497]),
        (200, True, 4, [3, 9.497]),
        (200, True, 5, [3, 8]),
    ],
)
def test_get_amp_order(m_total, HM, m_HM, expected):
    """"Check that the starting frequency and amp_order are as expected"""
    amp_order, f_start, _ = get_amp_order(m_total, HM=HM, m_HM=m_HM)
    assert amp_order == expected[0], "amp_order was not correct!"
    assert np.allclose(f_start, expected[1], rtol=2e-2), "f_start was not correct!"


@pytest.mark.skipif(
    "LAL_DATA_PATH" not in os.environ, reason="LAL_DATA_PATH not found",
)
@pytest.mark.parametrize(
    "m1,m2,chi1z,chi2z,flow",
    [
        (40.0, 20.0, 0.8, 0.8, 20.0),
        (40.0, 20.0, -0.99, -0.99, 20.0),
        (40.0, 20.0, 0.8, 0.8, 10.0),
        (80.0, 20.0, 0.99, -0.8, 10.0),
        (300.0, 50.0, 0.99, 0.8, 10.0),
    ],
)
def test_estimate_seglen(m1, m2, chi1z, chi2z, flow):
    """ Test that the seglen is correct. This is done
    by comparing to an independent estimate of the seglen"""
    duration, roll_on, seglen_check = manual_seglen(m1, m2, chi1z, chi2z, flow)
    full_len, with_pad, seglen = estimate_seglen(
        flow, m1 + m2, safety_factor=0.03, q=m1 / m2, chi1z=chi1z, chi2z=chi2z
    )
    assert np.allclose(seglen, seglen_check), "seg lengths are not the same"
    assert np.allclose(
        full_len, duration, rtol=1e-1
    ), "Estimated durations differ by more than 10 %"


@pytest.mark.parametrize(
    "m1,m2,chi1z,chi2z,ell",
    [
        (40.0, 20.0, 0.8, 0.8, 2),
        (40.0, 20.0, -0.99, -0.99, 2),
        (40.0, 20.0, 0.8, 0.8, 2),
        (80.0, 20.0, 0.99, 0.1, 2),
        (300.0, 50.0, 0.99, 0.8, 2),
        (40.0, 20.0, 0.8, 0.8, 3),
        (40.0, 20.0, -0.99, -0.99, 3),
        (40.0, 20.0, 0.8, 0.8, 3),
        (80.0, 20.0, 0.99, -0.8, 3),
        (300.0, 50.0, 0.99, 0.8, 3),
        (40.0, 20.0, 0.8, 0.8, 4),
        (40.0, 20.0, -0.99, -0.99, 4),
        (40.0, 20.0, 0.8, 0.8, 4),
        (80.0, 20.0, 0.99, -0.8, 4),
        (300.0, 50.0, 0.99, 0.8, 4),
    ],
)
def test_min_sampling_rate(m1, m2, chi1z, chi2z, ell):
    """Check the sampling rate is correct. Uses PhenomX fits for QNM
    modes to be independent"""
    max_freq_check = manual_qnm_frequency(m1, m2, chi1z, chi2z, ell, ell)
    raw_srate_check = 2 * max_freq_check
    srate_check = next_power_of_2(int(raw_srate_check))
    raw_srate, srate = min_sampling_rate_EOB(
        m1 + m2, q=m1 / m2, chi1z=chi1z, chi2z=chi2z, HM=True, ell_max=ell
    )
    assert np.allclose(
        raw_srate, raw_srate_check, rtol=0.1
    ), "Raw sampling rates are not the same!"
    print(f"raw = {raw_srate}, raw_check = {raw_srate_check}")
    print(f"srate = {srate}, srate_check = {srate_check}")
    assert np.allclose(srate, srate_check), "Final sampling rates are not the same!"

