from views.domain_name_target_view import DomainNameTargetBlueprint
from controllers.dig import SPOOFER_ENDPOINT, SPOOFER_HOST_PARAMETER_NAME

class DigBlueprint(DomainNameTargetBlueprint):
    def __format_html__(self, results):
        html = "<table>"
        query_type = results['type'].lower()
        for row in results['response']:
            if query_type == "mx":
                row = self.__format_mx_result__(row)
                html += f'<tr class="open" onclick="redirectToSpoofer(\'{row}\')" title="Found a mail server. Click here to try spoofing an email." style="cursor: pointer;"><th>{query_type}</th><td>{row}</td></tr>'
            else:
                html += f"<tr><th>{query_type}</th><td>{row}</td></tr>"
        html += "</table>"
        if query_type == "mx":
            html += f"""
                    <script>
                    function redirectToSpoofer(host) {{
                        window.location.href = '/{SPOOFER_ENDPOINT}?{SPOOFER_HOST_PARAMETER_NAME}=' + host;
                    }}
                    </script>
                    """
        return html

    def __format_mx_result__(self, row):
        parts = row.split()

        if len(parts) >= 2 and parts[0].isdigit():
            domain = " ".join(parts[1:]).strip(".")
            return domain
        else:
            return row