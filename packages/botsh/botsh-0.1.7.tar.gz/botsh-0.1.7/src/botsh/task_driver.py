from botsh.docker_exec import DockerContainer
from botsh.history import CommandExecution
from botsh.llm import LLM
from botsh.logging import log
from botsh.prompt import parse_response


class TaskDriver:
    history: list[CommandExecution]
    task: str
    container: DockerContainer
    llm: LLM

    def __init__(self, task: str, container: DockerContainer, llm: LLM):
        self.task = task
        self.llm = llm
        self.container = container
        self.history = list()

        # Run a few commands. These serve both to orient the agent, and to
        # provide some examples of what we want.
        self.run_command_and_add_to_history(
            "I would like to know five files in the current directory.",
            "ls -al | head -n 5",
            True,
        )

        self.run_command_and_add_to_history(
            "I would like to know which directory I am in.", "pwd", True
        )

    def run_command_and_add_to_history(
        self, explanation: str, command: str, quiet: bool = False
    ):
        exit_code, output = self.container.run_command(command, quiet)
        self.history.append(CommandExecution(explanation, command, output, exit_code))
        return output

    def step(self):
        response = self.llm.completion(self.task, self.history)

        result = parse_response(response)

        if result.command == "":
            log.info(
                "Agent indicated that the task is complete.",
                explanation=result.explanation,
            )
            return True
        else:
            log.info(
                "Agent requested a command.",
                command=result.command,
                explanation=result.explanation,
            )

        exit_code, output = self.container.run_command(result.command)
        lines = output.splitlines()
        if len(lines) > 10:
            truncated = len(lines) - 10
            output = (
                f"[ {truncated} lines truncated ]"
                + "\n".join(lines[-10:])
                + "\n[...]\n"
            )

        self.history.append(
            CommandExecution(result.explanation, result.command, output, exit_code)
        )
