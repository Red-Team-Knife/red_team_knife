import os
import uuid
from flask import render_template, request, url_for
from controllers.w4af_audit import BASE_URL, TMP_FOLDER, W4afAuditController
from models.current_scan import CurrentScan
from utils.utils import debug_route, render_dictionary_as_table
from views.view import BaseBlueprint, FORMAT_FOR_DISPLAY_RESULT, FORMAT_FOR_REPORT
from loguru import logger as l
from controllers.dig import (
    TOOL_NAME as DIG_NAME,
    TOOL_DISPLAY_NAME as DIG_DISPLAY_NAME,
    QUERY_TYPE,
)
from controllers.sqlmap import (
    TOOL_NAME as SQLMAP_NAME,
    TOOL_DISPLAY_NAME as SQLMAP_DISPLAY_NAME,
)
from controllers.commix import (
    TOOL_NAME as COMMIX_NAME,
    TOOL_DISPLAY_NAME as COMMIX_DISPLAY_NAME,
)
from views.web_target import WebTargetBlueprint


class W4afBlueprint(WebTargetBlueprint):
    def __init__(
        self,
        name,
        import_name,
        controller: W4afAuditController,
        tool_name: str,
        interface_template: str,
        results_template: str,
        options_list: list,
        sections: dict,
    ):
        super().__init__(
            name,
            import_name,
            controller,
            tool_name,
            interface_template,
            results_template,
            options_list,
            sections,
        )
        self.controller: W4afAuditController

    def interface(self):
        extra = {
            "sqlmap_name": SQLMAP_NAME,
            "sqlmap_display_name": SQLMAP_DISPLAY_NAME,
            "commix_name": COMMIX_NAME,
            "commix_display_name": COMMIX_DISPLAY_NAME,
            "dig_name": DIG_NAME,
            "dig_display_name": DIG_DISPLAY_NAME,
            "query_type": QUERY_TYPE,
        }
        return super().interface(extra=extra)

    def __get_interface_page_for_get_request__(self, extra=None):
        no_scan_started = CurrentScan.scan is None

        # Check if an unsaved scan is still stored and
        # the scan has been stopped
        if (
            self.controller.last_scan_result
            and not self.controller.is_scan_in_background
        ):
            return render_template(
                self.results_template,
                sections=self.sections,
                past_scan_available=True,
                save_disabled=no_scan_started,
                scan_result=self.__format_result__(FORMAT_FOR_DISPLAY_RESULT),
                current_section=self.name,
                tool=self.tool_name,
                stopped=True,
                extra=extra,
            )

        return super().__get_interface_page_for_get_request__(extra)

    def __get_interface_page_for_post_request__(self, request, extra=None):
        if request.form.get("new_scan_requested"):
            self.controller.delete_scan()

        # Check if a past scan needs to be restored
        if request.form.get("load_previous_results"):
            if CurrentScan.scan is not None and CurrentScan.scan.get_tool_scan(
                self.tool_name
            ):
                self.controller.last_scan_result = CurrentScan.scan.get_tool_scan(
                    self.tool_name
                )
                self.controller.restore_scan()
                self.controller.restore_scan_status()

                return render_template(
                    self.results_template,
                    sections=self.sections,
                    past_scan_available=True,
                    save_disabled=True,
                    scan_result=self.__format_result__(FORMAT_FOR_DISPLAY_RESULT),
                    current_section=self.name,
                    tool=self.tool_name,
                    stopped=True,
                    extra=extra,
                )

        return super().__get_interface_page_for_post_request__(request, extra)

    def __format_html__(self, result):
        try:
            html_table = "<table>\n"
            html_table += (
                "<tr><th>ID</th><th>Name</th><th>URL</th><th>Reference</th></tr>\n"
            )

            for item in result["items"]:
                html_table += (
                    f'<tr><td>{item["id"]}</td>'
                    + f'<td>{item["name"]}</td>'
                    + f'<td>{item["url"]}</td>'
                )
                if item.get("info"):
                    description_file_path, description_file_name = (
                        self.__create_temp_description_file__(item)
                    )
                    html_table += f'<td><a href="/{description_file_name}" target="_blank">Read more</a></td></tr>\n'
                else:
                    html_table += f'<td><a href="{BASE_URL + item["href"]}" target="_blank">Read more</a></td></tr>\n'

            html_table += "</table>"

            return {
                "status": self.__create_dictionary_html_table__(result["status"]),
                "results": html_table,
                "progress": result["status"].get("progress"),
            }
        except Exception as e:
            print(e)
            return {
                "status": "<p>Fetching results...</p>",
                "results": "<p>Fetching results...</p>",
                "progress": 0,
            }

    def __create_dictionary_html_table__(self, dictionary: dict, indent=""):
        html = ""
        for key, value in dictionary.items():
            if isinstance(value, dict):
                html += (
                    f"<tr><th>{indent}{key}</th><td><table>"
                    + render_dictionary_as_table(value, indent + "&nbsp;&nbsp;")
                    + "</table></td></tr>"
                )
            else:
                html += f"<tr><th>{indent}{key}</th><td>{value}</td></tr>"
        return html

    def __create_temp_description_file__(self, item):
        random_uuid = uuid.uuid4()
        # Convert UUID to a string and remove dashes
        random_filename = str(random_uuid).replace("-", "")
        file_path = os.path.join(TMP_FOLDER, random_filename + ".html")
        with open(file_path, "w") as file:

            print(self.__generate_description_html_page__(item["info"]), file=file)

            return file_path, file_path

    def __generate_description_html_page__(self, data):
        html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Vulnerability Description</title>
                <link rel="stylesheet" href="{url_for('static', filename='styles.css')}">
            </head>
            <body>
                <table border="1">
                    {render_dictionary_as_table(data)}
                </table>
            </body>
            </html>
            """

        return html_content
