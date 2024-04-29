import html
import json
from flask import Blueprint, request, render_template, jsonify, url_for
from utils.dictionary import remove_empty_values
from current_scan import CurrentScan
from controllers.controller_thread import Controller


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

    def interface(self):
        # A scan was requested (run scan)
        options = request.json
        print(options)

        target = options["target"]
        options.pop("target")

        self.controller.run(target, options)

        no_scan_started = CurrentScan.scan is None

        return '<p>Fetching result...</p>'

    def is_scan_in_progress(self):
        print('here')
        return jsonify({"scan_in_progress": self.controller.is_scan_in_progress})

    def results(self):
        return jsonify(self.controller.get_formatted_results())

    def stop_scan(self):
        self.controller.stop_scan()
        return "<p>Scan stopped.</p>"
