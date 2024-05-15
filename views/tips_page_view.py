from flask import Blueprint, render_template


class TipsPageBlueprint(Blueprint):
    def __init__(self, name, import_name, template, sections, title, next_tip_name):
        super().__init__(name, import_name)
        self.template = template
        self.sections = sections
        self.title = title
        self.next_tip_name = next_tip_name
        self.route("/" + name, methods=["GET"])(self.interface)

    def interface(self):
        return render_template(self.template, title=self.title, sections=self.sections, next_tip_name= self.next_tip_name)
