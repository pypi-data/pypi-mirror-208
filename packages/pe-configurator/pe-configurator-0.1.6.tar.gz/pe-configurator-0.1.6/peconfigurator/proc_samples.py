#!/usr/bin/env python3

import argparse
from copy import deepcopy
import datetime
import json
import subprocess as sp

import click
import numpy as np
import pandas as pd
from pesummary.gw.file.read import read
from tqdm import tqdm

from .get_settings import *
from .auxiliary.make_report import make_report
from .auxiliary.run_analyzer import railing_check

# This script will iterate through a repository and check for a preferred run,
# use that to determine the seglen, srate and amp-order for Production runs,
# and Check the ini files for those


def eta_from_q(q):
    """Compute the symmetric mass ratio from the mass ratio"""
    return q / (1.0 + q) ** 2


def mt_from_eta_mc(eta, mc):
    """Compute total mass from symmetric mass ratio and chirp mass"""
    return mc / eta ** (3.0 / 5)


def check_railing(samples, label, nbins, tolerance, checks, recommendations=None):

    rail_low, rail_high, recommendation,bounds = railing_check(
        samples, nbins, tolerance, label
    )
    if rail_low or rail_high:
        click.echo(
            f"Checking for railing in {label}: " + click.style("FAILED", fg="red")
        )
        click.secho(
            f"WARNING: Found railing in {label}, please examine the posterior visually!",
            fg="red",
        )
        checks[label] = False

        recommendations[label] = recommendation
    else:
        click.echo(
            f"Checking for railing in {label}: " + click.style("PASSED", fg="green")
        )
        checks[label] = True
        recommendations[label] = ""
    return bounds

def create_json_output(recommended_settings, output_name, args):
    """Write the results to a json file to allow for easy injections"""
    metadata = dict(date=str(datetime.datetime.now()), command_line_args=str(args))
    dc = deepcopy(recommended_settings)
    dc.update(metadata=metadata)

    with open(f"{args.output_dir}/{output_name}", "w") as json_file:
        json.dump(dc, json_file, indent=4)


def get_preferred_result(file_path):
    """
    Return a pesummary object for the repo
    """
    try:
        sumfile = read(file_path)
    except FileNotFoundError:
        print(f"Could not find the samples file, {file_path}!")
        raise
    return sumfile


