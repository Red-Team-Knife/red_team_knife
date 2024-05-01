import threading
import subprocess, os, json, shutil, time

from utils.commands import build_command_string
from controllers.controller_thread import Controller, CommandThread


RUNNING_MESSAGE = "Running Searchsploit DB with command: "
TOOL_NAME = "searchsploit-DB"
EDB = "EDB-ID"
CVE = "CVE"


class SearchsploitController(Controller):
    def __init__(self):
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.tool_name = TOOL_NAME
        self.query = None
        self.type_query = None
        self.command_output = None

    def run(self, query, options):
        print("QUERY", query)
        self.last_scan_result = None
        self.__format_query__(query)

        command = ["searchsploit", "-w", "-j", self.query]

        print(command)

        command_string = build_command_string(command)
        print(RUNNING_MESSAGE + command_string[:-1])

        class SearchsploitCommandThread(CommandThread):
            def run(self):
                # Set the flag indicating the scan is in progress
                self.calling_controller.is_scan_in_progress = True

                # Start the subprocess and capture its output
                command_output = ""
                self.process = subprocess.Popen(
                    self.command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )

                self.process.wait()

                # Accumulate the output while the command is running
                for output in self.process.stdout:
                    command_output += output

                # Print the accumulated output once the command completes
                command_output = command_output.strip()
                print(command_output)
                self.calling_controller.command_output = command_output

                # Terminate the process if it's still running
                if self.process.poll() is None:
                    self.process.kill()

                # Print completion message if the process wasn't stopped
                if not self._stop_event.is_set():
                    print(self.tool_name + " scan completed.")

                # Wait for the process to terminate
                # self.process.wait()
                self.calling_controller.is_scan_in_progress = False

        self.thread = SearchsploitCommandThread(command, self)
        self.thread.start()

    def __format_result__(self):
        if not self.last_scan_result:

            print(self.command_output)

            json_results = json.loads(self.command_output)
            self.last_scan_result = json_results

        with open("test.json", "w") as file:
            print(json.dumps(self.last_scan_result), file=file)

        return self.__format_html__()

    def __format_query__(self, query):

        if EDB in query:

            # take db code
            query = query.split(":")[1]
            self.type_query = EDB
            self.query = query

        elif CVE in query:

            self.type_query = CVE
            self.query = query
        else: 
            self.query = None

    def __format_html__(self):
        html_string = ""
        if self.type_query == EDB:

            for result in self.last_scan_result["RESULTS_EXPLOIT"]:

                # check if there is a query result
                if result.get("URL", False):

                    # check if it is correct result
                    if (
                        result["URL"]
                        == f"https://www.exploit-db.com/exploits/{self.query}"
                    ):

                        html_string += "<p><b>Title: </b>"
                        html_string += f'{result["Title"]}</p><br>'

                        html_string += "<p><b>Url: </b>"
                        html_string += (
                            f'<a href= "{result["URL"]}" target="_blank">{result["URL"]}</a></p><br>'
                        )

        elif self.type_query == CVE:

            for result in self.last_scan_result["RESULTS_EXPLOIT"]:

                if result.get("URL", False):

                    html_string += "<p><b>Title: </b>"
                    html_string += f'{result["Title"]}</p><br>'

                    html_string += "<p><b>Url: </b>"
                    html_string += (
                        f'<a href= "{result["URL"]}">{result["URL"]}</a></p><br>'
                    )

        return html_string
