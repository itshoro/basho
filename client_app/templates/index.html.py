# -*- coding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1582799132.1913815
_enable_loop = True
_template_filename = 'C:/Development/vsy_pax-counter/client_app/templates/index.html'
_template_uri = 'index.html'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer('<!DOCTYPE html>\r\n<html lang="en">\r\n<head>\r\n    <meta charset="UTF-8">\r\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\r\n    <meta http-equiv="X-UA-Compatible" content="ie=edge">\r\n    <title>Document</title>\r\n\r\n    <link rel="stylesheet" href="style/style.css">\r\n    <script src="scripts/main.js"></script>\r\n    <script src="scripts/index.js"></script>\r\n</head>\r\n<body>\r\n    <div id="wrapper"></div>\r\n</body>\r\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "C:/Development/vsy_pax-counter/client_app/templates/index.html", "uri": "index.html", "source_encoding": "ascii", "line_map": {"16": 0, "21": 2, "27": 21}}
__M_END_METADATA
"""