def main():
    parser = argparse.ArgumentParser(
        description="Set up / confirm config files for O3a"
    )
    parser.add_argument(
        "samples_file",
        metavar="samples_file",
        type=str,
        help="path to file with samples",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="The dataset inside the samples file that should be used",
    )
    parser.add_argument(
        "--output_dir", type=str, help="Directory where to place output", default="./"
    )
    parser.add_argument(
        "--HM",
        default=False,
        action="store_true",
        help="Do checks with higher modes enabled",
    )
    parser.add_argument(
        "--q-min",
        default=None,
        type=float,
        help="The lower bound of the q-prior to be used for production",
    )
    parser.add_argument(
        "--ell-max", help="The ell to use for HM Nyquist check for EOB", default=3
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        help="Tolerance used when checking for railing",
        default=2.0,
    )
    parser.add_argument(
        "--nbins",
        type=int,
        help="Number of bins used when checking for railing",
        default=50,
    )
    parser.add_argument(
        "--flow",
        type=float,
        help="The frequency used for lower bound of likelihood integral [Hz]",
        default=20.0,
    )
    parser.add_argument(
        "--f_ref", type=float, help="The reference frequency [Hz]", default=20.0
    )
    parser.add_argument(
        "--bounds_tol",
        type=float,
        help="Tolerance to use when suggesting bounds for prior",
        default=0.2,
    )
    parser.add_argument(
        "--json_file",
        type=str,
        help="If supplied write the recommended settings to this json file",
    )
    parser.add_argument(
        "--report_file", type=str, help="If supplied, create a report with plots"
    )
    parser.add_argument(
        "--override_safeties",
        action="store_true",
        help="Disregard all warnings and generate json file anyway. USE AT OWN RISK!",
    )
    parser.add_argument("--debug", action="store_true", help="For debugging")
    parser.add_argument("--include_dL_recommendations",action="store_true",help="Including recommendations for distance in output")
    args = parser.parse_args()

    pesum = get_preferred_result(args.samples_file)

    try:
        samples = pesum.samples_dict[args.dataset]
    except KeyError:
        k = list(pesum.samples_dict.keys())[-1]
        click.secho(
            f"Pesum object in {args.samples_file} did not contain {args.dataset}, exiting!",
            fg="red",
        )
        exit(1)

    mtot = np.array(samples["total_mass"])
    q = np.array(samples["mass_ratio"])
    chi1z = np.array(samples["spin_1z"])
    chi2z = np.array(samples["spin_2z"])
    dist = np.array(samples["luminosity_distance"])
    chirp_mass = np.array(samples["chirp_mass"])

    dc = {
        "total mass": mtot,
        "q": q,
        "Mc": chirp_mass,
        "chi1z": chi1z,
        "chi2z": chi2z,
        "dL": dist,
    }
    df = pd.DataFrame(dc)

    # Round to multiples of 5
    mtot_max = 5 * (float(mtot.max()) // 5 + 1)
    mtot_min = 5 * (float(mtot.min()) // 5)

    # Round up to nearest Gpc
    dist_max = 1000 * (dist.max() // 1000 + 1)

    # Proposed chirp mass bounds

    chirpmass_min = chirp_mass.min()
    chirpmass_max = chirp_mass.max()
    chirpmass_width = chirpmass_max - chirpmass_min

    if chirpmass_width > 30.0:
        chirpmass_min_bound = (1 - args.bounds_tol) * chirpmass_min
        chirpmass_max_bound = (1 + args.bounds_tol) * chirpmass_max
    else:
        chirpmass_min_bound = chirpmass_min - args.bounds_tol * chirpmass_width
        chirpmass_max_bound = chirpmass_max + args.bounds_tol * chirpmass_width

    q_min = float(q.min())
    if args.q_min is not None:
        if args.q_min > q_min:
            q_min = args.q_min

    eta_min = q_min / (1 + q_min) ** 2

    click.echo("Processing....")
    click.echo("Estimating seglen based on posterior samples")

    # seglen section
    # Compute the seglen from the actual samples
    safelens, fulllens, seglens = zip(
        *[
            estimate_seglen(args.flow, mt, q=1.0 / qp, chi1z=s1z, chi2z=s2z)
            for mt, qp, s1z, s2z in tqdm(list(zip(mtot, q, chi1z, chi2z)))
        ]
    )
    nopad_len = np.max(safelens)
    max_seglen = np.max(seglens)

    # Compute a conservative estimate for seglen
    # This is constructed as follows:
    # 1. We find the sample that gives the longest waveform
    # 2. Compute the total mass from this sample's q and proposed lower chirp mass bound
    # 3. Use this total mass and the other params from step 2. to compute the seglen
    # This procedure should overestimate the seglen and therefore be relatively safe.
    idx_max = np.argmax(fulllens)
    q_max = q[idx_max]
    eta_max = eta_from_q(q_max)
    # Given the lower bound of recommended chirp mass compute the corresponding total mass
    mt_lower_bound = mt_from_eta_mc(eta_max, chirpmass_min_bound)
    nopad, full, pof2 = estimate_seglen(
        args.flow,
        mt_lower_bound,
        q=1 / q_max,
        chi1z=chi1z[idx_max],
        chi2z=chi2z[idx_max],
    )

    # seglen section ends

    # srate section
    # Compute sampling rate from the samples
    click.echo("Estimating srate based on posterior samples")
    click.secho(f"Using ell = {args.ell_max} for Nyquist check", bold=True)
    real_srates, srates = zip(
        *[
            min_sampling_rate_EOB(
                mt, q=1.0 / qp, HM=args.HM, chi1z=s1z, chi2z=s2z, ell_max=args.ell_max
            )
            for mt, qp, s1z, s2z in tqdm(list(zip(mtot, q, chi1z, chi2z)))
        ]
    )
    max_srate = np.max(srates)
    max_real_rate = np.max(real_srates)

    click.echo("Checking this srate works with the proposed lower chirp mass bound")
    # We do the following:
    # 1.  Find the sample that gives the highest srate
    # 2. Use that samples's q to and lower chirp mass bound to compute a new total mass
    # 3. Use this total mass and other params from the sample to recompue the srate
    mx_config = np.argmax(real_srates)
    q_max = q[mx_config]
    eta_max = eta_from_q(q_max)
    mtot_est = mt_from_eta_mc(eta_max, chirpmass_min_bound)

    real_srate_adj, srate_adj = min_sampling_rate_EOB(
        mtot_est,
        q=1.0 / q[mx_config],
        HM=args.HM,
        chi1z=chi1z[mx_config],
        chi2z=chi2z[mx_config],
        ell_max=args.ell_max,
    )

    if srate_adj > max_srate:
        click.secho(
            "Adjusting the sampling rate to take into account proposed chirp mass bounds"
        )
        max_srate = srate_adj
        max_real_rate = real_srate_adj
    else:
        click.secho("No adjustment necessary!")
    # srate section ends

    # f_start section
    # The f_start based on preliminary samples
    click.echo("Estimating f_start based on posterior samples")
    seobp_amporder, f_start, hm_dominated = get_amp_order(
        mtot_max, f_low=args.flow, HM=args.HM
    )

    click.echo("Checking this f_start works with the proposed upper chirp mass bound")
    # The f_start taking into account the proposed change to chirp mass bounds
    # The change can only happen if the total mass is so high that EOB can
    # no longer generate a waveform. If that's the case, we adjust the starting
    # frequency accordingly
    # Use the heaviest samples parameters
    idx = np.argmax(mtot)
    q_max = q[idx]
    eta_max = eta_from_q(q_max)
    mtot_max_adj = mt_from_eta_mc(eta_max, chirpmass_max_bound)
    seobp_amporder_adj, f_start_adj, hm_dominated_adj = get_amp_order(
        mtot_max_adj, f_low=args.flow, HM=args.HM
    )
    if f_start_adj < f_start:
        f_start = f_start_adj
        seobp_amporder = seobp_amporder_adj
        click.echo(
            "The start frequency had to be adjusted to accomodate the changed chirp mass"
        )
    else:
        click.echo("No adjustment necessary!")
    # f_start section ends

    click.echo("Done processing")
    click.echo()
    click.echo("#" * 30 + " SUMMARY " + 30 * "#")
    click.echo("Posterior parameters")
    click.echo("--" * 20)
    print(df.describe())
    click.echo("--" * 20)
    click.echo("Sanity checks")

    checks_passed = True
    checks = {}
    recs = {}

    # Railing checks
    check_railing(
        chirp_mass,
        "chirp_mass",
        args.nbins,
        args.tolerance,
        checks,
        recommendations=recs,
    )
    bounds_distance = check_railing(
        dist, "distance", args.nbins, args.tolerance, checks, recommendations=recs
    )
    check_railing(
        q, "mass_ratio", args.nbins, args.tolerance, checks, recommendations=recs
    )
    # End railing checks

    # MECO check section
    new_checks = checks.copy()
    f_ref = args.f_ref

    f_MECOs = np.array(
        [
            MECO_freq(mt, 1 / qp, s1z, s2z)
            for mt, qp, s1z, s2z in list(zip(mtot, q, chi1z, chi2z))
        ]
    )

    f_MECO_min = np.min(f_MECOs)
    if f_ref >= 0.97 * f_MECO_min:
        click.echo(
            "Checking that f_ref is not above f_MECO: "
            + click.style("FAILED", fg="red")
        )
        click.secho(
            f"WARNNING: the reference frequency {f_ref}>=0.97*min(f_MECO), f_MECO = {f_MECO_min}, overwritting reference frequency to f_ref=0.95*min(f_MECO)",
            fg="red",
        )
        checks["f_ref"] = False
        f_ref = 0.95 * f_MECO_min
        new_checks["f_ref"] = True

    else:
        click.echo(
            "Checking that f_ref is not above f_MECO: "
            + click.style("PASSED", fg="green")
        )
        checks["f_ref"] = True
        new_checks["f_ref"] = True

    # Do we pass the MECO check with the expanded chirp mass?
    idx_min = np.argmin(f_MECOs)
    q_min = q[idx_min]
    eta_min = eta_from_q(q_min)
    mtot_min_adj = mt_from_eta_mc(eta_min, chirpmass_max_bound)
    f_meco = MECO_freq(mtot_min_adj, 1 / q_min, chi1z[idx_min], chi2z[idx_min])
    if f_ref >= 0.97 * f_meco:
        click.secho(
            f"The reference frequency ({f_ref}) is too close to the new MECO frequency, {f_meco} Hz, overwritting reference frequency to f_ref=0.95*f_MECO",
            fg="red",
        )
        checks["f_ref"] = False
        f_ref = 0.95 * f_meco
        new_checks["f_ref"] = True

    if f_ref < f_start:
        click.secho(
            f"The reference frequency ({f_ref}) is lower than the starting waveform generation frequency, {f_start} Hz, overwritting reference frequency to f_start.",
            fg="red",
        )
        checks["f_ref"] = False
        f_ref = f_start
        new_checks["f_ref"] = True

    # MECO check section ends

    click.echo()
    click.echo(30 * "+" + " Suggested settings " + 30 * "+")
    click.echo(f"Real required srate  {max_real_rate}, as power of 2: {max_srate}")

    click.echo(
        f"Real seglen: {nopad}, with padding+rollon: {full}, as power of 2: {pof2}"
    )

    click.echo("Check from samples:")
    click.echo(
        f"Real seglen: {nopad_len}, with padding+rollon: {np.max(fulllens)}, as power of 2: {max_seglen}"
    )

    click.echo(f"f_start: {f_start}")
    click.echo(
        f"Real bounds on chirp mass: [{chirpmass_min},{chirpmass_max}], suggested bounds: [{chirpmass_min_bound},{chirpmass_max_bound}]"
    )
    click.echo(f"Real distance max: {dist_max}")
    recommended_settings = dict(
        srate=int(max_srate),
        f_start=f_start,
        f_ref=f_ref,
        seglen=pof2,
        chirpmass_min=chirpmass_min_bound,
        chirpmass_max=chirpmass_max_bound,
        meco_status=str(checks["f_ref"]),
    )
    if args.debug:
        recommended_settings.update(
            seglen_conservative=full,
            seglen_liberal=np.max(fulllens),
            real_srate=max_real_rate,
            srate_adjusted=srate_adj,
            real_srate_adj=real_srate_adj,
            start_frequency_adj=f_start_adj,
            f_MECO=f_MECO_min,
            f_MECO_adj=f_meco,
        )
    if args.include_dL_recommendations:
        if bounds_distance[0] is not None:
            recommended_settings.update(dL_min=bounds_distance[0])
        if bounds_distance[1] is not None:
            recommended_settings.update(dL_max=bounds_distance[1])

    # np.savetxt("liberal_seglens.dat",fulllens)
    # Did all the checks pass?
    checks_passed = all(new_checks.values())
    click.echo(80 * "+")
    click.echo()

    click.echo("Creating machine-readable json file")
    if args.override_safeties:
        click.secho("Overriding safeties as requested!", fg="yellow")
    # If requested, make the json file with output
    if args.json_file is not None and (checks_passed or args.override_safeties):
        create_json_output(recommended_settings, args.json_file, args)

    click.echo("Creating a more detailed report with plots")

    # If requested, make a detailed report with plots
    if args.report_file is not None:
        make_report(
            args.samples_file,
            recommended_settings,
            args,
            f_ref,
            checks=checks,
            recommendations=recs,
            analysis=args.dataset,
            filename=args.report_file,
            outdir=args.output_dir,
        )
        sp.call(
            f"jupyter nbconvert --output-dir={args.output_dir} --no-input --to html  --execute --ExecutePreprocessor.timeout=120 {args.output_dir}/{args.report_file}",
            shell=True,
        )


if __name__ == "__main__":
    main()
