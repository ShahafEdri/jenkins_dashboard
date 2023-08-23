import curses
import time
from collections import Counter

from config import config
from general_utils import validate_pickle_file_name
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs_file_name', '-f', type=validate_pickle_file_name, default='job_numbers.pickle', help='Path to jobs pickle file')
    config.update(parser.parse_args().__dict__)
from action_factory import Action_Factory
from dashboard import Dashboard
from general_utils import timeit
from input_handler import InputHandler
from job_manager import JobManager
from singleton import Singleton


def print_colorized_text(text:str, stdscr):
    # Initialize curses
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # SUCCESS color
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # PENDING color
    curses.init_pair(3, curses.COLOR_RED, -1)     # FAILURE color
    curses.init_pair(4, curses.COLOR_BLUE, -1)     # RUNNING color
    color_dict={
        "SUCCESS": curses.color_pair(1),   # SUCCESS color
        "PENDING": curses.color_pair(2),  # PENDING color
        "FAILURE": curses.color_pair(3),     # FAILURE color
        "RUNNING": curses.color_pair(4)     # RUNNING color
        }    

    # Split the text into lines
    lines = text.splitlines()

    # Print each line with appropriate color
    for line in lines:
        for word_mark, color_grade in color_dict.items():
            if word_mark in line:
                stdscr.addstr(line + '\n', color_grade)
                break
        else:
            stdscr.addstr(line + '\n')


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
            time_str = time.strftime('%a, %d %b %Y %H:%M', time.localtime())
            jobs_data = self.jm.get_all_jobs_data()
            t_shape, t_str = self.dsb.show(jobs_data=jobs_data, print_flag=False)
            t_height, t_width = t_shape
            results = Counter(job_info["result"] for job_info in jobs_data.values())
            string = f"""{" Job Manager ".center(t_width, "=")}
Current jobs:\t\t\t{time_str}
{t_str}
Summary: {dict(results)}

You can {'/'.join(Action_Factory.get_actions())} <job number>, unlock <lab number>, exit/quit
Command: {self.ih.get_input_text()}"""

            if self.prev_string != string:
                self.stdscr.clear()
                # self.stdscr.addstr(0, 0, string)
                print_colorized_text(string, self.stdscr)
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


if __name__ == '__main__':
    
    curses.wrapper(main)
