import curses
import time
from dashboard import Dashboard
from job_manager import JobManager
from datetime import datetime, timedelta

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.job_manager = JobManager()
        self.dashboard = Dashboard(self.stdscr)
        self.run_flag = True
        self.waiting_for_input = False
        self.job_number = ""
        self.action = None
        self.last_update = datetime.now()
        self.jobs_data = self.job_manager.get_jobs_data()

        
    def handle_input(self, c):
        if self.waiting_for_input:
            if c == curses.KEY_EXIT:  # ESC key
                self.waiting_for_input = False
                self.job_number = ""
                self.action = None
            elif c == curses.KEY_BACKSPACE:  # Backspace key
                self.job_number = self.job_number[:-1]
            elif c == curses.KEY_ENTER:  # Enter key
                self.waiting_for_input = False
                if self.job_number:
                    self.job_manager.action_factory(self.action)(self.job_number)
                else:
                    self.stdscr.addstr("Job number cannot be empty")
                self.job_number = ""
                self.action = None
            elif c in range(48, 58):  # Numeric keys
                self.job_number += chr(c)
        else:
            if c == ord('q'):
                self.run_flag = False
            elif c == ord('a'):
                self.waiting_for_input = True
                self.action = "add"
            elif c == ord('r'):
                self.waiting_for_input = True
                self.action = "remove"


    def render(self):
        # Clear the screen
        self.stdscr.clear()

        # Add a header
        self.stdscr.addstr(0, 0, " Job Manager ".center(curses.COLS, "="))

        # Add the current jobs table
        self.stdscr.addstr(1, 0, "Current jobs:\n")

        # once every 5 seconds, update the jobs data
        if datetime.now() - self.last_update > timedelta(seconds=30):
            self.last_update = datetime.now()
            self.jobs_data = self.job_manager.get_jobs_data()
        self.dashboard.show(jobs_data=self.jobs_data)

        # Add the instructions to add/remove jobs
        self.stdscr.addstr("\n")
        self.stdscr.addstr("Press 'q' to exit\n")
        self.stdscr.addstr("Press 'a' to add a job\n")
        self.stdscr.addstr("Press 'r' to remove a job\n")

        # Add the input prompt if necessary
        if self.waiting_for_input:
            self.stdscr.addstr("\n")
            self.stdscr.addstr(f"Enter job number to {self.action}: " + self.job_number, curses.A_REVERSE)

        # Add a footer
        self.stdscr.addstr(curses.LINES - 1, 0, "Press ESC to cancel input")
        self.stdscr.refresh()

    def run(self):
        curses.curs_set(0)  # Hide the cursor
        self.stdscr.nodelay(True)  # Set the getch() method to non-blocking
        curses.echo()  # Turn on input echo
        while self.run_flag:
            c = self.stdscr.getch()  # Non-blocking input
            self.handle_input(c)
            self.render()
            self.stdscr.refresh()
            curses.napms(20)  # Wait for 100 ms

def main(stdscr):
    app = App(stdscr)
    app.run()

curses.wrapper(main)
