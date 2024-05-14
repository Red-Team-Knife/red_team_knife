from views.view import BaseBlueprint
from utils.utils import debug_route
from flask import request
from controllers.exploitation_tips import EXPLOITATION_TIPS_NAME


class NmapVulnBlueprint(BaseBlueprint):

    def interface(self):
        extra = {"exploitation_tips_name": EXPLOITATION_TIPS_NAME}
        return super().interface(extra=extra)
