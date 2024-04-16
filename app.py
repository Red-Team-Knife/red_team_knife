from flask import *
from controllers.nmap import NmapController, scan_options as nmap_scan_options
from controllers.the_harvester import (
    TheHarvesterController,
    scan_options as the_harvester_scan_options,
)
from controllers.feroxbuster import (
    FeroxbusterController,
    scan_options as feroxbuster_scan_options,
)
import utils.hyperlink_constants as hyperlink_constants
from models.scan import Scan
from utils import *
import os
from utils.html_format_util import render_dictionary
from views.nmap import nmap_blueprint
from views.the_harvester import the_harvester_blueprint
from views.feroxbuster import feroxbuster_blueprint
from views.view import BaseBlueprint
from current_scan import CurrentScan
import controllers

app = Flask(__name__, static_url_path="/static")


nmap_blueprint = BaseBlueprint(
    "nmap",
    __name__,
    NmapController(),
    "Nmap",
    "nmap/interface.html",
    "nmap/results.html",
    nmap_scan_options,
)

the_harvester_blueprint = BaseBlueprint(
    "the_harvester",
    __name__,
    TheHarvesterController(),
    "theHarvester",
    "the_harvester/interface.html",
    "the_harvester/results.html",
    the_harvester_scan_options,
)

feroxbuster_blueprint = BaseBlueprint(
    "feroxbuster",
    __name__,
    FeroxbusterController(),
    "Feroxbuster",
    "feroxbuster/interface.html",
    "feroxbuster/results.html",
    feroxbuster_scan_options,
)
app.register_blueprint(nmap_blueprint)
app.register_blueprint(the_harvester_blueprint)
app.register_blueprint(feroxbuster_blueprint)

sections = hyperlink_constants.SECTIONS


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
