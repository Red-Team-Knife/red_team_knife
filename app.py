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
from controllers.sqlmap import(
    SqlmapController,
    scan_options as sqlmap_scan_options,
    TOOL_DISPLAY_NAME as SQLMAP_DISPLAY_NAME,
    TOOL_NAME as SQLMAP_NAME,
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
    "Exploitation": [(SQLMAP_DISPLAY_NAME, SQLMAP_NAME)],
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
    SQLMAP_NAME: SqlmapController(),
}

app = Flask("red_team_knife", static_url_path="/static")


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
    
    sqlmap_blueprint = BaseBlueprint(
        SQLMAP_NAME,
        __name__,
        CONTROLLERS[SQLMAP_NAME],
        SQLMAP_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        sqlmap_scan_options,
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
        sqlmap_blueprint
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

    REPORTS_PATH = os.path.abspath(REPORTS_FOLDER)
    if not os.path.exists(REPORTS_PATH):
        os.makedirs(REPORTS_FOLDER)
        os.path.abspath(REPORTS_PATH)

    TEMP_PATH = os.path.abspath(TEMP_FOLDER)
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_FOLDER)
        os.path.abspath(TEMP_PATH)
    else:
        shutil.rmtree(TEMP_FOLDER)
        os.makedirs(TEMP_FOLDER)

    os.chmod(SCANS_FOLDER, 0o777)
    os.chmod(TEMP_FOLDER, 0o777)
    os.chmod(REPORTS_FOLDER, 0o777)


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


@app.route("/generate_report", methods=["GET"])
def generate_report():
    debug_route(request)
    if not CurrentScan.scan:
        redirect(url_for("index"))
    scan = CurrentScan.scan
    date = datetime.datetime.now().date()
    time = datetime.datetime.now().time()
    report_folder = f"reports/{str(date)+str(time)}"

    os.mkdir(report_folder)
    os.chmod(report_folder, 0o777)
    for key in scan.data_storage.data:
        if key in CONTROLLERS.keys():
            file_path = f"{report_folder}/{key}.html"
            with open(file_path, "w") as file:
                CONTROLLERS[key].last_scan_result = CurrentScan.scan.get_tool_scan(key)
                print(CONTROLLERS[key].get_formatted_results(), file=file)
                CONTROLLERS[key].last_scan_result = None
            os.chmod(file_path, 0o777)

    return f"Report generated in {report_folder}"


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
    
    app.run(host="0.0.0.0", debug="True")


