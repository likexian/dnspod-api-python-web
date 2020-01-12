# DNSPod API Python Web 示例

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 功能说明

用 Python 实现了一个 DNSPod API 的 Web 示例，已完成对域名和记录的基本操作，可直接使用。

*已调整为只支持通过 Token 登录，请到 DNSPod 用户中心创建 API Token 获取 Token ID 及 Token Key。*

功能包括：
- 用户登录
- 域名列表
- 域名暂停/启用
- 域名添加
- 域名删除
- 记录列表
- 记录暂停/启用
- 记录添加
- 记录修改
- 记录删除

## 环境要求

- Python2.x/3.x
- flask
- requests

## 安装说明

下载代码库之后，在当前目录运行

    $ python app.py

您还可以通过 pip 来安装并测试

    $ pip install dnspod-web
    $ dnspod-web

然后在浏览器中打开 http://127.0.0.1:5000/ 即可查看示例。

## DEMO

请打开 [demo](demo) 目录查看相关截图。

## LICENSE

Copyright 2011-2020 Li Kexian

Licensed under the Apache License 2.0

## About

- [Li Kexian](https://www.likexian.com/)
