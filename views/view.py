import html
import json
from flask import Blueprint, request, render_template, jsonify, url_for
from utils.utils import debug_route
from utils.utils import remove_empty_values
from models.current_scan import CurrentScan
from controllers.base_controller import Controller
from loguru import logger as l

FORMAT_FOR_DISPLAY_RESULT = "format_for_display_result"
FORMAT_FOR_REPORT = "format_for_report"

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
        self.route("/save_report", methods=["POST"])(self.save_report)

    def interface(self, extra: dict = None):
        """
        Returns proper interface or result page based on user request

        Args:
            extra (dict, optional): Dictionary containing extra variables to customize inherited views. Defaults to None.

        Returns:
            flask.Response: Requested page.
        """
        debug_route(request)

        if request.method == "POST":
            return self.__get_interface_page_for_post_request__(request, extra)
        return self.__get_interface_page_for_get_request__(extra)

    def __get_interface_page_for_get_request__(self, extra: dict = None):
        """
        Decides which version of the web page needs to be returned after a GET request.

        GET request implies accessing the scan interface. If an unsaved scan result
        is present, it will be shown, giving the opportunity to save it or request
        a new scan (reset page).

        Args:
            extra (dict, optional): Dictionary containing extra variables to customize inherited views. Defaults to None.

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
                extra=extra,
            )

        # Check if an unsaved scan is still stored
        if self.controller.last_scan_result:
            return render_template(
                self.results_template,
                sections=self.sections,
                past_scan_available=True,
                save_disabled=no_scan_started,
                scan_result=self.__format_result__(FORMAT_FOR_DISPLAY_RESULT),
                current_section=self.name,
                tool=self.tool_name,
                extra=extra,
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
                    extra=extra,
                )

            # Tool scan is not present, we only pass the target
            return render_template(
                self.interface_template,
                sections=self.sections,
                past_scan_available=False,
                target=target,
                options_list=self.options_list,
                tool=self.tool_name,
                extra=extra,
            )

        # No scan has been started
        return render_template(
            self.interface_template,
            sections=self.sections,
            options_list=self.options_list,
            tool=self.tool_name,
            extra=extra,
        )

    def __get_interface_page_for_post_request__(self, request, extra: dict = None):
        """
        Determines the version of the web page to return after a POST request.

        A POST request can indicate one of the following:
        - A new scan (page reset) is requested.
        - A scan is requested (run scan).
        - A past scan needs to be restored.

        Args:
            request (flask.Request): The HTTP request object containing form data.
            extra (dict, optional): Dictionary containing extra variables to customize inherited views. Defaults to None.

        Returns:
            flask.Response: The version of the web page to be returned.
        """
        # Check if a new scan (page reset) was requested
        if request.form.get("new_scan_requested"):
            l.info(f"{self.tool_name} scan reset requested.")
            self.controller.last_scan_result = None
            return self.__get_interface_page_for_get_request__(extra)

        # Check if a past scan needs to be restored
        if request.form.get("load_previous_results"):
            if (
                CurrentScan.scan is not None
                and CurrentScan.scan.get_tool_scan(self.name) is not None
            ):
                self.controller.restore_scan()
                l.info(f"Loading previous {self.tool_name} scan results.")

                return render_template(
                    self.results_template,
                    sections=self.sections,
                    past_scan_available=True,
                    save_disabled=True,
                    scan_result=self.__format_result__(FORMAT_FOR_DISPLAY_RESULT),
                    current_section=self.name,
                    tool=self.tool_name,
                    extra=extra,
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
            extra=extra,
        )

    def __build_target__(self) -> str:
        """Builds target.

        Can be inherited for customization.

        Returns:
            str: target string.
        """
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
            l.info(f"{self.tool_name} running...")
        else:
            l.info(f"{self.tool_name} not running.")

        return jsonify({"scan_in_progress": self.controller.is_scan_in_progress})

    def results(self):
        """
        Returns HTML-formatted scan results.

        Returns:
            flask.Response: response containing the HTML-formatted scan results.
        """
        debug_route(request)

        return jsonify(self.__format_result__(FORMAT_FOR_DISPLAY_RESULT))

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

        is_results_saved = self.controller.save_results()

        if isinstance(is_results_saved, Exception):
            return "<p>An error occured during the operation, check terminal for more information.</p>"
        elif is_results_saved:
            return "<p>Results successfully saved.</p>"
        else:
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

    def save_report(self):
        """
        Save the scan result as a PDF file.

        Returns:
            str: A message indicating the status of the file creation.
        """
        debug_route(request)
        l.info(f"Generating {self.tool_name} report...")
        
        html = self.__format_result__(FORMAT_FOR_REPORT)
        
        if html != "<p>An error occurred during results retrieval. Check terminal for more information.</p>":      
            is_report_saved = self.controller.save_report(html)
            
            if isinstance(is_report_saved, Exception):
                l.error(f"{self.tool_name} failed to generate report!")
                return "<p>An error occured during the operation, check terminal for more information.</p>"
            elif is_report_saved:
                l.success("Report generated successfully")
                return "<p> Report successfully saved. </p>"
        else:
            return html

    def __format_result__(self, option:str):
        """
        Formats the result in HTML.

        Returns:
            str: HTML-formatted results.
        """
        results = self.controller.get_results()
        if results:
            l.info(f"Generating HTML for {self.tool_name} results...")
            if option == FORMAT_FOR_REPORT:
                html = self.__format_html_for_report__(results)
            elif option == FORMAT_FOR_DISPLAY_RESULT:
                html = self.__format_html__(results)
            l.success("HTML generated successfully.")
            return html
        else:
            return "<p>An error occurred during results retrieval. Check terminal for more information.</p>"

    def __format_html__(self, results) -> str:
        """
        Formats results into HTML form.

        Args:
            results: object containing the results.

        Returns:
            str: HTML-formatted results.
        """
        pass
    
    def __format_html_for_report__(self, results) -> str:
        """
        Generate the HTML string for the PDF report.

        Args:
            results: object containing the results.

        Returns:
            str: object containing the results.
        """
        return self.__format_html__(results)
