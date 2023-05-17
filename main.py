import curses
import time
from dashboard import Dashboard
from job_manager import JobManager
import re


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
            'unlock': self.job_manager.data_collector.jenkins_api.trigger_unlock_node_job,
            'abort': self.job_manager.data_collector.jenkins_api.stop_job,
            'rebuild': self.job_manager.start_rebuild_job
        }

    def action_factory(self, action):
        return self.action_factory_dict[action]

    def print_error_msg(self, msg, timeout=5000):
        """
        Print error message on the last line
        :param msg: error message
        :return: None
        """
        # print on the last line
        self.stdscr.addstr(curses.LINES - 1, 0, msg)
        self.stdscr.refresh()
        curses.napms(timeout)  # Default wait for 5 seconds
        self.stdscr.addstr(curses.LINES - 1, 0, " " * (curses.COLS-1))

    def clear_input(self):  # TODO: change to property
        self._input_text = ""

    def handle_input(self, c):
        if c == curses.KEY_BACKSPACE:  # Backspace key
            self.input_text = self.input_text[:-1]
        elif c in [curses.KEY_ENTER, 10]:  # Enter key
            self.validate_input(self.input_text)
            self.handle_command(self.input_text)
            self.clear_input()
        elif 32 <= c <= 126:  # Regular key
            self.input_text += chr(c)

    def validate_input(self, command):
        """
        Validate the input command
        :param command: command string
        :return: None
        """
        command_parts = command.split()
        if command_parts == []:
            pass
        elif len(command_parts) == 1:
            if command_parts[0] in ["quit", "exit"]:
                pass
            else:
                self.print_error_msg(f"Invalid command: {command_parts[0]}, valid commands are: {'/'.join(['quit', 'exit'])}")
        elif len(command_parts) == 2:
            action, target = command_parts
            if action in self.action_factory_dict.keys():
                if re.match(r'[Ll][Aa][Bb]\w+', target) or re.match(r'\d+', target):
                    pass
                else:
                    self.print_error_msg(f"Invalid target: {target}, valid targets are: LABXXXX or jenkins build number ####.. ")
            else:
                self.print_error_msg(f"Invalid action: {action}, valid actions are: {'/'.join(self.action_factory_dict.keys())}")
        elif len(command_parts) > 2:
            self.print_error_msg("Too many arguments inserted, please insert only one action and one target")
        self.clear_input()


    def handle_command(self, command):
        """
        Handle the command
        :param command: command string
        :return: None
        """
        command_parts = command.split()
        if command_parts == []:
            pass
        elif command_parts[0] in ["quit", "exit"]:
            self.run_flag = False
        elif len(command_parts) == 2:
            action, target = command_parts
            result = self.action_factory(action)(target)
            if result == False:
                self.print_error_msg(f"action {action} failed on target {target}")

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
            jobs_data = self.job_manager.get_all_jobs_data()
            t_height, t_width = self.dashboard.show(jobs_data=jobs_data)
            spacing_rows = 2

            # Add a header
            header_rows = 2
            header = " Job Manager ".center(t_width, "=")
            self.stdscr.addstr(0, 0, header)

            # Add the input prompt
            footer_rows = 2
            self.stdscr.addstr(t_height + sum([header_rows, footer_rows, spacing_rows]) - 2, 0,
                               f"you can {'/'.join(self.action_factory_dict.keys())} <job number/lab nubmer> or quit to exit")
            self.stdscr.addstr(t_height + sum([header_rows, footer_rows, spacing_rows]) - 1, 0, "Command: " + self.input_text)
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
