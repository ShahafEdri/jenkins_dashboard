import re

from config import config
from project_errors import ActionError

class WebUtils():
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
        return re.match(r'^(https?://.+?)/job/([^/]+)/(\d+)/?$', url)

    def extract_build_number_and_job_name(self, url):
        """
        Extract the build number and job name from the url
        :param url: job number or url
        :return: build number and job name

        for example: https://pl-jenkins01:8443/job/request_runner/50518/
        """
        if self.is_valid_url(url):
            match = re.match(r'^(https?://.+?)/job/([^/]+)/(\d+)/?$', url)
            if match:
                return match.group(3), match.group(2)
            else:
                raise ValueError(f'Invalid url: {url}')
        else:
            raise ActionError(f'Invalid url: {url}')