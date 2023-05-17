import re

from config import config


class WebUtils():
    def get_node_base_path(self):
        return f"{config['test_manager_url']}/nodes/"
    
    def get_job_base_path(self):
        return f"{config['jenkins_url']}/job/{config['job_name']}/"