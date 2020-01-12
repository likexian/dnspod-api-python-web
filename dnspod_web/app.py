#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
 ' Copyright 2011-2020 Li Kexian
 '
 ' Licensed under the Apache License, Version 2.0 (the "License");
 ' you may not use this file except in compliance with the License.
 ' You may obtain a copy of the License at
 '
 '     http://www.apache.org/licenses/LICENSE-2.0
 '
 ' Unless required by applicable law or agreed to in writing, software
 ' distributed under the License is distributed on an "AS IS" BASIS,
 ' WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 ' See the License for the specific language governing permissions and
 ' limitations under the License.
 '
 ' DNSPod API Python Web 示例
 ' https://www.likexian.com/
 '''

import os
from flask import Flask
from flask import request
from flask import send_from_directory
from flask import session
import dnspod


app = Flask('app')
dnspod_api = dnspod.dnspod()
base_dir = os.path.dirname(os.path.realpath(__file__))


@app.route('/css/bootstrap.css')
def favicon():
    return send_from_directory(os.path.join(base_dir, 'css'), 'bootstrap.css')


@app.route('/', methods=['GET'])
@dnspod.utils.html_wrap
def get_login():
    text = dnspod.utils.get_template(base_dir, 'login')
    text = text.replace('{{title}}', u'用户登录')
    return text


@app.route('/domainlist', methods=['GET', 'POST'])
@dnspod.utils.html_wrap
def get_domainlist():
    if request.method == 'POST':
        if not request.form['token_id']:
            raise dnspod.DNSPodException('danger', u'请输入Token ID。', -1)
        else:
            session['token_id'] = request.form['token_id']

        if not request.form['token_key']:
            raise dnspod.DNSPodException('danger', u'请输入Token Key。', -1)
        else:
            session['token_key'] = request.form['token_key']

    response = dnspod_api.api_call('Domain.List', {})

    list_text = ''
    domain_sub = dnspod.utils.read_text(base_dir+'/template/domain_sub.html')
    for domain in response['domains']:
        list_sub = domain_sub.replace('{{id}}', str(domain['id']))
        list_sub = list_sub.replace('{{domain}}', domain['name'])
        list_sub = list_sub.replace('{{grade}}', dnspod_api.grade_list[domain['grade']])
        list_sub = list_sub.replace('{{status}}', dnspod_api.status_list[domain['status']])
        list_sub = list_sub.replace('{{status_new}}', 'enable' if domain['status'] == 'pause' else 'disable')
        list_sub = list_sub.replace('{{status_text}}', u'启用' if domain['status'] == 'pause' else u'暂停')
        list_sub = list_sub.replace('{{records}}', domain['records'])
        list_sub = list_sub.replace('{{updated_on}}', domain['updated_on'])
        list_text += list_sub

    text = dnspod.utils.get_template(base_dir, 'domain')
    text = text.replace('{{title}}', u'域名列表')
    text = text.replace('{{list}}', list_text)
    return text


@app.route('/domaincreate', methods=['POST'])
@dnspod.utils.html_wrap
def post_domaincreate():
    if not request.form['domain']:
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    dnspod_api.api_call('Domain.Create', {'domain': request.form['domain']})

    raise dnspod.DNSPodException('success', u'添加成功。', '/domainlist')


@app.route('/domainstatus', methods=['GET', 'POST'])
@dnspod.utils.html_wrap
def get_domainstatus():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)
    if not request.args.get('status'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    dnspod_api.api_call('Domain.Status', {'domain_id': request.args.get('domain_id'),
        'status': request.args.get('status')})

    raise dnspod.DNSPodException('success',
        (u'启用' if request.args.get('status') == 'enable' else u'暂停') + u'成功。', '/domainlist')


@app.route('/domainremove', methods=['GET', 'POST'])
@dnspod.utils.html_wrap
def get_domainremove():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    dnspod_api.api_call('Domain.Remove', {'domain_id': request.args.get('domain_id')})

    raise dnspod.DNSPodException('success', u'删除成功。', '/domainlist')


@app.route('/recordlist', methods=['GET'])
@dnspod.utils.html_wrap
def get_recordlist():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    response = dnspod_api.api_call('Record.List', {'domain_id': request.args.get('domain_id')})
    list_text = ''
    domain_sub = dnspod.utils.read_text(base_dir+'/template/record_sub.html')
    for record in response['records']:
        list_sub = domain_sub.replace('{{domain_id}}', request.args.get('domain_id'))
        list_sub = list_sub.replace('{{id}}', str(record['id']))
        list_sub = list_sub.replace('{{name}}', record['name'])
        list_sub = list_sub.replace('{{value}}', record['value'])
        list_sub = list_sub.replace('{{type}}', record['type'])
        list_sub = list_sub.replace('{{line}}', record['line'])
        list_sub = list_sub.replace('{{enabled}}', u'启用' if int(record['enabled']) else u'暂停')
        list_sub = list_sub.replace('{{status_new}}', 'disable' if int(record['enabled']) else 'enable')
        list_sub = list_sub.replace('{{status_text}}', u'暂停' if int(record['enabled']) else u'启用')
        list_sub = list_sub.replace('{{mx}}', record['mx'])
        list_sub = list_sub.replace('{{ttl}}', record['ttl'])
        list_sub = list_sub.replace('{{remark}}', record['remark'])
        list_text += list_sub

    text = dnspod.utils.get_template(base_dir, 'record')
    text = text.replace('{{title}}', u'记录列表 - %s' % (response['domain']['name']))
    text = text.replace('{{list}}', list_text)
    text = text.replace('{{domain_id}}', str(response['domain']['id']))
    text = text.replace('{{grade}}', response['domain']['grade'])
    return text


@app.route('/recordcreatef', methods=['GET'])
@dnspod.utils.html_wrap
def get_recordcreatef():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    if 'type_' + request.args.get('grade') not in session:
        response = dnspod_api.api_call('Record.Type', {'domain_grade': request.args.get('grade')})
        session['type_' + request.args.get('grade')] = response['types']

    if 'line_' + request.args.get('domain_id') not in session:
        response = dnspod_api.api_call('Record.Line',
            {'domain_id': request.args.get('domain_id'), 'domain_grade': request.args.get('grade')})
        session['line_' + request.args.get('domain_id')] = response['lines']

    type_list = ''
    for value in session['type_' + request.args.get('grade')]:
        type_list += '<option value="%s">%s</option>' % (value, value)

    line_list = ''
    for value in session['line_' + request.args.get('domain_id')]:
        line_list += '<option value="%s">%s</option>' % (value, value)

    text = dnspod.utils.get_template(base_dir, 'recordcreatef')
    text = text.replace('{{title}}', u'添加记录')
    text = text.replace('{{action}}', 'recordcreate')
    text = text.replace('{{domain_id}}', request.args.get('domain_id'))
    text = text.replace('{{record_id}}', request.args.get('record_id', ''))
    text = text.replace('{{type_list}}', type_list)
    text = text.replace('{{line_list}}', line_list)
    text = text.replace('{{sub_domain}}', '')
    text = text.replace('{{value}}', '')
    text = text.replace('{{mx}}', '10')
    text = text.replace('{{ttl}}', '600')
    text = text.replace('{{remark}}', '')
    return text


@app.route('/recordcreate', methods=['POST'])
@dnspod.utils.html_wrap
def post_recordcreate():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    sub_domain = None
    if not request.form.get('sub_domain'):
        sub_domain = '@'

    if not request.form.get('value'):
        raise dnspod.DNSPodException('danger', u'请输入记录值。', -1)

    mx = None
    if request.form.get('type') == 'MX' and not request.form.get('mx'):
        mx = 10

    ttl = None
    if not request.form.get('ttl'):
        ttl = 600

    response = dnspod_api.api_call('Record.Create',
        {'domain_id': request.args.get('domain_id'),
        'sub_domain': sub_domain or request.form['sub_domain'],
        'record_type': request.form['type'],
        'record_line': request.form['line'],
        'value': request.form['value'],
        'mx': mx or request.form['mx'],
        'ttl': ttl or request.form['ttl']}
    )

    if request.form['remark'] != "":
        dnspod_api.api_call('Record.Remark',
            {'domain_id': request.args.get('domain_id'),
            'record_id': response['record']['id'],
            'remark': request.form['remark'],
            }
        )

    raise dnspod.DNSPodException('success', u'添加成功。', '/recordlist?domain_id=%s' % request.args.get('domain_id'))


@app.route('/recordeditf', methods=['GET'])
@dnspod.utils.html_wrap
def get_recordeditf():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)
    if not request.args.get('record_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    record = dnspod_api.api_call('Record.Info', {'domain_id': request.args.get('domain_id'),
        'record_id': request.args.get('record_id')})
    record = record['record']

    if 'type_' + request.args.get('grade') not in session:
        response = dnspod_api.api_call('Record.Type', {'domain_grade': request.args.get('grade')})
        session['type_' + request.args.get('grade')] = response['types']

    if 'line_' + request.args.get('domain_id') not in session:
        response = dnspod_api.api_call('Record.Line',
            {'domain_id': request.args.get('domain_id'), 'domain_grade': request.args.get('grade')})
        session['line_' + request.args.get('domain_id')] = response['lines']

    type_list = ''
    for value in session['type_' + request.args.get('grade')]:
        type_list += '<option value="%s" %s>%s</option>' % (value,
            'selected="selected"' if record['record_type'] == value else '', value)

    line_list = ''
    for value in session['line_' + request.args.get('domain_id')]:
        line_list += '<option value="%s" %s>%s</option>' % (value,
        'selected="selected"' if record['record_line'] == value else '', value)

    text = dnspod.utils.get_template(base_dir, 'recordcreatef')
    text = text.replace('{{title}}', u'修改记录')
    text = text.replace('{{action}}', 'recordedit')
    text = text.replace('{{domain_id}}', request.args.get('domain_id'))
    text = text.replace('{{record_id}}', request.args.get('record_id'))
    text = text.replace('{{type_list}}', type_list)
    text = text.replace('{{line_list}}', line_list)
    text = text.replace('{{sub_domain}}', record['sub_domain'])
    text = text.replace('{{value}}', record['value'])
    text = text.replace('{{mx}}', record['mx'])
    text = text.replace('{{ttl}}', record['ttl'])
    text = text.replace('{{remark}}', record['remark'])
    return text


@app.route('/recordedit', methods=['POST'])
@dnspod.utils.html_wrap
def post_recordedit():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)
    if not request.args.get('record_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    sub_domain = None
    if not request.form.get('sub_domain'):
        sub_domain = '@'

    if not request.form.get('value'):
        raise dnspod.DNSPodException('danger', u'请输入记录值。', -1)

    mx = None
    if request.form.get('type') == 'MX' and not request.form.get('mx'):
        mx = 10

    ttl = None
    if not request.form.get('ttl'):
        ttl = 600

    dnspod_api.api_call('Record.Modify',
        {'domain_id': request.args.get('domain_id'),
        'record_id': request.args.get('record_id'),
        'sub_domain': sub_domain or request.form['sub_domain'],
        'record_type': request.form['type'],
        'record_line': request.form['line'],
        'value': request.form['value'],
        'mx': mx or request.form['mx'],
        'ttl': ttl or request.form['ttl']}
    )

    if request.form['remark'] != request.form['oremark']:
        dnspod_api.api_call('Record.Remark',
            {'domain_id': request.args.get('domain_id'),
            'record_id': request.args.get('record_id'),
            'remark': request.form['remark'],
            }
        )

    raise dnspod.DNSPodException('success', u'修改成功。', '/recordlist?domain_id=%s' % request.args.get('domain_id'))


@app.route('/recordremove', methods=['GET'])
@dnspod.utils.html_wrap
def get_recordremove():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)
    if not request.args.get('record_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    dnspod_api.api_call('Record.Remove',
        {'domain_id': request.args.get('domain_id'),
        'record_id': request.args.get('record_id')}
    )

    raise dnspod.DNSPodException('success', u'删除成功。', '/recordlist?domain_id=%s' % request.args.get('domain_id'))


@app.route('/recordstatus', methods=['GET'])
@dnspod.utils.html_wrap
def get_recordstatus():
    if not request.args.get('domain_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)
    if not request.args.get('record_id'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)
    if not request.args.get('status'):
        raise dnspod.DNSPodException('danger', u'参数错误。', -1)

    dnspod_api.api_call('Record.Status',
        {'domain_id': request.args.get('domain_id'),
        'record_id': request.args.get('record_id'),
        'status': request.args.get('status')}
    )

    raise dnspod.DNSPodException('success', (u'启用' if request.args.get('status') == 'enable' else u'暂停') + u'成功。',
        '/recordlist?domain_id=%s' % request.args.get('domain_id'))


def main():
    app.secret_key = '7roTu0tLyfksj48G0rbRb556b3tv94q0'
    app.debug = True
    app.run()


if __name__ == '__main__':
    main()
