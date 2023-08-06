import json
import os.path
import re
import sys
import requests
import time

from commen import admin_host, projects_path, service_path, testcase_path, files_path


class GetApi:
    def __init__(self, api_type=1, value="", name="", yapi_url="", app_key=""):
        """api_type: 0时，value是swagger的api，json的url
                     1时，value值为yapi项目token,
                     2时，value是yapi下载的json文件名，文件放在file目录下,
                     3时，value是yapi的yapi-swagger.json
           name:项目名称，空时默认当前py文件所在文件名上级目录
        """
        self.dir = projects_path
        self.url = admin_host
        self.api_testcase_list = []
        self.api_testcase_file_str = ""
        self.api_testcase_file_path = ""
        self.sql_fun_list = None
        self.name2 = None
        self.api_fun_fun_list = None
        self.api_fun_file_str = None
        self.api_fun_file_path = None
        self.assert_fun_list = None
        self.assert_file_str = None
        self.assert_file_path = None
        self.sql_file_str = None
        self.sql_file_str = None
        self.sql_file_path = None
        self.fun_init_list = None
        self.fun_init_str = None
        self.fun_file_path = None
        self.fun_file_str = None
        self.testcase_dir = ""
        self.api_file_path = ""
        self.service_dir = ""
        self.api_file_str = ""
        self.size_names = ("pageSize", "size")
        self.page_names = ("pageNum", "current")
        self.page_and_size = self.size_names + self.page_names
        self.yapi_url = yapi_url
        self.value = value
        self.api_type = api_type
        self.app_key = app_key
        self.name = name
        self.api_list_old = []
        self.api_list = []
        self.get_project()
        self.run()

    def get_project(self):
        if self.app_key:
            project = requests.post(self.url + '/variable/variable/',
                                    json={"app_key": self.app_key, "environment": "sit"}).json()
            if project.get('project'):
                self.name = project.get('project')[0].get('code')
            else:
                self.name = "demo"

            if project.get('api_settings'):
                self.api_type = project.get('api_settings')[0].get('api_type')
                if self.api_type == 2:
                    self.yapi_file_str = requests.get(self.url + "/media/" +
                                                      project.get('api_settings')[0].get('file')).text
                elif self.api_type in (0, 3):
                    self.value = project.get('api_settings')[0].get('url')
                elif self.api_type == 1:
                    self.yapi_url = project.get('api_settings')[0].get('url').strip()
                    if self.yapi_url[-1] == "/":
                        self.yapi_url = self.yapi_url[:-1]
                    self.value = project.get('api_settings')[0].get('token')
    def run(self):
        """
        创建项目
        """
        # 创建项目目录
        self.set_file_path()
        # 获取已维护api方法接口列表
        self.get_api_fun_list()
        # 获取全量api接口列表
        self.get_api_list()
        # 添加api封装方法
        self.write_api_fun()

    def get_api_fun_list(self):
        """获取已维护方法列表，无则创建文件标题"""
        self.name2 = self.name.title()
        self.api_file_path = os.path.join(self.service_dir, self.name + "_api.py")
        if os.path.exists(self.api_file_path):
            self.api_file_str = self.read_file(self.api_file_path)
        else:
            self.api_file_str = "import allure\n\nfrom service.%s import http_requester\n" \
                                "from commen.unit_request import get_url\n\n\n" % self.name
        tmp = re.findall("def +(.*)?\([\d\D]*?_method = [\"'](.*)?[\"']", self.api_file_str)
        self.api_list_old = re.findall("def +(.*)?\(", self.api_file_str)

        self.fun_file_path = os.path.join(self.service_dir, self.name + "_fun.py")
        if os.path.exists(self.fun_file_path):
            self.fun_file_str = self.read_file(self.fun_file_path)
        else:
            self.fun_file_str = "import requests\n\nfrom commen.unit_fun import FunBase\n" \
                                "from commen import admin_host\n\n\nclass %sFun(FunBase):\n" \
                                "    def __init__(self):\n        super().__init__()\n        self.res = None\n\n" \
                                "    def run_mysql(self, sql_str):\n" \
                                "        # id是后台http://47.96.124.102/admin 项目数据库链接的id\n" \
                                '        out = requests.post(admin_host + "/sql/running_sql/", ' \
                                'json={"id": 1, "sql_str": sql_str}).json()\n' \
                                '        if out.get("code") == "0000":\n' \
                                '            return out.get("data")\n        else:\n' \
                                '            assert False, sql_str + str(out.get("msg"))\n\n\n' \
                                "if __name__ == '__main__':\n    f = %sFun()\n" \
                                '    out = f.run_mysql("SELECT * FROM `t_accept_log`  LIMIT 1;")\n' \
                                '    print(out)\n\n' % (self.name2, self.name2)
        self.fun_init_str = re.findall(r"(def +[\d\D]*?\n)\s*def", self.fun_file_str)[0]
        self.fun_init_list = [i.split('=')[0].strip()[5:] for i in self.fun_init_str.split('\n') if "=" in i]

        self.sql_file_path = os.path.join(self.service_dir, self.name + "_sql.py")
        if os.path.exists(self.sql_file_path):
            self.sql_file_str = self.read_file(self.sql_file_path)
        else:
            self.sql_file_str = "from service.%s.%s_fun import %sFun\n\n\n" % (self.name, self.name, self.name2)
            self.sql_file_str += "class %sSql(%sFun):\n\n\n" \
                                 "if __name__ == '__main__':\n    s = %sSql()\n\n" % (
                self.name2, self.name2, self.name2)
        self.sql_fun_list = re.findall("    def +(.*)?\(", self.sql_file_str)

        self.assert_file_path = os.path.join(self.service_dir, self.name + "_assert.py")
        if os.path.exists(self.assert_file_path):
            self.assert_file_str = self.read_file(self.assert_file_path)
        else:
            self.assert_file_str = "import allure\n\nfrom service.%s.%s_sql import %sSql\n\n\n" % (self.name, self.name, self.name2)
            self.assert_file_str += "class %sAssert(%sSql):\n\n\n" \
                                    "if __name__ == '__main__':\n    s = %sAssert()\n\n" % (
                self.name2, self.name2, self.name2)
        self.assert_fun_list = re.findall("    def +(.*)?\(", self.assert_file_str)

        self.api_fun_file_path = os.path.join(self.service_dir, self.name + "_api_fun.py")
        if os.path.exists(self.api_fun_file_path):
            self.api_fun_file_str = self.read_file(self.api_fun_file_path)
        else:
            self.api_fun_file_str = "from service.%s.%s_assert import %sAssert\n" % (self.name, self.name, self.name2)
            self.api_fun_file_str += "from service.%s import %s_api\n\nimport allure\n" % (self.name, self.name)
            self.api_fun_file_str += "\n\nclass %sApiFun(%sAssert):\n\n" \
                                    "if __name__ == '__main__':\n    s = %sApiFun()\n\n" % (
                                        self.name2, self.name2, self.name2)
        self.api_fun_fun_list = re.findall("    def +(.*)?\(", self.api_fun_file_str)

        self.api_testcase_file_path = os.path.join(self.testcase_dir, "test_api.py")
        if os.path.exists(self.api_testcase_file_path):
            self.api_testcase_file_str = self.read_file(self.api_testcase_file_path)
        else:
            self.api_testcase_file_str = "import pytest\nimport allure\n\n" \
                                         "from service.%s.%s_api_fun import %sApiFun\n\n\n" % (
                self.name, self.name, self.name2)
            self.api_testcase_file_str += '@allure.epic("针对单api的测试")\n@allure.feature("场景：")\nclass TestApi:\n' \
                                          '    def setup(self):\n        self.f = %sApiFun()\n\n' % self.name2
        self.api_testcase_list = re.findall("    def +test_(.*)?\(", self.api_testcase_file_str)

    def set_file_path(self):
        """创建项目目录"""
        if not self.name:
            self.name = os.path.basename(sys.argv[0])
        for path in [service_path, os.path.join(service_path, self.name), 
                     testcase_path, os.path.join(testcase_path,self.name)]:
            if not os.path.exists(path):
                os.makedirs(path)

        self.service_dir = os.path.join(service_path, self.name)
        if not os.path.exists(os.path.join(self.service_dir, "__init__.py")):
            self.write_file(os.path.join(self.service_dir, "__init__.py"), value=self.get_init_value())
        self.testcase_dir = os.path.join(testcase_path, self.name)

    def get_init_value(self):
        """生成项目__init__.py文件"""
        value = 'from commen.init_project import GetApi\n' \
                'from commen.unit_request import unit_http_requester, get_variable\n\n\n' \
                'SERVICE_NAME = "%s"\nZEST_ENV = "SIT"\nAPP_KEY = "%s"\n' \
                '# 环境变量\nvariable = get_variable(APP_KEY, ZEST_ENV)\n' \
                '# 接口超时时间（毫秒）\n\nTIMEOUT = 30000\n\n\n' \
                '# 默认headers\ndef init_headers(**kwargs):\n' \
                '    headers = {"Content-Type": "application/json"}\n' \
                '    host = variable.get(kwargs.get("_host", "HOST"))\n    if host:\n' \
                '        headers.update({"referer": host})\n' \
                '    token = variable.get(kwargs.get("_token", "TOKEN"))\n' \
                '    if token:\n        headers.update({"authorization": token})\n    return headers\n\n\n' \
                'def http_requester(*args, **kwargs):\n    host = variable.get(kwargs.get("_host", "HOST"))\n' \
                '    return unit_http_requester(*args, host=host, timeout=TIMEOUT,' \
                ' init_headers=init_headers(**kwargs), **kwargs)\n\n\n' \
                'if __name__ == "__main__":\n' % (self.name, self.app_key)
        if self.app_key:
            value += "    GetApi(app_key='%s')\n" % (self.app_key,)
        else:
            value += "    GetApi("
            value += "api_type=%s, " % self.api_type if self.api_type else ""
            value += "value='%s', " % self.value if self.value else ""
            value += "name='%s', " % self.name if self.name else ""
            value += "yapi_url='%s', " % self.yapi_url if self.yapi_url else ""
            value = value[:-2] + ")"
        return value

    @staticmethod
    def write_file(file_path, value=""):
        """写文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(value)

    @staticmethod
    def read_file(file_path):
        """读文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            value = f.read()
        return value

    def get_api_list(self):
        """根据api文档不同方式生成api文件"""
        if self.api_type == 1:
            self.get_list_menu()
        elif self.api_type == 2:
            self.get_list_json()
        elif self.api_type == 0:
            self.get_list_menu_swagger()

    def get_list_json(self):
        if self.value:
            file_path = os.path.join(self.dir, 'file', self.value)
            if os.path.exists(file_path):
                value = self.read_file(file_path)
                value = json.loads(value)
                self.api_list = []
                for v in value:
                    self.api_list.extend(v.get('list'))
            else:
                assert not "Yapi的json文件在file中不存在"
        elif self.app_key:
            value = json.loads(self.yapi_file_str)
            self.api_list = []
            for v in value:
                self.api_list.extend(v.get('list'))

    def get_list_menu_swagger(self):
        if self.value:
            try:
                data = requests.get(self.value)
                data = data.json()
                self.api_list = []
                for k, v in data.get("paths", {}).items():
                    api = {}
                    api["path"] = data.get("basePath", "") + k
                    
                    for k2, v2 in v.items():
                        api["method"] = k2
                        api["title"] = v2.get('summary', "")
                        api["up_time"] = int(time.time())
                        api["req_headers"] = []
                        if v2.get('consumes'):
                            api["req_headers"].append(
                                {'name': 'Content-Type', 'value': v2.get('consumes')[0], 'desc': ''})
                        else:
                            api["req_headers"].append(
                                {'name': 'Content-Type', 'value': 'application/x-www-form-urlencoded', 'desc': ''})
                        api["req_params"] = []
                        api["req_query"] = []
                        api["req_body_other"] = []
                        api["res_body"] = []
                        for parameter in v2.get('parameters', []):
                            if parameter.get('in') == "body":
                                if parameter.get('name') not in ("params", "headers"):
                                    if parameter.get("schema") and parameter.get("schema").get("$ref"):
                                        tmp = parameter.get("schema").get("$ref").split("/")
                                        if len(tmp) > 2:
                                            tmp2 = data.get(tmp[1], {}).get(tmp[2], {})
                                            for k3, v3 in tmp2.get('properties', {}).items():
                                                api["res_body"].append({'name': k3, 'desc': v3.get('description', "")})
                                    else:
                                        api["res_body"].append({'name': parameter.get("name"),
                                                                 'desc': parameter.get('description')})
                            elif parameter.get('in') in ("params", "path"):
                                api["req_params"].append({'name': parameter.get("name"),
                                                         'desc': parameter.get('description')})
                            elif parameter.get('in') == "query":
                                if parameter.get('name') not in  ("params", ):
                                    api["req_query"].append({'name': parameter.get("name"),
                                                             'desc': parameter.get('description')})
                            else:
                                print()
                        self.api_list.append(api)
            except:
                assert False, "swagger路径错误"
        else:
            assert False, "swagger路径不存在"

    def get_list_menu(self):
        try:
            url = self.yapi_url + "/api/project/get?token=" + self.value
            res = requests.get(url)
            res_json = json.loads(res.text)
            project_id = res_json.get("data", {}).get('_id')
            url = self.yapi_url + "/api/interface/list_menu"
            data = {"token": self.value, "project_id": project_id}
            res = requests.get(url, data=data)
            res_json = json.loads(res.text)
            self.api_list = []
            for menu in res_json.get("data"):
                self.api_list += menu.get('list')
            return res_json
        except:
            self.api_list = []
            return None

    def get_api(self, _id):
        url = self.yapi_url + "/api/interface/get"
        data = {"token": self.value, "id": _id}
        res = requests.get(url, data=data)
        res_json = json.loads(res.text)
        return res_json

    @staticmethod
    def get_req_json(_list, value=False):
        """"""
        json_str = '{\n'
        for p in _list:
            json_str += f'        "{p.get("name", "")}": ' + (
                '"%s"' % p.get("value", "") if value else p.get("name", "")) + ","
            json_str += ("  # " + p.get("desc").replace('\n', ' ') if p.get("desc") else "") + '\n'
        json_str += '    }'
        return json_str

    def list_add(self, _list):
        """列表变量叠加"""
        _list3 = []
        _list4 = ["Content-Type"]
        for i in _list:
            name = i.get("name").split("[")[0]
            if name not in _list4:
                _list4.append(name)
                i["name"] = name
                _list3.append(i)
        
        return _list3

    def get_description(self, req_body_other):
        try:
            if not req_body_other:
                return []
            elif isinstance(req_body_other, str):
                properties = json.loads(req_body_other).get('properties') or {}
            elif isinstance(req_body_other, list):
                return req_body_other
            else:
                properties = req_body_other.get('properties') if req_body_other.get('properties') else req_body_other
            _list = []
            for k, v in properties.items():
                if type(v) == dict:
                    _properties = self.get_description(v.get('properties')) if v.get('properties') else None
                    _items = self.get_description(v.get('items')) if v.get('items') else None
                    _row = {"name": k,
                            "desc": v.get('description', ""),
                            "type": v.get('type', ""),
                            "properties": _properties,
                            "items": _items}
                else:
                    _row = {"name": k,
                            "desc": None,
                            "type": v,
                            "properties": None,
                            "items": None}
                _list.append(_row)
        except Exception as e:
            print(e)
        return _list

    def get_params_string(self, req_all, res_body):
        """方法描述生成"""
        def get_str(l):
            _str = ""
            for p in l:
                _str += f'    params: {p.get("name", "")} : {p.get("type", "")} : {p.get("desc", "")}\n'
                if p.get('properties') or p.get('items'):
                    for p2 in p.get('properties') or p.get('items'):
                        _str += f'              {p2.get("name", "")} : {p2.get("type", "")} : {p2.get("desc", "")}\n'
            return _str
        try:
            api_str = get_str(req_all)
            api_str += "    params: headers : 请求头\n    ====================返回======================\n"
            api_str += get_str(res_body)
            return api_str
        except Exception as e:
            print(e)

    def get_api_fun_str(self, name, row):
        if self.api_type == 1:
            row = self.get_api(_id=row.get('_id')).get('data')
        api_str = '@allure.step(title="调接口：%s")\n' % row.get("path").split('{')[0]
        api_str += "def " + name + "("
        req_params = row.get('req_params', [])
        req_query = row.get('req_query', [])
        req_body_form = row.get('req_body_form', [])
        req_headers = row.get('req_headers', [])
        req_body = self.get_description(row.get('req_body_other'))
        res_body = self.get_description(row.get('res_body'))
        req_all = self.list_add(req_params + req_query + req_body_form + req_body)
        req_all_data = self.list_add(req_query + req_body_form + req_body)

        api_str += " ".join(set([i.get('name') + '=None,' for i in req_all])) + " headers=None, **kwargs):\n"
        api_str += f'    """\n    {row["title"]}\n    up_time={row["up_time"]}\n\n'
        api_str += self.get_params_string(req_all, res_body)
        api_str += f'    """\n    _method = "{row.get("method")}"\n    _url = "{row.get("path")}"\n'
        if '/{' in row.get("path"):
            api_str += f'    _url = get_url(_url, locals())\n'
        api_str += '\n    _headers = ' + self.get_req_json(req_headers, True)
        api_str += '\n    _headers.update({"headers": headers})\n\n'
        api_str += '    _data = ' + self.get_req_json(req_all_data)
        api_str += '\n\n    _params = ' + self.get_req_json(req_params)
        api_str += '\n\n    return http_requester(_method, _url, params=_params, data=_data, ' \
                   'headers=_headers, **kwargs)\n\n\n'
    
        return api_str
            

    @staticmethod
    def get_fun_name(name):
        name = name.strip()
        if name.startswith('/'):
            name = name[1:]
        if "/{" in name:
            name = name.split('{')[0]

        name = re.sub(r'\W', '_', name)
        return name

    def write_api_fun(self):
        for row in self.api_list:
            fun_name = self.get_fun_name(row.get('path'))
            if fun_name in self.api_list_old:
                ord_str = re.findall(r'(def %s\(.+\)[\w\W]*?)(def|$)' % fun_name, self.api_file_str)
                up_time = re.findall(r'up_time=(\d+)([\w\W]+)', ord_str[0][0])
                if up_time and int(up_time[0][0]) < row.get('up_time'):
                    new_str = self.get_api_fun_str(fun_name, row)
                    self.api_file_str = self.api_file_str.replace(ord_str[0][0], new_str)
            else:
                self.api_list_old.append(fun_name)
                self.api_file_str += self.get_api_fun_str(fun_name, row)
        if not self.api_list_old:
            self.api_list_old.append("demo")
            self.api_file_str += """@allure.step(title="调接口：/demo")\ndef demo(mobile=None, headers=None, **kwargs):
    \"""\n    发送手机验证码\n    up_time=1657087679\n\n    params: mobile :  : 用户电话号码
    params: headers : 请求\n    ====================返回======================
    params: code : number : \n    params: msg : string : \n    params: data : null : 
    \"""\n    _method = "GET"\n    _url = "/common/common/sendSmsCode"\n
    _headers = {\n        "Content-Type": "application/x-www-form-urlencoded",\n    }
    _headers.update({"headers": headers})\n\n    _data = {\n        "mobile": mobile,  # 用户电话号码\n    }\n
    _params = {\n    }\n
    return http_requester(_method, _url, params=_params, data=_data, headers=_headers, **kwargs)\n\n"""
        for fun_name in self.api_list_old:
            if fun_name not in self.api_fun_fun_list:
                self.api_fun_fun_list.append(fun_name)
                self.get_api_fun_fun_str(fun_name)
        for fun_name in self.api_fun_fun_list:
            if "assert_" + fun_name not in self.assert_fun_list and "self.assert_" + fun_name + '(' in self.api_fun_file_str:
                self.assert_fun_list.append("assert_" + fun_name)
                self.get_assert_fun_str(fun_name)
        for fun_name in self.assert_fun_list:
            fun_name = fun_name[7:]
            if "sql_" + fun_name not in self.sql_fun_list and "self.sql_" + fun_name + '(' in self.assert_file_str:
                self.sql_fun_list.append("sql_" + fun_name)
                self.get_sql_fun_str(fun_name)
        for fun_name in self.api_fun_fun_list:
            if fun_name not in self.api_testcase_list:
                self.api_testcase_list.append("test_" + fun_name)
                self.get_api_testcase_str(fun_name)

        self.write_file(self.api_file_path, self.api_file_str)
        self.write_file(self.fun_file_path, self.fun_file_str)
        self.write_file(self.sql_file_path, self.sql_file_str)
        self.write_file(self.assert_file_path, self.assert_file_str)
        self.write_file(self.api_fun_file_path, self.api_fun_file_str)
        self.write_file(self.api_testcase_file_path, self.api_testcase_file_str)

    def get_sql_fun_str(self, api_fun_name):
        sql_fun_str = "    def sql_%s(self, **kwargs):\n" % api_fun_name
        sql_fun_str += "        # name = self.kwargs_pop(kwargs, 'name')  # 单独处理字段\n" \
                       "        # self.kwargs_replace(kwargs, likes=[], ins=[], before_end=[])  # 模糊查询字段，数组包含查询字段，区间字段处理\n" \
                       '        # kwargs["order_by"] = None  # 排序\n' \
                       '        sql_str = self.get_sql_str("table", **kwargs)  # 生成sql语句\n' \
                       '        # out = self.run_mysql(sql_str)  # 执行sql语句\n        # return out\n\n'
        sql_file_str_tmp = re.split(r"(\nif __name__ == '__main__':)", self.sql_file_str)
        sql_file_str_tmp.insert(1, sql_fun_str)
        self.sql_file_str = "".join(sql_file_str_tmp)

    def get_api_fun_fun_str(self, api_fun_name):
        api_fun_str = re.findall(r'(def %s\(.+\)[\w\W]*?)(def |$)' % api_fun_name, self.api_file_str)
        if api_fun_str:
            api_fun_str = api_fun_str[0][0]
        else:
            return False
        data = re.findall(r'def.+\((.*)?\)', api_fun_str)[0]
        data_list = [i.split('=')[0].strip() for i in data.split(',') if len(i.split('=')) > 1]
        data_list_tmp = []

        for n in data_list:
            if n in self.size_names:
                data_list_tmp.append(n.strip() + '=10')
            elif n in self.page_names:
                data_list_tmp.append(n.strip() + '=1')
            else:
                data_list_tmp.append(n.strip() + '="$None$"')
        api_fun_fun_str = "    def %s(self, %s, _assert=True, " % (api_fun_name, ", ".join(data_list_tmp))
        data_list = [n for n in data_list if n not in self.page_and_size and n != 'headers']
        if len(data_list) > 2 and api_fun_name.lower()[-4:] not in ('page', 'list', 'ages'):
            api_fun_fun_str += "_all_is_None=False, "
        api_fun_fun_str += " **kwargs):\n"

        desc = re.findall(r'"""([\w\W]*)"""', api_fun_str)
        url = re.findall(r'url *=[ \'\"]*(.+?)[\'\"]', api_fun_str)[0]
        if desc:
            desc = desc[0].split('====================返回======================')[0]
            desc_list = [" " * 8 + i.strip() for i in desc.split('\n') if "up_time=" not in i and i.strip()
                         and "params: headers" not in i]
            if desc_list:
                api_fun_fun_str = '    @allure.step(title="%s")\n' % desc_list[0].strip() + api_fun_fun_str
                api_fun_fun_str += '        """url=%s\n%s"""\n' % (url, "\n".join(desc_list[1:]))

        if api_fun_name.lower()[-4:] in ('page', 'list', 'ages'):
            if data_list:
                api_fun_fun_str += "        if self.has_true(locals()) and not self._list_%s:\n" \
                                   "            self.%s(_assert=False)\n\n" % (data_list[0], api_fun_name)
            for n in data_list:
                api_fun_fun_str += "        %s = self.get_list_choice(%s, self._list_%s)\n" % (n, n, n)
        else:
            for n in data_list:
                if len(data_list) > 2:
                    api_fun_fun_str += "        %s = self.get_value_choice(%s, list_or_dict=None, " \
                                       "_all_is_None=_all_is_None)\n" % (n, n)
                else:
                    api_fun_fun_str += "        %s = self.get_value_choice(%s, list_or_dict=None)\n" % (n, n)
        api_fun_fun_str += '\n' if data_list else ''
        api_fun_fun_str += "        _kwargs = self.get_kwargs(locals())\n"

        api_fun_fun_str += "        self.res = %s_api.%s(**_kwargs)\n\n" % (self.name, api_fun_name)

        if api_fun_name.lower()[-4:] in ('page', 'list', 'ages'):
            for n in data_list:
                api_fun_fun_str += "        self._list_%s = self.get_res_value_list('%s')\n" % (n, n)
                if "_list_%s" % n not in self.fun_init_list:
                    self.fun_init_list.append("_list_%s" % n)
                    self.fun_file_str = self.fun_file_str.replace(self.fun_init_str,
                                                              self.fun_init_str + "        self._list_%s = []\n" % n)
        for n in data_list:
            api_fun_fun_str += "        self._v_%s = %s\n" % (n, n)
            if "_v_%s" % n not in self.fun_init_list:
                self.fun_init_list.append("_v_%s" % n)
                self.fun_file_str = self.fun_file_str.replace(self.fun_init_str,
                                                              self.fun_init_str + "        self._v_%s = None\n" % n)
        api_fun_fun_str += '\n' if data_list else ''
        api_fun_fun_str += "        if _assert is True:\n"
        api_fun_fun_str += "            self.assert_%s(**_kwargs)\n" % api_fun_name
        api_fun_fun_str += "        elif _assert is not False:\n" \
                           '            assert self.res.rsp.code == _assert, "校验code=%s不通过" % _assert\n'
        api_fun_fun_str += "        return self.res\n\n"
        fun_file_str_tmp = re.split(r"(\nif __name__ == '__main__':)", self.api_fun_file_str)
        fun_file_str_tmp.insert(1, api_fun_fun_str)
        self.api_fun_file_str = "".join(fun_file_str_tmp)

    def get_api_testcase_str(self, fun_name):
        api_fun_str = re.findall(r'(def %s\(.+\)[\w\W]*?)(def |$)' % fun_name, self.api_file_str)
        if api_fun_str:
            api_fun_str = api_fun_str[0][0]
        else:
            return False
        desc = re.findall(r'"""([\w\W]*)"""', api_fun_str)
        api_testcase_str = '    @pytest.mark.skip("待维护")\n'
        if desc:
            desc = desc[0].split('====================返回======================')[0]
            desc_list = [" " * 8 + i.strip() for i in desc.split('\n') if "up_time=" not in i and i.strip()
                         and "params: headers" not in i]
            api_testcase_str += '    @allure.step(title="%s")\n' % (
                desc_list[0].strip() if desc_list else "")
        api_testcase_str += '    def test_%s(self):\n        self.f.%s()\n\n\n' % (fun_name, fun_name)
        self.api_testcase_file_str += api_testcase_str

    def get_assert_fun_str(self, fun_name):
        data = re.findall(r'def %s\((.*)?\)' % fun_name, self.api_fun_file_str)[0]
        data_list = [i.split('=')[0].strip() for i in data.split(',') if len(i.split('=')) > 1
                     and i.strip()[0] != '_' and i.split('=')[0].strip() != "headers"]
        assert_fun_str = '    @allure.step(title="接口返回结果校验")\n    def assert_%s(self, **kwargs):\n' \
                         '        assert self.res.rsp.code in (0, 200), self.res.rsp.msg\n' \
                         '        # out = self.sql_%s(**kwargs)\n' % (fun_name, fun_name)
        assert_fun_str += '        # flag = self.compare_json_list(self.res, out, [%s])\n' % \
                          ', '.join(['"%s"' % i for i in data_list if i not in self.page_and_size])
        assert_fun_str += '        assert True, "数据比较不一致"\n\n'
        assert_file_str_tmp = re.split(r"(\nif __name__ == '__main__':)", self.assert_file_str)
        assert_file_str_tmp.insert(1, assert_fun_str)
        self.assert_file_str = "".join(assert_file_str_tmp)

    def sub_hz(self, _id, _str):
        if re.findall(r'[^\da-zA-Z_\ (=,*):]', re.findall(r"def .*?\):", _str)[0]):
            api = self.get_api(_id)
            tmp2 = api.get('data', {}).get('req_params', [])
            for tmp3 in tmp2:
                name = tmp3.get('name', "")
                desc = tmp3.get('desc', "")
                if re.findall(r'[^\da-zA-Z_\ (=,*):]', name) and not re.findall(r'\W', desc):
                    _str = _str.replace(name, desc)
        if re.findall(r'[( ]async[,=)]', _str):
            for tmp in re.findall(r'[( ]async[,=)]', _str):
                tmp1 = str(tmp).replace('async', 'async1')
                _str = _str.replace(tmp, tmp1)
        return _str


if __name__ == '__main__':
    GetApi(app_key="a63ca17b-3cf3-46cb-b8b6-9ad20518e1e1")
