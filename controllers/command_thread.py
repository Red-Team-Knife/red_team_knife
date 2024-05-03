from loguru import logger as l
import subprocess
import threading

from controllers.base_controller import Controller


class CommandThread(threading.Thread):
    """
    Represents a thread for executing and stopping a command.

    Attributes:
        command (list): The command to be executed.
        _stop_event (threading.Event): Flag indicating a stop request.
        calling_controller (Controller): Reference to the controller invoking the thread.
        tool_name (str): Display name of the tool associated with the command.
        process (subprocess.Popen or None): Reference to the process running the command.
    """

    def __init__(self, command: list, calling_controller: Controller):
        """
        Initializes a CommandThread instance.

        Args:
            command (list): The command to be executed.
            calling_controller (Controller): The controller invoking the thread.
        """
        super().__init__()
        self.command = command
        self._stop_event = threading.Event()
        self.calling_controller = calling_controller
        self.tool_name = calling_controller.tool_name
        self.process = None

    def run(self):
        """
        Runs the command in a subprocess.

        Sets `calling_controller.is_scan_in_progress` to `True` to indicate the running status.
        Saves a reference to the subprocess for future handling and
        prints all the process output as soon as it is available.
        After the scan is completed, sets `calling_controller.is_scan_in_progress` to `False`.

        """
        l.info(f"Running {self.tool_name} in a new thread.")
        self.calling_controller.is_scan_in_progress = True

        self.process = subprocess.Popen(
            self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        # Print output while the command is running
        while self.process.poll() is None and not self._stop_event.is_set():
            output = self.process.stdout.readline()
            if output:
                print(output.strip())

        if not self._stop_event.is_set():
            l.success(f"{self.tool_name} finished running successfully.")

        # Wait for the process to terminate
        self.process.wait()
        self.calling_controller.is_scan_in_progress = False

    def stop(self):
        """
        Stops the execution of the command thread.

        If the process is running, it terminates the process.
        Resets the `last_scan_result` attribute of the calling controller to `None`.
        Sets `is_scan_in_progress` attribute of the calling controller to `False`.
        Sets the stop event to indicate that the thread should stop execution.
        """
        l.info(f"Handling stop request for {self.tool_name}.")
        if self.process:
            self.process.terminate()
        self.calling_controller.last_scan_result = None
        self.calling_controller.is_scan_in_progress = False
        self._stop_event.set()
        self.print_stop_completed_message()

    def print_stop_completed_message(self):
        l.success(f"Stop completed for {self.tool_name}.")
