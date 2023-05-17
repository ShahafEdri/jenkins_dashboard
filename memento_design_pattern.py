# Originator: CLI


class CommandLineInterface:
    def __init__(self):
        self.command_history = []
        self.current_index = -1

    def record_command(self, command):
        if (command == "") or (self.get_command() == command):
            self.set_index_to_last()
            return
        self.command_history.append(command)
        self.current_index = len(self.command_history) - 1

    def get_previous_command(self):
        command = self.get_command()
        if self.current_index >= 0:
            self.current_index -= 1
        return command

    def get_next_command(self):
        if self.current_index < len(self.command_history) - 1:
            self.current_index += 1
            return self.get_command()
        return ""

    def get_command(self):
        return self.command_history[self.current_index] if self.current_index >= 0 else ""

    def set_index_to_last(self):
        self.current_index = len(self.command_history) - 1

# Caretaker: CLIController


class CLIController:
    def __init__(self, cli: CommandLineInterface):
        self.cli = cli

    def run(self):
        while True:
            user_input = input("Enter a command: ")
            if user_input.lower() == "q":
                break
            elif user_input.lower() == "p":
                self.cli.get_previous_command()
            elif user_input.lower() == "n":
                self.cli.get_next_command()
            else:
                self.cli.record_command(user_input)


if __name__ == "__main__":
    cli = CommandLineInterface()
    cli_controller = CLIController(cli)
    cli_controller.run()
