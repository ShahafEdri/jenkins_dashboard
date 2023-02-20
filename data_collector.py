import re
from datetime import datetime
from jenkins_api import JenkinsAPI
from config import config
from test_manager_api import TestManagerAPI

class DataCollector:
    def __init__(self):
        self.jenkins_api = JenkinsAPI(config['jenkins_url'], config['jenkins_user'], config['jenkins_token'])
        self.test_manager_api = TestManagerAPI(config['test_manager_url'], config['test_manager_element_selector'])
        
    def fix_params(self, info_dict):
        info_dict['timestamp_origin'] = info_dict['timestamp']
        info_dict['duration_origin'] = info_dict['duration']
        info_dict['timestamp'] = datetime.fromtimestamp(info_dict['timestamp']/1000).strftime('%Y-%m-%d')
        info_dict['duration'] = datetime.fromtimestamp(info_dict['duration']/1000).strftime('%H:%M:%S')
        # 'displayName': 'RID: #346267, Lab4233, J#24282 (Controller none), swrelease@pliops.com'
        # take only the Lab name
        info_dict['server'] = re.search(r'Lab\d+', info_dict['displayName']).group(0)
        if bool(info_dict['inProgress']):
            info_dict['result'] = 'Running...'

    def is_server_hold_on_failure(self, server_name):
        return self.test_manager_api.is_server_hold_on_failure(server_name)

    def get_build_params(self, job_name, build_number):
        info = self.jenkins_api.get_job_info(job_name, build_number)
        params_list = ["result", "inProgress", "duration", "timestamp", "displayName"]
        info_dict = {param: info.get(param) for param in params_list}
        self.fix_params(info_dict)
        return info_dict