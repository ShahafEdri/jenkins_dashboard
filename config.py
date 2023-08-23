import os
import json

# get config
with open('config.json') as f:
    config = json.load(f)

config['jenkins_url'] = os.environ['JENKINS_URL']
config['jenkins_user'] = os.environ['JENKINS_USER']
config['jenkins_token'] = os.environ['JENKINS_TOKEN']
config['test_manager_url'] = os.environ['TEST_MANAGER_URL']
