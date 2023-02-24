import requests
import json
import warnings
from datetime import datetime, timedelta
import os
from config import config
import re
import yaml


class JenkinsAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = (username, password)
        self.cache_file = 'cache.json'
        self.cache_expiry = timedelta(minutes=1)
        warnings.filterwarnings('ignore')

    def _make_get_request(self, endpoint):
        url = self.base_url + endpoint
        if self._is_cache_expired(url):
            data = self._get_data_from_jenkins(url)
            self._cache_data(url, data)
        else:
            data = self._get_cached_data(url)
        return data

    def _get_data_from_jenkins(self, url):
        response = requests.get(url, auth=self.auth, verify=False)
        response.raise_for_status()
        return response.json()

    def _cache_data(self, url:str, data) -> None:
        # save the cache by url as key and time and data as value
        # if the cache is expired
        cache = {
            url:{
                'time': datetime.now().timestamp(),
                'data': data
                }
            }
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f)

    def _get_cached_data(self, url):
        with open(self.cache_file, 'r') as f:
            cache = json.load(f)
            return cache[url]['data']

    def _is_cache_expired(self, url):
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                if url in cache:
                    time = cache[url]['time']
                    time = datetime.fromtimestamp(time)
                    if time + self.cache_expiry > datetime.now():
                        return False
        except FileNotFoundError:
            return True
        return True

    def _make_post_request(self, endpoint, data):
        url = self.base_url + endpoint
        response = requests.post(url, auth=self.auth, data=data, verify=False)
        response.raise_for_status()
        return response.status_code == 201  # 201 is the status code for successful POST request

    def get_job_info(self, job_name, build_number):
        endpoint = f'/job/{job_name}/{build_number}/api/json'
        return self._make_get_request(endpoint)

    def trigger_job(self, job_name, parameters):
        endpoint = f'/job/{job_name}/buildWithParameters'
        data = parameters
        return self._make_post_request(endpoint, data)

    def trigger_unlock_node_job(self, node_name):
        parameters = {
            'NODE': node_name
        }
        return self.trigger_job('Unlock_Node', parameters)

    def stop_job(self, job_name, build_number):
        endpoint = f'/job/{job_name}/{build_number}/stop'
        return self._make_post_request(endpoint, None)


if __name__ == "__main__":
    jenkins_api = JenkinsAPI(os.environ['JENKINS_URL'], os.environ['JENKINS_USER'], os.environ['JENKINS_TOKEN'])
    print(jenkins_api.get_job_info('request_runner', 24282))
    # print(jenkins_api.trigger_unlock_node_job('4444'))
