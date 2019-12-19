import cherrypy

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

class TemplateHandler:
    def __init__(self, template_dir):
        self.lookup = TemplateLookup(template_dir, module_directory=template_dir)
        self.templateMethods = {
            "login": [
                self._create_login_site,
                "login.html"
            ],
            "index": [
                "index.html"
            ]
        }

    def create_form(self, form_name):
        return self.lookup.get_template(f"form_{form_name}.html").render()

    def _create_login_site(self, templateName, data, userId = None):
        try:
            template = self.lookup.get_template(templateName)
            formMarkup = self.create_form(data["form"])

            markup = template.render(form = formMarkup, error = data["error"])
        except:
            print(exceptions.text_error_template().render())
            markup = exceptions.html_error_template().render()
        return markup

    def create_view(self, type, data, userId = None):
        markup = ""
        if type in self.templateMethods:
            templateName = self.templateMethods[type][1]
            method = self.templateMethods[type][0] # Call create method.
            markup += method(templateName, data, userId)
        return markup