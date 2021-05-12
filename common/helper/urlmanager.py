# -*- coding: utf-8 -*-
from flask import current_app, url_for, request, redirect
from urllib.parse import urlparse, urljoin
import time


class UrlManager(object):
    def __init__(self):
        pass

    @classmethod
    def makeup_static_url(cls, filename):
        release_version = current_app.config['RELEASE_VERSION']
        ver = "%s" % (int(time.time())) if not release_version else release_version
        return url_for('static', filename=filename, ver=ver)

    @classmethod
    def makeup_image_url(cls, filename):
        if len(filename) < 1:
            return False
        if filename.startswith('http://') or filename.startswith('https://'):
            return filename
        return current_app.config['IMAGE_URL_PREFIX'] + filename


def redirect_back(default='manage.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
