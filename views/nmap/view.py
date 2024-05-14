from views.view import BaseBlueprint
from utils.utils import debug_route
from flask import request
from controllers.nmap_vuln import TOOL_NAME as NMAP_VULN_NAME




class NmapBlueprint(BaseBlueprint):
    
    def interface(self):
        extra = {"nmap_vuln_name" : NMAP_VULN_NAME}
        return super().interface(extra= extra)
    