import os
import shutil
import csv
import json
from threading import Thread
from typing import Tuple
from loguru import logger as l
from controllers.base_controller import Controller
from controllers.command_thread import CommandThread
from utils.utils import render_list_in_dictionary_as_table


REQUEST_DATA = "request_data"
SET_COOKIE = "set_cookie"
SET_PROXY = "set_proxy"
SET_TOR = "set_tor"
CHECK_TOR = "check_tor"
SET_PARAMETER = "set_parameter"
SET_DBMS = "set_dbms"
SET_LEVEL = "set_level"
SET_RISK = "set_risk"
SET_TECHNIQUE = "set_technique"
RETRIEVE_ALL = "retrieve_all"
RETRIEVE_BANNERS = "retrieve_banners"
RETRIEVE_CURRENT_USER = "retrieve_current_user"
RETRIEVE_CURRENT_DB = "retrieve_current_db"
RETRIEVE_PASSWORD_HASH = "retrieve_password_hash"
LIST_PRIVILEGES = "list_privileges"
LIST_DB = "list_db"
LIST_TABLES = "list_tables"
LIST_COLUMNS = "list_columns"
LIST_SCHEMA = "list_schema"
DUMP_TABLES_ENTRIES = "dump_tables_entries"
DUMP_DB_ENTRIES = "dump_db_entries"
SET_DB = "set_db"
SET_TABLE = "set_table"
SET_COLUMN = "set_column"
SET_THREADS = "set_threads"
SET_OS = "set_os"
SET_AUTH_TYPE = "set_auth_type"
SET_AUTH_CREDS = "set_auth_creds"
SET_STRING = "set_string"
SET_FILE = "set_file"
SET_CRAWL = "set_crawl"
TEST_FORMS = "test_forms"


TEMP_FILE_NAME = "tmp/sqmap-temp"
TOOL_DISPLAY_NAME = "Sqlmap"
TOOL_NAME = "sqlmap"
RUNNING_MESSAGE = f"Running {TOOL_DISPLAY_NAME} with command: "


scan_options = [
    ("Set Data for Requests", "text", REQUEST_DATA, "id=* / data1=*&data2=*"),
    ("Set Cookie value", "text", SET_COOKIE, "PHPSESSID=a8d127e"),
    ("Set Proxy to connect with", "text", SET_PROXY, "http://proxy.com"),
    ("Set Tor", "checkbox", SET_TOR, ""),
    ("Check for Tor Usage", "checkbox", CHECK_TOR, ""),
    ("Set a Parameter to Test on", "text", SET_PARAMETER, "id, resource"),
    ("Set DBMS type", "text", SET_DBMS, "MySQL, SQLite"),
    ("Set Tests Level", "number", SET_LEVEL, "0-5"),
    ("Set Risk Level", "number", SET_RISK, "0-3"),
    ("Specify Sql Injection technique", "text", SET_TECHNIQUE, "Default BEUSTQ"),
    ("Retrieve all DBMS content", "checkbox", RETRIEVE_ALL, ""),
    ("Retrieve DBMS banners", "checkbox", RETRIEVE_BANNERS, ""),
    ("Retrieve current User", "checkbox", RETRIEVE_CURRENT_USER, ""),
    ("Retrieve current Database", "chechbox", RETRIEVE_CURRENT_DB, ""),
    ("Retrieve Password Hashes", "checkbox", RETRIEVE_PASSWORD_HASH, ""),
    ("List Priviledges", "checkbox", LIST_PRIVILEGES, ""),
    ("List Databases", "checkbox", LIST_DB, ""),
    ("List Tables", "checkbox", LIST_TABLES, ""),
    ("List Columns", "checkbox", LIST_COLUMNS, ""),
    ("List Schema", "checkbox", LIST_SCHEMA, ""),
    ("Dump tables entries", "checkbox", DUMP_TABLES_ENTRIES, ""),
    ("Dump Database entries", "checkbox", DUMP_DB_ENTRIES, ""),
    ("Set Database to retrieve", "text", SET_DB, ""),
    ("Set Table to retrieve", "text", SET_TABLE, ""),
    ("Set Column to retrieve", "text", SET_COLUMN, ""),
    ("Set Threads", "number", SET_THREADS, "Default 10"),
    ("Set Target OS", "text", SET_OS, "Windows"),
    ("Set Authentication Type", "text", SET_AUTH_TYPE, "Basic, Digest, NTLM or PKI"),
    ("Set Authentication Credentials", "text", SET_AUTH_CREDS, "name:password"),
    ("Set String to show when Injection is successful", "text", SET_STRING, ""),
    ("Set File to Read", "text", SET_FILE, "/etc/passwd"),
    ("Set Crawling depth", "number", SET_CRAWL, "Default 0"),
    ("Test Forms", "checkbox", TEST_FORMS, ""),
]



