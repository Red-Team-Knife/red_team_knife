from views.web_target import WebTargetBlueprint
from loguru import logger as l

class DirsearchBlueprint(WebTargetBlueprint):
    """
    Blueprint specific to Dirsearch. 
    Inherits base logic and customizes the view.
    """

    def __format_html__(self, results) -> str:
        # CONTROL LOG: You will see this line in the terminal if everything works
        l.warning("!!! DIRSEARCH PARSER IS ACTIVE !!!")

        if not results or results == "None":
            return "<p class='w3-panel w3-red'>No results received from the controller.</p>"

        html = "<table class='w3-table-all w3-hoverable w3-card-4'>"
        html += "<thead><tr class='w3-red'><th>Status</th><th>Size</th><th>URL</th></tr></thead><tbody>"
        
        lines = results.split('\n')
        for line in lines:
            if not line.strip() or line.startswith('#'):
                continue
                
            parts = line.split()
            if len(parts) >= 3:
                status = parts[0]
                size = parts[1]
                url = parts[2]
                
                color = "green" if status == "200" else "orange" if status.startswith("3") else "red"
                
                html += f"<tr>"
                html += f"<td><b style='color:{color}'>{status}</b></td>"
                html += f"<td>{size}</td>"
                html += f"<td><a href='{url}' target='_blank' style='word-break: break-all;'>{url}</a></td>"
                html += f"</tr>"
                
        html += "</tbody></table>"
        return html
