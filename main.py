import curses
import re
import time

from chrome_controller import ChromeController
from dashboard import Dashboard
from job_manager import JobManager


class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.job_manager = JobManager()
        self.dashboard = Dashboard(self.stdscr)
        self.chrome = ChromeController()

        self.run_flag = True
        self._input_text = ""

        self.action_factory_dict = {
            'add': self.job_manager.add_job_number,
            'remove': self.job_manager.remove_job_number,
            'unlock': self.job_manager.data_collector.jenkins_api.trigger_unlock_node_job,
            'abort': self.job_manager.data_collector.jenkins_api.stop_job,
            'rebuild': self.job_manager.start_rebuild_job,
            'open': self.job_manager.open_chrome,
        }

    def action_factory(self, action):
        return self.action_factory_dict[action]

    def print_error_msg(self, msg, timeout=5):
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
        self.clear_input()

    def clear_input(self):  # TODO: change to property
        self._input_text = ""

    def get_input_text(self):  # TODO: change to getter
        return self._input_text

    def set_input_text(self, text):  # TODO: change to setter
        self._input_text = text

    def handle_input(self, c):
        if c == curses.KEY_BACKSPACE:  # Backspace key
            self.set_input_text(self.get_input_text()[:-1])
        elif c in [curses.KEY_ENTER, 10]:  # Enter key
            actions, targets = self.validate_and_extract_command(self.get_input_text())
            self.handle_command(actions, targets)
            self.clear_input()
        elif 32 <= c <= 126:  # Regular key
            self.set_input_text(self.get_input_text() + chr(c))

    def is_valid_action(self, action):
        return bool(action in self.action_factory_dict.keys())

    def is_valid_target(self, target):
        return bool(re.match(r'[Ll][Aa][Bb]\w+', target) or re.match(r'\d+', target))

    def validate_and_extract_command(self, command):
        """
        Validate the input command
        :param command: command string
        :return: None
        """
        actions = []
        targets = []
        command_parts = command.split()
        if len(command_parts) == 0:
            pass
        elif len(command_parts) == 1:
            if command_parts[0] in ["quit", "exit"]:
                actions.append(command_parts[0])
            else:
                self.print_error_msg(f"Invalid command: {command_parts[0]}, valid commands are: {'/'.join(['quit', 'exit'])}")
        elif len(command_parts) >= 2:
            for part in command_parts:
                if self.is_valid_action(part):
                    actions.append(part)
                elif self.is_valid_target(part):
                    targets.append(part)
                else:
                    self.print_error_msg(
                        f"Invalid command: {part}, valid actions are: <{'/'.join(self.action_factory_dict.keys())}>, valid targets are: <job number/lab name>")
        return actions, targets

    def handle_command(self, actions, targets):
        """
        Handle the command
        :param command: command string
        :return: None
        """
        if actions == []:
            pass
        elif actions[0] in ["quit", "exit"]:
            self.run_flag = False
        else:
            for action in actions:
                for target in targets:
                    result = self.action_factory(action)(target)
                    if bool(result) is False:
                        self.print_error_msg(f"action {action} failed on target {target} with error message: {result}", timeout=1)

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
            self.stdscr.addstr(t_height + sum([header_rows, footer_rows, spacing_rows]) - 1, 0, "Command: " + self.get_input_text())
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
