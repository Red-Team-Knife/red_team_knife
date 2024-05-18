import json
import os
import time
from loguru import logger as l
import uuid

from flask import jsonify, send_from_directory, url_for
import requests
from controllers.base_controller import Controller
from controllers.command_thread import CommandThread
from utils.utils import render_dictionary_as_table

W4AF_DIRECTORY = "tools/w4af/"

PROFILE = "profile"
PROFILE_RELATIVE_PATH = f"{W4AF_DIRECTORY}/profiles/"
SCAN_PROFILE = "scan_profile"
TARGET_URLS = "target_urls"
W4AF_PORT = 5001
TOOL_DISPLAY_NAME = "w4af (Audit)"
TOOL_NAME = "w4af_audit"
BASE_URL = f"http://127.0.0.1:{W4AF_PORT}"
TMP_FOLDER = "tmp"

if os.path.exists(PROFILE_RELATIVE_PATH) and os.path.isdir(PROFILE_RELATIVE_PATH):
    filenames = os.listdir(PROFILE_RELATIVE_PATH)


options = []
for filename in filenames:
    options.append((filename, filename))
scan_options = [("Set scan profile", "select", PROFILE, options)]


class W4afAuditController(Controller):
    def __init__(self):
        super().__init__(TOOL_DISPLAY_NAME, None)

        self.is_scan_in_background = False
        self.scan_id = None
        self.status = None

    def run(self, target, options: dict):
        profile_content = ""

        with open(PROFILE_RELATIVE_PATH + options[PROFILE], "r") as file:

            profile_content = file.read()

        if profile_content != "":
            request_data = {SCAN_PROFILE: profile_content, TARGET_URLS: [target]}

        self.is_scan_in_progress = True
        response = requests.post(
            BASE_URL + "/scans/",
            data=json.dumps(request_data),
            headers={"content-type": "application/json"},
        )
        while True:
            try:
                self.scan_id = response.json().get("id")
                l.info(f"{self.tool_name} scan ID: {str(self.scan_id)}")
                break
            except Exception as e:
                l.error(f"Something went wrong during {self.tool_name}.")
                print(e)
                time.sleep(2)

        self.is_scan_in_progress = False
        self.is_scan_in_background = True

    def stop_scan(self):
        l.info(
            f"Handling stop request for {self.tool_name}, for scan id {self.scan_id}."
        )
        requests.get(BASE_URL + f"/scans/{self.scan_id}/stop")
        while True:
            try:
                res = requests.get(BASE_URL + f"/scans/{self.scan_id}/status")

                paused = res.json().get("is_running")
                time.sleep(1)
                if not paused:
                    break
            except Exception as e:
                print(e)

        status = requests.get(BASE_URL + f"/scans/{self.scan_id}/status")

        if status.status_code == 200:
            self.status = status.json()

        self.last_scan_result["status"] = self.status
        self.is_scan_in_background = False
        l.success(f"Stop completed for scan id {self.scan_id}.")

    def delete_scan(self):
        l.info(
            f"Handling deletion request for {self.tool_name}, for scan id {self.scan_id}."
        )
        if self.is_scan_in_background:
            self.stop_scan()
        url = BASE_URL + f"/scans/{self.scan_id}"
        requests.delete(url)
        self.scan_id = None
        l.success(f"Deletion completed for scan id {self.scan_id}.")

    def __format_result__(self):
        l.info(f"Generating HTML for {self.tool_name} results...")

        status = requests.get(BASE_URL + f"/scans/{self.scan_id}/status")

        if status.status_code == 200:
            self.status = status.json()

        if self.is_scan_in_background:
            self.last_scan_result = requests.get(
                BASE_URL + f"/scans/{self.scan_id}/kb"
            ).json()
            self.last_scan_result["status"] = self.status

        try:
            html_table = "<table>\n"
            html_table += (
                "<tr><th>ID</th><th>Name</th><th>URL</th><th>Reference</th></tr>\n"
            )

            for item in self.last_scan_result["items"]:
                html_table += (
                    f'<tr><td>{item["id"]}</td>'
                    + f'<td>{item["name"]}</td>'
                    + f'<td>{item["url"]}</td>'
                )
                if item.get("info"):
                    description_file_path, description_file_name = (
                        self.__create_temp_description_file__(item)
                    )
                    html_table += f'<td><a href="/{description_file_name}" target="_blank">Read more</a></td></tr>\n'
                else:
                    html_table += f'<td><a href="{BASE_URL + item["href"]}" target="_blank">Read more</a></td></tr>\n'

            html_table += "</table>"
            l.success("HTML generated successfully.")
            return {
                "status": self.__create_dictionary_html_table__(self.status),
                "results": html_table,
                "progress": self.status.get("progress"),
            }
        except Exception as e:
            print(e)
            return {
                "status": "<p>Fetching results...</p>",
                "results": "<p>Fetching results...</p>",
                "progress": 0,
            }

    def __retrieve_complete_scan__(self):
        for item in self.last_scan_result["items"]:
            item["info"] = requests.get(BASE_URL + item["href"]).json()

    def __create_temp_description_file__(self, item):
        random_uuid = uuid.uuid4()
        # Convert UUID to a string and remove dashes
        random_filename = str(random_uuid).replace("-", "")
        file_path = os.path.join(TMP_FOLDER, random_filename + ".html")
        with open(file_path, "w") as file:

            print(self.__generate_description_html_page__(item["info"]), file=file)

            return file_path, file_path

    def __create_dictionary_html_table__(self, dictionary: dict, indent=""):
        html = ""
        for key, value in dictionary.items():
            if isinstance(value, dict):
                html += (
                    f"<tr><th>{indent}{key}</th><td><table>"
                    + render_dictionary_as_table(value, indent + "&nbsp;&nbsp;")
                    + "</table></td></tr>"
                )
            else:
                html += f"<tr><th>{indent}{key}</th><td>{value}</td></tr>"
        return html

    def __generate_description_html_page__(self, data):
        html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Vulnerability Description</title>
                <link rel="stylesheet" href="{url_for('static', filename='styles.css')}">
            </head>
            <body>
                <table border="1">
                    {render_dictionary_as_table(data)}
                </table>
            </body>
            </html>
            """

        return html_content

    def restore_last_scan(self):
        self.status = self.last_scan_result.get("status")
        return self.__format_result__()

    def get_formatted_results(self):
        if not self.is_scan_in_progress:
            return self.__format_result__()
