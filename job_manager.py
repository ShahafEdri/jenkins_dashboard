import pickle
import re

from chrome_controller import ChromeController
from config import config
from data_collector import DataCollector
from web_utils import WebUtils
from project_errors import ActionError

class JobManager:
    def __init__(self, job_numbers_file='job_numbers.pickle'):
        self.data_collector = DataCollector()
        self.chrome = ChromeController()
        self.web_utils = WebUtils()
        self._job_numbers_file = job_numbers_file
        self._job_numbers = self._load_job_numbers()

    def add_job_number(self, job_number):
        self._job_numbers.append(job_number)  # Add the job number to the set
        self._job_numbers = sorted(self._job_numbers)  # Sort the job numbers
        self._save_job_numbers() # Save the job numbers to the file

    def remove_job_number(self, job_number):
        if job_number in self._job_numbers:
            self._job_numbers.remove(job_number)
            self._save_job_numbers()
            return True
        else:
            err_msg = f"Job number {job_number} is not in the jobs list"
            return ActionError(err_msg)

    def get_job_numbers(self):
        return self._job_numbers

    def _save_job_numbers(self):
        with open(self._job_numbers_file, 'wb') as f:
            pickle.dump(self._job_numbers, f)

    def _load_job_numbers(self):
        try:
            with open(self._job_numbers_file, 'rb') as f:
                return list(pickle.load(f))
        except FileNotFoundError:
            return list()

    def get_job_data(self, build_number, job_name=config['job_name']):
        data_dict = self.data_collector.get_build_params(job_name=job_name, build_number=build_number)
        return data_dict

    def get_all_jobs_data(self, job_name=config['job_name']):
        jobs_dict = {}
        for job_number in self._job_numbers:
            data_dict = self.get_job_data(build_number=job_number, job_name=job_name)
            jobs_dict[job_number] = data_dict
        return jobs_dict
    
    def start_rebuild_job(self, job_number):
        jobs_number_list = self.data_collector.jk_api.trigger_rebuild_job(build_number=job_number)
        if jobs_number_list:
            for new_job_number in jobs_number_list:
                self.add_job_number(str(new_job_number))
            return True
        else:
            return False
    
    def open_chrome(self, job_number_or_url):
        """
        Open the job in chrome
        
        Args:
        - job_number_or_url (str): The job number or url to open
        
        Returns:
        - None
        """
        if re.match(r'^https?://', job_number_or_url):
            url = job_number_or_url
        elif re.match(r'^\d+$', job_number_or_url):
            url = f'{self.web_utils.get_job_base_path()}/{job_number_or_url}/'
        elif re.match(r'^Lab\d{4}$', job_number_or_url):
            url = f'{self.web_utils.get_node_base_path()}/{job_number_or_url}'
        else:
            raise ValueError(f'Invalid job number or url: {job_number_or_url}')
        self.chrome.open(url)
        return True

if __name__ == '__main__':
    job_manager = JobManager()
    # job_manager.add_job_number(24282)
    # job_manager.add_job_number(24283)
    # job_manager.add_job_number(24284)
    # print(job_manager.get_job_numbers())
    # job_manager.remove_job_number(24284)
    # print(job_manager.get_job_numbers())
    # print(job_manager.get_jobs_data())
    # job_manager.start_rebuild_job(48592)
    job_manager.data_collector.jk_api.stop_job(48649)
    # job_manager.get_all_jobs_data()
