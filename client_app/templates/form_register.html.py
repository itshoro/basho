# -*- coding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1576758294.0044515
_enable_loop = True
_template_filename = 'C:/Development/vsy_pax-counter/client_app/templates/form_register.html'
_template_uri = 'form_register.html'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer('<form class="login">\r\n    <h1>Register</h1>\r\n    <div class="input"><input type="text" placeholder="E-Mail" name="email"></div>\r\n    <div class="input"><input type="password" placeholder="Password" name="password"></div>\r\n    <div class="input"><input type="password" placeholder="Repeat Password" name="passwordSafety"></div>\r\n    <div>\r\n        <input type="button" onclick="register()" value="Register">\r\n        <input type="button" class="link" onclick="toggleRegisterForm()" value="I already have an account">\r\n    </div>\r\n</form>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "C:/Development/vsy_pax-counter/client_app/templates/form_register.html", "uri": "form_register.html", "source_encoding": "ascii", "line_map": {"16": 0, "21": 1, "27": 21}}
__M_END_METADATA
"""
