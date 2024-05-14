from views.view import BaseBlueprint
from utils.utils import debug_route
from flask import request
from controllers.nmap_vuln import (
    TOOL_NAME as NMAP_VULN_NAME,
    TOOL_DISPLAY_NAME as NMAP_VULN_DISPLAY_NAME,
    PORT_RANGE,
)
from controllers.feroxbuster import (
    TOOL_NAME as FEROXBUSTER_NAME,
    TOOL_DISPLAY_NAME as FEROXBUSTER_DISPLAY_NAME,
)
from controllers.w4af_audit import (
    TOOL_NAME as W4AF_TOOL_NAME,
    TOOL_DISPLAY_NAME as W4AF_TOOL_DISPLAY_NAME,
)


class NmapBlueprint(BaseBlueprint):

    def interface(self):
        extra = {
            "nmap_vuln_name": NMAP_VULN_NAME,
            "nmap_vuln_display_name": NMAP_VULN_DISPLAY_NAME,
            "port_range": PORT_RANGE,
            "feroxbuster_name": FEROXBUSTER_NAME,
            "feroxbuster_display_name": FEROXBUSTER_DISPLAY_NAME,
            "w4af_name": W4AF_TOOL_NAME,
            "w4af_display_name": W4AF_TOOL_DISPLAY_NAME,
        }
        return super().interface(extra=extra)
