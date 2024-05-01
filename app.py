import shutil
import subprocess
from flask import *
from controllers.nmap_scan import (
    NmapController,
    scan_options as nmap_scan_options,
)
from controllers.nmap_vuln import (
    NmapVulnController,
    script_options as nmap_vuln_script_options,
)
from controllers.the_harvester import (
    TheHarvesterController,
    scan_options as the_harvester_scan_options,
)
from controllers.feroxbuster import (
    FeroxbusterController,
    scan_options as feroxbuster_scan_options,
)
from controllers.w4af_audit import (
    W4afAuditController,
    scan_options as w4af_audit_scan_options,
)
from controllers.searchexploit import SearchsploitController

from models.scan import Scan
from utils import *
import os
from utils.html_format_util import render_dictionary
from views.view import BaseBlueprint
from views.searchslpoit.headless_view import HeadlessBlueprint
from current_scan import CurrentScan
from views.w4af_audit.view import W4afBlueprint

app = Flask(__name__, static_url_path="/static")

#TODO centrare il titolo nella finestra ridimensionata

SCANS_PATH = None
SCANS_FOLDER = "scans"
TEMP_FOLDER = "tmp"

INTERFACE_TEMPLATE = "interface_base.html"
RESULTS_TEMPLATE = "results_base.html"

BLUEPRINTS = []

SECTIONS = {
    "Reconnaissance": [
        ("Nmap", "nmap"),
        ("theHarvester", "the_harvester"),
        ("Feroxbuster", "feroxbuster"),
    ],
    "Weaponization": [("w4af-Audit", "w4af_audit"), ("Nmap-Vuln Scanner", "nmap_vuln")],
    "Delivery": [("None", "nmap")],
    "Exploitation": [("None", "nmap")],
    "Installation": [("None", "nmap")],
    "Command and Control": [("None", "nmap")],
    "Action": [("None", "nmap")],
}


def register_blueprints(app):
    nmap_blueprint = BaseBlueprint(
        "nmap",
        __name__,
        NmapController(),
        "Nmap",
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        nmap_scan_options,
        SECTIONS,
    )

    nmap_vuln_blueprint = BaseBlueprint(
        "nmap_vuln",
        __name__,
        NmapVulnController(),
        "Nmap-Vuln Scanner",
        INTERFACE_TEMPLATE,
        "nmap_vuln/results.html",
        nmap_vuln_script_options,
        SECTIONS,
    )

    the_harvester_blueprint = BaseBlueprint(
        "the_harvester",
        __name__,
        TheHarvesterController(),
        "theHarvester",
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        the_harvester_scan_options,
        SECTIONS,
    )

    feroxbuster_blueprint = BaseBlueprint(
        "feroxbuster",
        __name__,
        FeroxbusterController(),
        "Feroxbuster",
        INTERFACE_TEMPLATE,
        RESULTS_TEMPLATE,
        feroxbuster_scan_options,
        SECTIONS,
    )

    w4af_audit_blueprint = W4afBlueprint(
        "w4af_audit",
        __name__,
        W4afAuditController(),
        "w4af_audit",
        INTERFACE_TEMPLATE,
        "w4af_audit/results.html",
        w4af_audit_scan_options,
        SECTIONS,
    )

    searchsploit_blueprint = HeadlessBlueprint(
        "searchsploit",
        __name__,
        SearchsploitController(),
        "Searchsploit",
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
        searchsploit_blueprint,
    ]

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

# TODO permessi directory sudo
def create_folders():
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
    # Start w4af api server
    W4AF_PORT = 5001
    W4AF_COMMAND = [
        "pipenv",
        "run",
        "./w4af_api",
        "--i-am-a-developer",
        "--no-ssl",
        f"localhost:{W4AF_PORT}",
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
    return dict(render_dictionary=render_dictionary)

# TODO semplificare visualizzazione scan
@app.route("/")
def index():

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

    # TODO fixare il redirect
    if request.method == "GET":
        CurrentScan.scan = None
        return redirect(url_for("index"))

    scan_name = request.form.get("scan_name")
    scan_host = request.form.get("scan_host")

    CurrentScan.scan = Scan(scan_name, scan_host, SCANS_PATH)

    return redirect(url_for("index"))


@app.route("/scan_detail", methods=["GET"])
def scan_detail():
    scan_file_name = request.args.get("scan_file_name")
    CurrentScan.scan = Scan(file_source=SCANS_PATH + "/" + scan_file_name)
    return redirect(url_for("index"))


# Execute setup functions
start_w4af_server_api()
create_folders()
register_blueprints(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
