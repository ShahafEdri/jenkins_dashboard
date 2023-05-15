import requests
import json
import warnings
from datetime import datetime, timedelta
import os
from config import config
import re
import yaml
from cache_api import Cache


class JenkinsAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = (username, password)
        self.cache_file = 'cache_jenkins.json'
        self.cache = Cache(self.cache_file, 1)
        warnings.filterwarnings('ignore')

    def _make_get_request(self, endpoint):
        url = self.base_url + endpoint
        if self.cache.is_cache_expired(url):
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
        return response.status_code == 201  # 201 is the status code for successful POST request

    def get_job_info(self, build_number, job_name=config["job_name"]):
        endpoint = f'/job/{job_name}/{build_number}/api/json'
        return self._make_get_request(endpoint)

    def trigger_job(self, job_name, parameters):
        endpoint = f'/job/{job_name}/buildWithParameters'
        data = parameters
        return self._make_post_request(endpoint, data)

    def trigger_unlock_node_job_by_build_number(self, build_number):
        info_dict = self.get_job_info(build_number)
        info_dict['server'] = re.search(r'Lab\d{4}', info_dict['displayName']).group(0)
        return self.trigger_unlock_node_job(info_dict['server'])

    def trigger_unlock_node_job(self, node_name):
        parameters = {
            'NODE': node_name
        }
        return self.trigger_job('Unlock_Node', parameters)

    def stop_job(self,  build_number, job_name=config['job_name']):
        endpoint = f'/job/{job_name}/{build_number}/stop'
        return self._make_post_request(endpoint, None)


if __name__ == "__main__":
    jenkins_api = JenkinsAPI(os.environ['JENKINS_URL'], os.environ['JENKINS_USER'], os.environ['JENKINS_TOKEN'])
    print(jenkins_api.get_job_info('request_runner', 24282))
    print(jenkins_api.get_job_info('request_runner', 24283))
    # print(jenkins_api.trigger_unlock_node_job('4444'))
