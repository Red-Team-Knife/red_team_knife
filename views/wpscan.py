import json
from controllers.exploitation_tips import EXPLOITATION_TIPS_NAME
from views.web_target import WebTargetBlueprint
from copy import deepcopy

from utils.utils import (
    move_key,
    render_dictionary_as_table,
    render_list_as_bullet_list,
    render_list_in_dictionary_as_table,
)


class WPScanBlueprint(WebTargetBlueprint):

    def interface(self):
        extra = {"exploitation_tips_name": EXPLOITATION_TIPS_NAME}
        return super().interface(extra=extra)

    def __format_html__(self, result) -> str:
        html_output = ""
        scan: dict = deepcopy(result)

        split_list_1 = ["main_theme", "version"]
        split_list_2 = ["plugins", "themes"]
        split_list_3 = ["medias", "users"]

        api_detail = scan.pop("vuln_api", None)
        if api_detail:
            html_output += "<b>Api Details</b><br>"
            for tag, detail in api_detail.items():
                html_output += f"<p><b>{tag}: </b>{detail}</p>"
            html_output += "<br>"

        html_output += "<b>General Infos</b><br>\n"
        html_output += f"<p><b>Target url:</b> {scan['target_url']}</p>\n"
        scan.pop("target_url")
        html_output += f"<p><b>Target ip:</b> {scan['target_ip']}</p>\n"
        scan.pop("target_ip")
        html_output += f"<p><b>Effective url:</b> {scan['effective_url']}</p>\n"
        scan.pop("effective_url")

        for section in scan:
            if scan[section] is None or not scan[section]:
                continue
            html_output += f"<b>{section}</b><br>"

            # interesting_findings block
            if isinstance(scan[section], list):
                html_output += "<table>\n"
                html_output += "<tr>\n"
                for header in scan[section][0].keys():
                    html_output += f"<th>{header}</th>\n"
                html_output += "</tr>\n"
                for row in scan[section]:
                    html_output += "<tr>\n"

                    for column in row:
                        html_output += "<td>\n"
                        if isinstance(row[column], dict):
                            html_output += f"<table>\n{render_dictionary_as_table(row[column])}</table>\n"
                        elif isinstance(row[column], list):
                            html_output += f"<ul>\n{render_list_as_bullet_list(row[column])}</ul>\n"
                        else:
                            html_output += f"{row[column]}\n"
                        html_output += "</td>\n"
                    html_output += "</tr>\n"

                html_output += "</table><br><br>\n"
            elif section in split_list_1:
                for tag, detail in scan[section].items():
                    if tag == "vulnerabilities" and len(detail) != 0:
                        html_output += f"<b>{tag}:</b><table>\n{self.__render_list_in_dictionary_as_table__(detail)}</table><br>\n"
                    elif isinstance(detail, dict):
                        html_output += f"<b>{tag}:</b><table>\n{render_dictionary_as_table(detail)}</table><br>\n"
                    elif isinstance(detail, list) and len(detail) != 0:
                        if isinstance(detail[0], dict):
                            html_output += f"<b>{tag}: </b> <table>\n{render_list_in_dictionary_as_table(detail)}</table><br>\n"
                        elif isinstance(detail[0], str):
                            html_output += f"<b>{tag}:</b><ul>\n{render_list_as_bullet_list(detail)}</ul>\n"
                            html_output += "<br>\n"
                        else:
                            html_output += f"<p><b>{tag}:</b> {detail}</p>\n"
                    else:
                        html_output += f"<p><b>{tag}: </b>{detail}</p>"
            elif section in split_list_2:
                html_output += "<table>\n"
                html_output += "<tr>\n"
                first_item = next(iter(scan[section].keys()))
                for header in scan[section][first_item].keys():
                    html_output += f"<th>{header}</th>\n"
                html_output += "</tr>\n"

                for item in scan[section]:
                    if (
                        scan[section][item].get("vulnerabilities", False)
                        and len(scan[section][item].get("vulnerabilities", False)) != 0
                    ):
                        html_output += '<tr class= "vulnerable_plugin">'
                    else:
                        html_output += "<tr>\n"
                    for tag, detail in scan[section][item].items():
                        html_output += "<td>\n"
                        if isinstance(detail, dict):
                            html_output += "<table>\n"
                            html_output += render_dictionary_as_table(detail)
                            html_output += "</table>\n"
                        elif isinstance(detail, list):
                            if tag == "vulnerabilities":
                                if len(detail) == 0:
                                    html_output += "No Vulnerability Found\n"
                                else:
                                    html_output += f"<table>\n{self.__render_list_in_dictionary_as_table__(detail)}</table>\n"
                            elif len(detail) != 0 and isinstance(detail[0], str):
                                html_output += (
                                    f"<ul>{render_list_as_bullet_list(detail)}</ul>"
                                )
                        else:
                            html_output += f"{detail}\n"
                        html_output += "</td>\n"
                    html_output += "</tr>\n"

                html_output += "</table><br><br>\n"
            elif section in split_list_3:
                html_output += "<table>"
                html_output += "<tr>\n"
                first_item = next(iter(scan[section].keys()))
                html_output += "<th>media_id</th>"
                for header in scan[section][first_item].keys():
                    html_output += f"<th>{header}</th>\n"
                html_output += "</tr>\n"

                for item in scan[section]:
                    html_output += "<tr>\n"
                    html_output += f"<td>{item}</td>"
                    for tag, detail in scan[section][item].items():
                        html_output += f"<td>{detail}</td>\n"
                    html_output += "</tr>\n"

                html_output += "</table><br><br>\n"
            else:
                html_output += f"<b>{section}</b><br>"
        

        return html_output

    def __build_href__(self, key: str, value: str) -> str:
        WPVULNDB = "https://wpscan.com/vulnerability/"

        html = ""
        if key == "wpvulndb":
            html += f'<a href="{WPVULNDB + value + "/"}" target="_blank">{value}</a>'
        elif key == "url":
            html += f'<a href="{value}" target="_blank>{value}</a>'
        elif key in "cve":
            html += f'<a class= "open_modal_link" data-vuln_code="{key + "-" + value}" data-vuln_type="{key}" href= "#">{value}</a>'
        elif key == "exploitdb":
            html += f'<a class= "open_modal_link" data-vuln_code="{key + ":" + value}" data-vuln_type="{key}" href= "#">{value}</a>'
        else:
            return value

        return html

    def __render_dictionary_as_table__(self, dictionary: dict, indent=""):
        """
        Render a dictionary as an HTML table.

        Args:
            dictionary (dict): The dictionary to render as a table.
            indent (str, optional): The string to use for indentation. Defaults to "".

        Returns:
            str: The HTML representation of the dictionary as a table.
        """
        html = ""
        for key, value in dictionary.items():
            html += "<tr class= open>"
            if isinstance(value, dict):
                html += (
                    f"<th>{indent}{key}</th><td><table>\n"
                    + render_dictionary_as_table(value, indent + "&nbsp;&nbsp;")
                    + "\n</table></td>\n"
                )
            elif isinstance(value, list):
                html += f"<th>{indent}{key}</th><td><ul>\n{self.__render_list_as_bullet_list__(value, key)}</ul></td>\n"
            else:
                html += f"<th>{indent}{key}</th><td>{value}</td>\n"
            html += "</tr>\n"
        return html

    def __render_list_as_bullet_list__(self, content: list, tag: str) -> str:
        """
        Render a list as an HTML bullet list.

        Args:
            content (list): The list to render as bullet list.

        Returns:
            str: The HTML representation of the list as a bullet list.
        """
        html = ""
        if len(content) == 0:
            html += "<li>No Infos</li>\n"
        else:
            for item in content:
                ref = self.__build_href__(tag, item)
                html += f"<li>{ref}</li>\n"
        return html

    def __render_list_in_dictionary_as_table__(self, content: list) -> str:
        """
        Render a list as an HTML table content.

        Args:
            list (list): The list to render as table content.

        Returns:
            str: The HTML representation of the dictionary as a table.
        """
        html = ""
        html += "<tr>\n"
        for header in content[0].keys():
            html += f"<th>{header}</th>\n"
        html += "</tr>\n"

        for row in content:
            html += "<tr>\n"
            for column in row:
                html += "<td>\n"
                if isinstance(row[column], list):
                    if isinstance(row[column][0], dict):
                        html += f"<table>\n{render_dictionary_as_table(row[column])}</table>\n"
                    else:
                        html += (
                            f"<ul>\n{render_list_as_bullet_list(row[column])}</ul>\n"
                        )
                elif isinstance(row[column], dict):
                    html += f"<table>\n{self.__render_dictionary_as_table__(row[column])}</table>\n"
                else:
                    html += f"{row[column]}\n"
                html += "</td>\n"
            html += "</tr>\n"

        return html
