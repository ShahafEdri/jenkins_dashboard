import re
from datetime import datetime, timedelta
from jenkins_api import JenkinsAPI
from config import config
from test_manager_api import TestManagerAPI
import yaml
from project_errors import ActionError


class DataCollector:
    def __init__(self):
        self.jk_api = JenkinsAPI(config['jenkins_url'], config['jenkins_user'], config['jenkins_token'])
        self.tst_m_api = TestManagerAPI()

    def _is_build_hold_on_failure_on_server(self, server, build_number):
        return self.tst_m_api.is_build_hold_on_failure_on_server(build_number=build_number, server=server)

    def _fix_params(self, info_dict):
        info_dict['timestamp_origin'] = info_dict['timestamp']
        info_dict['duration_origin'] = info_dict['duration']
        info_dict['timestamp'] = datetime.fromtimestamp(info_dict['timestamp_origin']/1000).strftime('%Y-%m-%d %H:%M')
        duration = timedelta(milliseconds=info_dict['duration_origin'])
        info_dict['duration'] = str(duration)[:-7] if str(duration) != '0:00:00' else str(duration)  # remove milliseconds
        # 'displayName': 'RID: #346267, Lab4233, J#24282 (Controller none), swrelease@pliops.com'
        try:
            info_dict['server'] = re.search(r'Lab\w+', info_dict['displayName']).group(0)
        except AttributeError:
            info_dict['server'] = "None"
        if info_dict['result'] == 'ABORTED':
            info_dict['result'] = 'Aborted'
        elif info_dict['server'] == "None":
            info_dict['result'] = 'Pending'
        elif bool(info_dict['inProgress']):
            info_dict['result'] = 'Running..'

    def _assign_build_params(self, info, job_name, build_number):
        info["job_name"] = job_name
        info["build_number"] = build_number

    def _concat_hold_on_failure(self, info_dict):
        if info_dict['result'] == 'FAILURE':
            response = self._is_build_hold_on_failure_on_server(info_dict['server'], info_dict['build_number'])
            if response==True:
                info_dict['server'] = f"{info_dict['server']}(HOF)"
            elif str(response)=="error":
                info_dict['server'] = f"{info_dict['server']}*"

    def _get_additional_params_from_yaml(self, info_dict):
        actions_list = info_dict["actions"]
        # find "name": "ADDITIONAL_PARAMS" in actions_list which is a list of dicts
        for action in actions_list:
            if action.get("_class", "") == "hudson.model.ParametersAction":
                tmp_list = action["parameters"]
        for action in tmp_list:
            if action["name"] == "ADDITIONAL_PARAMS":
                additional_params_yaml_text = action["value"]
        try:
            return yaml.safe_load(additional_params_yaml_text)
        except:
            return None

    def _parameters_picker(self, info_dict, additional_params):
        config["job_parameters_yaml_selector"]
        for param, nest_path_list in config["job_parameters_yaml_selector"].items():
            info_dict[param] = additional_params
            for nest in nest_path_list:
                try:
                    info_dict[param] = info_dict[param][nest]
                except (KeyError, TypeError):
                    info_dict[param] = None
                    break

    def _get_parameters_from_jenkins_additional_params(self, info_dict):
        additional_params = self._get_additional_params_from_yaml(info_dict)
        self._parameters_picker(info_dict, additional_params)

    def get_build_params(self, job_name, build_number):
        # add catch exception
        info_dict = self.jk_api.get_job_info(job_name=job_name, build_number=build_number)
        if info_dict is None:
            info_dict = {}
            self._assign_build_params(info_dict, job_name, build_number)
        else:
            self._assign_build_params(info_dict, job_name, build_number)
            self._fix_params(info_dict)
            self._concat_hold_on_failure(info_dict)
            self._get_parameters_from_jenkins_additional_params(info_dict)
        params_list = config['job_parameters_display']
        info_dict = {param: info_dict.get(param, '-') for param in params_list}
        return info_dict

    def trigger_unlock_node_job(self, lab_or_build_number: str):
        if re.match(r'[Ll][Aa][Bb]\w+', lab_or_build_number):
            return self.jk_api._trigger_unlock_node_job_by_node(lab_or_build_number.title())
        elif re.match(r'\d+', lab_or_build_number):
            server = self.jk_api.get_server_name(build_number=lab_or_build_number)
            if self._is_build_hold_on_failure_on_server(server=server, build_number=lab_or_build_number):
                return self.jk_api._trigger_unlock_node_job_by_build_number(lab_or_build_number)
            return ActionError(f'Build {lab_or_build_number} is not hold on failure on server {server}')
        else:
            raise ValueError(f'lab_or_build_number: {lab_or_build_number} is not a valid value, can be LabXXXX or build number')


if __name__ == '__main__':
    data_collector = DataCollector()
    print(data_collector.get_build_params('request_runner', 24282))
