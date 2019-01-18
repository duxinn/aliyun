# -*- coding:utf-8 -*-
import traceback
from functools import partial
from pprint import pprint
import time
import gevent
from gevent import monkey
monkey.patch_all()
from config import DBUtil, write_log, send_alarm_v2, sign_gen, AccessKeyId, AccessKeySecret

'''此模块的任务是10分钟一次，从zabbix库中，把监控数据存入数据库'''

mintue = 10
start_time = time.time() - 60 * mintue * 1 * 1
end_time = time.time()

sql_error = ''
sql_time = 0
wait_time = 60 * 8

LOG = './log/ecs_error.log'
write_log = partial(write_log, LOG)

# 告警数据
alert_data = {
        'id': 'ggzh',
        'level': '13',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        'alert_business': 'ecs 实时入库',
        'alert_function': '',
        # 'exception_spec' : '异常说明',
    }


def change_coroutine(fn):
    '''此装饰器用于将被修饰函数注册为协程'''
    def inner(*args, **kw):
        g = gevent.spawn(fn, *args, **kw)
        g.join(timeout=wait_time)
        if not g.value:  # 如果没有值
            string = '{} 在 10 分钟内返回值为0，sql_error: {}, sql_time:{}'.format(fn.__qualname__, sql_error,
                                                                          time.time() - sql_time)
            print(string)
            write_log(string)
            send_alarm_v2(alert_data, string)
        return g.value
    return inner


@change_coroutine
def get_data(db):
    global sql_error
    global sql_time
    sql = """select a.host, item_name, itemid from
            (select hosts.hostid, hosts.name host_name, hosts.host
            from hosts_groups
            left join hosts
            on hosts_groups.hostid = hosts.hostid
            ) a
        left join
            (select host, hosts.hostid, hosts.name, items.itemid, items.name item_name
            from hosts
            right join items
            on hosts.hostid = items.hostid
            where items.name in (
             'CPU-空闲百分比', '内存-可用百分比', '硬盘-剩余百分比（/）',
             '硬盘-剩余百分比（/data00）', '硬盘-剩余百分比（/data01）', '硬盘-剩余百分比（/data02）',
             '硬盘-剩余百分比（/data03）', '硬盘-剩余百分比（/data04）', '硬盘-剩余百分比（/data05）',
             '网络-内网进流量', '网络-内网出流量',
             '硬盘-剩余百分比（/data）',
             '硬盘-剩余百分比（/data1）', '硬盘-剩余百分比（/data2）',
             '硬盘-剩余百分比（/data3）', '硬盘-剩余百分比（/data4）', '硬盘-剩余百分比（/data5）')
            ) b
        on a.hostid = b.hostid
        order by host, item_name;"""
    t0 = time.time()
    db.exec_sql('use zabbix')
    sql_error = 'use zabbix'; sql_time = t0

    t1 = time.time()
    temp = db.exec_sql(sql)  # 查询到机器的名字和监控项的id
    sql_error = sql; sql_time = t1

    if temp:
        print('temp 长度', len(temp))
        d_l = []
        for ind, d in enumerate(temp):  # d是 每个机器的host， 监控项名字， 监控项id  的字典
            itemid = d.get('itemid')
            if itemid:
                sql2 = 'select value, clock from history where itemid = {1} and {0} < clock and clock < {2};' \
                    if d['item_name'] not in ('网络-内网进流量', '网络-内网出流量', '网络-外网进出流量', '网络-内网进出流量') \
                    else 'select (max(value)-min(value))/({2}-{0}) value from history_uint \
                        where {0} < clock and clock < {2} and itemid = {1};'
                sql_query = sql2.format(start_time, itemid, end_time)

                t3 = time.time()
                temp2 = db.exec_sql(sql_query)  # 拿监控项去查值
                sql_error = 'temp 第{}个sql语句'.format(ind) + sql_query; sql_time = t3

                if temp2:
                    # 整理，入库
                    for j in temp2:
                        t = j.get('clock')
                        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)) \
                            if t else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        try:
                            value_num = float(j['value'])
                        except Exception:
                            pass
                        else:
                            k = {'host': d['host'], 'metric': d['item_name'], 'value_num': value_num, 'time': t}
                            d_l.append(k)
        return d_l


@change_coroutine
def insert(db, d_l):
    global sql_time
    global sql_error
    sql_error = 'use aliyun_monitor'
    sql_time = time.time()
    db.exec_sql('use aliyun_monitor')
    t4 = time.time()
    print(time.ctime(), 'use aliyun_monitor', t4 - sql_time)
    sql_error = '插入数据库语句'
    sql_time = t4
    db.insert_ecs_data(d_l)
    print(time.ctime(), 'insert_ecs_data used', time.time() - t4)
    return 1


def ecs_main():
    print(time.ctime(), 'ecs_main, begin')
    db = DBUtil()

    t0 = time.time()
    d_l = get_data(db)
    t1 = time.time()
    print(time.ctime(), 'get_data,', t1 - t0)

    if d_l:
        insert(db, d_l)
    else:
        string = 'get_data 在 10 分钟内返回值为0，sql_error: {}'.format(sql_error)
        print(time.ctime(), string)
        write_log(string)
        send_alarm_v2(alert_data, string)
    db.close()
    print(time.ctime(), '入库成功, total used: ', time.time() - t0)


if __name__ == '__main__':
    try:
        ecs_main()
    except Exception:
        string = '''{}'''.format(str(traceback.format_exc()))
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
    else:
        print('ecs_main() 正常结束')
    # ecs_main()

