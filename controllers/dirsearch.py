import os
import shutil
from threading import Thread
from typing import Tuple
from controllers.base_controller import Controller
from controllers.command_thread import CommandThread
from loguru import logger as l

TOOL_DISPLAY_NAME = "Dirsearch"
TOOL_NAME = "dirsearch"
TEMP_FILE_NAME = "tmp/dirsearch-temp"

SET_EXTENSIONS = "set_extensions"
SET_THREADS = "set_threads"
SET_WORDLIST = "set_wordlist"

scan_options = [
    ("Extensions (e.g. php,html,txt)", "text", SET_EXTENSIONS, "php,html"),
    ("Threads", "number", SET_THREADS, "Default 30"),
    ("Custom Wordlist Path", "text", SET_WORDLIST, "/usr/share/wordlists/..."),
]

class DirsearchController(Controller):
    def __init__(self):
        super().__init__(TOOL_DISPLAY_NAME, TEMP_FILE_NAME, TOOL_NAME)

    def __build_command__(self, target: str, options: dict) -> list:
        temp_path = os.path.join(os.getcwd(), TEMP_FILE_NAME)
        
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        # Base command: dirsearch -u target --format=plain -o output_file
        command = [
            "dirsearch",
            "-u", target,
            "--format", "plain",
            "-o", os.path.join(temp_path, "report.txt")
        ]

        # Adding dynamic options
        if options.get(SET_EXTENSIONS):
            command.extend(["-e", options[SET_EXTENSIONS]])
        else:
            command.extend(["-e", "php,html,txt"]) 

        if options.get(SET_THREADS):
            command.extend(["-t", str(options[SET_THREADS])])

        if options.get(SET_WORDLIST):
            command.extend(["-w", options[SET_WORDLIST]])

        return command

    def __run_command__(self, command: list) -> Thread:
        class DirsearchCommandThread(CommandThread):
            def run(self):
                super().run()
                l.info("Dirsearch scan completed. Files ready for parsing.")

        return DirsearchCommandThread(command, self)

    def __parse_temp_results_file__(self) -> Tuple[object, Exception]:
        import os
        report_path = os.path.abspath("tmp/dirsearch-temp/report.txt")
        
        l.info(f"Attempting to read report from: {report_path}")
        
        try:
            if os.path.exists(report_path):
                with open(report_path, "r") as f:
                    content = f.read()
                if content.strip():
                    return content, None
                else:
                    return None, Exception("report.txt file exists but is empty")
            else:
                return None, Exception(f"File not found at {report_path}")
        except Exception as e:
            return None, e

    def __remove_temp_file__(self):
        return
        import shutil
        try:
            if os.path.exists(self.temp_file_name):
                l.info(f"Removing temp directory {self.temp_file_name}...")
                shutil.rmtree(self.temp_file_name) 
                l.success("Directory removed successfully.")
        except Exception as e:
            l.error(f"Error removing directory: {e}")
