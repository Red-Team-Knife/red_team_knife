from flask import Request
from loguru import logger as l
from weasyprint import HTML, CSS


def debug_route(request: Request):
    """
    Prints debug message to keep track of http requests

    Args:
        request:
    """
    l.debug(f"{request.method} {request.path}")


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
                f"<tr><th>{indent}{key}</th><td><table>\n"
                + render_dictionary_as_table(value, indent + "&nbsp;&nbsp;")
                + "\n</table></td></tr>\n"
            )
        elif isinstance(value, list):
            html += f"<tr><th>{indent}{key}</th><td><ul>\n{render_list_as_bullet_list(value)}</ul></td></tr>\n"
        else:
            html += f"<tr><th>{indent}{key}</th><td>{value}</td></tr>\n"
    return html

def render_list_as_bullet_list(content: list) -> str:
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
            html += f"<li>{item}</li>\n"
    return html


def render_list_in_dictionary_as_table(content: list) -> str:
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
                    html += f"<ul>\n{render_list_as_bullet_list(row[column])}</ul>\n"
            elif isinstance(row[column], dict):
                html += f"<table>\n{render_dictionary_as_table(row[column])}</table>\n"
            else:
                html += f"{row[column]}\n"
            html += "</td>\n"
        html += "</tr>\n"

    return html


def move_key(dictionary:dict, key:str, pos:int) -> dict:
    """
    Move the key of a dictionary into a specific position of the dictionary.

    Args:
        dictionary (dict): The dictionary to modify.
        key (str): The key of the dictionary to move
        pos (int): The position of the dictionary in which to place the key.

    Returns:
        dict: The dictionary with the key in the desired position.
    """
    if dictionary.get(key, False):
        keys = list(dictionary.keys())
        if key in keys:
            keys.insert(pos, keys.pop(keys.index(key)))
        return {k: dictionary[k] for k in keys}
    else:
        return dictionary


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

def create_pdf_from_html(css_files:list, content:str, save_path:str, tool_name:str):
    """
        Create a PDF File based on an HTML string.

    Args:
        css_files (list): List of CSS files to use in rendering.
        content (str): The HTML string.
        save_path (str): The path to save the PDF.
        tool_name (str): the name of the tool that requested the generation.

    Returns:
        Exception | True : Returns a True value representing the outcome of file creation or the Exception raised.
    """
    
    
    stylesheets = []
    html = f"""
    <html>
        <head>
        <title>{tool_name} report</title>
    """
    
    for file in css_files:
        html += f"<link rel= 'stylesheet' type= 'text/css' href='{file}'>"
        stylesheets.append(CSS(filename='static/' + file))
        
    html += """
            <style>
                @page {
                    size: A4 landscape;
                    margin: 20mm;
                }

                #results {
                    overflow-x: auto;
                    white-space: nowrap;
                }

                table {
                    width: 15%;
                    font-size: 10px;
                    table-layout: auto;
                }

                th, td {
                    padding: 5px;
                }
            </style>
        </head>
        <body>
            <h1>
            \{\}
        </body>
    </html>
    """
    
    html_content = HTML(string=html.replace("\{\}", content))
    try:
        file_path =save_path + f"{tool_name}_report.pdf"
        with open(file_path, "w") as file:
            print("", file=file)
        html_content.write_pdf(file_path, stylesheets=stylesheets)
        return True
    except Exception as e:
        return e
    