import html
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

        options = request.form.to_dict()

        target = options["target"]
        options.pop("target")


        return render_template(
            "the_harvester/the_harvester_results.html",
            target=target,
            sections=sections,
            options= json.dumps(options)
        )

    if CurrentScan.scan is not None:
        return render_template(
            "the_harvester/the_harvester_interface.html",
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
        "the_harvester/the_harvester_interface.html",
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
    target = request.json["target"]
    form = html.unescape(request.json["options"])
    options = remove_empty_values(json.loads(form))


    html_scan_result = the_harvester_controller.run(
        domain=target,
        options=options
    )

    return jsonify(html_scan_result)


@the_harvester_blueprint.route('/save_results', methods=["POST"])
def save_results():
    if CurrentScan.scan is not None:
        CurrentScan.scan.save_scan("theHarvester", the_harvester_controller.scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"




