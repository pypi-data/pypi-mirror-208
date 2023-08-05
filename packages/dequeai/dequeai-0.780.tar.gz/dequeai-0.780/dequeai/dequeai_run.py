import datetime
import os
import traceback
import coolname
from dequeai.rest_connect import RestConnect
from dequeai.deque_environment import AGENT_API_SERVICE_URL
import pickle
import multiprocessing
from dequeai.parsing_service import ParsingService
from dequeai.datatypes import Image, Audio, Histogram, BoundingBox2D, Table  # , Plot
from dequeai.util import MODEL, CODE, DATA, ENVIRONMENT, RESOURCES, TRACKING_ENDPOINT
import requests
import glob
import time
import psutil
import GPUtil
import socket
import types
from IPython.display import display, HTML
from tabulate import tabulate
import numpy as np

_RESOURCE_MONITORING_INTERVAL = 60


class Run:

    def __init__(self):
        self.user_name = None
        self._workload_type = None
        self.project_id = None
        self._project_name = None
        self._workload_id = None
        self._api_key = None
        self._submission_id = None
        self._agent_id = None
        self.params = dict()
        self._history = dict()
        self._step = 1
        self._run_id = None
        self._rest = RestConnect()
        self._agent_network_details = self._get_network_details()
        self._run_meta_data = None
        self._model_logged = False
        self._code_logged = False
        self._running = False
        self._environment_logged = False
        self._resources_logged = False
        self._res_monitor = None
        self._run_start_time = None

    def init(self, user_name, api_key, project_name=None):

        os.environ["running"] = "yes"
        is_authenticated = self._authenticate(user_name=user_name, api_key=api_key)
        if is_authenticated:
            self.user_name = user_name
            self._api_key = api_key
        else:
            self.user_name = None
            raise ValueError("Invalid user and/or api key")
        self._run_start_time = datetime.datetime.now()
        self._running = True
        self._workload_type = os.getenv("workload_type")
        self._workload_id = os.getenv("workload_id")
        #if self._workload_type is None or self._workload_id is None:
            #raise ValueError(
               # "Deque AI package is only supported wihtin the Creator's App. Download the app from https://deque.ai")

        self._submission_id = os.getenv("submission_id")
        self._agent_id = os.getenv("agent_id")
        if project_name is None:
            raise ValueError("Project name cannot be empty")
        else:
            self._project_name = project_name

        self._run_id = str(coolname.generate_slug(2))
        self._step = 1
        # p2 = multiprocessing.Process(target=self._start_parser)
        # p2.start()
        self._run_meta_data = {"submission_id": self._submission_id, "run_id": self._run_id,
                               "workload_type": self._workload_type, "workload_id": self._workload_id,
                               "project_name": self._project_name, "user_name": user_name}
        self._model_logged = False
        self._code_logged = False
        self._environment_logged = False
        self._resources_logged = False
        print(
            f"Run initialized with project name as {self._project_name} for user {self.user_name} and run id {self._run_id}")

    def finish(self):
        self._running = False
        os.environ["running"] = "no"
        if self._res_monitor is not None:
            self._res_monitor.terminate()

    def _monitor_resources(self, agent_id, run_id, user_name, project_name, workload_id, submission_id,
                           workload_type, run_start_time):
        running = os.getenv("running")
        step = os.getenv("step")
        current = datetime.datetime.now()
        duration_in_min = (current - run_start_time).total_seconds() / 60
        duration_in_hours = duration_in_min / 60
        while running == "yes":
            current = datetime.datetime.now()
            duration_in_min = (current - run_start_time).total_seconds() / 60
            duration_in_hours = duration_in_min / 60
            running = os.getenv("running")
            gpu_count = len(GPUtil.getGPUs())
            gpu_list = []
            for i in range(gpu_count):
                gpu_dict = {}
                gpu_dict['gpu_name'] = GPUtil.getGPUs()[i].name
                gpu_dict['gpu_driver'] = GPUtil.getGPUs()[i].driver
                gpu_dict['total_memory'] = GPUtil.getGPUs(
                )[i].memoryTotal / 1024  # converted to GB
                gpu_dict['gpu_free_memory'] = GPUtil.getGPUs()[i].memoryFree
                gpu_dict['current_gpu_load'] = 100 * GPUtil.getGPUs()[i].load
                gpu_list.append(gpu_dict)
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            monitoring_info = {
                'agent_id': agent_id,
                'run_id': run_id,
                'user_name': user_name,
                'project_name': project_name,
                'step': step,
                'workload_id': workload_id,
                'submission_id': submission_id,
                'workload_type': workload_type,
                'current_cpu_usage': float(psutil.cpu_percent(interval=1)),
                'cpu_count': int(psutil.cpu_count()),
                'cpu_cores': int(psutil.cpu_count(logical=True)),
                # /(1024*1024*1024) ,# converted to GB
                'available_memory': int(psutil.virtual_memory()[1]),
                # / (1024*1024*1024) ,# converted to GB
                'total_memory': psutil.virtual_memory()[0],
                'memory_utilization': psutil.virtual_memory()[2],
                'current_network_usage': 'unknown',
                'current_gpu_usage': gpu_list,
                'free_disk_space': psutil.disk_usage(os.path.sep)[1],
                'ip_address': host_ip,
                'gpu_list': gpu_list,
                'gpu_count': len(gpu_list),
                'agent_network_details': self._agent_network_details,
                'create_datetime': current,
                'update_datetime': current,
                'duration_in_min': duration_in_min,
                'duration_in_hours': duration_in_hours

            }
            try:
                resp = self._rest.post(
                    AGENT_API_SERVICE_URL + '/fex/experiment/monitor/',
                    json=monitoring_info, )
            except requests.exceptions.ConnectionError as e:
                traceback.print_exc(e)
                time.sleep(10)
                self._monitor_resources(agent_id, run_id, user_name, project_name, workload_id, submission_id,
                                        workload_type)
            except Exception as ge:
                traceback.print_exc(ge)
                time.sleep(10)
                self._monitor_resources(agent_id, run_id, user_name, project_name, workload_id, submission_id,
                                        workload_type)
            time.sleep(_RESOURCE_MONITORING_INTERVAL)

    def _get_network_details(self):

        interfaces = psutil.net_if_addrs()
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        agent_network_details = {'hostname': hostname, 'fqdn': fqdn}
        agent_ip_details = []
        for name, addrs in interfaces.items():

            status = {
                "ipv4": "-",
                "ipv6": "-",
                "mac": "-"
            }
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.netmask is not None:
                    status["ipv4"] = addr.address

                    agent_ip_detail = {'name': name, 'ip_address': addr.address, 'netmask': addr.netmask}
                    agent_ip_details.append(agent_ip_detail)

                if addr.family == socket.AF_INET6:
                    status["ipv6"] = addr.address

                if addr.family == psutil.AF_LINK:
                    status["mac"] = addr.address
        agent_network_details.update({'agent_ip_details': agent_ip_details})
        return agent_network_details

    def log(self, data, step=None, commit=True):
        self._validate_data(data=data)
        full_data = {"experiment_data": data}
        full_data.update(
            {"user_name": self.user_name, "run_id": self._run_id, "workload_type": self._workload_type,
             "workload_id": self._workload_id, "submission_id": self._submission_id,
             "project_name": self._project_name, "deque_log_time": datetime.datetime.now(), "step": self._step})
        p = multiprocessing.Process(target=self._log_task, args=(full_data, self._run_meta_data))
        p.start()
        os.environ['step'] = str(self._step)
        if commit:
            self._step += 1

    def log_hyperparams(self, hyperparams):
        self._validate_hyperparams(hyperparams=hyperparams)
        full_data = {"hyperparams": hyperparams}
        full_data.update(
            {"user_name": self.user_name, "run_id": self._run_id, "workload_type": self._workload_type,
             "workload_id": self._workload_id, "submission_id": self._submission_id,
             "project_name": self._project_name})

        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/experiment/hyperparams/create/",
                             json=full_data)
        res = resp.json()
        print(res)

    def _log_task(self, data, run_meta_data):
        # let's add some System metadata to the data

        metadata = {"GPU": {}}
        gpu_list = GPUtil.getGPUs()
        gpu_count = len(gpu_list)

        for i in range(gpu_count):
            gpu = gpu_list[i]
            gpu_free_memory = gpu.memoryFree
            current_gpu_load = 100 * gpu.load
            total_gpu_memory = gpu.memoryTotal
            metadata["GPU"][str(i)] = {
                "name": gpu.name,
                "memory": {"total": total_gpu_memory, "free": gpu_free_memory},
                "utilization": current_gpu_load
            }

        metadata.update({"CPU": {"utilization": psutil.cpu_percent(interval=1)}})

        metadata.update({"CPU": {"count": int(psutil.cpu_count()),"cores": int(psutil.cpu_count(logical=True))}})
        metadata.update({"memory": {"available": psutil.virtual_memory()[1]}})
        metadata.update({"memory": {"total": psutil.virtual_memory()[0]}})
        metadata.update({"memory": {"utilization": psutil.virtual_memory()[2]}})
        metadata.update({"disk": {"free": psutil.disk_usage(os.path.sep)[1]/(1024.0 ** 3)}})
        data["experiment_data"].update({"System": metadata})

        pickled_data = pickle.dumps(data)
        self._rest.post_binary(url=TRACKING_ENDPOINT, data=pickled_data)

    def log_artifact(self, artifact_type, path):
        if self._run_meta_data is None:
            raise ValueError("Run not initialized. Please call init first")
        if artifact_type == MODEL:
            self._model_logged = True
        elif artifact_type == CODE:
            self._code_logged = True
        elif artifact_type == ENVIRONMENT:
            self._environment_logged = True
        elif artifact_type == RESOURCES:
            self._resources_logged = True
        p2 = multiprocessing.Process(target=self._log_artifact_task, args=(artifact_type, path, self._run_meta_data))
        p2.start()

    def _log_artifact_task(self, artifact_type, path, run_meta_data):

        file_name = os.path.basename(path)
        if artifact_type == MODEL:
            dest_path = "users/" + self.user_name + "/projects/" + self._project_name + "/runs/" + self._run_id + "/model/" + file_name
            valid_extensions = [".h5", ".hdf5", ".pt", ".pth", ".pkl", ".pklz", ".pkl.gz", ".pkl.bz2", ".pkl.xz",
                                ".joblib"]
            if not any(file_name.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("Model file must be one of the following extensions: " + str(valid_extensions))
        elif artifact_type == CODE:
            dest_path = "users/" + self.user_name + "/projects/" + self._project_name + "/runs/" + self._run_id + "/code/" + file_name
            valid_extensions = [".ipynb", ".py"]
            if not any(file_name.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("Code file must be one of the following extensions: " + str(valid_extensions))
        elif artifact_type == ENVIRONMENT:
            dest_path = "users/" + self.user_name + "/projects/" + self._project_name + "/runs/" + self._run_id + "/environment/" + file_name
            if not file_name.lower().endswith("yml"):
                raise ValueError("Environment file must be a .yml file")
        else:
            raise ValueError(
                "artifact_type must be model (file), environment (file), code (file) ")  # or resources (directory)")

        if os.path.isdir(path):
            artifact_uris = []
            for filename in glob.iglob(path + '**/**', recursive=True):
                if os.path.isdir(filename):
                    continue
                dest_path = dest_path + filename
                req_data = {"user_name": self.user_name, "destination_path": dest_path}
                resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/drive/contents/upload/presigned_url/read/",
                                     json=req_data)
                res = resp.json()
                print(res)
                with open(filename, 'rb') as f:
                    files = {'file': (filename, f)}
                    if "fields" in res:
                        http_response = requests.post(url=res['url'], data=res['fields'], files=files)
                    else:
                        # TODO: for google we need a different way to save data
                        object_text = f.read()
                        headers = {'Content-type': "application/octet-stream"}
                        http_response = requests.put(url=res['url'], data=object_text, headers=headers)
                    print(http_response)
                # we record the meta data
            artifact_uris.append(dest_path)
            req_data = {"user_name": self.user_name, "destination_path": dest_path, "artifact_type": artifact_type,
                        "project_name": self._project_name, "run_id": self._run_id, "artifact_uris": artifact_uris}
            resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/artifact/metadata/create/",
                                 json=req_data)
            res = resp.json()
            print(res)
        else:
            req_data = {"user_name": self.user_name, "destination_path": dest_path}
            resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/drive/contents/upload/presigned_url/read/",
                                 json=req_data)
            res = resp.json()
            with open(path, 'rb') as f:
                files = {'file': (path, f)}
                if "fields" in res:
                    http_response = requests.post(url=res['url'], data=res['fields'], files=files)
                else:
                    # TODO: for google we need a different way to save data
                    object_text = f.read()
                    headers = {'Content-type': "application/octet-stream"}
                    http_response = requests.put(url=res['url'], data=object_text, headers=headers)
                print(http_response)
            req_data = {"user_name": self.user_name, "destination_path": dest_path, "artifact_type": artifact_type,
                        "project_name": self._project_name, "run_id": self._run_id, "artifact_uri": dest_path}
            resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/artifact/metadata/create/",
                                 json=req_data)
            res = resp.json()
            print(res)

    def register_artifacts(self, latest=True, label=None, tags=None):
        if not self._model_logged:
            raise ValueError(
                "Please log the model (and optionally code and environment) before calling register_artifacts")
        req_data = {"user_name": self.user_name, "latest": latest, "label": label,
                    "project_name": self._project_name, "run_id": self._run_id, "tags": tags}
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/project/artifacts/register/",
                             json=req_data)
        res = resp.json()
        print(res)

    def load_artifact(self, artifact_type, run_id):
        if self.user_name is None:
            raise ValueError("Please initialize using dequeai.init() before calling load_artifact")
        req_data = {
            "user_name": self.user_name,
            "run_id": run_id,
            "artifact_type": artifact_type
        }
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/artifact/metadata/read/", json=req_data)
        metadata = resp.json()

        if not metadata:
            print("No metadata found for the given run_id and user_name.")
            return

        artifacts = metadata["artifacts"]

        # Download the artifacts using the artifact URIs
        for artifact in artifacts:

            if artifact['artifact_type'] == artifact_type:
                req_data = {
                    "user_name": self.user_name,
                    "complete_object_path": artifact['artifact_uri']
                }
                resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/drive/contents/download/presigned_url/read/",
                                     json=req_data)
                res = resp.json()
                # Download the artifact using the pre-signed URL
                http_response = requests.get(url=res["url"])
                file_name = os.path.basename(artifact['artifact_uri'])
                with open(file_name, "wb") as f:
                    f.write(http_response.content)
                print(f"Downloaded artifact '{file_name}'")

    def _validate_data(self, data):
        new_data = {}
        for key, value in data.items():
            if key is None:
                raise ValueError("Key cannot be None")

            if isinstance(value, dict):
                new_data[key] = self._validate_data(value)
            else:
                if isinstance(value, (Audio, BoundingBox2D, Histogram, Table, Image)) or \
                        type(value) in types.__builtins__.values():
                    new_data[key] = value
                elif isinstance(value, np.generic):  # Check if the value is a numpy type
                    new_data[key] = self._convert_numpy_to_python(value)  # Convert numpy to Python scalar
                else:
                    raise ValueError(
                        "Invalid type in dictionary. Allowed values include builtin types and Deque data types " + str(
                            type(value)) + " " + str(value.__class__.__module__))
        return new_data

    def _convert_numpy_to_python(self, val):
        if np.isscalar(val) and isinstance(val, np.generic):
            return val.item()
        else:
            return val

    def _validate_hyperparams(self, hyperparams):
        for key, value in hyperparams.items():
            if type(value) in types.__builtins__.values():
                pass
            else:
                raise ValueError(
                    "Invalid type in hyperparam dict. Allowed values include builtin types " + str(
                        type(value)) + " " + str(value.__class__.__module__))

    def _send_upstream(self):
        self._rest.post(url=AGENT_API_SERVICE_URL + "/fex/python/track/", json=self._history)
        self._history = dict()

    def _authenticate(self, user_name, api_key):
        req_data = {
            "user_name": user_name,
            "api_key": api_key
        }
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/authenticate/sdk/", json=req_data)
        res = resp.json()
        print(res)
        if "authenticated" in res:
            return res["authenticated"]
        else:
            return False

    def compare_runs(self, project_name, metric_key):
        if self.user_name is None:
            raise ValueError("Please initialize using dequeai.init() before calling compare_runs")

        if project_name is None:
            project_name = self._project_name

        req_data = {
            "user_name": self.user_name,
            "project_name": project_name,
            "metric_key": metric_key
        }
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/project/run/compare/", json=req_data)
        data_list = resp.json()
        # print(data_list)
        # Extract header names
        first_run_data_keys = list(data_list['runs'][0]['best_experiment_data']['data'].keys())
        headers = ['Run ID', 'Best Metric Key', 'Best Metric'] + [f'{key}.{sub_key}' for key in first_run_data_keys for
                                                                  sub_key in
                                                                  data_list['runs'][0]['best_experiment_data']['data'][
                                                                      key]]

        # Extract rows
        rows = []
        for run in data_list['runs']:
            best_metric = self._get_nested_value(run['best_experiment_data']['data'], metric_key)
            row = [run['run_id'], metric_key, best_metric]
            for key in first_run_data_keys:
                row.extend(run['best_experiment_data']['data'][key].values())
            rows.append(row)

        # Use tabulate to generate the HTML table
        html_table = tabulate(rows, headers=headers, tablefmt="html")

        # Style the table with your color palette
        styled_table = f"""
            <style>
                table {{
                    border-collapse: collapse;
                    font-family: Arial, sans-serif;
                    background-color: #60507D;
                    color: #FFFFFF;
                    width: 100%;
                }}
                th {{
                    background-color: #60507D;
                    color: #FFFFFF;
                    padding: 8px;
                    text-align: left;
                }}
                td {{
                    background-color: #60507D;
                    color: #FFFFFF;
                    padding: 8px;
                    text-align: left;
                }}
                tr:nth-child(even) td {{
                    background-color: #60507D;
                    color: #FFFFFF;
                }}
            </style>
            {html_table}
            """

        # Wrap the table in a scrollable div
        scrollable_table = f'<div style="width: 100%; height: 200px; overflow: auto;">{styled_table}</div>'

        # Display the scrollable table in the notebook
        display(HTML(scrollable_table))

    def read_best_run(self, project_name, metric_key):

        if self.user_name is None:
            raise ValueError("Please initialize using dequeai.init() before calling compare_runs")

        if project_name is None:
            project_name = self._project_name

        req_data = {
            "user_name": self.user_name,
            "project_name": project_name,
            "metric_key": metric_key
        }
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/project/run/best/read/", json=req_data)
        data_list = resp.json()
        # print(data_list)
        # Extract header names
        first_run_data_keys = list(data_list['run'][0]['best_experiment_data']['data'].keys())
        headers = ['Run ID', 'Best Metric Key', 'Best Metric'] + [f'{key}.{sub_key}' for key in first_run_data_keys for
                                                                  sub_key in
                                                                  data_list['run'][0]['best_experiment_data']['data'][
                                                                      key]]

        # Extract rows
        rows = []
        for run in data_list['run']:
            best_metric = self._get_nested_value(run['best_experiment_data']['data'], metric_key)
            row = [run['run_id'], metric_key, best_metric]
            for key in first_run_data_keys:
                row.extend(run['best_experiment_data']['data'][key].values())
            rows.append(row)

        # Use tabulate to generate the HTML table
        html_table = tabulate(rows, headers=headers, tablefmt="html")

        # Style the table with your color palette
        styled_table = f"""
            <style>
                table {{
                    border-collapse: collapse;
                    font-family: Arial, sans-serif;
                    background-color: #60507D;
                    color: #FFFFFF;
                    width: 100%;
                }}
                th {{
                    background-color: #60507D;
                    color: #FFFFFF;
                    padding: 8px;
                    text-align: left;
                }}
                td {{
                    background-color: #60507D;
                    color: #FFFFFF;
                    padding: 8px;
                    text-align: left;
                }}
                tr:nth-child(even) td {{
                    background-color: #60507D;
                    color: #FFFFFF;
                }}
            </style>
            {html_table}
            """

        # Wrap the table in a scrollable div
        scrollable_table = f'<div style="width: 100%; height: 200px; overflow: auto;">{styled_table}</div>'

        # Display the scrollable table in the notebook
        display(HTML(scrollable_table))

    def search_runs(self, filter_dict):
        if self.user_name is None:
            raise ValueError("Please initialize using dequeai.init() before calling search_runs")
        req_data = {
            "user_name": self.user_name,
            "filter_dict": filter_dict
        }
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/project/run/search/", json=req_data)
        res = resp.json()
        print(res)
        return res

    def create_report(self, run_ids, file_format="pdf"):
        if self.user_name is None:
            raise ValueError("Please initialize using dequeai.init() before calling create_report")
        req_data = {
            "user_name": self.user_name,
            "run_ids": run_ids,
            "file_format": file_format,
        }
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/project/run/report/create/", json=req_data)
        res = resp.json()
        print(res)
        return res

    def _filter_dicts_by_keys(self, dicts_list, keys, values=None, operators=None):
        filtered_dicts = []

        if not values:
            values = [None] * len(keys)

        if not operators:
            operators = ['=='] * len(keys)

        for d in dicts_list:
            match = True
            for key, value, op in zip(keys, values, operators):
                nested_value = self._get_nested_value(d, key)

                if op == '==':
                    if nested_value != value:
                        match = False
                        break
                elif op == '>':
                    if nested_value is None or nested_value <= value:
                        match = False
                        break
                elif op == '<':
                    if nested_value is None or nested_value >= value:
                        match = False
                        break

            if match:
                filtered_dicts.append(d)

        return filtered_dicts

    def _get_nested_value(self, nested_dict, key):
        keys = key.split('.')
        current_dict = nested_dict

        for k in keys:
            if k in current_dict:
                current_dict = current_dict[k]
            else:
                return None

        return current_dict

    def _gradient_hook(self, module, grad_input, grad_output):
        module_name = module.__class__.__name__

        # Handling multiple input gradients
        for idx, grad in enumerate(grad_input):
            if grad is not None:
                self._log_histogram(f"{module_name}_input_{idx}_grad", grad.cpu().numpy())

        # Handling multiple output gradients
        for idx, grad in enumerate(grad_output):
            if grad is not None:
                self._log_histogram(f"{module_name}_output_{idx}_grad", grad.cpu().numpy())

    def _log_histogram(self, values, bins, min_value=None, max_value=None, density=True):
        """
        Log histogram data from the given values.

        Args:
            values (list or np.array): The values to create the histogram from.
            bins (int): The number of bins to divide the data into.
            min_value (float, optional): The lower bound of the histogram range. Defaults to the minimum value in the dataset.
            max_value (float, optional): The upper bound of the histogram range. Defaults to the maximum value in the dataset.
            density (bool, optional): If True, the histogram will be normalized so that the integral over the range is 1. Defaults to True.

        Returns:
            tuple: A tuple containing the bin edges and the histogram counts.
        """
        if min_value is None:
            min_value = np.min(values)
        if max_value is None:
            max_value = np.max(values)

        # Compute the histogram using numpy
        hist, bin_edges = np.histogram(values, bins=bins, range=(min_value, max_value), density=density)

        return bin_edges, hist

    def log_gradients(self, model):
        for module_name, module in model.named_modules():
            module.register_backward_hook(self._gradient_hook)




if __name__ == "__main__":
    deque = Run()
    deque._validate_hyperparams({"train": {"accuracy": "1.3", "loss": "2.2"}})
    # deque.log_artifact_task(artifact_type=RESOURCES, path="//dequeapp.egg-info",
    #                     run_meta_data=None)
    # deque.init(user_name="riju@deque.app", project_name="awesome-dude")
    # for i in range(100):
    # deque.log(data={"train": {"accuracy": i, "loss": i - 100}, "image": deque.im})

    # deque.log(data={"image":deque.im})
