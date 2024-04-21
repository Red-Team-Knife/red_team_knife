import html
import json
from flask import Blueprint, request, render_template, jsonify, url_for
from utils.dictionary import remove_empty_values
from current_scan import CurrentScan
from controllers.controller_thread import Controller


class BaseBlueprint(Blueprint):
    def __init__(
        self,
        name,
        import_name,
        controller: Controller,
        tool_name: str,
        interface_template: str,
        results_template: str,
        options_list: list,
        sections: dict,
    ):
        super().__init__(name, import_name, url_prefix="/" + tool_name)
        self.sections = sections
        self.controller = controller
        self.tool_name = tool_name
        self.interface_template = interface_template
        self.results_template = results_template
        self.options_list = options_list

        self.route("/", methods=["GET", "POST"])(self.interface)
        self.route("/results", methods=["GET"])(self.results)
        self.route("/save_results", methods=["POST"])(self.save_results)
        self.route("/scan_in_progress", methods=["GET"])(self.is_scan_in_progress)
        self.route("/stop_scan", methods=["GET"])(self.stop_scan)

    def interface(self):
        if request.method == "POST":
            return self.get_interface_page_for_post_request(request)
        return self.get_interface_page_for_get_request()

    # GET request means we want to access scan interface.
    # An unsaved scan result could be present, in that case it will be shown,
    # giving the opportunity to save it or to request a new scan (reset page).

    def get_interface_page_for_get_request(self):
        no_scan_started = CurrentScan.scan is None

        print('no scan started', no_scan_started)
        # Check if a scan is already in progress

        if self.controller.is_scan_in_progress:
            return render_template(
                self.results_template,
                sections=self.sections,
                past_scan_available=False,
                scan_result="",
                save_disabled=no_scan_started,
                current_section=self.name,
                tool=self.tool_name,
            )

        # Check if an unsaved scan is still stored
        if self.controller.last_scan_result:
            return render_template(
                self.results_template,
                sections=self.sections,
                past_scan_available=True,
                save_disabled=no_scan_started,
                scan_result=self.controller.get_formatted_results(),
                current_section=self.name,
                tool=self.tool_name,
            )

        # Check if current scan has a value
        if CurrentScan.scan is not None:

            # Check if a tool scan is present in the current scan
            if CurrentScan.scan.get_tool_scan(self.tool_name):
                return render_template(
                    self.interface_template,
                    sections=self.sections,
                    past_scan_available=True,
                    target=CurrentScan.scan.host,
                    options_list=self.options_list,
                    tool=self.tool_name,
                )

            # Tool scan is not present, we only pass the target
            return render_template(
                self.interface_template,
                sections=self.sections,
                past_scan_available=False,
                target=CurrentScan.scan.host,
                options_list=self.options_list,
                tool=self.tool_name,
            )

        # No scan has been started
        return render_template(
            self.interface_template,
            sections=self.sections,
            options_list=self.options_list,
            tool=self.tool_name,
        )

    # POST request means that either:
    #   - a new scan (page reset) is requested
    #   - a scan is requested (run scan)
    #   - a past scan needs to be restored

    def get_interface_page_for_post_request(self, request):

        # Check if a new scan (page reset) was requested
        if request.form.get("new_scan_requested"):
            self.controller.last_scan_result = None
            return self.get_interface_page_for_get_request()

        # Check if a past scan needs to be restored
        if request.form.get("load_previous_results"):
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
                    save_disabled=True,
                    scan_result=self.controller.restore_last_scan(),
                    current_section=self.name,
                    tool=self.tool_name,
                )

        # A scan was requested (run scan)
        options = request.form.to_dict()
        print(options)

        target = options["target"]
        options.pop("target")

        self.controller.run(target, options)

        no_scan_started = CurrentScan.scan is None

        return render_template(
            self.results_template,
            sections=self.sections,
            past_scan_available=False,
            save_disabled=no_scan_started,
            scan_result="",
            target=target,
            options=json.dumps(options),
            current_section=self.name,
            tool=self.tool_name,
        )

    def is_scan_in_progress(self):
        return jsonify({"scan_in_progress": self.controller.is_scan_in_progress})

    def results(self):
        return jsonify(self.controller.get_formatted_results())

    def save_results(self):
        if CurrentScan.scan is not None:
            CurrentScan.scan.save_scan(self.tool_name, self.controller.last_scan_result)
            self.controller.last_scan_result = None
            return "<p>Results successfully saved.</p>"
        return "<p>No scan started.</p>"

    def stop_scan(self):
        self.controller.stop_scan()
        return "<p>Scan stopped.</p>"
