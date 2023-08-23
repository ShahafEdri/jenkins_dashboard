import curses
import re

from action_factory import Action_Factory
from memento_design_pattern import CommandLineInterface
from web_utils import WebUtils
from job_manager import JobManager
from general_utils import timeit


class InputHandler():
    def __init__(self):
        self._input_text = ""
        self.cli = CommandLineInterface()
        self.web_utils = WebUtils()
        self.run_flag = None
        self.jm = JobManager()
        self.valid_input = {
            "action": '/'.join(Action_Factory.get_actions()),
            "target": '/'.join(['job number', 'lab name', 'index']),
            "exit": '/'.join(['quit', 'exit']),
            "example": "action target1 target2 ...",
        }

    def clear_input(self):  # TODO: change to property
        self._input_text = ""

    def get_input_text(self):  # TODO: change to getter
        return self._input_text

    def set_input_text(self, text):  # TODO: change to setter
        self._input_text = text

    def handle_input(self, c):
        if c != -1:
            if c in [curses.KEY_BACKSPACE]:  # Backspace key
                self.set_input_text(self.get_input_text()[:-1])
            elif c in [curses.KEY_ENTER, 10]:  # Enter key
                actions, targets, errors = self.validate_and_extract_command(self.get_input_text())
                self.cli.record_command(self.get_input_text())
                if not errors:
                    errors = self.handle_command(actions, targets, errors)
                self.clear_input()
                return errors
            elif c in [curses.KEY_UP]:  # Up key
                self.set_input_text(self.cli.get_previous_command())
            elif c in [curses.KEY_DOWN]:  # Down key
                self.set_input_text(self.cli.get_next_command())
            elif 32 <= c <= 126:  # Regular key
                self.set_input_text(self.get_input_text() + chr(c))
            elif c in [23]:  # Ctrl + backspace, remove the last word
                self.set_input_text(self.get_input_text().rsplit(' ', 1)[0])
            elif c in [curses.KEY_EXIT, 27]:  # Esc key
                self.run_flag = False

    def is_valid_action(self, action):
        return bool(action in Action_Factory.get_actions())

    def is_valid_target(self, target):
        return bool(re.match(r'[Ll][Aa][Bb]\w+', target) or re.match(r'\d+', target) or self.web_utils.is_valid_url(target))

    def validate_and_extract_command(self, command):
        """
        Validate the input command
        :param command: command string
        :return: None
        """
        actions = []
        targets = []
        errors = []
        command_parts = command.split()
        if len(command_parts) == 0:
            pass
        elif len(command_parts) == 1:
            if command_parts[0] in ["quit", "exit"]:
                actions.append(command_parts[0])
            else:
                errors.append(f"Invalid command: {command_parts[0]}, valid commands are: {self.valid_input['exit']}")
        elif len(command_parts) >= 2:
            for part in command_parts:
                if self.is_valid_action(part):
                    actions.append(part)
                elif self.is_valid_target(part):
                    if re.match(r'\d{1,2}', part):
                        part, error = self.jm.get_job_by_index(part)
                        if error:
                            errors.append(f"Invalid target: {part}, returned with error {error}, valid targets are: <{self.valid_input['target']}>")
                            continue
                    targets.append(part)
                else:
                    errors.append(
                        f"Invalid command: {part}, valid actions are: <{self.valid_input['action']}>, valid targets are: <{self.valid_input['target']}>")
        return actions, targets, errors

    def handle_command(self, actions, targets, errors):
        """
        Handle the command
        :param command: command string
        :return: None
        """
        if errors:
            return errors
        if actions == []:
            pass
        elif actions[0] in ["quit", "exit"]:
            self.run_flag = False
        else:
            for action in actions:
                for target in targets:
                    result = Action_Factory(action)(target)
                    if bool(result) is False:
                        errors.append(f"action {action} failed on target {target} with error message: '{result}'")
        return errors
