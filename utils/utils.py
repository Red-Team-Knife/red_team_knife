from flask import Request
from loguru import logger as l


def debug_route(request:Request):
    """
    Prints debug message to keep track of http requests

    Args:
        request: 
    """
    l.debug(f"{request.method} {request.path}")

#TODO fixare rendering
def render_scan_dictionary(dictionary: dict, tools: dict, indent_level=0):
    """
    Render a dictionary into HTML with special handling for certain keys based on tools references.

    Args:
        dictionary (dict): The dictionary to render into HTML.
        tools (dict): A dictionary containing tools and their associated references.
                      Keys are tool names, and values are lists of tool details, where each detail is a tuple
                      containing the tool information and its reference.
        indent_level (int, optional): The level of indentation for the HTML output. Defaults to 0.

    Returns:
        str: The HTML representation of the dictionary.
    """
    
    html = ""
    check_list = []
    reference_list = []
    for key in dictionary.keys():
        for _, tools_references in tools.items():
            for tool_details in tools_references:
                if key in tool_details:
                    check_list.append(key)
                    reference_list.append(tool_details[1])

    for key, value in dictionary.items():
        if key not in check_list:
            html += f'<p style="margin-left: {indent_level * 20}px;"><strong>{key}:</strong> {value}</p>'
        else:
            for i in range(len(check_list)):
                if key == check_list[i]:
                    html += f'<p style="margin-left: {indent_level * 20}px;"><strong>{key}: </strong>'
                    html += f'<a id="{reference_list[i]}" class="scan_reference" style="margin-left: {indent_level * 20}px;" href="#" >Scan Details</a></p>'

    return html


def remove_empty_values(dict) -> dict:
    """
    Remove keys with empty (None, '', [], {}) values from a dictionary.

    Args:
        dictionary (dict): The dictionary to remove empty values from.

    Returns:
        dict: A dictionary with empty values removed.
    """
    keys_to_remove = []

    for key, value in dict.items():
        if not value:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        dict.pop(key)
    return dict


def render_dictionary_as_table(dictionary: dict, indent="") -> str:
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
        if isinstance(value, dict):
            html += (
                f"<tr><th>{indent}{key}</th><td><table>"
                + render_dictionary_as_table(value, indent + "&nbsp;&nbsp;")
                + "</table></td></tr>"
            )
        else:
            html += f"<tr><th>{indent}{key}</th><td>{value}</td></tr>"
    return html

def render_list_in_dictionary_as_table(list:list) -> str:
    """
    Render a list as an HTML table content.

    Args:
        list (list): The list to render as table content.

    Returns:
        str: The HTML representation of the dictionary as a table.
    """
    html = ''
    html += '<tr>'
    for header in list[0].keys():
        html += f"<th>{header}</th>"
    html += '</tr>'
    
    for row in list:
        html += '<tr>'
        for column in row:
            html += f'<td>{row[column]}</td>'
        html += '</tr>'

    return html 


def fill_table_column_list(row, key):
    """
    Fill a table column with data from a dictionary.

    Args:
        row (dict): The dictionary containing data for the table column.
        key (str): The key in the dictionary representing the column.

    Returns:
        str: The HTML representation of the table column.
    """
    html = "<table>"
    html += "<tr>"

    for headers in row[key][0].keys():
        html += "<th>{}</th>".format(headers.replace("@", ""))

    html += "</tr>"

    for subrow in row[key]:
        html += "<tr>"

        for content in subrow:
            html += "<td>{}</td>".format(subrow[content])

        html += "</tr>"
    html += "</table>"

    return html


def fill_table_column_dict(row, key):
    """
    Fill a table column with data from a dictionary.

    Args:
        row (dict): The dictionary containing data for the table column.
        key (str): The key in the dictionary representing the column.

    Returns:
        str: The HTML representation of the table column.
    """
    html = ""

    for subkey in row[key]:
        html += f'<b>{subkey.replace("@", "")}: </b>'
        html += f"{row[key][subkey]} <br>"
    return html


def get_python_style_list_string_from_comma_separated_str(string: str):
    """
    Convert a comma-separated string to a Python-style list string.

    Args:
        string (str): The comma-separated string.

    Returns:
        str: Python-style list string.
    """
    elements = [element.strip() for element in string.split(",")]
    return "[" + ",".join(elements) + "]"


def build_command_string(command):
    """
    Build a command string from a list of command elements.

    Args:
        command (list): List of command elements.

    Returns:
        str: The command string.
    """
    command_string = ""
    for i in command:
        command_string += i
        command_string += " "
    return command_string
