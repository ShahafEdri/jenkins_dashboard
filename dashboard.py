import curses
from tabulate import tabulate
from job_manager import JobManager
from config import config

class Dashboard:
    def __init__(self, stdscr=None):
        self.stdscr = stdscr

    def _jobs_dict_to_list_of_lists(self, jobs_data):
        data = []
        if jobs_data:
            for job_number, job_params in jobs_data.items():
                job_row_data = []
                for param in config['job_parameters_display']:
                    job_row_data.append(job_params.get(param))
                data.append(job_row_data)
        return data
        
    def get_table_string(self, jobs_data):
        data = self._jobs_dict_to_list_of_lists(jobs_data)
        headers = config['job_parameters_display_headers']
        return tabulate(data, headers=headers, tablefmt='orgtbl', colalign=("center",)*len(headers))

    def show(self, jobs_data):
        table_str = self.get_table_string(jobs_data)
        if self.stdscr:
            self.stdscr.addstr(table_str)
        else:
            print(table_str)

if __name__ == '__main__':
    job_manager = JobManager()
    job_manager.add_job_number(24282)
    job_manager.add_job_number(24287)
    jobs_data = job_manager.get_jobs_data()
    dashboard = Dashboard()
    dashboard.show(jobs_data)