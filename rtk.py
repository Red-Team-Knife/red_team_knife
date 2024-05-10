from flask import Flask
from datetime import time
import datetime
import shutil
import subprocess
import sys
from flask import *
from controllers.dig_controller import (
    DigController,
    scan_options as dig_scan_options,
    TOOL_NAME as DIG_NAME,
    TOOL_DISPLAY_NAME as DIG_DISPLY_NAME,
)
from controllers.nmap_scan import (
    NmapController,
    scan_options as nmap_scan_options,
    TOOL_DISPLAY_NAME as NMAP_SCAN_DISPLAY_NAME,
    TOOL_NAME as NMAP_SCAN_NAME,
)
from controllers.nmap_vuln import (
    NmapVulnController,
    script_options as nmap_vuln_scan_options,
    TOOL_DISPLAY_NAME as NMAP_VULN_DISPLAY_NAME,
    TOOL_NAME as NMAP_VULN_NAME,
)
from controllers.smtp_email_spoofer_controller import (
    SmtpEmailSpooferController,
    scan_options as smtp_email_spoofer_scan_options,
    TOOL_NAME as SMTP_EMAIL_SPOOFER_NAME,
    TOOL_DISPLAY_NAME as SMTP_EMAIL_SPOOFER_DISPLAY_NAME,
)
from controllers.the_harvester import (
    TheHarvesterController,
    scan_options as the_harvester_scan_options,
    TOOL_DISPLAY_NAME as THE_HARVESTER_DISPLAY_NAME,
    TOOL_NAME as THE_HARVESTER_NAME,
)
from controllers.feroxbuster import (
    FeroxbusterController,
    scan_options as feroxbuster_scan_options,
    TOOL_DISPLAY_NAME as FEROXBUSTER_DISPLAY_NAME,
    TOOL_NAME as FEROXBUSTER_NAME,
)
from controllers.w4af_audit import (
    W4afAuditController,
    scan_options as w4af_audit_scan_options,
    TOOL_DISPLAY_NAME as W4AF_AUDIT_DISPLAY_NAME,
    TOOL_NAME as W4AF_AUDIT_NAME,
    W4AF_DIRECTORY,
)
from controllers.search_exploit import (
    SearchExploitController,
    TOOL_DISPLAY_NAME as SEARCH_EXPLOIT_DISPLAY_NAME,
    TOOL_NAME as SEARCH_EXPLOIT_NAME,
)

from models.scan import Scan
from utils import *
import os
from utils.utils import render_scan_dictionary, debug_route
from views.view import BaseBlueprint
from views.headless_view import HeadlessBlueprint
from views.web_target_view import WebTargetBlueprint
from current_scan import CurrentScan
from views.w4af_audit.view import W4afBlueprint
import logging
from loguru import logger as l
SCANS_PATH = None
SCANS_FOLDER = "scans"
TEMP_FOLDER = "tmp"
REPORTS_FOLDER = "reports"

INTERFACE_TEMPLATE = "interface_scan_target.html"
RESULTS_TEMPLATE = "results_base.html"

NMAP_VULN_RESULTS_TEMPLATE = "nmap_vuln/results.html"
W4AF_RESULTS_TEMPLATE = "w4af_audit/results.html"
SMTP_EMAIL_SPOOFER_INTERFACE_TEMPLATE = "smtp_email_spoofer/interface.html"
SMTP_EMAIL_SPOOFER_RESULTS_TEMPLATE = "smtp_email_spoofer/results.html"

W4AF_ADDRESS = "localhost"
W4AF_PORT = 5001

BANNER = """
__________           .___        
\______   \ ____   __| _/        
 |       _// __ \ / __ |         
 |    |   \  ___// /_/ |         
 |____|_  /\___  >____ |         
        \/     \/     \/         
___________                      
\__    ___/___ _____    _____    
  |    |_/ __ \\__  \  /     \   
  |    |\  ___/ / __ \|  Y Y  \  
  |____| \___  >____  /__|_|  /  
             \/     \/      \/   
 ____  __.      .__  _____       
|    |/ _| ____ |__|/ ____\____  
|      <  /    \|  \   __\/ __ \ 
|    |  \|   |  \  ||  | \  ___/ 
|____|__ \___|  /__||__|  \___  >
        \/    \/              \/ 
        """
