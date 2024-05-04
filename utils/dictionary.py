
def remove_empty_values(dict) -> dict:
    keys_to_remove=[]

    for key, value in dict.items():
        if not value:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        dict.pop(key)
    return dict

def render_dictionary_as_table(dictionary: dict, indent="") -> str:
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


def fill_table_column_list(row, key):
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
    html = ''

    for subkey in row[key]:
        html += f'<b>{subkey.replace("@", "")}: </b>'
        html += f"{row[key][subkey]} <br>"
    return html


