from controllers.base_controller import Controller
import pydig
from controllers.smtp_email_spoofer import (
    TOOL_NAME as SPOOFER_ENDPOINT,
    HOST as SPOOFER_HOST_PARAMETER_NAME,
)

QUERY_TYPE = "query_type"

TEMP_FILE_NAME = "tmp/dig-temp"
TOOL_DISPLAY_NAME = "Dig - Dns Lookup"
TOOL_NAME = "dig"


scan_options = [
    ("Query type", "text", QUERY_TYPE, "a, mx, ..."),
]


class DigController(Controller):

    def __init__(self):
        super().__init__(TOOL_DISPLAY_NAME, TEMP_FILE_NAME, TOOL_NAME)

    def run(self, target: str, options: dict):
        self.last_scan_result = None
        self.is_scan_in_progress = True
        query_type = options.get(QUERY_TYPE)
        self.last_scan_result = {'response': pydig.query(target, query_type), 'type': query_type}
        self.is_scan_in_progress = False
