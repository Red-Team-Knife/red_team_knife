from views.web_target import WebTargetBlueprint


class SmtpEmailSpooferBlueprint(WebTargetBlueprint):
    def __format_result__(self, *args, **kwargs):
        self.controller.__remove_temp_file__()
        return '<p>Operation completed, check terminal for more inforamtion.</p>'
