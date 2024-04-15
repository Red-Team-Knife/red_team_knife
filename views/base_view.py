from flask import Blueprint, request, render_template, jsonify
from controllers.nmap import NmapController
import utils.hyperlink_constants as hyperlink_constants
from current_scan import CurrentScan

# TODO make controller class to inherit and put hint in init signature
class BaseBlueprint(Blueprint):
    def __init__(self, name, import_name, controller, tool_name:str, interface_template:str, results_template:str, options_list:list):
        super().__init__(name, import_name, url_prefix='/'+tool_name)
        self.sections = hyperlink_constants.SECTIONS
        self.controller = controller
        self.tool_name = tool_name
        self.interface_template = interface_template
        self.results_template = results_template
        self.options_list = options_list

        self.route("/", methods=["GET", "POST"])(self.interface)
        self.route("/results", methods=["POST"])(self.results)
        self.route("/save_results", methods=["POST"])(self.save_results)

    def interface(self):
        # POST request means that either a scan is requested or a past scan needs to be restored
        if request.method == "POST":

            # check if a past scan needs to be restored
            load_previous_results = request.form.get("load_previous_results")

            if load_previous_results:
                if CurrentScan.scan is not None and CurrentScan.scan.get_tool_scan(
                    self.tool_name
                ):
                    self.controller.last_scan_result = CurrentScan.scan.get_tool_scan(
                        self.tool_name
                    )

                    return render_template(
                        self.results_template,
                        sections=self.sections,
                        past_scan_available=True,
                        scan_result=self.controller.restore_last_scan(),
                    )

            # a new scan was requested
            target = request.form.get("target")
            option = request.form.get("options")

            return render_template(
                self.results_template,
                sections=self.sections,
                past_scan_available=False,
                scan_result="",
                target=target,
                options=option,
            )

        # GET request means we want to access scan interface
        # Check if current scan has a value
        if CurrentScan.scan is not None:

            # Check if a nmap scan is present in the current scan
            if CurrentScan.scan.get_tool_scan(self.tool_name):
                return render_template(
                    self.interface_template,
                    sections=self.sections,
                    past_scan_available=True,
                    target=CurrentScan.scan.host,
                    options_list=self.options_list
                )

            return render_template(
                self.interface_template,
                sections=self.sections,
                past_scan_available=False,
                target=CurrentScan.scan.host,
                options_list=self.options_list
            )

        return render_template(
            self.interface_template,
            sections=self.sections,
            options_list=self.options_list
        )

    def results(self):
        target = request.form.get("target")
        options = request.form.get("options")

        html_scan_result = self.controller.run(target, options)
        return jsonify(html_scan_result)

    def save_results(self):
        if CurrentScan.scan is not None:
            CurrentScan.scan.save_scan(self.tool_name, self.controller.last_scan_result)
            return "<p>Results successfully saved.</p>"
        return "<p>No scan started.</p>"
