from singleton import Singleton
import curses
import time

from action_factory import Action_Factory
from dashboard import Dashboard
from input_handler import InputHandler
from job_manager import JobManager


class App(metaclass=Singleton):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.jm = JobManager()
        self.dsb = Dashboard(self.stdscr)
        self.ih = InputHandler()

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

    def render(self):
        """
        Render the UI
        :return: None
        """
        # Render UI
        try:
            # Clear the screen
            self.stdscr.clear()

            # current time
            time_str = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
            # Add the current jobs table
            self.stdscr.addstr(1, 0, f"Current jobs:\t\t\t{time_str}\n")
            jobs_data = self.jm.get_all_jobs_data()
            t_height, t_width = self.dsb.show(jobs_data=jobs_data)
            spacing_rows = 2

            # Add a header
            header_rows = 2
            header = " Job Manager ".center(t_width, "=")
            self.stdscr.addstr(0, 0, header)

            # Add the input prompt
            footer_rows = 2
            self.stdscr.addstr(t_height + sum([header_rows, footer_rows, spacing_rows]) - 2, 0,
                               f"you can {'/'.join(Action_Factory.get_actions())} <job number/lab nubmer> or quit to exit")
            self.stdscr.addstr(t_height + sum([header_rows, footer_rows, spacing_rows]) - 1, 0, "Command: " + self.ih.get_input_text())
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
            curses.napms(10)  # Wait for 100 ms


def main(stdscr):
    app = App(stdscr)
    app.run()


curses.wrapper(main)
