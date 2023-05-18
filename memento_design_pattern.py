# Originator: CLI


class CommandLineInterface:
    def __init__(self):
        self.command_history = []
        self.current_index = -1

    def record_command(self, command):
        if (command == "") or (self.get_command() == command):
            return
        self.command_history.append(command)
        self.set_index_to_last()

    def get_previous_command(self):
        if self.current_index > 0:
            self.current_index -= 1
        return self.get_command()

    def get_next_command(self):
        if self.current_index <= len(self.command_history) - 1:
            self.current_index += 1
        return self.get_command()

    def get_command(self, index=None):
        if index is None:
            index = self.current_index
        if 0 <= index <= (len(self.command_history)-1):
            return self.command_history[index]
        return ""

    def set_index_to_last(self):
        self.current_index = len(self.command_history)

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
