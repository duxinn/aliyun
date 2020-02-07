# -*- coding:utf-8 -*-
import base64
import datetime
import hashlib
import hmac
import traceback
from collections import OrderedDict
from pprint import pprint
from urllib import parse
import json

import pymysql
import requests

AccessKeyId = 'xxx'
AccessKeySecret = 'xxx'


# 告警数据
alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        # 'alert_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'alert_business': '阿里云ECS情况统计',
        'alert_function': '',
        # 'exception_spec' : '异常说明',
    }


aliyun_monitor = {
    'host': '172.17.146.238',
    'port': 3306,
    'user': 'root',
    'password': 'Sui@911120',
    'database': 'aliyun_monitor',
    'charset': 'utf8'
}


def write_log(LOG, string):
    with open(LOG, 'a') as f:
        now_time = datetime.datetime.now().strftime("[ %Y-%m-%d %H:%M:%S ] ")
        f.write(now_time + str(string) + '\n')


def func_try(fn):
    '''此装饰器用于将被修饰函数注册为协程'''
    def inner(*args, **kw):
        try:
            temp = fn(*args, **kw)
        except Exception as e:
            string = fn.__qualname__ + '调用失败'
            write_log(string + str(e) + str(traceback.format_exc()))
            return 0
        else:
            return temp
    return inner


def send_alarm_v2(alert_data, string):
    '''此函数用于发送告警'''
    alert_data.setdefault('exception_spec', string)
    alert_data.setdefault('alert_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    data_sign = OrderedDict(sorted(alert_data.items(), key=lambda x: x[0]))
    sign_string_a = ''.join(data_sign.values())
    sign_string_b = hashlib.md5(sign_string_a.encode('utf-8'))
    sign_string_b.update('YYLmfY6IRdjZMQ1'.encode('utf-8'))
    alert_data.setdefault("sign", sign_string_b.hexdigest())
    data = json.dumps(alert_data)
    try:
        resp = requests.post('http://osa.shuzilm.cn/alarm_v2', data=data)
        code = eval(resp.text)['code']
    except Exception as e:
        write_log('send_alarm_v2发送告警异常, e=' + str(e))
    else:
        if code not in (0, 1010):
            write_log('send_alarm_v2发送告警异常, code=' + str(code))


def sign_gen(params):
    '''
    功能: 生成签名
    返回: 签名, 返回类型是字符串
    params: 请求参数，类型为字典
    '''
    list_params = sorted(params.items(), key=lambda d: d[0])
    encode_str = parse.urlencode(list_params)
    res = parse.quote(encode_str.encode('utf8'), '')
    res = res.replace("+", "%20")
    res = res.replace("*", "%2A")
    res = res.replace("%7E", "~")
    # res = res.replace("%26", "&")
    # 将编码后的字符串
    url_string = res
    # 拼接
    string_to_sign = 'GET'+'&'+'%2F'+'&'+url_string
    # 编码
    signature_hmac = hmac.new((AccessKeySecret+'&').encode(), string_to_sign.encode(), hashlib.sha1).digest()
    signature = base64.encodebytes(signature_hmac).strip().decode()
    return signature


class DBUtil:
    def __init__(self, host="172.17.146.238", user='root', password='Sui@911120',
                 database='aliyun_monitor', port=3306, charset='utf8'):

        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
        if conn:
            self.conn = conn
            self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        else:
            raise Exception('zabbix-bj mysql数据库参数异常')

    def query(self, inst_id):
        sql = "select department from ecs_dep where inst_id=%s"
        self.cur.execute(sql, inst_id)
        result = self.cur.fetchall()
        if result:
            return result[0]['department']
        else:
            return False

    def query_zabbix(self, sql):
        self.cur.execute("use zabbix")
        self.cur.execute(sql)
        result = self.cur.fetchall()
        if result:
            return result
        else:
            return False

    # --------------------------------------------------------------------------------------
    def exec_sql(self, sql, parame=None):
        self.cur.execute(sql, parame)
        result = self.cur.fetchall()
        if result:
            return result
        else:
            return 0

    def start_transaction(self):
        self.cur.execute('start transaction')

    def close(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        return True


if __name__ == '__main__':

    db = DBUtil()

    temp = db.query('i-2zeioe8vrh4db63s9aeg')

    pprint(temp)



