from flask import render_template
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

    def __get_interface_page_for_get_request__(self):
        no_scan_started = CurrentScan.scan is None

        # Check if an unsaved scan is still stored and
        # the scan has been stopped
        if self.controller.last_scan_result and not self.controller.is_scan_in_background:
            return render_template(
                self.results_template,
                sections=self.sections,
                past_scan_available=True,
                save_disabled=no_scan_started,
                scan_result=self.controller.get_formatted_results(),
                current_section=self.name,
                tool=self.tool_name,
                stopped=True,
            )

        return super().__get_interface_page_for_get_request__()

    def __get_interface_page_for_post_request__(self, request):
        if request.form.get("new_scan_requested"):
            self.controller.delete_scan()

        # Check if a past scan needs to be restored
        if request.form.get("load_previous_results"):
            if CurrentScan.scan is not None and CurrentScan.scan.get_tool_scan(
                self.tool_name
            ):
                self.controller.last_scan_result = CurrentScan.scan.get_tool_scan(
                    self.tool_name
                )

                return render_template(
                    self.results_template,
                    sections=self.sections,
                    past_scan_available=True,
                    save_disabled=True,
                    scan_result=self.controller.restore_last_scan(),
                    current_section=self.name,
                    tool=self.tool_name,
                    stopped=True,
                )

        return super().__get_interface_page_for_post_request__(request)

    def save_results(self):
        if CurrentScan.scan is not None:
            self.controller.__retrieve_complete_scan__()
            CurrentScan.scan.save_scan(self.tool_name, self.controller.last_scan_result)
            self.controller.last_scan_result = None
            return "<p>Results successfully saved.</p>"
        return "<p>No scan started.</p>"
