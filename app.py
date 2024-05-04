import shutil
import subprocess
from flask import *
from controllers.nmap_scan import (
    NmapController,
    scan_options as nmap_scan_options,
    TOOL_DISPLAY_NAME as NMAP_SCAN_DISPLAY_NAME,
    TOOL_NAME as NMAP_SCAN_NAME,
)
from controllers.nmap_vuln import (
    NmapVulnController,
    script_options as nmap_vuln_script_options,
    TOOL_DISPLAY_NAME as NMAP_VULN_DISPLAY_NAME,
    TOOL_NAME as NMAP_VULN_NAME,
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
)
from controllers.search_exploit import (
    SearchExploitController,
    TOOL_DISPLAY_NAME as SEARCH_EXPLOIT_DISPLAY_NAME,
)

from models.scan import Scan
from utils import *
import os
from utils.html_format_util import render_scan_dictionary
from utils.log import debug_route
from views.view import BaseBlueprint
from views.headless_view import HeadlessBlueprint
from current_scan import CurrentScan
from views.w4af_audit.view import W4afBlueprint
import logging
from loguru import logger as l

SCANS_PATH = None
SCANS_FOLDER = "scans"
TEMP_FOLDER = "tmp"

INTERFACE_TEMPLATE = "interface_base.html"
RESULTS_TEMPLATE = "results_base.html"

W4AF_ADDRESS = "localhost"
W4AF_PORT = 5001

BLUEPRINTS = []

# TODO riempire con costanti
SECTIONS = {
    "Reconnaissance": [
        (NMAP_SCAN_DISPLAY_NAME, NMAP_SCAN_NAME),
        (THE_HARVESTER_DISPLAY_NAME, THE_HARVESTER_NAME),
        (FEROXBUSTER_DISPLAY_NAME, FEROXBUSTER_NAME),
    ],
    "Weaponization": [
        (W4AF_AUDIT_DISPLAY_NAME, W4AF_AUDIT_NAME),
        (NMAP_VULN_DISPLAY_NAME, NMAP_VULN_NAME),
    ],
    "Delivery": [("None", "nmap")],
    "Exploitation": [("None", "nmap")],
    "Installation": [("None", "nmap")],
    "Command and Control": [("None", "nmap")],
    "Action": [("None", "nmap")],
}

app = Flask("red_team_knife", static_url_path="/static")


def register_blueprints(app):
    l.info("Registering blueprints.")

    nmap_blueprint = BaseBlueprint(
        "nmap",
        __name__,
        NmapController(),
        NMAP_SCAN_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        nmap_scan_options,
        SECTIONS,
    )

    nmap_vuln_blueprint = BaseBlueprint(
        "nmap_vuln",
        __name__,
        NmapVulnController(),
        NMAP_VULN_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        "nmap_vuln/results.html",
        nmap_vuln_script_options,
        SECTIONS,
    )

    the_harvester_blueprint = BaseBlueprint(
        "the_harvester",
        __name__,
        TheHarvesterController(),
        THE_HARVESTER_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        the_harvester_scan_options,
        SECTIONS,
    )

    feroxbuster_blueprint = BaseBlueprint(
        "feroxbuster",
        __name__,
        FeroxbusterController(),
        FEROXBUSTER_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        feroxbuster_scan_options,
        SECTIONS,
    )

    w4af_audit_blueprint = W4afBlueprint(
        "w4af_audit",
        __name__,
        W4afAuditController(),
        W4AF_AUDIT_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        "w4af_audit/results.html",
        w4af_audit_scan_options,
        SECTIONS,
    )

    search_exploit_blueprint = HeadlessBlueprint(
        "search_exploit",
        __name__,
        SearchExploitController(),
        SEARCH_EXPLOIT_DISPLAY_NAME,
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        [],
        SECTIONS,
    )

    global BLUEPRINTS

    BLUEPRINTS = [
        nmap_blueprint,
        the_harvester_blueprint,
        feroxbuster_blueprint,
        nmap_vuln_blueprint,
        w4af_audit_blueprint,
        search_exploit_blueprint,
    ]

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)


# TODO permessi directory sudo
def create_folders():
    l.info("Creating folders.")

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


def start_w4af_server_api():
    l.info(f"Starting w4af server on {W4AF_ADDRESS}:{W4AF_PORT}.")
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
    W4AF_DIRECTORY = "w4af/"

    # Start the subprocess
    subprocess.Popen(
        W4AF_COMMAND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=W4AF_DIRECTORY,
    )


@app.context_processor
def utility_processor():
    return dict(render_dictionary=render_scan_dictionary)


@app.route("/")
def index():
    debug_route(request)

    if CurrentScan.scan is not None:
        scan = CurrentScan.scan.data_storage.__data__
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
    l.info("Executing setup.")
    start_w4af_server_api()
    create_folders()
    register_blueprints(app)

    app.run(debug=True, host="0.0.0.0")
