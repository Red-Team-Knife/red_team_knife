from views.web_target_view import WebTargetBlueprint


class SmtpEmailSpooferBlueprint(WebTargetBlueprint):
    def __format_result__(self):
        self.controller.__remove_temp_file__()
        return '<p>Operation completed, check terminal for more inforamtion.</p>'