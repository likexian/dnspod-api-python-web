#!/usr/bin/env python
# -*- coding:utf-8 -*-

##
# DNSPod API Flask Web 示例
# https://www.likexian.com/
#
# Copyright 2011-2019, Li Kexian
# Released under the Apache License, Version 2.0
#
##


import ssl
import json
import requests
from flask import session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


class utils:
    @staticmethod
    def get_template(template):
        text = utils.read_text('./template/%s.html' % template)
        master = utils.read_text('./template/index.html')
        master = master.replace('{{content}}', text)
        return master

    @staticmethod
    def read_text(fname):
        fp = open(fname, 'r')
        text = fp.read().decode('utf-8')
        fp.close()
        return text

    @staticmethod
    def html_wrap(fn):
        import functools

        @functools.wraps(fn)
        def wrap(*args, **kargs):
            try:
                r = fn(*args, **kargs)
                return r
            except DNSPodException, e:
                text = utils.get_template('message')
                text = text.replace('{{title}}', u'操作成功' if e.status == 'success' else u'操作失败')
                text = text.replace('{{status}}', e.status)
                text = text.replace('{{message}}', e.message)
                text = text.replace('{{url}}', e.url)
                return text
            except Exception, e:
                return str(e)
        return wrap


class DNSPodException(Exception):
    def __init__(self, status, message, url):
        self.status = status
        self.message = message
        self.url = str(url)


class dnspod(object):
    grade_list = {
        'D_Free': u'免费套餐',
        'D_Plus': u'豪华 VIP套餐',
        'D_Extra': u'企业I VIP套餐',
        'D_Expert': u'企业II VIP套餐',
        'D_Ultra': u'企业III VIP套餐',
        'DP_Free': u'新免费套餐',
        'DP_Plus': u'个人专业版',
        'DP_Extra': u'企业创业版',
        'DP_Expert': u'企业标准版',
        'DP_Ultra': u'企业旗舰版',
    }

    status_list = {
        'enable': u'启用',
        'pause': u'暂停',
        'spam': u'封禁',
        'lock': u'锁定',
    }

    def api_call(self, api, data):
        if not api or not isinstance(data, dict):
            raise DNSPodException('danger', u'内部错误：参数错误', '')

        api = 'https://dnsapi.cn/' + api
        data.update({'login_email': session['login_email'], 'login_password': session['login_password'],
            'login_code': session['login_code'], 'format': 'json', 'lang': 'cn', 'error_on_empty': 'no'})

        results = self.post_data(api, data, session.get('cookies', ''))
        code = int(results.get('status', {}).get('code', 0))
        if code not in [1, 50]:
            raise DNSPodException('danger', results.get('status', {}).get('message', u'内部错误：未知错误'), '')

        return results

    def post_data(self, api, data, cookies):
        try:
            request = requests.Session()
            request.mount('https://', MyAdapter())
            headers = {'User-Agent': 'DNSPod API Flask Web Client/1.0.0 (i@likexian.com)'}
            response = request.post(api, data=data, headers=headers, cookies=cookies, timeout=30)
            results = json.loads(response.text)
        except:
            raise DNSPodException('danger', u'内部错误：调用失败', '')

        if hasattr(response, 'cookies'):
            for i in response.cookies:
                    if i.name[0] == 't':
                        session['cookies'] = {i.name: i.value}

        return results
