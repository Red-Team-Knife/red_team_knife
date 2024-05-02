import html
import json
from flask import Blueprint, request, render_template, jsonify, url_for
from utils.log import debug_route
from utils.dictionary import remove_empty_values
from current_scan import CurrentScan
from controllers.controller_thread import Controller
from loguru import logger as l


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
        super().__init__(name, import_name, url_prefix="/" + name)
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
        debug_route(request)

        if request.method == "POST":
            return self.__get_interface_page_for_post_request__(request)
        return self.__get_interface_page_for_get_request__()

    # GET request means we want to access scan interface.
    # An unsaved scan result could be present, in that case it will be shown,
    # giving the opportunity to save it or to request a new scan (reset page).
    def __get_interface_page_for_get_request__(self):
        no_scan_started = CurrentScan.scan is None

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
    def __get_interface_page_for_post_request__(self, request):

        # Check if a new scan (page reset) was requested
        if request.form.get("new_scan_requested"):
            l.info(f"{self.tool_name} scan reset requested.")
            self.controller.last_scan_result = None
            return self.__get_interface_page_for_get_request__()

        # Check if a past scan needs to be restored
        if request.form.get("load_previous_results"):
            if CurrentScan.scan is not None and CurrentScan.scan.get_tool_scan(
                self.tool_name
            ):
                self.controller.last_scan_result = CurrentScan.scan.get_tool_scan(
                    self.tool_name
                )
                l.info(f"Loading previous {self.tool_name} scan results.")

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

    # Returns scan status (in progress/not in progress).
    # Called by results page to check if scan is finished and ask for results.
    def is_scan_in_progress(self):
        debug_route(request)

        if self.controller.is_scan_in_progress:
            l.info(f"{self.tool_name} scan in progress...")
        else:
            l.info(f"{self.tool_name} scan not in progress.")

        return jsonify({"scan_in_progress": self.controller.is_scan_in_progress})

    # Returns html-formatted scan results.
    def results(self):
        debug_route(request)

        return jsonify(self.controller.get_formatted_results())

    # Called to save current results that are cached in the controller.
    def save_results(self):
        debug_route(request)
        l.info(f"Saving {self.tool_name} results...")

        if CurrentScan.scan is not None:
            try:
                CurrentScan.scan.save_scan(
                    self.tool_name, self.controller.last_scan_result
                )
                self.controller.last_scan_result = None
                l.success(f"{self.tool_name} results saved.")
            except Exception as e:
                l.error(f"{self.tool_name} results were not saved!")
                print(e)

            return "<p>Results successfully saved.</p>"
        l.warning(f"No scan was started!")
        return "<p>No scan started.</p>"

    # Called to stop a running scan.
    def stop_scan(self):
        l.info(f"Stopping {self.tool_name} scan...")
        try:
            self.controller.stop_scan()
            l.success(f"{self.tool_name} scan stopped.")
            return "<p>Scan stopped.</p>"
        except Exception as e:
            return "<p>Something went wrong. Check terminal for more information.</p>"
