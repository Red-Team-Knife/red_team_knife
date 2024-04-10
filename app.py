from flask import *
import utils.hyperlink_constants as hyperlink_constants
from models.scan import Scan
from utils import *
import os
from utils.html_format_util import render_dictionary
from view.nmap import nmap_blueprint
from view.the_harvester import the_harvester_blueprint
from view.feroxbuster import feroxbuster_blueprint
from current_scan import CurrentScan


#TODO: implementare visualizzazione risultati di un tool già utilizzato anche in fase di re-click


app = Flask(__name__, static_url_path="/static")
app.register_blueprint(nmap_blueprint, url_prefix='/nmap')
app.register_blueprint(the_harvester_blueprint, url_prefix='/theHarvester')
app.register_blueprint(feroxbuster_blueprint, url_prefix='/feroxbuster')



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
