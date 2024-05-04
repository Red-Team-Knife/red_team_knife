

def render_scan_dictionary(dictionary:dict, tools:dict, indent_level=0):
    html = ""
    check_list = []
    reference_list = []
    for key in dictionary.keys():
        for section, tools_references in tools.items():
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


