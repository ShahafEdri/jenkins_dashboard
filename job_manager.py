import pickle
from data_collector import DataCollector
from config import config

class JobManager:
    def __init__(self, job_numbers_file='job_numbers.pickle'):
        self.data_collector = DataCollector()
        self._job_numbers_file = job_numbers_file
        self._job_numbers = self._load_job_numbers()

    def add_job_number(self, job_number):
        self._job_numbers.add(job_number)  # Add the job number to the set
        self._job_numbers = sorted(self._job_numbers, reverse=True)  # Sort the job numbers
        self._save_job_numbers() # Save the job numbers to the file

    def remove_job_number(self, job_number):
        self._job_numbers.remove(job_number)
        self._save_job_numbers()

    def get_job_numbers(self):
        return self._job_numbers

    def prompt_for_job_number(self):
        job_number = input("Enter the job number: ")
        self.add_job_number(job_number)

    def remove_job_number_prompt(self):
        job_number = input("Enter the job number to remove: ")
        self.remove_job_number(job_number)

    def _save_job_numbers(self):
        with open(self._job_numbers_file, 'wb') as f:
            pickle.dump(self._job_numbers, f)

    def _load_job_numbers(self):
        try:
            with open(self._job_numbers_file, 'rb') as f:
                return set(pickle.load(f))
        except FileNotFoundError:
            return set()

    def get_job_data(self, build_number, job_name=config['job_name']):
        data_dict = self.data_collector.get_build_params(job_name=job_name, build_number=build_number)
        return data_dict

    def get_all_jobs_data(self, job_name=config['job_name']):
        jobs_dict = {}
        for job_number in self._job_numbers:
            data_dict = self.get_job_data(build_number=job_number, job_name=job_name)
            jobs_dict[job_number] = data_dict
        return jobs_dict


if __name__ == '__main__':
    job_manager = JobManager()
    job_manager.add_job_number(24282)
    job_manager.add_job_number(24283)
    job_manager.add_job_number(24284)
    print(job_manager.get_job_numbers())
    job_manager.remove_job_number(24284)
    print(job_manager.get_job_numbers())
    print(job_manager.get_jobs_data())