from controllers.w4af_audit import W4afAuditController
from current_scan import CurrentScan
from views.view import BaseBlueprint


class W4afBlueprint(BaseBlueprint):
    def __init__(
        self,
        name,
        import_name,
        controller: W4afAuditController,
        tool_name: str,
        interface_template: str,
        results_template: str,
        options_list: list,
        sections: dict,
    ):
        super().__init__(
            name,
            import_name,
            controller,
            tool_name,
            interface_template,
            results_template,
            options_list,
            sections,
        )
        self.controller: W4afAuditController

    def __get_interface_page_for_post_request__(self, request):
        if request.form.get("new_scan_requested"):
            self.controller.delete_scan()

        return super().__get_interface_page_for_post_request__(request)

    def save_results(self):
        if CurrentScan.scan is not None:
            self.controller.__retrieve_complete_scan__()
            CurrentScan.scan.save_scan(self.tool_name, self.controller.last_scan_result)
            self.controller.last_scan_result = None
            return "<p>Results successfully saved.</p>"
        return "<p>No scan started.</p>"