BLUEPRINTS = []

SECTIONS = {
    "Reconnaissance": [
        (NMAP_SCAN_DISPLAY_NAME, NMAP_SCAN_NAME),
        (DIG_DISPLY_NAME, DIG_NAME),
        (THE_HARVESTER_DISPLAY_NAME, THE_HARVESTER_NAME),
        (FEROXBUSTER_DISPLAY_NAME, FEROXBUSTER_NAME),
    ],
    "Weaponization": [
        (W4AF_AUDIT_DISPLAY_NAME, W4AF_AUDIT_NAME),
        (NMAP_VULN_DISPLAY_NAME, NMAP_VULN_NAME),
    ],
    "Delivery": [(SMTP_EMAIL_SPOOFER_DISPLAY_NAME, SMTP_EMAIL_SPOOFER_NAME)],
    "Exploitation": [("None", "nmap")],
    "Installation": [("None", "nmap")],
    "Command and Control": [("None", "nmap")],
    "Action": [("None", "nmap")],
}

CONTROLLERS = {
    NMAP_SCAN_NAME: NmapController(),
    NMAP_VULN_NAME: NmapVulnController(),
    DIG_NAME: DigController(),
    THE_HARVESTER_NAME: TheHarvesterController(),
    FEROXBUSTER_NAME: FeroxbusterController(),
    W4AF_AUDIT_NAME: W4afAuditController(),
    SEARCH_EXPLOIT_NAME: SearchExploitController(),
    SMTP_EMAIL_SPOOFER_NAME: SmtpEmailSpooferController(),
}

SCANS_PATH = None
SCANS_FOLDER = "scans"
TEMP_FOLDER = "tmp"
REPORTS_FOLDER = "reports"

INTERFACE_TEMPLATE = "interface_scan_target.html"
RESULTS_TEMPLATE = "results_base.html"

NMAP_VULN_RESULTS_TEMPLATE = "nmap_vuln/results.html"
W4AF_RESULTS_TEMPLATE = "w4af_audit/results.html"
SMTP_EMAIL_SPOOFER_INTERFACE_TEMPLATE = "smtp_email_spoofer/interface.html"
SMTP_EMAIL_SPOOFER_RESULTS_TEMPLATE = "smtp_email_spoofer/results.html"

W4AF_ADDRESS = "localhost"
W4AF_PORT = 5001

BANNER = """
__________           .___        
\______   \ ____   __| _/        
 |       _// __ \ / __ |         
 |    |   \  ___// /_/ |         
 |____|_  /\___  >____ |         
        \/     \/     \/         
___________                      
\__    ___/___ _____    _____    
  |    |_/ __ \\__  \  /     \   
  |    |\  ___/ / __ \|  Y Y  \  
  |____| \___  >____  /__|_|  /  
             \/     \/      \/   
 ____  __.      .__  _____       
|    |/ _| ____ |__|/ ____\____  
|      <  /    \|  \   __\/ __ \ 
|    |  \|   |  \  ||  | \  ___/ 
|____|__ \___|  /__||__|  \___  >
        \/    \/              \/ 
        """
BLUEPRINTS = []

SECTIONS = {
    "Reconnaissance": [
        (NMAP_SCAN_DISPLAY_NAME, NMAP_SCAN_NAME),
        (DIG_DISPLY_NAME, DIG_NAME),
        (THE_HARVESTER_DISPLAY_NAME, THE_HARVESTER_NAME),
        (FEROXBUSTER_DISPLAY_NAME, FEROXBUSTER_NAME),
    ],
    "Weaponization": [
        (W4AF_AUDIT_DISPLAY_NAME, W4AF_AUDIT_NAME),
        (NMAP_VULN_DISPLAY_NAME, NMAP_VULN_NAME),
    ],
    "Delivery": [(SMTP_EMAIL_SPOOFER_DISPLAY_NAME, SMTP_EMAIL_SPOOFER_NAME)],
    "Exploitation": [("None", "nmap")],
    "Installation": [("None", "nmap")],
    "Command and Control": [("None", "nmap")],
    "Action": [("None", "nmap")],
}

