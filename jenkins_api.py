import time
import requests
import json
import warnings
from datetime import datetime, timedelta
import os
from config import config
import re
from cache_api import Cache


class JenkinsAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = (username, password)
        self.cache_file = 'cache_jenkins.json'
        self.cache = Cache(self.cache_file, 1)
        warnings.filterwarnings('ignore')

    def _make_get_request(self, endpoint, force=False):
        url = self.base_url + endpoint
        if self.cache.is_cache_expired(url) or force:
            data = self._get_data_from_jenkins(url)
            self.cache[url] = data
        else:
            data = self.cache[url]
        return data

    def _get_data_from_jenkins(self, url):
        response = requests.get(url, auth=self.auth, verify=False)
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return None
            else:
                raise e

    def _make_post_request(self, endpoint, data):
        url = self.base_url + endpoint
        response = requests.post(url, auth=self.auth, data=data, verify=False)
        response.raise_for_status()
        return response.status_code in [200, 201]  # 201 is the status code for successful POST request

    def get_job_info(self, build_number, job_name=config["job_name"]):
        endpoint = f'/job/{job_name}/{build_number}/api/json'
        return self._make_get_request(endpoint)

    def trigger_job(self, job_name, parameters):
        endpoint = f'/job/{job_name}/buildWithParameters'
        data = parameters
        return self._make_post_request(endpoint, data)

    def _trigger_unlock_node_job_by_build_number(self, build_number):
        info_dict = self.get_job_info(build_number)
        info_dict['server'] = re.search(r'Lab\d{4}', info_dict['displayName']).group(0)
        return self._trigger_unlock_node_job(info_dict['server'])

    def _trigger_rebuild_job(self, build_number):
        jenkins_dict = self.get_job_info(build_number=build_number)
        parameters = self.extract_input_parameters(jenkins_dict)
        return self.trigger_job(job_name=config['job_name'], parameters=parameters)

    def trigger_rebuild_job(self, build_number):
        last_build_number = self.get_last_build_number()
        rebuild_job_status = self._trigger_rebuild_job(build_number)
        if rebuild_job_status:
            if self.wait_for_new_build(last_build_number):
                # get list of builds started after last_build_number
                builds = self.get_job_builds()
                # get build number of the new build
                build_count = builds[0]['number'] - last_build_number
                # get build list of the new builds
                builds_list = self.get_job_builds()[0:build_count]
                # get build numbers of the new builds
                build_numbers_list = [build['number'] for build in builds_list]
                return build_numbers_list
        else:
            return False

    def wait_for_new_build(self, last_build_number, timeout=60):
        time_now = datetime.now()
        while time_now + timedelta(seconds=timeout) > datetime.now():
            new_build_number = self.get_last_build_number()
            if new_build_number != last_build_number:
                return True
            else:
                time.sleep(1)
        return False

    def extract_input_parameters(self,jenkins_dict):
        # get 'action' parameters
        actions_list = jenkins_dict['actions']
        # from actions_list get key _class with value hudson.model.ParametersAction
        parameters_jenkins_json = next((item for item in actions_list if item["_class"] == "hudson.model.ParametersAction"), None)
        # from parameters_action get key parameters with value list of parameters
        parameter_list = parameters_jenkins_json['parameters']
        # transform parameter_list to dictionary
        parameters_dict = self.transform_paramters_form_jenkins_parameter_list(parameter_list)
        return parameters_dict

    @staticmethod
    def transform_paramters_form_jenkins_parameter_list(parameter_list):
        # parameters are in format of list of dictionaries, located in _class=hudson.model.StringParameterValue
        # and _class=hudson.model.TextParameterValue. if there is a problem, use this. 
        # from all parameters_list get key _class with value hudson.model.StringParameterValue
        # from all parameters_list get key _class with value hudson.model.TextParameterValue
        parameters_dict = {item['name']: item['value'] for item in parameter_list if(('name' in item )and ('value' in item))}
        return parameters_dict

    def trigger_unlock_node_job(self, lab_or_build_number):
        if re.match(r'Lab\d{4}', lab_or_build_number):
            return self._trigger_unlock_node_job(lab_or_build_number)
        elif re.match(r'\d+', lab_or_build_number):
            return self._trigger_unlock_node_job_by_build_number(lab_or_build_number)
        else:
            raise ValueError(f'lab_or_build_number: {lab_or_build_number} is not a valid value, can be LabXXXX or build number')



    def _trigger_unlock_node_job(self, node_name):
        parameters = {
            'NODE': node_name
        }
        return self.trigger_job('Unlock_Node', parameters)

    def stop_job(self,  build_number, job_name=config['job_name']):
        endpoint = f'/job/{job_name}/{build_number}/stop'
        return self._make_post_request(endpoint, None)

    def get_job_builds(self, job_name=config['job_name'], force=False):
        endpoint = f'/job/{job_name}/api/json'
        job_info = self._make_get_request(endpoint, force=force)
        return job_info['builds']
    
    def get_last_build_number(self, job_name=config['job_name']):
        builds = self.get_job_builds(job_name, force=True)
        return builds[0]['number']

if __name__ == "__main__":
    jenkins_api = JenkinsAPI(os.environ['JENKINS_URL'], os.environ['JENKINS_USER'], os.environ['JENKINS_TOKEN'])
    # print(jenkins_api.get_job_info('request_runner', 24282))
    # print(jenkins_api.get_job_info('request_runner', 24283))
    # print(jenkins_api.trigger_unlock_node_job('4444'))
    print(jenkins_api.trigger_rebuild_job('47914'))
