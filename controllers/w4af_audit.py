from controllers.w4af import *
from controllers.controller import Controller


w4af_controller = W4afController()

scan_options = [
    ("Set scan profile", "select", PROFILE, [])
]


class W4afAuditController(Controller):
    def __init__(self):
        self.last_scan_result = None

    def run(self, target, options: dict):

        return w4af_controller.run_audit(target, options.get(PROFILE) + ".w4af")