CONTROLLERS = {
    NMAP_SCAN_NAME: NmapController(),
    NMAP_VULN_NAME: NmapVulnController(),
    DIG_NAME: DigController(),
    THE_HARVESTER_NAME: TheHarvesterController(),
    FEROXBUSTER_NAME: FeroxbusterController(),
    W4AF_AUDIT_NAME: W4afAuditController(),
    SEARCH_EXPLOIT_NAME: SearchExploitController(),
    SMTP_EMAIL_SPOOFER_NAME: SmtpEmailSpooferController(),
}


def register_blueprints(app):
    l.info("Registering blueprints...")

    nmap_blueprint = BaseBlueprint(
        NMAP_SCAN_NAME,
        __name__,
        CONTROLLERS[NMAP_SCAN_NAME],
        NMAP_SCAN_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        nmap_scan_options,
        SECTIONS,
    )

    nmap_vuln_blueprint = BaseBlueprint(
        NMAP_VULN_NAME,
        __name__,
        CONTROLLERS[NMAP_VULN_NAME],
        NMAP_VULN_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        NMAP_VULN_RESULTS_TEMPLATE,
        nmap_vuln_scan_options,
        SECTIONS,
    )

    dig_blueprint = BaseBlueprint(
        DIG_NAME,
        __name__,
        CONTROLLERS[DIG_NAME],
        DIG_DISPLY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        dig_scan_options,
        SECTIONS,
    )

    the_harvester_blueprint = WebTargetBlueprint(
        THE_HARVESTER_NAME,
        __name__,
        CONTROLLERS[THE_HARVESTER_NAME],
        THE_HARVESTER_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        the_harvester_scan_options,
        SECTIONS,
    )

    feroxbuster_blueprint = WebTargetBlueprint(
        FEROXBUSTER_NAME,
        __name__,
        CONTROLLERS[FEROXBUSTER_NAME],
        FEROXBUSTER_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        feroxbuster_scan_options,
        SECTIONS,
    )

    w4af_audit_blueprint = W4afBlueprint(
        W4AF_AUDIT_NAME,
        __name__,
        CONTROLLERS[W4AF_AUDIT_NAME],
        W4AF_AUDIT_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        W4AF_RESULTS_TEMPLATE,
        w4af_audit_scan_options,
        SECTIONS,
    )

    search_exploit_blueprint = HeadlessBlueprint(
        SEARCH_EXPLOIT_NAME,
        __name__,
        CONTROLLERS[SEARCH_EXPLOIT_NAME],
        SEARCH_EXPLOIT_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        [],
        SECTIONS,
    )

    smtp_email_spoofer_blueprint = WebTargetBlueprint(
        SMTP_EMAIL_SPOOFER_NAME,
        __name__,
        CONTROLLERS[SMTP_EMAIL_SPOOFER_NAME],
        SMTP_EMAIL_SPOOFER_DISPLAY_NAME,
        SMTP_EMAIL_SPOOFER_INTERFACE_TEMPLATE,
        SMTP_EMAIL_SPOOFER_RESULTS_TEMPLATE,
        smtp_email_spoofer_scan_options,
        SECTIONS,
    )

    global BLUEPRINTS

    BLUEPRINTS = [
        nmap_blueprint,
        dig_blueprint,
        the_harvester_blueprint,
        feroxbuster_blueprint,
        nmap_vuln_blueprint,
        w4af_audit_blueprint,
        search_exploit_blueprint,
        smtp_email_spoofer_blueprint,
    ]

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

def create_app():
    app = Flask("red_team_knife", static_url_path="/static")
    register_blueprints(app)
    print('okay')
    return app