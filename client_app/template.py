import cherrypy

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

class TemplateHandler:
    def __init__(self, template_dir):
        self.lookup = TemplateLookup(template_dir, module_directory=template_dir)
        self.templateMethods = {
            "login": [
                self.create_login_form(),
                "login_form.html"
            ],
            "register": [
                self.create_register_form(),
                "register_form.html"
            ],
            "index": [
                "index.html"
            ]
        }

    def create_login_form(self, context, data, userId):
        pass

    def create_form(self, context):
        try:
            template = self.lookup.get_template("login.html")
            

    def create_register_form(self, context, data, userId):
        pass

    def create_view(self, type, data, userId = None):
        markup = ""
        if type in self.templateMethods:
            context = self.templateMethods[type][1]
            markup += self.templateMethods[type][0](context, data, userId) # Call create method.

        return markup