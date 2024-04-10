from flask import *
from controllers.the_harvester import *
import utils.hyperlink_constants as hyperlink_constants
from current_scan import CurrentScan

the_harvester_blueprint = Blueprint('theHarvester', __name__)
sections = hyperlink_constants.SECTIONS
the_harvester_controller = TheHarvester()


# THE HARVESTER
@the_harvester_blueprint.route('/',  methods=["GET", "POST"])
def interface():
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

    if CurrentScan.scan is not None:
        return render_template(
            "the_harvester_interface.html",
            sections=sections,
            target=CurrentScan.scan.host,
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


@the_harvester_blueprint.route('/results', methods=["POST"])
def results():
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


@the_harvester_blueprint.route('/save_results', methods=["POST"])
def save_results():
    if CurrentScan.scan is not None:
        CurrentScan.scan.save_scan("theHarvester", the_harvester_controller.scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"




