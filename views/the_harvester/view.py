from views.view import BaseBlueprint
from utils.utils import debug_route
from flask import request
from controllers.feroxbuster import (
    TOOL_NAME as FEROXBUSTER_NAME,
    TOOL_DISPLAY_NAME as FEROXBUSTER_DISPLAY_NAME,
)
from controllers.w4af_audit import (
    TOOL_NAME as W4AF_TOOL_NAME,
    TOOL_DISPLAY_NAME as W4AF_TOOL_DISPLAY_NAME,
)


class TheHarvesterBlueprint(BaseBlueprint):

    def interface(self):
        extra = {
            "feroxbuster_name": FEROXBUSTER_NAME,
            "feroxbuster_display_name": FEROXBUSTER_DISPLAY_NAME,
            "w4af_name": W4AF_TOOL_NAME,
            "w4af_display_name": W4AF_TOOL_DISPLAY_NAME,
        }
        return super().interface(extra=extra)
