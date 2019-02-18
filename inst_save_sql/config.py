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
from functools import partial

AccessKeyId = 'xxx'
AccessKeySecret = 'xxx'

LOG = './log/config.log'

# 告警数据
alert_data = {
        'id': 'xxx',
        'level': 'xx',
        'dep': 'xx',
        'env': 'xxx',
        'alert_level': '低',
        'alert_business': '阿里云ECS情况统计',
        'alert_function': 'config.py',
        # 'exception_spec' : '异常说明',
    }

aliyun_monitor = {
    'host': 'xxx',
    'port': 3306,
    'user': 'root',
    'password': 'xxx',
    'database': 'aliyun_monitor',
    'charset': 'utf8'
}


def write_log(LOG, string):
    with open(LOG, 'a') as f:
        now_time = datetime.datetime.now().strftime("[ %Y-%m-%d %H:%M:%S ] ")
        f.write(now_time + str(string) + '\n')


write_log2 = partial(write_log, LOG)


def send_alarm_v2(alert_data, string):
    '''此函数用于发送告警'''
    string = str(string)
    alert_data.setdefault('exception_spec', string)
    alert_data.setdefault('alert_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    data_sign = OrderedDict(sorted(alert_data.items(), key=lambda x: x[0]))
    sign_string_a = ''.join(data_sign.values())
    sign_string_b = hashlib.md5(sign_string_a.encode('utf-8'))
    sign_string_b.update('YYLmfY6IRdjZMQ1'.encode('utf-8'))
    alert_data.setdefault("sign", sign_string_b.hexdigest())
    data = json.dumps(alert_data)
    try:
        resp = requests.post('http://xxx', data=data)
        code = json.loads(resp.text)['code']
    except Exception as e:
        write_log2('send_alarm_v2发送告警异常, e=' + str(e) + '\n' + str(traceback.format_exc()))
    else:
        if code not in (0, 1010):
            write_log2('send_alarm_v2发送告警异常, code=' + str(code) + '\n' + str(traceback.format_exc()))


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
    url_string = res
    # 拼接
    string_to_sign = 'GET'+'&'+'%2F'+'&'+url_string
    # 编码
    signature_hmac = hmac.new((AccessKeySecret+'&').encode(), string_to_sign.encode(), hashlib.sha1).digest()
    signature = base64.encodebytes(signature_hmac).strip().decode()
    return signature


class DBUtil:
    def __init__(self, host="127.0.0.1", user='root', password='password',
                 database='aliyun_monitor', port=3306, charset='utf8'):

        try:
            conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
        except Exception:
            write_log2(str(traceback.format_exc()))
            raise
        else:
            self.conn = conn
            self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    # ------------------------------  rds    --------------------------------------------------------
    def insert_rds_attr(self, d_l):
        sql = "insert into rds_attr(rds_id, descr, status, lock_mode, max_iops, max_conn, \
               engine_v, time, note) values \
               (%s, %s, %s, %s, %s, %s, %s, %s, %s);"

        parame = tuple((d.get('rds_id'), d.get('desc'), d.get('status'),
                        d.get('lock_mode'), d.get('max_iops'), d.get('max_conn'),
                        d.get('engine_v'), d.get('time'), d.get('note')) for d in d_l)
        try:
            self.cur.execute('start transaction')
            # print('parame', parame)
            self.cur.executemany(sql, parame)
        except Exception as e:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def insert_rds_data(self, d_l):
        sql = "insert into rds_data(rds_id, metric, value_num, value_attr, \
               time, note) values \
               (%s, %s, %s, %s, %s, %s);"

        parame = tuple((d.get('rds_id'), d.get('metric'), d.get('value_num'),
                        d.get('value_attr'),
                        d.get('time'), d.get('note')) for d in d_l)
        try:
            self.cur.execute('start transaction')
            # print('parame', parame)
            self.cur.executemany(sql, parame)
        except Exception as e:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    # --------------------------------    mongo   ------------------------------------------------------
    def insert_mongo_attr(self, d_l):
        sql = "insert into mongo_attr(mongodb_id, engine_v, descr, status, \
              mongo_id, shard_id, time) \
              values (%s, %s, %s, %s, %s, %s, %s)"

        parame = tuple((d.get('mongodb_id'), d.get('engine_v'), d.get('desc'), d.get('status'),
                        d.get('mongo_id'), d.get('shard_id'), d.get('time')) for d in d_l)
        try:
            self.cur.execute('start transaction')
            self.cur.executemany(sql, parame)
        except Exception as e:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def insert_mongo_data(self, d_l):
        sql = "insert into mongo_data(mongodb_id, metric, value_num, value_attr, \
              time, note) values \
              (%s, %s, %s, %s, \
              %s, %s);"
        parame = tuple((d.get('mongodb_id'), d.get('metric'), d.get('value_num'), d.get('value_attr'),
                        d.get('time'), d.get('note')) for d in d_l)
        try:
            self.cur.execute('start transaction')
            self.cur.executemany(sql, parame)
        except Exception:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def insert_mongo_node_data(self, d_l):
        sql = "insert into mongo_node_data(node_id, metric, value_num, value_attr, \
              time, note) values \
              (%s, %s, %s, %s, \
              %s, %s);"
        parame = tuple((d.get('node_id'), d.get('metric'), d.get('value_num'), d.get('value_attr'),
                        d.get('time'), d.get('note')) for d in d_l)
        try:
            self.cur.execute('start transaction')
            self.cur.executemany(sql, parame)
        except Exception as e:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    # --------------------------   slb    ------------------------------------------------------------
    def insert_slb_attr(self, d_l):
        sql = "insert into slb_attr (slb_id, name, status, addr, \
              bandwidth, spec, port_list, region, \
              time, note) values \
              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        parame = tuple((d.get('slb_id'), d.get('name'), d.get('status'), d.get('addr'),
                        d.get('bandwidth'), d.get('spec'), d.get('port_list'), d.get('region'),
                        d.get('time'), d.get('note')) for d in d_l)
        try:
            self.cur.execute('start transaction')
            self.cur.executemany(sql, parame)
        except Exception as e:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def insert_slb_data(self, d_l):
        sql = "insert into slb_data (slb_id, metric, value_num, value_attr, \
              time, note) values \
              (%s, %s, %s, %s, %s, %s)"
        parame = tuple((d.get('slb_id'), d.get('metric'), d.get('value_num'), d.get('value_attr'),
                        d.get('time'), d.get('note')) for d in d_l)
        try:
            self.cur.execute('start transaction')
            self.cur.executemany(sql, parame)
        except Exception as e:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def insert_ecs_data(self, d_l):
        sql = "insert into ecs_data(host, metric, value_num, value_attr, \
                     time, note) values \
                     (%s, %s, %s, %s, \
                     %s, %s);"
        parame = tuple((d.get('host'), d.get('metric'), d.get('value_num'), d.get('value_attr'),
                        d.get('time'), d.get('note')) for d in d_l)
        try:
            self.cur.execute('use aliyun_monitor')
            self.cur.execute('start transaction')
            self.cur.executemany(sql, parame)
        except Exception:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

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






