import curses
from tabulate import tabulate
from job_manager import JobManager
from config import config

class Dashboard:

    def show(self, jobs_data, stdscr=None):
        data = []
        if jobs_data:
            for job_number, job_params in jobs_data.items():
                job_row_data = []
                for param in config['job_parameters_display']:
                    job_row_data.append(job_params.get(param))
                data.append(job_row_data)

        # Print the table
        headers = config['job_parameters_display_headers']
        if stdscr:
            stdscr.addstr(tabulate(data, headers=headers, tablefmt='orgtbl', colalign=("center",)*len(headers))+"\n")
        else:
            print(tabulate(data, headers=headers, tablefmt='orgtbl', colalign=("center",)*len(headers)))

if __name__ == '__main__':
    job_manager = JobManager()
    job_manager.add_job_number(24282)
    job_manager.add_job_number(24287)
    jobs_data = job_manager.get_jobs_data()
    dashboard = Dashboard()
    dashboard.show(jobs_data)