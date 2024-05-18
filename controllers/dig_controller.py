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
        super().__init__(TOOL_DISPLAY_NAME, TEMP_FILE_NAME)

    def run(self, target: str, options: dict):
        self.last_scan_result = None
        self.is_scan_in_progress = True
        self.query_type = options.get(QUERY_TYPE)
        self.last_scan_result = pydig.query(target, self.query_type)
        self.is_scan_in_progress = False

    def __format_result__(self):
        html = "<table>"

        for row in self.last_scan_result:
            if self.query_type.lower() == "mx":
                row = self.__format_mx_result__(row)
                html += f'<tr class="open" onclick="redirectToSpoofer(\'{row}\')" title="Found a mail server. Click here to try spoofing an email." style="cursor: pointer;"><th>{self.query_type}</th><td>{row}</td></tr>'
            else:
                html += f"<tr><th>{self.query_type}</th><td>{row}</td></tr>"
        html += "</table>"
        if self.query_type.lower() == "mx":
            html += f"""
                    <script>
                    function redirectToSpoofer(host) {{
                        window.location.href = '/{SPOOFER_ENDPOINT}?{SPOOFER_HOST_PARAMETER_NAME}=' + host;
                    }}
                    </script>
                    """
        return html

    def __format_mx_result__(self, row):
        parts = row.split()

        if len(parts) >= 2 and parts[0].isdigit():
            domain = " ".join(parts[1:]).strip(".")
            return domain
        else:
            return row
