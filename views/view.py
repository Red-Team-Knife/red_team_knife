import html
import json
from flask import Blueprint, request, render_template, jsonify, url_for
from utils.utils import debug_route
from utils.utils import remove_empty_values
from current_scan import CurrentScan
from controllers.base_controller import Controller
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
        self.name = name
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

    def __get_interface_page_for_get_request__(self):
        """
        Decides which version of the web page needs to be returned after a GET request.

        GET request implies accessing the scan interface. If an unsaved scan result
        is present, it will be shown, giving the opportunity to save it or request
        a new scan (reset page).

        Returns:
        flask.Response: The version of the web page to be returned.
        """
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
            
            target = self.__build_target__()

            # Check if a tool scan is present in the current scan
            if CurrentScan.scan.get_tool_scan(self.name):
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
                target=target,
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

    def __get_interface_page_for_post_request__(self, request):
        """
        Determines the version of the web page to return after a POST request.

        A POST request can indicate one of the following:
        - A new scan (page reset) is requested.
        - A scan is requested (run scan).
        - A past scan needs to be restored.

        Args:
            request (flask.Request): The HTTP request object containing form data.

        Returns:
            flask.Response: The version of the web page to be returned.
        """
        # Check if a new scan (page reset) was requested
        if request.form.get("new_scan_requested"):
            l.info(f"{self.tool_name} scan reset requested.")
            self.controller.last_scan_result = None
            return self.__get_interface_page_for_get_request__()

        # Check if a past scan needs to be restored
        if request.form.get("load_previous_results"):
            if CurrentScan.scan is not None and CurrentScan.scan.get_tool_scan(
                self.name
            ) is not None:
                self.controller.last_scan_result = CurrentScan.scan.get_tool_scan(
                    self.name
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
    
    # Builds the target for the specific tool
    def __build_target__(self):
        return CurrentScan.scan.host

    def is_scan_in_progress(self):
        """
        Returns the status of the scan (in progress or not).

        This method is called by the results page to check if the scan is finished
        and to request results.

        Returns:
            flask.Response: JSON response indicating whether the scan is in progress
            or not.
        """
        debug_route(request)

        if self.controller.is_scan_in_progress:
            l.info(f"{self.tool_name} scan in progress...")
        else:
            l.info(f"{self.tool_name} scan not in progress.")

        return jsonify({"scan_in_progress": self.controller.is_scan_in_progress})

    def results(self):
        """
        Returns HTML-formatted scan results.

        Returns:
            flask.Response: response containing the HTML-formatted scan results.
        """
        debug_route(request)

        return jsonify(self.controller.get_formatted_results())

    def save_results(self):
        """
        Saves the current results that are cached in the controller.

        This method is called to save the results of the current scan, which are
        stored in the controller.

        Returns:
            str: A message indicating the status of the save operation.
        """
        debug_route(request)
        l.info(f"Saving {self.tool_name} results...")

        if CurrentScan.scan is not None:
            try:
                CurrentScan.scan.save_scan(
                    self.name, self.controller.last_scan_result
                )
                self.controller.last_scan_result = None
                l.success(f"{self.tool_name} results saved.")
            except Exception as e:
                l.error(f"{self.tool_name} results were not saved!")
                print(e)

            return "<p>Results successfully saved.</p>"
        l.warning(f"No scan was started!")
        return "<p>No scan started.</p>"

    def stop_scan(self):
        """
        Stops a running scan.

        This method is called to stop a running scan associated with the controller.

        Returns:
            str: A message indicating the status of the stop operation.
        """
        l.info(f"Stopping {self.tool_name} scan...")
        try:
            self.controller.stop_scan()
            l.success(f"{self.tool_name} scan stopped.")
            return "<p>Scan stopped.</p>"
        except Exception as e:
            l.error(f"Could not stop {self.tool_name} scan:")
            print(e)
            return "<p>Something went wrong. Check terminal for more information.</p>"
