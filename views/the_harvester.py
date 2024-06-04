import os
from controllers.the_harvester import NO_RESULTS_FOUND, SCREENSHOTS_DIRECTORY
from views.view import BaseBlueprint
from utils.utils import debug_route, remove_empty_values
from flask import request
from controllers.feroxbuster import (
    TOOL_NAME as FEROXBUSTER_NAME,
    TOOL_DISPLAY_NAME as FEROXBUSTER_DISPLAY_NAME,
)
from controllers.w4af_audit import (
    TOOL_NAME as W4AF_TOOL_NAME,
    TOOL_DISPLAY_NAME as W4AF_TOOL_DISPLAY_NAME,
)


class TheHarvesterBlueprint(BaseBlueprint):

    def interface(self):
        extra = {
            "feroxbuster_name": FEROXBUSTER_NAME,
            "feroxbuster_display_name": FEROXBUSTER_DISPLAY_NAME,
            "w4af_name": W4AF_TOOL_NAME,
            "w4af_display_name": W4AF_TOOL_DISPLAY_NAME,
        }
        return super().interface(extra=extra)

    def __format_html__(self, result):
        if result == NO_RESULTS_FOUND:
            return f'<p>{result}</p>'
        data = remove_empty_values(result)

        html_output = ""

        if result.get("screenshots_available", False):
            html_output += (
                "<p>Screenshots saved here: "
                + os.path.abspath(SCREENSHOTS_DIRECTORY)
                + "</p><br>"
            )
            result.pop("screenshots_available")

        html_output += """
                        <table>
                        """

        for key in result.keys():
            html_output += f"""
                <tr>
                    <td><b class='table_bold'>{key}</b></td>
                """

            items = ""
            for i in result[key]:
                items += i
                items += "<br>"

            # remove last '<br>'
            items = items[:-4]

            html_output += f"""
                <td>{items}</td>
                </tr>
            """
        html_output += "</table>"
        return html_output