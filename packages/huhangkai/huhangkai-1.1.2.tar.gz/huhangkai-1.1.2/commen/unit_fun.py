import re
import random
import time
import requests
import datetime
# import pymysql

from typing import List
from faker import Faker
from commen.unit_logger import logger


class FunBase:
    def __init__(self):
        self._time2 = 0
        self._time1 = 0
        self.sql_str = ""
        # self.locale_list = {"zh_CN": "简体中文", "de_DE": "德语-德国", "sv_SE": "Swedish", "ja_JP": "日语-日本", "ko_KR": "朝鲜语-韩国"}
        # faker方法： http://www.manongjc.com/detail/28-mhkegnrmyzaafky.html
        self._faker = Faker(locale='zh_CN')
        self._db = {}
        self._route = ""
        self._token = ""
        self._host = ""

    # mock 方法，默认中国，详情搜python Faker模块
    def faker(self, locale='zh_CN'):
        return Faker(locale=locale)
    
    def seelp(self, v=1, *args, **kwargs):
        if isinstance(v, int):
            self.log_info("seelp: %s" % v)
            time.sleep(v)
        else:
            time.sleep(1)
            

    def _faker_name(self):
        return self._faker.name() + str(self._faker.numerify())

    @staticmethod
    def random_vin():
        # 内容的权值
        content_map = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
            'F': 6, 'G': 7, 'H': 8, 'I': 0, 'J': 1, 'K': 2, 'L': 3,
            'M': 4, 'N': 5, 'O': 0, 'P': 7, 'Q': 8, 'R': 9, 'S': 2, 'T': 3,
            'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9, "0": 0, "1": 1,
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9
        }
        # 位置的全值
        location_map = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
        vin = ''.join(random.sample('0123456789ABCDEFGHJKLMPRSTUVWXYZ', 17))
        num = 0
        for i in range(len(vin)):
            num = num + content_map[vin[i]] * location_map[i]
        vin9 = num % 11
        if vin9 == 10:
            vin9 = "X"
        list1 = list(vin)
        list1[8] = str(vin9)
        vin = ''.join(list1)
        return vin

    @staticmethod
    def random_carnum():
        char0 = '京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽赣粤青藏川宁琼'
        char1 = 'ABCDEFGHJKLMNPQRSTUVWXYZ'  # 车牌号中没有I和O，可自行百度
        char2 = '1234567890ABCDEFGHJKLMNPQRSTUVWXYZ'
        char3 = '1234567890'
        while True:
            code = random.choice(char0)
            code += random.choice(char1)
            code += "".join(random.choices(char2, k=4))
            code += random.choice(char3)
            return code
            test = re.match('^.\w.[A-Z]\d{4}$|^.\w.\d[A-Z]\d{3}$|^.\w.\d{2}[A-Z]\d{2}$|^.\w.\d{3}[A-Z]\d$|^.\w.\d{5}$', code)
            if test:
                return code

    # # mock方法，国家locale_list随机，也可根据数字获取第几个国家，超出时随机
    # def faker_random_country(self, locale=None):
    #     country = None
    #     if locale:
    #         try:
    #             if self.locale_list.get(locale):
    #                 country = locale
    #             else:
    #                 country = list(self.locale_list.keys())[int(locale)]
    #         except:
    #             pass
    #     if not country:
    #         country = random.choice(list(self.locale_list.keys()))
    #     return self.faker(locale=country)

    @staticmethod
    def log_info(msg):
        logger.info(str(msg))

    def sleep(self, t=1, debug=False):
        self.log_info("sleep %s 秒" % t)
        n = 1
        while debug and t > 1:
            self.log_info("sleep 第 %s 秒" % n)
            time.sleep(1)
            n += 1
            t -= 1
        time.sleep(t)

    # 时间戳，秒级
    @staticmethod
    def time(string=None, fmt="%Y-%m-%d"):
        time_array = int(time.mktime(time.strptime(string, fmt))) if string else int(time.time())
        return time_array

    def time_hms(self, string=None, fmt="%Y-%m-%d %H:%M:%S"):
        return self.time(string=string, fmt=fmt) * 1000

    def time_ms(self, string=None, fmt="%Y-%m-%d"):
        time_array = self.time(string=string, fmt=fmt)
        return time_array * 1000

    def data_str(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")
    # # 根据sql语句执行sql
    # def run_mysql(self, sql_str="", host="", user="", password="", database=""):
    #     sql_str = sql_str or self.sql_str
    #     if self._db.get(host+database):
    #         cursor = self._db.get(host+database)
    #     else:
    #         try:
    #             if database:
    #                 db = pymysql.connect(host=host, user=user, passwd=password, database=database)
    #             else:
    #                 db = pymysql.connect(host=host, user=user, passwd=password)
    #         except:
    #             assert False, "Couldn't connect to database"
    #         cursor = db.cursor()
    #         self._db[host+user+password+database] = cursor
    #     try:
    #         cursor.execute(sql_str)
    #
    #     except Exception as e:
    #         assert False, "执行sql失败，sql：" + sql_str + "\n执行报错：" + str(e)
    #
    #     return []

    # 传入表名加字段条件自动生成sql语句
    def get_sql_str(self, table: str, **kwargs):
        kwargs.update(kwargs.get('where') or {})
        where_str = "select * from " + table if len(table.split()) == 1 else table
        not_where_str = ('page', 'page_index', 'page_no', 'page_size', 'order_by', "where", "group_by", "having",
                         "where_list", "page_num", 'headers', '_route', 'current', 'size', '_token')
        where_if = [i for i in kwargs.keys() if i not in not_where_str and (kwargs.get(i) is not None or "null__" in i)]

        tmp_list = []
        for i in where_if:
            if "like__" in i:
                tmp_list.append("%s like \"%%%s%%\" " % (i[6:], kwargs.get(i)))
            elif "not_null__" in i:
                tmp_list.append("%s is not null " % (i[10:],))
            elif "null__" in i:
                tmp_list.append("%s is null " % (i[6:],))
            elif "in__" in i:
                if len(kwargs.get(i)) > 1:
                    tmp_list.append("%s in %s " % (i[4:], str(tuple(kwargs.get(i)))))
                elif len(kwargs.get(i)) == 1:
                    tmp_list.append("%s = \"%s\" " % (i[4:], str(kwargs.get(i)[0])))
                else:
                    tmp_list.append("%s = \"&$#@\" " % (i[4:], ))
            else:
                tmp_list.append("%s = \"%s\" " % (i, kwargs.get(i)))
        tmp_list.extend(kwargs.get("where_list") or [])
        if tmp_list:
            where_str += " where " + " and ".join(tmp_list)
        if kwargs.get("group_by"):
            where_str += " group by " + kwargs.get('group_by') + " "
        if kwargs.get("having"):
            where_str += " having " + kwargs.get('having') + " "
        if kwargs.get('order_by'):
            where_str += " order by " + kwargs.get('order_by') + " "
        if where_str.strip()[:6].lower() == "select":
            page = kwargs.get("page") or kwargs.get("page_no") or kwargs.get("page_index") or \
                   kwargs.get("page_num") or kwargs.get('current') or 1
            page_size = kwargs.get("page_size") or kwargs.get('size') or 100
            where_str += " limit %s, %s;" % ((page - 1) * page_size, page_size)
        else:
            where_str += ";"
        self.sql_str = where_str
        return where_str

    # 传入2个json，比较值是否一致，compare_list格式: [("res1_key1", "res2_key1"), ...]
    def compare_json(self, res1: dict, res2: dict, key_list=[]):
        if isinstance(res1, requests.Response):
            res1 = res1.rsp
            if "data" in res1.keys():
                res1 = res1["data"]
        self.log_info("比较：res1=" + str(res1))
        self.log_info("     res2=" + str(res2))
        key_list = key_list or res1.keys()
        self.log_info("校验字段：" + str(key_list))
        for key in key_list:
            try:
                if type(key) == str:
                    key1 = key
                    if key in res2.keys():
                        key2 = key
                    else:
                        key2 = re.sub(r'[A-Z]', lambda n: "_" + str(n.group()).lower(), key)
                else:
                    key1 = key[0]
                    key2 = key[1]
                if not(not res1[key1] and not res2[key2]):
                    if type(res1[key1]) == int:
                        res2[key2] = int(res2[key2])
                    elif type(res1[key1]) == float:
                        res2[key2] = float(res2[key2])
                    if not(res1[key1] == res2[key2] or str(res1[key1]).strip() == str(res2[key2]).strip() or
                           (not res1[key1] and not res2[key2])):
                        if not ("time" in key1.lower() and len(str(res1[key1])) == 19 and len(str(res2[key2])) == 19
                                and str(res1[key1])[0:10] == str(res2[key2])[0:10]
                                and str(res1[key1])[11:] == str(res2[key2])[11:]):
                            self.log_info("比较字段：" + str(key) + "  不一致")
                            return False
            except Exception as e:
                self.log_info("比较字段：" + str(key) + "  不一致")
                return False
        self.log_info("比较结果一致")
        return True

    # 传入2个json列表，比较值是否一致，compare_list格式: [("res1_key1", "res2_key1"), ...]
    def compare_json_list(self, res1, res2: List[dict], key_list=[]):
        if isinstance(res1, requests.Response):
            res1 = res1.rsp.data
            if isinstance(res1, dict):
                for key in res1.keys():
                    if isinstance(res1[key], list):
                        res1 = res1[key]
                        break
        self.log_info("比较数组：res1=" + str(res1))
        self.log_info("        res2=" + str(res2))
        if not res1 and not res2:
            return True
        elif len(res1) == len(res2):
            if len(res1) == 0:
                return True
            flag = True
            for v1, v2 in zip(res1, res2):
                flag = self.compare_json(v1, v2, key_list)
                if not flag:
                    break
            return flag
        else:
            self.log_info("比较结果：比较数组个数不一致")
            try:
                key = key_list[0] if key_list else res1[0].keys()[0]
                if type(key) == str:
                    key1 = key
                    if key in res2[0].keys():
                        key2 = key
                    else:
                        key2 = re.sub(r'[A-Z]', lambda n: "_" + str(n.group()).lower(), key)
                else:
                    key1 = key[0]
                    key2 = key[1]
                id_list1 = [str(i[key1]) for i in res1]
                id_list2 = [str(i[key2]) for i in res2]
                self.log_info("    res1[%s]: %s" % (key1, id_list1))
                self.log_info("    res2[%s]: %s" % (key2, id_list2))
                diff1 = list(set(id_list1).difference(set(id_list2)))
                diff2 = list(set(id_list2).difference(set(id_list1)))
                if diff1:
                    self.log_info("    res1中有res2中没有的%s: %s" % (key1, diff1))
                if diff2:
                    self.log_info("    res2中有res1中没有的%s: %s" % (key2, diff2))
            except:
                pass
            return False

    @staticmethod
    def _random_choice(list_or_dict, _type=1):
        if list_or_dict:
            if isinstance(list_or_dict, (list, tuple, type({}.keys()))):
                out = random.choice(list(list_or_dict))
            elif isinstance(list_or_dict, dict):
                out = random.choice(list(list_or_dict.keys()))
            else:
                return list_or_dict
            if _type == 2 and isinstance(out, str) and len(out) > 2:
                i = random.randint(0, 2)
                if i == 0:
                    return out[1:]
                elif i == 1:
                    return out[:-1]
                else:
                    return out[1:-1]
            return out
        else:
            return None

    # 列表或字典里随机取值, 列表接口取值随机取值用
    def get_list_choice(self, *args, list_or_dict=None, _type=1):
        if list_or_dict is None and isinstance(args[-1], (list, tuple, type({}.keys()))):
            list_or_dict = args[-1]
            args = args[:-1]

        out = None
        for i in args[1:]:
            out = out or i
        if args[0] == '$None$':
            return None or out
        elif args[0] is True:
            if list_or_dict:
                return self._random_choice(list_or_dict, _type=_type)
            else:
                return out
        else:
            return args[0]

    # 字典里取随机字段，截取一段用于随机查询
    def get_list_choice2(self, *args, list_or_dict=None):
        return self.get_list_choice(*args, list_or_dict=None, _type=2)

    def get_value_choice(self, *args, list_or_dict=None, _all_is_None=False):
        if list_or_dict is None and isinstance(args[-1], (list, tuple, type({}.keys()))):
            list_or_dict = args[-1]
            args = args[:-1]
        if args[0] != '$None$':
            return args[0]
        else:
            if _all_is_None:
                return None
            out = None
            for i in args[1:]:
                out = out or i
            if out is None:
                if list_or_dict:
                    return self._random_choice(list_or_dict)
                else:
                    return None
            else:
                return out

    # 随机获取两位小数, 或空
    def get_random_float(self, null=False):
        if null:
            return random.randint(1, 99999) / 100 if self._faker.boolean() else None
        else:
            return random.randint(1, 99999) / 100

    # 时间获取时间
    def get_random_date(self, type=0, null=False):
        """type：0 当天，1：后一个月内, 2:后一年内, 3:继上次一个月后， 4：继上次一年后，
                 5：上两次之间, """

        if type == 0:
            self._time2 = self._time1
            self._time1 = 0
        elif type == 1:
            self._time2 = self._time1
            self._time1 = random.randint(0, 30)
        elif type == 2:
            self._time2 = self._time1
            self._time1 = random.randint(0, 365)
        elif type == 3:
            self._time2 = self._time1
            self._time1 += random.randint(0, 30)
        elif type == 4:
            self._time2 = self._time1
            self._time1 += random.randint(0, 365)
        elif type == 5:
            tmp = random.randint(self._time2, self._time1)\
                if self._time1 > self._time2 else random.randint(self._time1, self._time2)

            self._time2 = self._time1
            self._time1 = tmp

        data = str(self._faker.date_between(self._time1, self._time1))
        return (data if self._faker.boolean() else None) if null else data

    @staticmethod
    def kwargs_replace(kwargs, likes=[], ins=[], joins=[], before_end=[]):
        for i in likes:
            try:
                kwargs["like__" + i] = kwargs.pop(i)
            except:
                pass
        for i in ins:
            try:
                kwargs["in__" + i] = kwargs.pop(i)
            except:
                pass
        for i in joins:
            try:
                kwargs[i] = kwargs.pop(i.split('.')[1])
            except:
                pass
        for i in before_end:
            try:
                kwargs["where_list"] = kwargs.get("where_list", [])
                if "before" == i.lower()[-6:] and kwargs.get(i) is not None:
                    kwargs["where_list"].append(' %s >= "%s"' % (i[:-6], kwargs.pop(i)))
                elif "end" == i.lower()[-3:] and kwargs.get(i) is not None:
                    kwargs["where_list"].append(' %s <= "%s"' % (i[:-3], kwargs.pop(i)))
            except:
                pass
        return kwargs

    @staticmethod
    def kwargs_pop(kwargs, name):
        try:
            return kwargs.pop(name)
        except:
            return None

    def get_kwargs(self, kwargs):
        kwargs.update(kwargs.get('kwargs', {}))
        _kwargs = {k: v for k, v in kwargs.items() if (k not in ('self', 'kwargs') and k[0] != '_')
                 or k in ('_route', '_token', '_host')}
        if not kwargs.get('_route') and self._route:
            _kwargs['_route'] = self._route
        if not kwargs.get('_token') and self._token:
            _kwargs['_token'] = self._token
        if not kwargs.get('_host') and self._host:
            _kwargs['_host'] = self._host
        return _kwargs

    @staticmethod
    def has_true(kwargs):
        _kwargs = {k: v for k, v in kwargs.items() if k not in ('self', 'kwargs') and k[0] != '_' and v is True}
        return _kwargs

    def get_res_value_list(self, name, property_path=''):
        if property_path:
            tmp = self.res.rsp
            for i in property_path.split('.'):
                if not isinstance(tmp, dict):
                    return []
                tmp = tmp.get(i)
            if isinstance(tmp, list) and tmp and isinstance(tmp[0], dict):
                return [i.get(name) for i in tmp if i.get(name)]
            return []
        else:
            if self.res.status_code == 200 and self.res.rsp and isinstance(self.res.rsp, dict):
                for key, value in self.res.rsp.items():
                    if isinstance(value, list):
                        return [i.get(name) for i in value]
                    elif isinstance(value, dict):
                        for key2, value2 in value.items():
                            if isinstance(value2, list):
                                return [i.get(name) for i in value2 if i.get(name)]
            return []

    def excelWriter(self, filename, data):
        from pandas import DataFrame, ExcelWriter
        filename = filename[:4] + filename[4:].replace(":", "").replace(' ', '_')
        with ExcelWriter(filename) as writer:
            # 写入到第一个sheet
            if data and isinstance(data[0], list):
                h = data[0]
                data1 = []
                for i in data[1:]:
                    data1.append({x[0]: str(x[1]) for x in zip(h, i)})
                data = data1
            elif data and isinstance(data[0], dict):
                data = [{k: str(v) for k, v in i.items()} for i in data]
            DataFrame(data).to_excel(writer,
                              sheet_name="sheet1",
                              index=False,
                              engine="openpyxl"
                              )


if __name__ == '__main__':
    print(FunBase().random_carnum())
    # f = FunBase().faker()

    # print(f.name())  # 随机姓名
    # print(f.ipv4())  # 随机IP4地址
    # print(f.uri())  # 随机URI地址
    # print(f.url())  # 随机URL地址
    # print(f.user_name())  # 随机⽤户名
    # print(f.paragraph())  # 随机⽣成⼀个段落
    # print(f.text())  # 随机⽣成⼀篇⽂章
    # print(f.word())  # 随机⽣成词语
    # print(f.boolean())  # True/False
    # print(f.email())  # email
    # print(f.safe_email())  # 安全邮箱
    # print(f.ssn())  # ⽣成⾝份证号
    # print(f.password())  # 随机⽣成密码,可选参数：length：密码长度；special_chars：是否能使⽤特殊字符；digits：是否包含数字；upper_case：是否包含⼤写字母；lower_case：是否包含⼩写字母
    # print(f.numerify())  # ⽣成三位随机数
    # print(f.random_digit())  # ⽣成0~9随机数
    # print(f.random_int())  # 随机数字，默认0~9999，可通过min,max参数修改
    # print(f.random_letter())  # 随机字母
    # print(f.random_number(digits=12))  # 参数digits设置⽣成的数字位数
    # print(f.date())  # 随机⽇期
    # print(f.datez())  # 随机时间
    # print(f.date_between('-1M', 0))  # 随机⽣成指定范围内⽇期，参数：start_date，end_date
    # print(f.future_date())  # 未来⽇期
    # print(f.past_date())  # 随机⽣成已经过去的⽇期
