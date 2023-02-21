import re
from datetime import datetime
from jenkins_api import JenkinsAPI
from config import config
from test_manager_api import TestManagerAPI
import yaml


class DataCollector:
    def __init__(self):
        self.jenkins_api = JenkinsAPI(config['jenkins_url'], config['jenkins_user'], config['jenkins_token'])
        self.test_manager_api = TestManagerAPI()

    def _is_build_hold_on_failure_on_server(self, server, build_number):
        return self.test_manager_api.is_build_hold_on_failure_on_server(build_number=build_number, server=server)

    def _fix_params(self, info_dict):
        info_dict['timestamp_origin'] = info_dict['timestamp']
        info_dict['duration_origin'] = info_dict['duration']
        info_dict['timestamp'] = datetime.fromtimestamp(info_dict['timestamp']/1000).strftime('%Y-%m-%d %H:%M')
        info_dict['duration'] = datetime.fromtimestamp(info_dict['duration']/1000).strftime('%H:%M:%S')
        # 'displayName': 'RID: #346267, Lab4233, J#24282 (Controller none), swrelease@pliops.com'
        info_dict['server'] = re.search(r'Lab\d+', info_dict['displayName']).group(0)
        if bool(info_dict['inProgress']):
            info_dict['result'] = 'Running...'

    def _assign_build_params(self, info, job_name, build_number):
        info["job_name"] = job_name
        info["build_number"] = build_number

    def _concat_hold_on_failure(self, info_dict):
        if self._is_build_hold_on_failure_on_server(info_dict['server'], info_dict['displayName']):
            info_dict['server'] = f"{info_dict['server']}(HOF)"

    def _get_additional_params_from_yaml(self, info_dict):
        yml_text = info_dict["actions"][1]["parameters"][1]["value"]
        return yaml.safe_load(yml_text)

    def _parameters_picker(self, info_dict, additional_params):
        config["job_parameters_yaml_selector"]
        for param, nest_path_list in config["job_parameters_yaml_selector"]:
            info_dict[param] = additional_params
            for nest in nest_path_list:
                info_dict[param] = info_dict[param][nest]

    def _get_parameters_from_jenkins_additional_params(self, info_dict):
        additional_params = self._get_additional_params_from_yaml(info_dict)
        self._parameters_picker(info_dict, additional_params)

    def get_build_params(self, job_name, build_number):
        info = self.jenkins_api.get_job_info(job_name, build_number)
        self._assign_build_params(info, job_name, build_number)
        self._fix_params(info)
        self._concat_hold_on_failure(info)
        params_list = config['job_parameters_display']
        info_dict = {param: info.get(param) for param in params_list}
        return info_dict


if __name__ == '__main__':
    data_collector = DataCollector()
    print(data_collector.get_build_params('request_runner', 24282))
