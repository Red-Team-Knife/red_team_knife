from flask import Blueprint, render_template


class TipsPageBlueprint(Blueprint):
    def __init__(self, name, import_name, template, sections):
        super().__init__(name, import_name)
        self.template = template
        self.sections = sections
        self.route("/" + name, methods=["GET"])(self.interface)

    def interface(self):
        return render_template(self.template, sections=self.sections)
