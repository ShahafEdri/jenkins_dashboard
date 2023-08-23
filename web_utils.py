import re
import requests

from config import config
from project_errors import ActionError
from cache_api import Cache

class WebUtils():
    def __init__(self):
        self.cache_file = 'cache_data.json'
        self.cache = Cache(self.cache_file, config["cache_timeout"])

    def _make_post_request(self, url, data):
        auth = (config['jenkins_user'], config['jenkins_token']) if "jenkins" in url else None
        response = requests.post(url, auth=auth, data=data, verify=False)
        response.raise_for_status()
        return response.status_code in [200, 201]  # 201 is the status code for successful POST request

    def _make_get_request(self, url, force=False):
        if self.cache.is_cache_expired(url) or force:
            data = self._get_json_response_from_url(url)
            self.cache[url] = data
        else:
            data = self.cache[url]
        return data

    def _get_json_response_from_url(self, url):
        auth = (config['jenkins_user'], config['jenkins_token']) if "jenkins" in url else None
        response = requests.get(url, auth=auth, verify=False)
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code in [404, 500]:
                return None
            else:
                raise e

    def get_node_base_path(self):
        return f"{config['test_manager_url']}/nodes/"
    
    def get_job_base_path(self):
        return f"{config['jenkins_url']}/job/{config['job_name']}/"
    
    def is_valid_url(self, url):
        """
        Check if the job number is a valid url
        :param url: job number or url
        :return: True if the job number is a valid url, False otherwise

        for example: https://pl-jenkins01:8443/job/request_runner/50518/
        """
        return re.match(r'^(https?://.+?)/job/([^/]+)/(\d+)', url)

    def extract_build_number_and_job_name(self, url):
        """
        Extract the build number and job name from the url
        :param url: job number or url
        :return: build number and job name

        for example: https://pl-jenkins01:8443/job/request_runner/50518/
        """
        if self.is_valid_url(url):
            match = re.match(r'^(https?://.+?)/job/([^/]+)/(\d+)', url)
            if match:
                return match.group(3), match.group(2)
            else:
                raise ValueError(f'Invalid url: {url}')
        else:
            raise ActionError(f'Invalid url: {url}')