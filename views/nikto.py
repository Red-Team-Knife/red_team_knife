from views.view import BaseBlueprint

class NiktoBlueprint(BaseBlueprint):
    def __init__(self, name, import_name, controller, display_name, interface_template, results_template, scan_options, sections):
        super().__init__(
            name,
            import_name,
            controller,
            display_name,
            interface_template,
            results_template,
            scan_options,
            sections,
        )

    # Nikto returns plain text, so we use the base formatter
    def __format_html__(self, results):
        return f"<pre>{results}</pre>"
