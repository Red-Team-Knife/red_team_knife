import os
import subprocess
import threading
from loguru import logger as l

from utils.commands import build_command_string

class Controller:
    def __init__(self):
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.thread = None
        self.tool_name = None
        self.running_message = 'Running {} with command: '

    # Override, start command in a new thread and save its reference in self.thread.
    # Use CommandThread or inherit from it.
    def run(self, target, options):
        pass

    def stop_scan(self):
        if self.thread is not None:
            self.thread.stop()

    def restore_last_scan(self):
        return self.get_formatted_results()

    def get_formatted_results(self):
        if not self.is_scan_in_progress:
            return self.__format_result__()

    def __format_result__(self):
        pass

    def __log_running_message__(self, command:list):
        command_string = build_command_string(command)

        l.info(self.running_message.format(self.tool_name))
        l.info(command_string[:-1])

    def __remove_temp_file__(self, temp_file_name):
        try:
            l.info(f'Removing temp {self.tool_name} file...')
            os.remove(temp_file_name)
            l.success('File removed successfully.')
        except:
            l.error(f"Couldn't remove temp {self.tool_name} file.")



class CommandThread(threading.Thread):
    def __init__(self, command: list, calling_controller: Controller):
        super().__init__()
        self.command = command
        self._stop_event = threading.Event()
        self.calling_controller = calling_controller
        self.tool_name = calling_controller.tool_name
        self.process = None

    # Override if needed. Call super().run() and then do cleanup if only cleanup operations are needed.
    def run(self):
        l.info(f'Starting {self.tool_name} scan in a new thread.')
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
            l.success(f'{self.tool_name} scan completed.')

        # Wait for the process to terminate
        self.process.wait()
        self.calling_controller.is_scan_in_progress = False

    def stop(self):
        l.info(f'Handling stop request for {self.tool_name}.')
        if self.process:
            self.process.terminate()
        self.calling_controller.last_scan_result = None
        self.calling_controller.is_scan_in_progress = False
        self._stop_event.set()

    def print_stop_completed_message(self):
        l.success(f'Stop completed for {self.tool_name}.')