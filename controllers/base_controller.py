import os
import threading
from typing import Tuple
from loguru import logger as l
from models.current_scan import CurrentScan
from models.scan import Scan
from utils.utils import build_command_string, create_pdf_from_html

REPORTS_DIR = "reports/"


class Controller:
    """
    Base class representing a controller that encapsulates a tool.

    Attributes:
        last_scan_result (any): Holds the last scan result data.
        is_scan_in_progress (bool): Indicates whether the scan is running or not.
        thread (threading.Thread or None): Holds a reference to the command thread.
        tool_name (str): Display name for the tool.
        temp_file_name (str): Filename for temporary results storage.
        running_message (str): String printed when starting the command.
    """

    def __init__(self, tool_display_name: str, temp_file_name: str, tool_name):
        """
        Initializes the instance assigning values to the class attributes.

        Args:
            tool_display_name (str): The display name for the tool, used in logging.
            temp_file_name (str): Used to save results and retrieve them after command execution.
            tool_name: Used to save the scan.
        """
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.thread = None
        self.tool_display_name = tool_display_name
        self.tool_name = tool_name
        self.temp_file_name = temp_file_name
        self.running_message = f"Running {self.tool_display_name} with command: "

    def run(self, target: str, options: dict):
        """
        Executes the command to run the tool scan.

        Deletes the previous reference to scan results, builds the command,
        runs the command saving the reference to the command thread.

        This method relies on the following methods, which need to be overridden:
        - `__build_command__()`
        - `__run_command__()`

        Args:
            target (str): The target of the scan.
            options (dict): Dictionary containing options for the command.
        """
        self.last_scan_result = None
        command = self.__build_command__(target, options)
        self.__log_running_message__(command)
        self.thread = self.__run_command__(command)
        self.thread.start()

    def stop_scan(self):
        """
        Stops a running scan.

        Checks if the thread has a value and calls the stop method.
        """
        if self.thread is not None:
            self.thread.stop()

    def get_results(self) -> object:
        """
        Returns scan results. the method checks if results need to be parsed from file,
        otherwise returns cached results.

        Returns:
            object: scan results.
        """
        if self.last_scan_result is None:
            l.info(f"Parsing {self.tool_display_name} temp file...")
            self.last_scan_result, exception = self.__parse_temp_results_file__()
            if self.last_scan_result:
                l.success("File parsed successfully.")
            else:
                l.error("Error parsing temp file.")
                print(exception)
                return None

            self.__remove_temp_file__()

        return self.last_scan_result

    def save_results(self):
        """
        Saves results in storage file.

        Args:
            current_scan (Scan): current scan where tool scan needs to be saved.

        Returns:
            Returns a boolean value representing the scan state (True = started, False = not started),
            or an Exception if something goes wrong.
        """
        current_scan = CurrentScan.scan

        if current_scan is not None:
            try:
                current_scan.save_scan(self.tool_name, self.last_scan_result)
                self.last_scan_result = None
                l.success(f"{self.tool_display_name} results saved.")
                return True
            except Exception as e:
                l.error(f"{self.tool_display_name} results were not saved!")
                print(e)
                return e
        l.warning(f"No scan was started!")
        return False

    def save_report(self, html: str):
        """
        Generate a PDF file based on the rendered HTML.

        Args:
            html (str): The HTML string.

        Returns:
            Exception | True : Returns a True value representing the outcome of file creation or the Exception raised.
        """

        report_path = os.path.join(os.getcwd(), REPORTS_DIR)
        if not os.path.exists(report_path):
            os.makedirs(report_path)

        if html != "":
            return create_pdf_from_html(
                ["styles.css", "w3.css"], html, REPORTS_DIR, self.tool_name
            )

    def restore_scan(self):
        current_scan = CurrentScan.scan
        self.last_scan_result = current_scan.get_tool_scan(self.tool_name)

    def __build_command__(self, target: str, options: dict) -> list:
        """
        Builds and returns the command to run.

        This method should be overridden in subclasses for customization.

        Args:
            target (str): The target of the scan.
            options (dict): Options for the command.

        Returns:
            list: A list representing the command.
                  Example: ["nmap", "-sV", "127.0.0.1"]
        """
        pass

    def __run_command__(self) -> threading.Thread:
        """
        Runs the command in a new thread.

        Use CommandThread or build a class that inherits from Thread and
        implements a stop() method.
        This method should be overridden in subclasses for customization.

        Returns:
            threading.Thread: A reference to the command thread.
        """
        pass

    def __log_running_message__(self, command: list):
        """
        Logs a running message after formatting the command.

        Args:
            command (list): The command about to be executed.
        """
        command_string = build_command_string(command)

        l.info(self.running_message)
        l.info(command_string[:-1])

    def __remove_temp_file__(self):
        """
        Removes a temporary results file.
        """
        try:
            l.info(f"Removing temp {self.tool_display_name} file...")
            os.remove(self.temp_file_name)
            l.success("File removed successfully.")
        except Exception as e:
            l.error(f"Couldn't remove temp {self.tool_display_name} file.")
            print(e)

    def __parse_temp_results_file__(self) -> Tuple[object, Exception]:
        """
        Parses a temporary file to extract results.

        This method should be overridden in subclasses for customization.

        Returns:
            Tuple[object, Exception]: A tuple containing the results and an exception.
                                    If results are present, the exception is ignored.
                                    If results are not present, the exception is considered.
        """
        pass
