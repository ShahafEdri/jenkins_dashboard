from singleton import Singleton
import curses
import time

from action_factory import Action_Factory
from dashboard import Dashboard
from input_handler import InputHandler
from job_manager import JobManager
from general_utils import timeit
from collections import Counter

class App(metaclass=Singleton):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.jm = JobManager()
        self.dsb = Dashboard(self.stdscr)
        self.ih = InputHandler()
        self.prev_string = ""
        self.ih.run_flag = True

    def print_error_msg(self, msg, timeout=2):
        """
        Print error message on the last line
        :param msg: error message
        :return: None
        """
        # print on the last line
        self.stdscr.addstr(curses.LINES - 1, 0, msg)
        self.stdscr.refresh()
        curses.napms(timeout*1000)  # Default wait for 5 seconds
        self.stdscr.addstr(curses.LINES - 1, 0, " " * (curses.COLS-1))

    @timeit
    def render(self):
        """
        Render the UI
        :return: None
        """
        # add static previous string to check if we need to render
        # Render UI
        try:
            # current time
            # Add the current jobs table
            time_str = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
            jobs_data = self.jm.get_all_jobs_data()
            t_shape, t_str = self.dsb.show(jobs_data=jobs_data, print_flag=False)
            t_height, t_width = t_shape
            results = Counter(job_info["result"] for job_info in jobs_data.values())
            string = f"""{" Job Manager ".center(t_width, "=")}
Current jobs:\t\t\t{time_str}
{t_str}
Summary: {dict(results)}

You can {'/'.join(Action_Factory.get_actions())} <job number>, unlock <lab number>, exit/quit
Command: {self.ih.get_input_text()}
"""

            if self.prev_string != string:
                self.stdscr.clear()
                self.stdscr.addstr(0, 0, string)
                self.prev_string = string

        except curses.error:
            # Terminal has been resized
            curses.resize_term(curses.LINES, curses.COLS)
            self.stdscr.clear()
        self.stdscr.refresh()

    def run(self):
        """
        Run the app
        Entry point of the app
        :return: None
        """
        curses.curs_set(0)  # Hide the cursor
        self.stdscr.nodelay(True)  # Set the getch() method to non-blocking
        curses.echo()  # Turn on input echo
        while self.ih.run_flag:
            c = self.stdscr.getch()  # Non-blocking input
            errors = self.ih.handle_input(c)
            if bool(errors):
                for error in errors:
                    self.print_error_msg(error, timeout=1)
            self.render()
            self.stdscr.refresh()
            curses.napms(1)  # Wait for 100 ms


def main(stdscr):
    app = App(stdscr)
    app.run()


curses.wrapper(main)