class SqlmapController(Controller):
    
    def __init__(self):
        super().__init__(TOOL_NAME, TEMP_FILE_NAME)
        
        
    def __build_command__(self, target: str, options: dict) -> list:
        command = [
            "sqlmap",
            "-u",
            target,
            '--output-dir',
            f'./{TEMP_FILE_NAME}',
            "--dump-format=CSV",
            "--batch",
            "-v 4",
        ]
        
        
        if options.get(REQUEST_DATA, False):
            command.extend(["--data", f'"{options[REQUEST_DATA]}"'])

        if options.get(SET_COOKIE, False):
            command.extend(["--cookie", f'"{options[SET_COOKIE]}"'])

        if options.get(SET_PROXY, False):
            command.extend(["--proxy=", options[SET_PROXY]])

        if options.get(SET_TOR, False):
            command.append("--tor")

        if options.get(CHECK_TOR, False):
            command.append("--check-tor")

        if options.get(SET_PARAMETER, False):
            command.extend(["-p ", f'"{options[SET_PARAMETER]}"'])

        if options.get(SET_DBMS, False):
            command.extend(["--dbms=", f'"{options[SET_DBMS]}"'])
        
        if options.get(SET_LEVEL, False):
            command.extend(["--level= ", options[SET_PARAMETER]])

        if options.get(SET_RISK, False):
            command.extend(["--risk= ", options[SET_RISK]])

        if options.get(SET_TECHNIQUE, False):
            command.extend(["--technique= ", f'"{options[SET_RISK]}"'])

        if options.get(RETRIEVE_ALL, False):
            command.append("-a")

        if options.get(RETRIEVE_BANNERS, False):
            command.append("-b")

        if options.get(RETRIEVE_CURRENT_USER, False):
            command.append("--current-user")

        if options.get(RETRIEVE_CURRENT_DB, False):
            command.append("--current-db")

        if options.get(RETRIEVE_PASSWORD_HASH, False):
            command.append("--passwords")

        if options.get(LIST_PRIVILEGES, False):
            command.append("--privileges")

        if options.get(LIST_DB, False):
            command.append("--dbs")

        if options.get(LIST_TABLES, False):
            command.append("--tables")

        if options.get(LIST_COLUMNS, False):
            command.append("--columns")

        if options.get(LIST_SCHEMA, False):
            command.append("--schema")

        if options.get(DUMP_TABLES_ENTRIES, False):
            command.append("--dump")

        if options.get(DUMP_DB_ENTRIES, False):
            command.append("--dump-all")

        if options.get(DUMP_DB_ENTRIES, False):
            command.extend(["--dump-all"])

        if options.get(SET_DB, False):
            command.extend(["-D", options[SET_DB]])

        if options.get(SET_TABLE, False):
            command.extend(["-T", options[SET_TABLE]])

        if options.get(SET_COLUMN, False):
            command.extend([["-C", options[SET_COLUMN]]])

        if options.get(SET_THREADS, False):
            command.extend(["--threads=", options[SET_THREADS]])

        if options.get(SET_OS, False):
            command.extend(["--os=", f'"{options[SET_OS]}"'])

        if options.get(SET_AUTH_TYPE, False):
            command.extend(["--auth-type=", f'"{options[SET_AUTH_TYPE]}"'])

        if options.get(SET_AUTH_CREDS, False):
            command.extend(["--auth-cred=", f'"{options[SET_AUTH_CREDS]}"'])

        if options.get(SET_STRING, False):
            command.extend(["--string=", f'"{options[SET_STRING]}"'])

        if options.get(SET_FILE, False):
            command.extend(["--file-read=", options[SET_FILE]])

        if options.get(SET_CRAWL, False):
            command.extend(["--crawl=", options[SET_CRAWL]])

        if options.get(TEST_FORMS, False):
            command.append("--forms")

        return command
    
    def __run_command__(self, command) -> Thread:
        class SqlmapCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    self.calling_controller.__remove_temp_file__()
                    
        return SqlmapCommandThread(command, self)
    
    def __remove_temp_file__(self):
        """
        Needs to override super method because sqlmap saves temp files in more folders.
        Removes a temporary results folder
        """
        try:
            l.info(f"Removing temp {self.tool_name} folder...")
            shutil.rmtree(self.temp_file_name)
            l.success("File removed successfully.")
        except Exception as e:
            l.error(f"Couldn't remove temp {self.tool_name} folder.")
            print(e)
            
    def __parse_temp_results_file__(self) -> Tuple[dict, Exception]:
        # List to store all dumped data
        json_objects = []
        TEMP_PATH = "./" + TEMP_FILE_NAME
        for scan in os.listdir(TEMP_PATH):
            scan_path = os.path.join(TEMP_PATH, scan)
            if os.path.isdir(scan_path):
                # Check if there is Dump Folder
                dump_path = os.path.join(scan_path, "dump")
                if os.path.isdir(dump_path):
                    # Iterate on all dump folders
                    for dump in os.listdir(dump_path):
                        json_object = {}
                        json_object[dump] = {}
                        dump_folder = os.path.join(dump_path, dump)
                        # Iterate for all files in dump folders
                        for file_name in os.listdir(dump_folder):
                            file_path = os.path.join(dump_folder, file_name)
                            if os.path.isfile(file_path):
                                
                                with open(file_path, 'r') as file:                              
                                    csv_content = [row for row in csv.DictReader(file)]
                                    json_object[dump][file_name] = csv_content
                    

                        json_objects.append(json_object)  
                        
                elif os.path.isfile(os.path.join(scan_path, "log")):
                    log_path = os.path.join(scan_path, "log")
                    
                    with open(log_path, "r") as file:
                        json_objects.append(file.read())
                                                
        if len(json_objects) == 0:
            return None, None                             
               
        return json_objects, None
    
    
    def __format_html__(self) -> str:
        html_output = ''
        
        for db in self.last_scan_result:
            if isinstance(db, str):
                html_output += "<b> Results: </b><br>"
                html_output += f"<textarea readonly class= 'sqlmap_textarea'> {db} </textarea>"
            else:
                html_output += f'<b> {list(db.keys())[0]} :</b> <br>'
                
                for section in db:
                    for table in db[section]:
                        html_output += f'<b> {table} :</b>'
                        if len(db[section][table]) == 0:
                            html_output += '<p> No data Retrieved </p><br>'
                        else:
                            html_output += '<table>'
                            html_output += render_list_in_dictionary_as_table(db[section][table])
                            html_output += '</table> <br>'
                                    
            html_output += '<br><br>'  
                    
        return html_output