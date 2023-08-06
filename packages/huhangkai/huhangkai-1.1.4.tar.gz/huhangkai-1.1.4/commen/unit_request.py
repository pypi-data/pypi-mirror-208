import re
import requests
import json
import time
import urllib
import os
import hashlib

from requests import ReadTimeout, ConnectTimeout
from requests.exceptions import MissingSchema
from urllib.parse import urlencode
from commen.unit_dict import Dict
from commen.unit_logger import logger
from openpyxl.reader.excel import load_workbook
from commen import admin_host, projects_path, files_path


def get_url(url, kwargs):
    tmp = re.findall(r'\{.+}', url)
    if not tmp:
        return url
    if kwargs.get(tmp[0][1:-1]):
        url = url.replace(tmp[0], kwargs.get(tmp[0][1:-1]))
        url = url.split('{')[0]
        return url
    else:
        assert False, "字段：" +tmp[0][1:-1] + "，为必填字段"


def unit_http_requester(method, url, params=None, data=None, headers=None, host=None, timeout=10000, init_headers={},
                        _route="", _files=None, **kwargs):
    if headers.get("headers"):
        _headers = init_headers
        tmp = headers.pop("headers")
        _headers.update(headers)
        if isinstance(tmp, dict):
            _headers.update(tmp)
    else:
        headers.pop("headers")
        _headers = headers

    if url[0] == '/' and host:
        if _route and _route[0] != '/':
            _route = '/' + _route
        url = host + _route + url
    if method.upper() == "GET":
        params = params or data
    logger.info("接口请求参数method: %s, url: %s" % (method, url))
    logger.info("接口请求参数headers: %s" % str(_headers))
    logger.info("接口请求参数params: %s" % str(params)) if params else logger.info("接口请求参数data: %s" % str(data))
    if "//" not in url:
        assert False, "url没有域名"
    time_s = time.time()
    try:
        if "application/x-www-form-urlencoded" in str(_headers):
            data = urlencode(data)
        if "multipart/form-data" in str(_headers) and "file" in data.keys():
            file = str(data.pop("file"))
            if not os.path.isfile(file):
                try:
                    out = requests.get(admin_host + '/files/file/', params={"value": file})
                    if "filename=" in str(out.raw.headers):
                        file_name = urllib.parse.unquote(re.findall(r'filename=(.+?)\'', str(out.raw.headers))[0])
                        file = os.path.join(files_path, file_name)
                        with open(file, 'wb') as f:
                            f.write(out.content)
                except:
                    pass
                if os.path.isfile(file):
                    pass
                elif os.path.isfile(os.path.join(files_path, file)):
                    file = os.path.join(files_path, file)
                elif os.path.isfile(os.path.join(projects_path, file)):
                    file = os.path.join(projects_path, file)
                else:
                    assert False, "对应的文件不存在"
            data.update({'md5': hashlib.md5('%d_%d'.encode() % (0, int(time.time()))).hexdigest(),
                         'filesize': len(open(file, 'rb').read()),})
            _files = {"file": (os.path.basename(file), open(file, 'rb'))} if file else {}
            try:
                del _headers['Content-Type']
            except:
                pass
            res = requests.request(method, url, params=params, data=data, files=_files,
                                   headers=_headers, timeout=timeout / 1000, verify=False)
        else:
            res = requests.request(method, url, params=params, json=data, headers=_headers, timeout=timeout / 1000, verify=False)

        logger.info("接口响应时间: %.3f毫秒" % (time.time() - time_s))
        try:
            res.rsp = Dict(json.loads(res.text)) if res.text else Dict({"code": -1, "msg": "该接口返回的数据为空字符串"})
        except:
            if "filename=" in str(res.raw.headers):
                file_name = urllib.parse.unquote(re.findall(r'filename=(.+?)\'', str(res.raw.headers))[0])
                if "xlsx" in file_name:
                    file_path = os.path.join(files_path, file_name)
                    with open(file_path, 'wb') as f:
                        f.write(res.content)
                    wb = load_workbook(file_path)
                    ws = wb.active
                    rows = [[cell.value for cell in row] for row in ws]
                    try:
                        data = [{c1: c2 for c1, c2 in zip(rows[0], row)} for row in rows[1:]]
                    except:
                        data = []
                    os.remove(file_path)
                    res.rsp = Dict({"code": 0, "data": data, "filename": file_name, "rows": rows})
                else:
                    res.rsp = res.text
            else:
                res.rsp = res.text
        logger.info("接口返回http_code: %s" % res.status_code)
        logger.info("接口数据res: %s" % str(res.rsp))
        return res
    except ReadTimeout:
        assert False, "接口响应时间%.3f秒, 超过设置的时间%.3f秒" % (time.time() - time_s, timeout / 1000)
    except ConnectTimeout:
        assert False, "接口响应时间%.3f秒, 超过设置的时间%.3f秒" % (time.time() - time_s, timeout / 1000)
    except MissingSchema:
        assert False, "url不对，无域名"
    except Exception as e:
        print(e)
        assert False, "调用接口报错"


def get_variable(app_key, env):
    project = requests.post(admin_host + '/variable/variable/',
                            json={"app_key": app_key, "environment": env}).json()
    _variable = {}
    print(admin_host)
    print(project)
    for v in project.get('variables', []):
        if v.get('type') == 0:
            _variable[v.get('name')] = v.get('value')
        elif v.get('type') == 1:
            _variable[v.get('name')] = json.loads(v.get('value'))
        elif v.get('type') == 2:
            _variable[v.get('name')] = int(json.loads(v.get('value')))
    return _variable