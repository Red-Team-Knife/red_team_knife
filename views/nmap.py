from flask import *
from controllers.nmap import NmapController
import utils.hyperlink_constants as hyperlink_constants
from current_scan import CurrentScan


nmap_blueprint = Blueprint('nmap', __name__)
sections = hyperlink_constants.SECTIONS
nmap_controller = NmapController()


# NMAP
@nmap_blueprint.route('/', methods=["GET", "POST"])
def interface():
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


    if CurrentScan.scan is not None:
            
        if CurrentScan.scan.get_tool_scan("nmap") is not None:
            return render_template(
                "nmap_interface.html",
                sections=sections,
                past_scan_available=True
            )
                 

        return render_template(
            "nmap_interface.html",
            sections=sections,
            options_list=nmap_controller.scan_options,
            target=CurrentScan.scan.host,
            hyperlink_constants=hyperlink_constants,
        )
    
    
    return render_template(
        "nmap_interface.html",
        sections=sections,
        options_list=nmap_controller.scan_options,
        hyperlink_constants=hyperlink_constants,
    )


@nmap_blueprint.route('/load_results', methods=["GET"])
def load_results():

    return render_template("nmap_results.html", 
                           sections= sections,
                           past_scan_available= True,
                           scan_result = jsonify()
                           )



@nmap_blueprint.route('/results', methods=["POST"])
def results():
    target = request.form.get("target")
    options = request.form.get("options")

    html_scan_result = nmap_controller.run(target, options)
    return jsonify(html_scan_result)


# TODO controllare a priori che non sia presente una scan in modo tale da non renderizzare direttamente il bottone di salvataggio
@nmap_blueprint.route('/save_results', methods=["POST"])
def save_results():
    if CurrentScan.scan is not None:
        CurrentScan.scan.save_scan("nmap", nmap_controller.last_scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"
