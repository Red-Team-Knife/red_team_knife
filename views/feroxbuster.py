from utils.utils import render_dictionary_as_table
from views.web_target import WebTargetBlueprint


class FeroxbusterBlueprint(WebTargetBlueprint):
    def __format_html__(self, results):
        sorted = {}
        for i in results:
            if i.get("status", False):
                status = i["status"]
                if sorted.get(status, False):
                    sorted[status].append(i)
                else:
                    sorted[status] = [i]

        # Extract status codes and build a string
        status_codes = ""
        for code in list(sorted.keys()):
            status_codes += str(code)
            status_codes += ", "

        status_codes = status_codes[:-2]

        html_output = f"""
        <h1>Status codes: {status_codes}</h1>
                        <table>
                        """

        for key in list(sorted.keys()):
            html_output += f"""
                <tr>
                    <td style="font-size: 24px;"><b>{key}</b></td>
                </tr>
                """

            items = ""
            for i in sorted[key]:
                items += "<tr><td><table>"
                items += render_dictionary_as_table(i)
                items += "</table></td></tr>"

            html_output += items
        html_output += "</table>"
        return html_output
