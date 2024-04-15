from flask import *
from controllers.nmap import NmapController
import utils.hyperlink_constants as hyperlink_constants
from current_scan import CurrentScan


nmap_blueprint = Blueprint("nmap", __name__)
sections = hyperlink_constants.SECTIONS
nmap_controller = NmapController()


@nmap_blueprint.route("/", methods=["GET", "POST"])
def interface():
    # POST request means that either a scan is requested or a past scan needs to be restored
    if request.method == "POST":

        # check if a past scan needs to be restored
        load_previous_results = request.form.get("load_previous_results")

        if load_previous_results:
            if (
                CurrentScan.scan is not None
                and CurrentScan.scan.get_tool_scan("nmap")
            ):
                nmap_controller.last_scan_result = CurrentScan.scan.get_tool_scan(
                    "nmap"
                )

                return render_template(
                    "nmap/nmap_results.html",
                    sections=sections,
                    past_scan_available=True,
                    scan_result=nmap_controller.restore_last_scan(),
                )

        # a new scan was requested
        target = request.form.get("target")
        option = request.form.get("options")

        return render_template(
            "nmap/nmap_results.html",
            sections=sections,
            past_scan_available=False,
            scan_result="",
            target=target,
            options=option,
        )

    # GET request means we want to access scan interface
    # Check if current scan has a value
    if CurrentScan.scan is not None:
        
        # Check if a nmap scan is present in the current scan
        if CurrentScan.scan.get_tool_scan("nmap"):
            return render_template(
            "nmap/nmap_interface.html",
            sections=sections,
            past_scan_available=True,
            options_list=nmap_controller.scan_options,
            target=CurrentScan.scan.host,
        )

        return render_template(
            "nmap/nmap_interface.html",
            sections=sections,
            past_scan_available=False,
            options_list=nmap_controller.scan_options,
            target=CurrentScan.scan.host,
        )

    return render_template(
        "nmap/nmap_interface.html",
        sections=sections,
        options_list=nmap_controller.scan_options,
    )

# Endpoint used for AJAX requests to gather scan results
@nmap_blueprint.route("/results", methods=["POST"])
def results():
    target = request.form.get("target")
    options = request.form.get("options")

    html_scan_result = nmap_controller.run(target, options)
    return jsonify(html_scan_result)

# Endpoint used for AJAX requests to save scan results
@nmap_blueprint.route("/save_results", methods=["POST"])
def save_results():
    if CurrentScan.scan is not None:
        CurrentScan.scan.save_scan("nmap", nmap_controller.last_scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"
