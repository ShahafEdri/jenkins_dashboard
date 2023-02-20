import curses
from tabulate import tabulate
from job_manager import JobManager
from config import config

class Dashboard:

    def show(self, stdscr, jobs_data):
        data = []
        if jobs_data:
            for job_number, job_params in jobs_data.items():
                job_row_data = [job_number]
                for param in config['job_parameters']:
                    job_row_data.append(job_params.get(param))
                data.append(job_row_data)

        # Print the table
        headers = ['job_number', *config["job_parameters"]]
        stdscr.addstr(tabulate(data, headers=headers, tablefmt='orgtbl', colalign=("center",)*len(headers))+"\n")

if __name__ == '__main__':
    job_manager = JobManager()
    job_manager.add_job_number(24282)
    job_manager.add_job_number(24283)
    jobs_data = job_manager.get_jobs_data()
    dashboard = Dashboard()
    dashboard.show(jobs_data)