import html
import json
from flask import Blueprint, request, render_template, jsonify, url_for
from utils.utils import remove_empty_values
from models.current_scan import CurrentScan
from controllers.base_controller import Controller
from utils.utils import debug_route
from loguru import logger as l


class HeadlessBlueprint(Blueprint):
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

        self.route("/", methods=["POST"])(self.interface)
        self.route("/results", methods=["GET"])(self.results)
        self.route("/scan_in_progress", methods=["GET"])(self.is_scan_in_progress)
        self.route("/stop_scan", methods=["GET"])(self.stop_scan)

    # A scan was requested (run scan)
    def interface(self):
        debug_route(request)

        options = request.json

        target = options["target"]
        options.pop("target")

        self.controller.run(target, options)

        return "<p>Fetching result...</p>"

    def is_scan_in_progress(self):
        debug_route(request)

        if self.controller.is_scan_in_progress:
            l.info(f"{self.tool_name} scan in progress...")
        else:
            l.info(f"{self.tool_name} scan not in progress.")

        return jsonify({"scan_in_progress": self.controller.is_scan_in_progress})

    def results(self):
        debug_route(request)
        return jsonify(self.__format_result__())

    def stop_scan(self):
        l.info(f"Stopping {self.tool_name} scan...")
        try:
            self.controller.stop_scan()
            l.success(f"{self.tool_name} scan stopped.")
            return "<p>Scan stopped.</p>"
        except Exception as e:
            return "<p>Something went wrong. Check terminal for more information.</p>"

    def __format_result__(self):
        """
        Formats the result in HTML.

        Returns:
            str: HTML-formatted results.
        """
        results = self.controller.get_results()
        if results:
            l.info(f"Generating HTML for {self.tool_name} results...")
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
