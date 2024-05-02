def render_dictionary(dictionary, indent_level=0):
    html = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            html += f'<p style="margin-left: {indent_level * 20}px;"><strong>{key}:</strong></p>'
            html += render_dictionary(value, indent_level + 1)
        else:
            html += f'<p style="margin-left: {indent_level * 20}px;"><strong>{key}:</strong> {value}</p>'
    return html

def render_dictionary_as_table(dictionary: dict, indent=""):
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
