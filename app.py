from flask import *
from controllers.nmap import *
from controllers.the_harvester import *
from controllers.feroxbuster import *
from data_storage import DataStorage
import hyperlink_constants
from models.scan import Scan
from html_format_util import *
import os

app = Flask(__name__, static_url_path="/static")
nmap_controller = NmapController()
the_harvester_controller = TheHarvester()
feroxbuster_controller = Feroxbuster()
sections = hyperlink_constants.SECTIONS

current_scan = None

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
    global current_scan
    if current_scan is not None:
        scan = current_scan.data_storage.__data__
        return render_template(
            "index_scan.html", sections=sections, scan=scan, scan_name=scan["name"]
        )

    # List all saved scans
    scan_list = {}

    for scan_name in os.listdir(SCANS_PATH):
        scan = Scan(file_source=SCANS_PATH + "/" + scan_name)
        scan_list[scan_name] = scan.name

    return render_template("index.html", sections=sections, scan_list=scan_list)

@app.route("/test")
def test():
    out = feroxbuster_controller.run('kali.org', {TIME_LIMIT: '10s'})
    return render_template("test.html", out=out)

@app.route("/new_scan", methods=["POST", "GET"])
def new_scan():
    global current_scan

    # TODO fixare il redirect
    if request.method == "GET":
        current_scan = None
        return redirect(url_for("index"))

    scan_name = request.form.get("scan_name")
    scan_host = request.form.get("scan_host")

    current_scan = Scan(scan_name, scan_host, SCANS_PATH)

    return redirect(url_for("index"))


@app.route("/scan_detail", methods=["GET"])
def scan_detail():
    global current_scan
    scan_file_name = request.args.get("scan_file_name")
    current_scan = Scan(file_source=SCANS_PATH + "/" + scan_file_name)
    return redirect(url_for("index"))


# NMAP
@app.route(hyperlink_constants.LINK_NMAP_INTERFACE, methods=["GET", "POST"])
def nmap_interface():
    if request.method == "POST":
        target = request.form.get("target")
        option = request.form.get("options")

        return render_template(
            "nmap_results.html",
            target=target,
            options=option,
            sections=sections,
            hyperlink_constants=hyperlink_constants,
        )

    global current_scan
    if current_scan is not None:
        return render_template(
            "nmap_interface.html",
            sections=sections,
            options_list=nmap_controller.scan_options,
            target=current_scan.host,
            hyperlink_constants=hyperlink_constants,
        )
    return render_template(
        "nmap_interface.html",
        sections=sections,
        options_list=nmap_controller.scan_options,
        hyperlink_constants=hyperlink_constants,
    )


@app.route(hyperlink_constants.LINK_NMAP_RESULTS, methods=["POST"])
def nmap_results():
    target = request.form.get("target")
    options = request.form.get("options")

    html_scan_result = nmap_controller.run(target, options)
    return jsonify(html_scan_result)


# TODO controllare a priori che non sia presente una scan in modo tale da non renderizzare direttamente il bottone di salvataggio
@app.route(hyperlink_constants.LINK_NMAP_SAVE_RESULTS, methods=["POST"])
def nmap_save_results():
    global current_scan
    print(current_scan)
    if current_scan is not None:
        current_scan.save_scan("nmap", nmap_controller.last_scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"


# THE HARVESTER
@app.route(hyperlink_constants.LINK_THE_HARVESTER_INTERFACE, methods=["GET", "POST"])
def the_harvester_interface():
    if request.method == "POST":

        target = request.form.get("target")

        return render_template(
            "the_harvester_results.html",
            target=target,
            sections=sections,
            hyperlink_constants=hyperlink_constants,
            source=request.form.get(SOURCE),
            result_limit=request.form.get(LIMIT),
            result_limit_enable=request.form.get(LIMIT_ENABLE),
            offset=request.form.get(OFFSET),
            proxy=request.form.get(PROXY),
            dns_bruteforce=request.form.get(DNS_BRUTEFORCE),
            dns_lookup=request.form.get(DNS_LOOKUP),
            dns_resolution_virtual_hosts=request.form.get(DNS_RESOLUTION),
            dns_server=request.form.get(DNS_SERVER),
            screenshot=request.form.get(SCREENSHOT),
            shodan=request.form.get(SHODAN),
            subdomain_resolution=request.form.get(SUBDOMAIN_RESOLUTION),
            takeover_check=request.form.get(TAKEOVER_CHECK),
        )

    global current_scan
    if current_scan is not None:
        return render_template(
            "the_harvester_interface.html",
            sections=sections,
            target=current_scan.host,
            LIMIT=LIMIT,
            LIMIT_ENABLE=LIMIT_ENABLE,
            OFFSET=OFFSET,
            PROXY=PROXY,
            SHODAN=SHODAN,
            SCREENSHOT=SCREENSHOT,
            DNS_RESOLUTION=DNS_RESOLUTION,
            DNS_SERVER=DNS_SERVER,
            TAKEOVER_CHECK=TAKEOVER_CHECK,
            SUBDOMAIN_RESOLUTION=SUBDOMAIN_RESOLUTION,
            DNS_LOOKUP=DNS_LOOKUP,
            DNS_BRUTEFORCE=DNS_BRUTEFORCE,
            SOURCE=SOURCE,
        )
    return render_template(
        "the_harvester_interface.html",
        sections=sections,
        LIMIT=LIMIT,
        LIMIT_ENABLE=LIMIT_ENABLE,
        OFFSET=OFFSET,
        PROXY=PROXY,
        SHODAN=SHODAN,
        SCREENSHOT=SCREENSHOT,
        DNS_RESOLUTION=DNS_RESOLUTION,
        DNS_SERVER=DNS_SERVER,
        TAKEOVER_CHECK=TAKEOVER_CHECK,
        SUBDOMAIN_RESOLUTION=SUBDOMAIN_RESOLUTION,
        DNS_LOOKUP=DNS_LOOKUP,
        DNS_BRUTEFORCE=DNS_BRUTEFORCE,
        SOURCE=SOURCE,
    )


@app.route(hyperlink_constants.LINK_THE_HARVESTER_RESULTS, methods=["POST"])
def the_harvester_results():
    target = request.form.get("target")

    limit = ""

    if request.form.get(LIMIT_ENABLE) == "on":
        limit = request.form.get(LIMIT)

    html_scan_result = the_harvester_controller.run(
        domain=target,
        source=request.form.get(SOURCE),
        result_limit=limit,
        offset=request.form.get(OFFSET),
        proxy=request.form.get(PROXY),
        dns_bruteforce=request.form.get(DNS_BRUTEFORCE),
        dns_lookup=request.form.get(DNS_LOOKUP),
        dns_resolution_virtual_hosts=request.form.get(DNS_RESOLUTION),
        dns_server=request.form.get(DNS_SERVER),
        screenshot=request.form.get(SCREENSHOT),
        shodan=request.form.get(SHODAN),
        subdomain_resolution=request.form.get(SUBDOMAIN_RESOLUTION),
        takeover_check=request.form.get(TAKEOVER_CHECK),
    )
    return jsonify(html_scan_result)


@app.route(hyperlink_constants.LINK_THE_HARVESTER_SAVE_RESULTS, methods=["POST"])
def the_harvester_save_results():
    global current_scan

    if current_scan is not None:
        current_scan.save_scan("theHarvester", the_harvester_controller.scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
