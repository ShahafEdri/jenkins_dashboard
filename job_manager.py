import pickle
import re

from chrome_controller import ChromeController
from config import config
from data_collector import DataCollector
from project_errors import ActionError
from singleton import Singleton
from web_utils import WebUtils
from cache_api import Cache

class JobManager(metaclass=Singleton):
    def __init__(self, job_numbers_file=config['jobs_file_name']):
        self.dc = DataCollector()
        self.chrome = ChromeController()
        self.web_utils = WebUtils()
        self.cache_file = 'cache_job_manager.json'
        self.cache = Cache(self.cache_file, 20)
        self._job_numbers_file = job_numbers_file
        self._job_numbers = self._load_job_numbers()


    def add_job_number(self, job_number):
        if self.web_utils.is_valid_url(job_number):
            job_number, _ = self.web_utils.extract_build_number_and_job_name(job_number)
            return self._add_job_number(job_number)
        elif re.match(r'^\d{3,}$', job_number):
            return self._add_job_number(job_number)
        else:
            err_msg = f"Job number {job_number} is not valid"
            return ActionError(err_msg)

    def _add_job_number(self, job_number):
        self._job_numbers.append(job_number)  # Add the job number to the set
        self._job_numbers = list(set(self._job_numbers))  # Remove duplicates
        self._job_numbers = sorted(self._job_numbers)  # Sort the job numbers
        self._save_job_numbers() # Save the job numbers to the file
        return True

    def get_job_by_index(self, index):
        if re.match(r'^\d{,2}$', index):
            index = int(index)
            if index < len(self._job_numbers):
                return self._job_numbers[index], None
            else:
                err_msg = f"Job number {index} is not in the jobs list"
                return index, ActionError(err_msg)
        else:
            err_msg = f"Job number {index} is not valid"
            return index, ActionError(err_msg)

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
        data_dict = self.dc.get_build_params(job_name=job_name, build_number=build_number)
        return data_dict

    from general_utils import timeit
    @timeit
    def get_all_jobs_data(self, job_name=config['job_name']):
        jobs_dict = {}
        for job_number in self._job_numbers:
            if self.cache.is_cache_expired(job_number):
                data = self.get_job_data(build_number=job_number, job_name=job_name)
                self.cache[job_number] = data
            else:
                data = self.cache[job_number]
            jobs_dict[job_number] = data
        return jobs_dict
    
    def start_rebuild_job(self, job_number):
        jobs_number_list = self.dc.jk.trigger_rebuild_job(build_number=job_number)
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
    job_manager.dc.jk.stop_job(48649)
    # job_manager.get_all_jobs_data()
