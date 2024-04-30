import json
import os
import time

import requests
from controllers.controller_thread import CommandThread, Controller

PROFILE = "profile"
PROFILE_RELATIVE_PATH = "w4af/profiles/"
SCAN_PROFILE = "scan_profile"
TARGET_URLS = "target_urls"
W4AF_PORT = 5001
TOOL_NAME = "w4af (Audit)"

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

        self.scan_id = None

    def run(self, target, options: dict):
        profile_content = ""

        with open(PROFILE_RELATIVE_PATH + options[PROFILE], "r") as file:

            profile_content = file.read()

        if profile_content != "":
            data = {SCAN_PROFILE: profile_content, TARGET_URLS: [target]}

        class W4afCommandThread(CommandThread):
            def __init__(self, caller: Controller):
                super().__init__([], caller)
                self.base_url = f"http://127.0.0.1:{W4AF_PORT}/scans/"

            def run(self):

                self.caller.is_scan_in_progress = True
                response = requests.post(
                    self.base_url,
                    data=json.dumps(data),
                    headers={"content-type": "application/json"},
                )
                while True:
                    try:
                        self.caller.scan_id = response.json().get("id")
                        print(self.tool_name + " scan ID: " + str(self.caller.scan_id))
                        break
                    except Exception as e:
                        print('Error:', e)
                        time.sleep(2)

                self.caller.is_scan_in_progress = False
                print('here')


            def stop(self):
                super().stop()

                res = requests.get(self.base_url + f"{self.caller.scan_id}/stop")
                while True:
                    try:
                        res = requests.get(self.base_url + f"{self.caller.scan_id}/status")

                        paused = res.json().get("is_running")
                        time.sleep(1)
                        if not paused:
                            break
                    except:
                        pass
                res = requests.delete(self.base_url + f"{self.caller.scan_id}")

                self.print_stop_completed_message()

        self.thread = W4afCommandThread(self)
        self.thread.start()
        self.thread.join()

    def __format_result__(self):
        print('here')
        res = requests.get(f"http://127.0.0.1:{W4AF_PORT}/scans/{self.scan_id}/kb").text
        print(res)
        return res
