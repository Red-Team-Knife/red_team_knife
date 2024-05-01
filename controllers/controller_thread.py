import subprocess
import threading


class Controller:
    def __init__(self):
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.thread = None
        self.tool_name = None

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
            print(self.tool_name + " scan completed.")

        # Wait for the process to terminate
        self.process.wait()
        self.calling_controller.is_scan_in_progress = False

    def stop(self):
        if self.process:
            self.process.terminate()
        self.calling_controller.last_scan_result = None
        print(self.tool_name + " scan stop requested.")
        self.calling_controller.is_scan_in_progress = False
        self._stop_event.set()

    def print_stop_completed_message(self):
        print(self.tool_name + " scan stop completed.")