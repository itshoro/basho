# -*- coding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1576761259.5703487
_enable_loop = True
_template_filename = 'C:/Development/vsy_pax-counter/client_app/templates/login.html'
_template_uri = 'login.html'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        form = context.get('form', UNDEFINED)
        error = context.get('error', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('<!DOCTYPE html>\r\n<html lang="en">\r\n<head>\r\n    <meta charset="UTF-8">\r\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\r\n    <meta http-equiv="X-UA-Compatible" content="ie=edge">\r\n    <title>Document</title>\r\n\r\n    <script src="scripts/main.js"></script>\r\n    <link rel="stylesheet" href="style/style.css">\r\n')
        if error != None:
            __M_writer('    <script>\r\n        document.addEventListener("DOMContentLoaded", () => {createError("')
            __M_writer(str(error))
            __M_writer('")});\r\n    </script>\r\n')
        __M_writer('</head>\r\n<body>\r\n    <nav>\r\n        <a href="/" class="logo">BASHO</a>\r\n    </nav>\r\n    <div class="splash_grid">\r\n        <div class="login_wrapper">\r\n            ')
        __M_writer(str(form))
        __M_writer('\r\n        </div>\r\n\r\n        <div class="advert">\r\n            <h1>Track your workplace. Find Hotspots.</h1>\r\n            <h3>Monitor movement to improve flow, stop congestion before it even happens.</h3>\r\n        </div>\r\n    </div>\r\n</body>\r\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "C:/Development/vsy_pax-counter/client_app/templates/login.html", "uri": "login.html", "source_encoding": "ascii", "line_map": {"16": 0, "23": 1, "24": 11, "25": 12, "26": 13, "27": 13, "28": 16, "29": 23, "30": 23, "36": 30}}
__M_END_METADATA
"""
