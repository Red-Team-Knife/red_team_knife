import json
import os
import time

from flask import jsonify
import requests
from controllers.controller_thread import CommandThread, Controller

PROFILE = "profile"
PROFILE_RELATIVE_PATH = "w4af/profiles/"
SCAN_PROFILE = "scan_profile"
TARGET_URLS = "target_urls"
W4AF_PORT = 5001
TOOL_NAME = "w4af (Audit)"
BASE_URL = f"http://127.0.0.1:{W4AF_PORT}"

if os.path.exists(PROFILE_RELATIVE_PATH) and os.path.isdir(PROFILE_RELATIVE_PATH):
    filenames = os.listdir(PROFILE_RELATIVE_PATH)

try:
    filenames.remove("sitemap.pw4af")
    filenames.remove("web_infrastructure.pw4af")
except:
    pass

options = []
for filename in filenames:
    options.append((filename, filename))
scan_options = [("Set scan profile", "select", PROFILE, options)]


class W4afAuditController(Controller):
    def __init__(self):
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.tool_name = TOOL_NAME

        self.is_scan_in_background = False
        self.scan_id = None

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
                print(self.tool_name + " scan ID: " + str(self.scan_id))
                break
            except Exception as e:
                print("Error:", e)
                time.sleep(2)

        self.is_scan_in_progress = False
        self.is_scan_in_background = True

    def stop_scan(self):
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

        self.is_scan_in_background = False

    def delete_scan(self):
        if self.is_scan_in_background:
            self.stop_scan()
        url = BASE_URL + f"/scans/{self.scan_id}"
        requests.delete(url)
        self.scan_id = None

    def __format_result__(self):
        self.last_scan_result = requests.get(
            BASE_URL + f"/scans/{self.scan_id}/kb"
        ).json()
        status = requests.get(BASE_URL + f"/scans/{self.scan_id}/status").json()

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
                    + f'<td><a href="{BASE_URL + item["href"]}" target="_blank">{item["href"]}</a></td></tr>\n'
                )

            html_table += "</table>"

            return {"status": status, "results": html_table}
        except:
            return "<p>Fetching results...</p>"

    def __retrieve_complete_scan__(self):
        for item in self.last_scan_result["items"]:
            item["info"] = requests.get(BASE_URL + item["href"]).json()
