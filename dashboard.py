import curses

import pandas as pd
from tabulate import tabulate

from config import config
from job_manager import JobManager


class Dashboard:
    def __init__(self, stdscr=None):
        self.stdscr = stdscr

    def _jobs_dict_to_list_of_lists(self, jobs_data):
        data = []
        if jobs_data:
            for job_number, job_params in jobs_data.items():
                job_row_data = []
                mlist = [k if "inner_name" not in v else v["inner_name"] for k,v  in config['job_parameters'].items()]
                for param in mlist:
                    job_row_data.append(job_params.get(param))
                data.append(job_row_data)
            return data
        else:
            return [["-"]*len(config["job_parameters"].keys())]
        
    def get_table_string(self, jobs_data):
        data = self._jobs_dict_to_list_of_lists(jobs_data)
        headers = config["job_parameters"].keys()
        # index is the job number
        df = pd.DataFrame(data, columns=headers, index=jobs_data.keys())
        # drop the index column
        df = df.reset_index(drop=True)
        # sort by marker
        if config.get("sort_by_header", None):
            df = df.sort_values(by=config["sort_by_header"], ascending=True)
        # outline table with | and - and center align
        return tabulate(df, headers=headers, tablefmt='orgtbl', colalign=("center",)*len(headers))
        # return tabulate(data, headers=headers, tablefmt='orgtbl', colalign=("center",)*len(headers))

    def show(self, jobs_data):
        table_str = self.get_table_string(jobs_data)
        if self.stdscr:
            self.stdscr.addstr(table_str)
        else:
            print(table_str)
        # return table_height and table_width
        return len(table_str.splitlines()), len(table_str.splitlines()[0])

if __name__ == '__main__':
    job_manager = JobManager()
    job_manager.add_job_number(24282)
    job_manager.add_job_number(24287)
    jobs_data = job_manager.get_jobs_data()
    dashboard = Dashboard()
    dashboard.show(jobs_data)
