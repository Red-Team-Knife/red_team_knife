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
        super().__init__(TOOL_DISPLAY_NAME, None, TOOL_NAME)

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
                l.info(f"{self.tool_display_name} scan ID: {str(self.scan_id)}")
                break
            except Exception as e:
                l.error(f"Something went wrong during {self.tool_display_name}.")
                print(e)
                time.sleep(2)

        self.is_scan_in_progress = False
        self.is_scan_in_background = True

    def stop_scan(self):
        l.info(
            f"Handling stop request for {self.tool_display_name}, for scan id {self.scan_id}."
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
            f"Handling deletion request for {self.tool_display_name}, for scan id {self.scan_id}."
        )
        if self.is_scan_in_background:
            self.stop_scan()
        url = BASE_URL + f"/scans/{self.scan_id}"
        requests.delete(url)
        self.scan_id = None
        l.success(f"Deletion completed for scan id {self.scan_id}.")

    def save_results(self):
        self.retrieve_complete_scan()
        return super().save_results()

    def get_results(self) -> object:

        status = requests.get(BASE_URL + f"/scans/{self.scan_id}/status")

        if status.status_code == 200:
            self.status = status.json()

        if self.is_scan_in_background:
            self.last_scan_result = requests.get(
                BASE_URL + f"/scans/{self.scan_id}/kb"
            ).json()
            self.last_scan_result["status"] = self.status

        return self.last_scan_result

    def retrieve_complete_scan(self):
        for item in self.last_scan_result["items"]:
            item["info"] = requests.get(BASE_URL + item["href"]).json()

    def restore_scan_status(self):
        self.status = self.last_scan_result.get("status")
