#!/usr/bin/env python3
import argparse
import glob
import json
import os
import subprocess as sp
import logging

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=str, help="The repo with all the superevents")
    p.add_argument(
        "--run_map",
        type=str,
        help="JSON file specifying the superevent names and corresponding datasets to consider",
    )
    p.add_argument("--output_dir", type=str, help="Directory for output", default=".")
    p.add_argument(
        "--json_output",
        action="store_true",
        help="Generate machine-readable json results",
    )
    p.add_argument(
        "--full_reports", action="store_true", help="Generate the verbose html reports"
    )
    args = p.parse_args()
    script_dir = os.path.abspath(os.path.dirname(__file__))
    # Load the json data
    try:
        with open(args.run_map, "rb") as fp:
            configs = json.load(fp)
    except:
        exit(1)

    # Loop over every superevent and run the configurator
    for sevent, dataset in configs.items():
        full_path = os.path.join(args.repo, sevent, "Preferred", "PESummary_metafile")
        posterior_samples = glob.glob(f"{full_path}/posterior_samples*")
        if len(posterior_samples) > 1:
            for it in posterior_samples:
                if "h5" in posterior_samples:
                    posterior_samples = it
        else:
            posterior_samples = posterior_samples[0]

        try:
            os.mkdir(f"{args.output_dir}/{sevent}")
        except OSError:
            pass
        if args.json_output and args.full_reports:
            cmd = f"python {script_dir}/proc_samples.py --HM --dataset {dataset} --json_file {sevent}.json --report_file {sevent}.ipynb --output_dir {args.output_dir}/{sevent}  {posterior_samples} > {args.output_dir}/{sevent}/{sevent}.log"
        elif args.json_output and args.full_reports is None:
            cmd = f"python {script_dir}/proc_samples.py --HM --dataset {dataset} --json_file {sevent}.json --output_dir {args.output_dir}/{sevent}  {posterior_samples} > {args.output_dir}/{sevent}/{sevent}.log"
        elif args.json_output is None and args.full_reports:
            cmd = f"python {script_dir}/proc_samples.py --HM --dataset {dataset} --report_file {sevent}.ipynb --output_dir {args.output_dir}/{sevent} {posterior_samples} > {args.output_dir}/{sevent}/{sevent}.log"
        else:
            cmd = f"python {script_dir}/proc_samples.py --HM --dataset {dataset} --output_dir {args.output_dir}/{sevent} {posterior_samples} > {args.output_dir}/{sevent}/{sevent}.log"

        try:
            sp.check_call(cmd, shell=True)
        except sp.CalledProcessError:
            logging.error(
                f"Failed to process {sevent} with dataset {dataset}. Will continue, but results should be inspected"
            )
            continue
