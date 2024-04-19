import requests
from controllers.controller import Controller
from controllers.w4af_audit import W4afAuditController


PROFILE = "profile"
PROFILE_RELATIVE_PATH = 'w4af/profiles/'
SCAN_PROFILE = 'scan_profile'
TARGET_URLS = 'target_urls'
AUDIT = "audit"
CRAWL = "crawl"
ATTACK = "attack"


w4af_audit_controller = W4afAuditController()

class W4afController(Controller):
    def __init__(self):
        self.last_scan_result = None


    def run_audit(self, target, profile):

        profile_content = ''

        with open(PROFILE_RELATIVE_PATH + profile, 'r') as file:

            profile_content = file.read()

        if profile_content != '':
            data = {
                SCAN_PROFILE: profile_content,
                TARGET_URLS : [target]
            }

        return 
    

    def run_crawl():
        pass

    def run_attack():
        pass

