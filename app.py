from flask import *
from controllers.nmap_thread import (
    NmapController,
    scan_options as nmap_scan_options,
)
from controllers.the_harvester_thread import (
    TheHarvesterController,
    scan_options as the_harvester_scan_options,
)
from controllers.feroxbuster_thread import (
    FeroxbusterController,
    scan_options as feroxbuster_scan_options,
)
'''
from controllers.w4af_audit import (
    W4afAuditController,
    scan_options as w4af_audit_scan_options,
)
'''
import utils.hyperlink_constants as hyperlink_constants
from models.scan import Scan
from utils import *
import os
from utils.html_format_util import render_dictionary
from views.view import BaseBlueprint
from views.view_thread import BaseBlueprint as BPT
from current_scan import CurrentScan

app = Flask(__name__, static_url_path="/static")

#TODO creare cartella tmp ad inizio esecuzione

sections = {
    "Reconnaissance": [
        ("Nmap", 'nmap'),
        ("theHarvester", 'the_harvester'),
        ("Feroxbuster", 'feroxbuster'),
    ],
    "Weaponization": [("w4af-Audit", "nmap")],
    "Delivery": [("None", "nmap")],
    "Exploitation": [("None", "nmap")],
    "Installation": [("None", "nmap")],
    "Command and Control": [("None", "nmap")],
    "Action": [("None", "nmap")],
}



nmap_blueprint = BPT(
    "nmap",
    __name__,
    NmapController(),
    "Nmap",
    "interface_base.html",
    "results_base_thread.html",
    nmap_scan_options,
    sections
)

the_harvester_blueprint = BPT(
    "the_harvester",
    __name__,
    TheHarvesterController(),
    "theHarvester",
    "interface_base.html",
    "results_base_thread.html",
    the_harvester_scan_options,
    sections,
)

feroxbuster_blueprint = BPT(
    "feroxbuster",
    __name__,
    FeroxbusterController(),
    "Feroxbuster",
    "interface_base.html",
    "results_base_thread.html",
    feroxbuster_scan_options,
    sections,
)
'''
w4af_audit_blueprint = BaseBlueprint(
    "w4af_audit",
    __name__,
    W4afAuditController(),
    "w4af_audit",
    "w4af_audit/interface.html",
    "w4af_audit/results.html",
    w4af_audit_scan_options,
)
'''
app.register_blueprint(nmap_blueprint)
app.register_blueprint(the_harvester_blueprint)
app.register_blueprint(feroxbuster_blueprint)
#app.register_blueprint(w4af_audit_blueprint)

ROOT_FOLDER = "scans"
SCANS_PATH = os.path.abspath(ROOT_FOLDER)
if not os.path.exists(SCANS_PATH):
    os.makedirs(ROOT_FOLDER)
    os.path.abspath(SCANS_PATH)


@app.context_processor
def utility_processor():
    return dict(render_dictionary=render_dictionary)


# INDEX
@app.route("/")
def index():

    if CurrentScan.scan is not None:
        scan = CurrentScan.scan.data_storage.__data__
        return render_template(
            "index_scan.html", sections=sections, scan=scan, scan_name=scan["name"]
        )

    # List all saved scans
    scan_list = {}

    for scan_name in os.listdir(SCANS_PATH):
        scan = Scan(file_source=SCANS_PATH + "/" + scan_name)
        scan_list[scan_name] = scan.name

    return render_template("index.html", sections=sections, scan_list=scan_list)


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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
