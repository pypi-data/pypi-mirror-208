# -*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import arthub_api
import pytest
import sys
import logging
from arthub_api import arthub_api_config
from . import _utils
import requests
import os
from arthub_api import (
    BladeAPI,
    Client,
    BladeCOSApi,
)
import six


def on_api_failed(res):
    logging.error("[TEST][API][API] \"%s\" failed, error: %s" % (res.url, res.error_message()))


def init_api(env, login=True):
    api = BladeAPI(_utils.get_config(env), False)
    if login:
        res = api.login(arthub_api_config.account_email, arthub_api_config.password)
        assert res.is_succeeded()
    return api

def print_percent(current, total):
    progress = (current / total) * 100
    filled_length = int(progress * 50 // 100)
    bar = "=" * filled_length + "-" * (50 - filled_length)
    print("\rProgress: |{bar}| {progress:.2f}% Complete".format(bar=bar, progress=progress), end="")
    if six.PY2:
        sys.stdout.flush()
    
    
def network_downloader(target, local):
    class TmpSigner(object):    
        def get_download_url(self, bucket, key):
            # this will returns a url expires in 10 minutes
            return target
        def get_file_size(self, bucket, key):
            # this will returns a url expires in 10 minutes
            with requests.get(target, stream=True) as r:
                return int(r.headers["Content-length"])
        
    cli = Client(TmpSigner())
    cli.download_file("xx", "xx", local, progress_callback=print_percent)

def test_simple_downloader(tmp_path):
    target = "https://arthub.woa.com/downloads/ImpressionStation_v2.0.0/img/desktopBg.1d6d3b5a.png"
    local = os.path.join(str(tmp_path), "tmp.png")
    network_downloader(target, local)

def test_downloader(tmp_path):
    target = "https://dldir1.qq.com/arthub/desktop/versions/ArtHub-1.12.0.dmg"
    local = os.path.join(str(tmp_path), "tmp.dmg")
    network_downloader(target, local)

def test_blade_downloader(env, tmp_path):
    blade_api = init_api(env)
    target = "pkg_distribution/7z/arthub_api/1.4.1/arthub_api.7z"
    local = os.path.join(str(tmp_path), "tmp.7z")
        
    cli = BladeCOSApi(api=blade_api)
    cli.download_file(target, local)
    
def test_blade_uploader_fail(env, tmp_path):
    blade_api = init_api(env)
    target = "pkg_distribution/7z/arthub_test_pkg/0.0.1/arthub_test_pkg.7z"
    source = os.path.join(str(tmp_path), "tmp.7z")
        
    cli = BladeCOSApi(api=blade_api)
    cli.download_file(target,source)
    try:
        cli.upload_file(target, source)
    except RuntimeError:
        # expected condition:
        return
    # package should already uploaded, an error should be raised
    assert False 

def test_blade_check_exists(env, tmp_path):
    blade_api = init_api(env)
    target = "pkg_distribution/7z/arthub_test_pkg/0.0.2/arthub_test_pkg.7z"
    cli = BladeCOSApi(api=blade_api, force=True)
    assert cli.check_file_exist(target)

def test_blade_get_download_url(env, tmp_path):
    blade_api = init_api(env)
    target = "pkg_distribution/7z/arthub_test_pkg/0.0.2/arthub_test_pkg.7z"
    cli = BladeCOSApi(api=blade_api, force=True)
    assert cli.get_download_url(target)
    
def test_blade_uploader(env, tmp_path):
    blade_api = init_api(env)
    target = "pkg_distribution/7z/arthub_test_pkg/0.0.2/arthub_test_pkg.7z"
    source = os.path.join(str(tmp_path), "tmp.7z")
        
    cli = BladeCOSApi(api=blade_api, force=True)
    cli.download_file(target,source)
    cli.upload_file(target, source, print_percent)
        
def test_blade_uploader_bigfile(env, tmp_path):
    blade_api = init_api(env)
    
    cli = BladeCOSApi(api=blade_api, force=True)
    target = "pkg_distribution/7z/pyqt/5.15.2-ng.1/pyqt.7z"
    source = os.path.join(str(tmp_path), "tmpbig.7z")
    cli.download_file(target,source)
    
    target = "pkg_distribution/7z/arthub_test_pkg/0.0.1/arthub_test_pkg.7z"
    def print_percent1(a, b):
        print_percent(a, b)
        if a > b/2:
            import os
            os.exit(1)
    cli.upload_file(target, source, print_percent)
        