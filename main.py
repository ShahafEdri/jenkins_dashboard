import curses
import time
from dashboard import Dashboard
from job_manager import JobManager



class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.job_manager = JobManager()
        self.dashboard = Dashboard(self.stdscr)
        self.run_flag = True
        self.input_text = ""


        self.action_factory_dict = {
            'add': self.job_manager.add_job_number,
            'remove': self.job_manager.remove_job_number,
            'unlock': self.job_manager.data_collector.jenkins_api.trigger_unlock_node_job_by_build_number,
            'abort': self.job_manager.data_collector.jenkins_api.stop_job
        }
        
    def action_factory(self, action):
        return self.action_factory_dict[action]

    def handle_input(self, c):
        if c == curses.KEY_BACKSPACE :  # Backspace key
            self.input_text = self.input_text[:-1]
        elif c in [curses.KEY_ENTER, 10]:  # Enter key
            self.handle_command(self.input_text)
            self.input_text = ""
        elif c != -1:  # Regular key
            self.input_text += chr(c)

    def handle_command(self, command):
        command_parts = command.split()
        if command_parts[0] == "quit":
            self.run_flag = False
        elif len(command_parts) == 2:
            job_number = command_parts[1]
            action = command_parts[0]
            self.action_factory(action)(job_number)

    def render(self):
        # Clear the screen
        self.stdscr.clear()

        # Add a header
        self.stdscr.addstr(0, 0, " Job Manager ".center(curses.COLS, "="))

        # Add the current jobs table
        self.stdscr.addstr(1, 0, "Current jobs:\n")
        jobs_data = self.job_manager.get_all_jobs_data()
        self.dashboard.show(jobs_data=jobs_data)

        # Add the input prompt
        self.stdscr.addstr(curses.LINES - 2, 0, f"you can {'/'.join(self.action_factory_dict.keys())} <job number> action")
        self.stdscr.addstr(curses.LINES - 1, 0, "Command: " + self.input_text)
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
