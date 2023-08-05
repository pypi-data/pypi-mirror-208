import importlib
import os
import configparser
import json

import h5py
from asimov.pipeline import Pipeline
from asimov import config
import htcondor
import yaml
from asimov.utils import set_directory

class AsimovPipeline(Pipeline):
    """
    An asimov pipeline for heron.
    """
    name = "peconfigurator"
    config_template = os.path.join(os.path.dirname(__file__), "asimov_template.yaml")
    #importlib.resources.path(__package__, "asimov_template.yaml")
    _pipeline_command = "peconfigurator"


    def _find_posterior(self):
        """
        Find the input posterior samples.
        """
        if self.production.dependencies:
            productions = {}
            for production in self.production.event.productions:
                productions[production.name] = production
            for previous_job in self.production.dependencies:
                print("assets", productions[previous_job].pipeline.collect_assets())
                try:
                    if "samples" in productions[previous_job].pipeline.collect_assets():
                        posterior_file = productions[previous_job].pipeline.collect_assets()['samples']
                        if "dataset" not in self.production.meta:
                            with h5py.File(posterior_file,'r') as f:
                                keys = list(f.keys())
                            keys.remove('version')
                            keys.remove('history')
                            self.production.meta['dataset'] = keys[0]
                        return posterior_file
                except Exception:
                    pass
        else:
            self.logger.error("Could not find an analysis providing the posterior to analyse.")
    
    def build_dag(self, dryrun=False):
        """
        Create a condor submission description.
        """
        name = self.production.name
        ini = self.production.event.repository.find_prods(name,
                                                          self.category)[0]

        meta = self.production.meta
        posterior = self._find_posterior()

        executable = f"{os.path.join(config.get('pipelines', 'environment'), 'bin', self._pipeline_command)}"
        command = ["--dataset", f"{meta['dataset']}",
                   "--output_dir", "results",
                   "--json_file", "recommendations.json",
	           "--q-min", f"{meta['minimum mass ratio']}",
                   ]
        if "higher modes" in meta['checks']:
            command += ["--HM"]
        if "luminosity distance" in meta['checks']:
            command += ["--include_dL_recommendations"]
        if "no safety" in meta['checks']:
            command += ["--override_safeties"]
        command += [posterior]
        # To do: Add remaining settings once you've decided where they should go
        full_command = executable + " " + " ".join(command)
        self.logger.info(full_command)
        
        description = {
            "executable": executable,
            "arguments": " ".join(command),
            "output": f"{name}.out",
            "error": f"{name}.err",
            "log": f"{name}.log",
            "getenv": "True",
            "request_memory": "4096 MB",
            "request_disk": "100 MB",
            "batch_name": f"{self.name}/{self.production.event.name}/{name}",
            "accounting_group_user": config.get('condor', 'user'),
            "accounting_group": self.production.meta['scheduler']["accounting group"],
            "request_disk": "8192MB",
            "+flock_local": "True",
            "+DESIRED_Sites": htcondor.classad.quote("nogrid"),
        }

        job = htcondor.Submit(description)
        os.makedirs(self.production.rundir, exist_ok=True)
        with set_directory(self.production.rundir):
            os.makedirs("results", exist_ok=True)
            
            with open(f"{name}.sub", "w") as subfile:
                subfile.write(job.__str__())

            with open(f"{name}.sh", "w") as bashfile:
                bashfile.write(str(full_command))
                
        with set_directory(self.production.rundir):
            try:
                schedulers = htcondor.Collector().locate(htcondor.DaemonTypes.Schedd, config.get("condor", "scheduler"))
            except configparser.NoOptionError:
                schedulers = htcondor.Collector().locate(htcondor.DaemonTypes.Schedd)
            schedd = htcondor.Schedd(schedulers)
            with schedd.transaction() as txn:
                cluster_id = job.queue(txn)

        self.clusterid = cluster_id

    def submit_dag(self, dryrun=False):
        self.production.status = "running"
        self.production.job_id = int(self.clusterid)
        return self.clusterid

    def collect_assets(self):
        output = {}
        if os.path.exists(os.path.join(self.production.rundir, "results")):
            output['recommendations'] = os.path.join(self.production.rundir, "results", "recommendations.json")
        return output
    
    def detect_completion(self):
        self.logger.info("Checking for completion.")
        results = self.collect_assets()
        if len(list(results.keys())) > 0:
            self.logger.info("Outputs detected, job complete.")
            return True
        else:
            self.logger.info("Datafind job completion was not detected.")
            return False

    def after_completion(self):
        """
        Add the recommendations to the ledger.
        """
        with open(self.collect_assets()['recommendations'], "r") as datafile:
            data = json.load(datafile)

        meta = self.production.event.meta

        if "waveform" not in meta:
            meta['waveform'] = {}
        if "likelihood" not in meta:
            meta['likelihood'] = {}
        
        if 'srate' in data:
            meta['likelihood']['sample rate'] = data['srate']

        if 'f_start' in data:
            meta['likelihood']['start frequency'] = data['f_start']
            
        if 'f_ref' in data:
            meta['waveform']['reference frequency'] = data['f_ref']

        if 'seglen' in data and 'segment length' not in meta['data']:
            meta['data']['segment length'] = data['seglen']
        if 'window length' not in meta['likelihood']:
            meta['likelihood']['window length'] = meta['data']['segment length']
        if 'psd length' not in meta['likelihood']:
            meta['likelihood']['psd length'] = meta['data']['segment length']

        if "chirpmass_min" in data:
            if not "chirp mass" in meta['priors']:
                meta['priors']['chirp mass'] = {}
            meta['priors']['chirp mass']['minimum'] = data['chirpmass_min']
            meta['priors']['chirp mass']['maximum'] = data['chirpmass_max']
        self.production.event.update_data()
        self.production.status = "uploaded"
