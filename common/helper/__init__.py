# -*- coding: utf-8 -*-
from flask import g, render_template
import cgi


def ops_render(template, context={}):
    if 'current_user' in g:
        context['current_user'] = g.current_user
    return render_template(template, **context)
