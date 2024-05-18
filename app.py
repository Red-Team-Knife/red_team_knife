from datetime import time
import datetime
import shutil
import subprocess
import sys
import colorama
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
from controllers.smtp_email_spoofer import (
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
from controllers.sqlmap import (
    SqlmapController,
    scan_options as sqlmap_scan_options,
    TOOL_DISPLAY_NAME as SQLMAP_DISPLAY_NAME,
    TOOL_NAME as SQLMAP_NAME,
)
from controllers.exploitation_tips import (
    EXPLOITATION_TIPS_DISPLAY_NAME,
    EXPLOITATION_TIPS_NAME,
)
from controllers.commix import (
    CommixController,
    scan_option as commix_scan_options,
    TOOL_DISPLAY_NAME as COMMIX_DISPLAY_NAME,
    TOOL_NAME as COMMIX_NAME,
)
from controllers.installation_tips import(
    INSTALLATION_TIPS_DISPLAY_NAME,
    INSTALLATION_TIPS_NAME
)

from controllers.command_and_control_tips import(
    COMMAND_AND_CONTROL_TIPS_DISPLAY_NAME,
    COMMAND_AND_CONTROL_TIPS_NAME,
)

from controllers.action_tips import(
    ACTION_TIPS_DISPLAY_NAME,
    ACTION_TIPS_NAME
)

from models.scan import Scan
from utils import *
import os
from utils.utils import (
    render_dictionary_as_table,
    render_scan_dictionary,
    debug_route,
)
from views.domain_name_target_view import DomainNameTargetBlueprint
from views.nmap_vuln.view import NmapVulnBlueprint
from views.tips_page_view import TipsPageBlueprint
from views.view import BaseBlueprint
from views.headless_view import HeadlessBlueprint
from views.web_target_view import WebTargetBlueprint
from models.current_scan import CurrentScan
from views.w4af_audit.view import W4afBlueprint
from views.nmap.view import NmapBlueprint
from views.the_harvester.view import TheHarvesterBlueprint
import logging
from loguru import logger as l

SCANS_PATH = None
SCANS_FOLDER = "scans"
TEMP_FOLDER = "tmp"

INTERFACE_TEMPLATE = "interface_scan_target.html"
RESULTS_TEMPLATE = "results_base.html"

NMAP_VULN_RESULTS_TEMPLATE = "nmap_vuln/results.html"
W4AF_RESULTS_TEMPLATE = "w4af_audit/results.html"
SMTP_EMAIL_SPOOFER_INTERFACE_TEMPLATE = "smtp_email_spoofer/interface.html"
SMTP_EMAIL_SPOOFER_RESULTS_TEMPLATE = "smtp_email_spoofer/results.html"
NMAP_RESULTS_TEMPLATE = "nmap/results.html"
THE_HARVESTER_RESULTS_TEMPLATE = "the_harvester/results.html"


EXPLOITATION_TIPS_TEMPLATE = "exploitation/tips.html"
INSTALLATION_TIPS_TEMPLATE = "installation/tips.html"
COMMAND_AND_CONTROL_TIPS_TEMPLATE = "command_and_control/tips.html"
ACTION_TIPS_TEMPLATE = "action/tips.html"

W4AF_ADDRESS = "localhost"
W4AF_PORT = 5001

BANNER = r"""
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

  %%########################%%  
 ############################## 
%###:++++++++++++++++++++++:###%
%###:######################:###%
%###:####+=----------=+####:###%
%###:###+--------------+###:###%
%###:###=---=------=---=###-###%
%###-###=-@@@@@--@@@@@-=##+-###%
%###==##=-@@@@*--@@@@+-=##-*###%
%####:##+------#=------+##:####%
%####:#+-------@@-------**-####%
%####+-#+--------------+#:#####%
%#####-*####--:-:-:+####-=#####%
%######:+##############-=######%
%#######+:*##########-:########%
%##########*-::::::=###########%
  %%########################%%  

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
    "Exploitation": [
        (SQLMAP_DISPLAY_NAME, SQLMAP_NAME),
        (EXPLOITATION_TIPS_DISPLAY_NAME, EXPLOITATION_TIPS_NAME),
        (COMMIX_DISPLAY_NAME, COMMIX_NAME),
    ],
    "Installation": [(INSTALLATION_TIPS_DISPLAY_NAME, INSTALLATION_TIPS_NAME)],
    "Command and Control": [(COMMAND_AND_CONTROL_TIPS_DISPLAY_NAME, COMMAND_AND_CONTROL_TIPS_NAME)],
    "Action": [(ACTION_TIPS_DISPLAY_NAME, ACTION_TIPS_NAME)],
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
    SQLMAP_NAME: SqlmapController(),
    COMMIX_NAME: CommixController(),
}

app = Flask("red_team_knife", static_url_path="/static")


def register_blueprints(app):
    l.info("Registering blueprints...")

    nmap_blueprint = NmapBlueprint(
        NMAP_SCAN_NAME,
        __name__,
        CONTROLLERS[NMAP_SCAN_NAME],
        NMAP_SCAN_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        NMAP_RESULTS_TEMPLATE,
        nmap_scan_options,
        SECTIONS,
    )

    nmap_vuln_blueprint = NmapVulnBlueprint(
        NMAP_VULN_NAME,
        __name__,
        CONTROLLERS[NMAP_VULN_NAME],
        NMAP_VULN_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        NMAP_VULN_RESULTS_TEMPLATE,
        nmap_vuln_scan_options,
        SECTIONS,
    )

    dig_blueprint = DomainNameTargetBlueprint(
        DIG_NAME,
        __name__,
        CONTROLLERS[DIG_NAME],
        DIG_DISPLY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        dig_scan_options,
        SECTIONS,
    )

    the_harvester_blueprint = TheHarvesterBlueprint(
        THE_HARVESTER_NAME,
        __name__,
        CONTROLLERS[THE_HARVESTER_NAME],
        THE_HARVESTER_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        THE_HARVESTER_RESULTS_TEMPLATE,
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

    sqlmap_blueprint = WebTargetBlueprint(
        SQLMAP_NAME,
        __name__,
        CONTROLLERS[SQLMAP_NAME],
        SQLMAP_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        sqlmap_scan_options,
        SECTIONS,
    )

    commix_blueprint = WebTargetBlueprint(
        COMMIX_NAME,
        __name__,
        CONTROLLERS[COMMIX_NAME],
        COMMIX_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        commix_scan_options,
        SECTIONS,
    )

    exploitation_tips_blueprint = TipsPageBlueprint(
        EXPLOITATION_TIPS_NAME,
        __name__,
        EXPLOITATION_TIPS_TEMPLATE,
        SECTIONS,
        EXPLOITATION_TIPS_DISPLAY_NAME,
        INSTALLATION_TIPS_NAME,
    )
    
    installation_tips_blueprint = TipsPageBlueprint(
        INSTALLATION_TIPS_NAME,
        __name__,
        INSTALLATION_TIPS_TEMPLATE,
        SECTIONS,
        INSTALLATION_TIPS_DISPLAY_NAME,
        COMMAND_AND_CONTROL_TIPS_NAME,
    )
    
    command_and_control_tips_blueprint = TipsPageBlueprint(
        COMMAND_AND_CONTROL_TIPS_NAME,
        __name__,
        COMMAND_AND_CONTROL_TIPS_TEMPLATE,
        SECTIONS,
        COMMAND_AND_CONTROL_TIPS_DISPLAY_NAME,
        ACTION_TIPS_NAME,
    )
    
    action_tips_blueprint = TipsPageBlueprint(
        ACTION_TIPS_NAME,
        __name__,
        ACTION_TIPS_TEMPLATE,
        SECTIONS,
        ACTION_TIPS_DISPLAY_NAME,
        None,
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
        sqlmap_blueprint,
        commix_blueprint,
        exploitation_tips_blueprint,
        installation_tips_blueprint,
        command_and_control_tips_blueprint,
        action_tips_blueprint,
    ]

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)


def create_folders():
    l.info("Creating folders...")

    global SCANS_PATH

    SCANS_PATH = os.path.abspath(SCANS_FOLDER)
    if not os.path.exists(SCANS_PATH):
        os.makedirs(SCANS_FOLDER)
        os.path.abspath(SCANS_PATH)

    TEMP_PATH = os.path.abspath(TEMP_FOLDER)
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_FOLDER)
        os.path.abspath(TEMP_PATH)
    else:
        shutil.rmtree(TEMP_FOLDER)
        os.makedirs(TEMP_FOLDER)

    os.chmod(SCANS_FOLDER, 0o777)
    os.chmod(TEMP_FOLDER, 0o777)


def start_w4af_server_api():
    l.info(f"Starting w4af server on {W4AF_ADDRESS}:{W4AF_PORT}...")
    # Start w4af api server

    W4AF_COMMAND = [
        "pipenv",
        "run",
        "./w4af_api",
        "--i-am-a-developer",
        "--no-ssl",
        f"{W4AF_ADDRESS}:{W4AF_PORT}",
    ]

    # Define the directory to change to

    # Start the subprocess
    subprocess.Popen(
        W4AF_COMMAND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=W4AF_DIRECTORY,
    )


def check_tools_exist():
    """
    Check if "w4af" and "smtp-email-spoofer-py" exist in the tools folder.

    Returns:
        bool: True if both tools exist, False otherwise.
    """
    l.info("Checking tools installation...")
    tools_folder = "tools"

    # Check if both tools exist
    w4af_exists = os.path.exists(os.path.join(tools_folder, "w4af"))
    smtp_email_spoofer_py_exists = os.path.exists(
        os.path.join(tools_folder, "smtp-email-spoofer-py")
    )

    return w4af_exists and smtp_email_spoofer_py_exists


@app.context_processor
def utility_processor():
    return dict(render_dictionary=render_scan_dictionary)


@app.route("/")
def index():
    debug_route(request)

    if CurrentScan.scan is not None:
        scan = CurrentScan.scan.data_storage.data
        return render_template(
            "index_scan.html", sections=SECTIONS, scan=scan, scan_name=scan["name"]
        )

    # List all saved scans
    scan_list = {}

    for scan_name in os.listdir(SCANS_PATH):
        scan = Scan(file_source=SCANS_PATH + "/" + scan_name)
        scan_list[scan_name] = scan.name

    return render_template("index.html", sections=SECTIONS, scan_list=scan_list)


@app.route("/new_scan", methods=["POST", "GET"])
def new_scan():
    debug_route(request)

    if request.method == "GET":
        CurrentScan.scan = None
        return redirect(url_for("index"))

    scan_name = request.form.get("scan_name")
    scan_host = request.form.get("scan_host")
    scan_protocol = request.form.get("protocol_radio")
    scan_resource = request.form.get("scan_resource")

    CurrentScan.scan = Scan(
        scan_name, scan_host, scan_protocol, scan_resource, SCANS_PATH
    )

    return redirect(url_for("index"))


@app.route("/scan_detail", methods=["GET"])
def scan_detail():
    debug_route(request)

    scan_file_name = request.args.get("scan_file_name")
    CurrentScan.scan = Scan(file_source=SCANS_PATH + "/" + scan_file_name)
    return redirect(url_for("index"))


@app.route("/tmp/<path:filename>")
def temp_file(filename):
    debug_route(request)

    print(url_for("temp_file", filename="test"))
    filepath = os.path.join(TEMP_FOLDER, filename)

    # Check if the file exists
    if os.path.isfile(filepath):
        # Serve the file
        return send_from_directory(TEMP_FOLDER, filename)
    else:
        # File not found
        return "File not found", 404


# Disable Flask's built-in logging
log = logging.getLogger("werkzeug")
log.disabled = True

if __name__ == "__main__":
    l.remove()
    l.add(sys.stdout, level="INFO")

    l.info("Executing setup...")
    if not check_tools_exist():
        l.critical("Tools not installed properly!")
        l.critical("Clone w4af and smtp-email-spoofer-py inside the tools folder.")
        sys.exit()
    start_w4af_server_api()
    create_folders()
    register_blueprints(app)

    print(colorama.Fore.RED)
    print(BANNER)
    print(colorama.Style.RESET_ALL)
    setup_executed = True

    app.run(host="0.0.0.0")
