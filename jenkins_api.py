import requests
import json
import warnings
from datetime import datetime, timedelta
import os
import re


class JenkinsAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.cache_file = 'cache.json'
        self.cache_expiry = timedelta(minutes=1)
        warnings.filterwarnings('ignore')

    def _make_request(self, endpoint):
        url = self.base_url + endpoint
        response = requests.get(url, auth=(self.username, self.password), verify=False)
        response.raise_for_status()
        return response.json()

    def get_job_info(self, job_name, build_number):
        endpoint = f'/job/{job_name}/{build_number}/api/json'
        return self._make_request(endpoint)

if __name__ == "__main__":
    jenkins_api = JenkinsAPI(os.environ['JENKINS_URL'], os.environ['JENKINS_USER'], os.environ['JENKINS_TOKEN'])
    print(jenkins_api.get_build_params('request_runner', 24282))
