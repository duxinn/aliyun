# -*- coding:utf-8 -*-
import os
import traceback
import gevent
from gevent import monkey
monkey.patch_all()
import copy
import json
from functools import partial
import requests
from urllib import parse
import uuid
import time
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
from config import AccessKeyId, AccessKeySecret, send_alarm_v2, write_log, \
    sign_gen, alert_data, DBUtil, func_try
from decimal import Decimal


LOG = './ecs_error.log'
write_log = partial(write_log, LOG)

# 起止时间
start_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime(time.time() - 3600 * 24 * 7))
end_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime())
period = '60'

alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        'alert_business': '阿里云ECS情况统计',
        'alert_function': 'get_ecs',
        # 'exception_spec' : '异常说明',
    }


def get_ecs_list(page_num=1, region='cn-beijing'):
    params = {
        'Action': 'DescribeInstanceStatus',
        'AccessKeyId': AccessKeyId,
        'RegionId': region,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'Version': '2014-05-26',
        'Format': 'json',
        'PageNumber': page_num,
        'PageSize': 50
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://ecs.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url)
        resp_data = json.loads(resp.text)
        page_num = resp_data['PageNumber']
        total_count = resp_data['TotalCount']
        insts_list = resp_data['InstanceStatuses']['InstanceStatus']
    except Exception as e:
        string = 'get_ecs_list 函数异常，e:%s' + str(e) + str(traceback.format_exc())
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return page_num, total_count, insts_list


def get_ecs_name(InstanceIds, page_num=1, retry_times=3, region='cn-beijing'):
    if retry_times <= 0:
        return 0
    params = {
        'Action': 'DescribeInstances',
        'AccessKeyId': AccessKeyId,
        'RegionId': region,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'Version': '2014-05-26',
        'Format': 'json',
        'InstanceIds': InstanceIds,
        'PageNumber': page_num,
        'PageSize': 100,
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://ecs.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url)
        resp_data = json.loads(resp.text)
        inst_name = resp_data['Instances']['Instance'][0]['InstanceName']
    except Exception as e:
        string = 'get_ecs_name 函数异常，e' + str(e) + str(traceback.format_exc())
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return inst_name


def get_ecs_metric(instanceId, Metric):
    # print(instanceId, Metric)
    '''
    参数 instanceId 实例id，类型：字符串
        Metric     监控项，类型：字符串
    功能 获取实例的最新监控数据
    以下为测试数据
    instanceId = 'i-2ze62mggaelqkrmo8ivd'
    Metric = 'cpu_total'
    '''
    params = {
        'Action': 'QueryMetricLast',
        'Project': 'acs_ecs_dashboard',
        'Metric': Metric,
        'Period': period,
        'StartTime': start_time,
        'EndTime': end_time,
        'Dimensions': '{"instanceId":"%s"}' % instanceId,
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'Format': 'JSON',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': str(uuid.uuid1()),
        'Version': '2017-03-01',
        'SignatureVersion': '1.0'
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'http://metrics.cn-beijing.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url)
        resp_dict = json.loads(resp.text)
        resp_list = resp_dict['Datapoints']
        # pprint(resp_list)
        # result = resp_list[0]['Average']
    except Exception as e:
        string = 'get_ecs_metric 获取监控数据失败，e' + str(e) + str(traceback.format_exc())
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return resp_list


# 监控项
metrics = ('cpu_total', 'memory_usedutilization', 'diskusage_utilization', 'IntranetInRate', 'IntranetOutRate')
# 'cpu_total', 'memory_usedutilization', 'diskusage_utilization', 是系统监控项，
# 'IntranetInRate', 'IntranetOutRate'是基础监控项


def get_ecs_beijing():
    temp = get_ecs_list()
    if not temp:
        string = '函数 get_ecs_list 获取失败, 返回值为空'
        write_log(string)
        return 0
    else:
        page_num, total_count, insts_list = temp
        if not (page_num == 1):
            string = '函数 get_ecs_list 获取到的不是第一页'
            write_log(string)
            return 0
        else:
            # 如果是第一页, 获取第二页
            temp2 = get_ecs_list(2)
            if not temp2:
                string = '函数 get_ecs_list 获取第二页失败, 返回值为空'
                write_log(string)
                return 0
            else:
                page_num2, total_count2, insts_list2 = temp2
                if not (page_num2 == 2 and total_count2 == total_count):
                    string = '函数 get_ecs_list 获取第二页数据和第一页不一致, 返回值为空'
                    write_log(string)
                    return 0
                else:  # beijing 获取完毕
                    # 拼接所有实例的id的列表
                    insts_list += insts_list2
                    # print(insts_list)
                    # [{"Status": "Running", "InstanceId": "i-2ze62mggaelqkrmo8ivf"}, ...

                    insts_id_list = [x['InstanceId'] for x in insts_list]  # id 的列表
                    insts_status_list = [x['Status'] for x in insts_list]  # 状态的列表

                    # 以下两行为测试数据
                    # insts_id_list = ['i-2ze724j2r1frq1l24iwy']
                    # insts_status_list = ['running']

                    inst_final = []  # 北京的 所有实例的字典
                    # metrics_without_disk = metrics[:2] + metrics[3:]

                    def per_inst(index, inst):
                        '''函数完成对一个实例的监控项的查询，并追加到实例的字典里'''
                        inst_name = get_ecs_name([inst])
                        print(time.ctime(), inst_name, 'begin')
                        # 一个实例的字典
                        d = {'inst_id': inst, 'name': inst_name, 'status': insts_status_list[index]}
                        # 构建内含实例参数,调用求监控项的偏函数
                        get_metric = partial(get_ecs_metric, inst)

                        g_l2 = []
                        for metric in metrics:
                            g_l2.append(gevent.spawn(get_metric, metric))
                        gevent.joinall(g_l2)

                        for ind2, g2 in enumerate(g_l2):
                            if ind2 != 2:
                                if g2.value:
                                    d[metrics[ind2]] = g2.value[0]['Average']
                                else:
                                    d[metrics[ind2]] = 0
                            else:
                                if g2.value:
                                    for i in g2.value:
                                        if i['diskname'] == '/':
                                            d['/_usage'] = i['Average']
                                        elif i['diskname'] == '/data':
                                            d['data_usage'] = i['Average']
                                        elif i['diskname'] == '/data1':
                                            d['data1_usage'] = i['Average']
                                        elif i['diskname'] == '/data2':
                                            d['data2_usage'] = i['Average']
                                        elif i['diskname'] == '/data3':
                                            d['data3_usage'] = i['Average']
                                        elif i['diskname'] == '/data4':
                                            d['data4_usage'] = i['Average']
                                        elif i['diskname'] == '/data5':
                                            d['data5_usage'] = i['Average']
                                        else:
                                            d[i['diskname'].split('/')[1]] = i['Average']

                        inst_final.append(d)
                        print(time.ctime(), inst_name, 'over')

                    g_l = []
                    for index, inst in enumerate(insts_id_list):
                        # 实例的第一次网络请求
                        g_l.append(gevent.spawn(per_inst, index, inst))
                    gevent.joinall(g_l)

                    # inst_final   北京的所有实例结束
                    return inst_final


def get_ecs_qingdao():
    temp = get_ecs_list(region='cn-qingdao')
    if not temp:
        string = '函数 get_ecs_list 获取失败, 返回值为空'
        write_log(string)
        return 0
    else:
        page_num, total_count, insts_list = temp

        insts_id_list = [x['InstanceId'] for x in insts_list]  # id 的列表
        insts_status_list = [x['Status'] for x in insts_list]  # 状态的列表

        # 以下两行为测试数据
        # insts_id_list = ['i-2ze724j2r1frq1l24iwy']
        # insts_status_list = ['running']

        inst_final = []  # 所有实例的字典

        metrics_without_disk = metrics[:2] + metrics[3:]
        for index, inst in enumerate(insts_id_list):
            # 实例的第一次网络请求
            inst_name = get_ecs_name([inst], region='cn-qingdao')
            print(time.ctime(), inst_name, 'begin')
            # 一个实例的字典
            d = {'inst_id': inst, 'name': inst_name, 'status': insts_status_list[index]}
            # 构建内含实例参数,调用求监控项的偏函数
            get_metric = partial(get_ecs_metric, inst)

            # 除了硬盘的监控项
            for metric in metrics_without_disk:
                # 实例的 第二次～第六次 网络请求
                metric_value = get_metric(metric)
                # print(metric_value)
                if metric_value:
                    d[metric] = metric_value[0]['Average']
                else:
                    d[metric] = 0

            # 硬盘监控项  实例的第七次网络请求
            metric_list = get_metric('diskusage_utilization')
            # i['diskname'] for i in metric_list
            for i in metric_list:
                if i['diskname'] == '/':
                    d['/_usage'] = i['Average']
                elif i['diskname'] == '/data':
                    d['data_usage'] = i['Average']
                elif i['diskname'] == '/data1':
                    d['data1_usage'] = i['Average']
                elif i['diskname'] == '/data2':
                    d['data2_usage'] = i['Average']
                elif i['diskname'] == '/data3':
                    d['data3_usage'] = i['Average']
                elif i['diskname'] == '/data4':
                    d['data4_usage'] = i['Average']
                elif i['diskname'] == '/data5':
                    d['data5_usage'] = i['Average']
                else:
                    d[i['diskname'].split('/')[1]] = i['Average']

            inst_final.append(d)
            print(time.ctime(), inst_name, 'over')

        return inst_final


@func_try
def data_process(dd, length='auto'):
    # print('length', length)
    '''
    dd:[{},{},{}]
    把所有实例里面的监控项，按照监控项进行分隔
    :return：{'top_/_usage': [{'name': 'du-idna-end-bj-1', 'top_/_usage': 82},
                 {'name': 'du-dcc-log-bj-1', 'top_/_usage': 70},
                 {'name': 'du-id-issue-test-bj', 'top_/_usage': 69},
                 {'name': 'du-dmp-bj-1', 'top_/_usage': 50},
                 {'name': 'du-dsp-bj-4', 'top_/_usage': 47},
    '''
    ll = {}  # ecs所有监控项的机器
    keys = ('top_cpu_usage', 'top_mem_usage',
            'top_networkin_rate', 'top_networkout_rate',
            'top_/_usage', 'top_data_usage',
            'top_data1_usage', 'top_data2_usage',
            'top_data3_usage')
    metrics_inner = ('cpu_total', 'memory_usedutilization',
                     'IntranetInRate', 'IntranetOutRate',
                     '/_usage', 'data_usage',
                     'data1_usage', 'data2_usage',
                     'data3_usage')

    def sorted_key(n):  # 排序key函数
        temp = n.get(metric)
        if isinstance(temp, int) or isinstance(temp, float):
            return temp
        else:
            return 0
    for ind, metric in enumerate(metrics_inner):


        # 过滤
        dd_metric = list(filter(sorted_key, dd))
        # print('dd_metric', dd_metric)

        # 排序
        sorted_metric = sorted(dd_metric, key=sorted_key, reverse=True)
        # print('sorted_metric', sorted_metric)

        # 取值
        l = []  # 是这个监控项metric的值
        if length == 'auto':
            if len(sorted_metric) < 10:  # 如果排序后的长度小于10
                length_sort = len(sorted_metric)
            else:
                length_sort = 10
        elif length == 'all':
            length_sort = len(sorted_metric)
        else:
            length_sort = 10
        
        for i in range(length_sort):
            temp_d = sorted_metric[i]
            # print(temp_d)
            l.append({'name': temp_d['name'], keys[ind]: temp_d.get(metric)})

        # 赋值
        ll[keys[ind]] = l

    # 得到 ll
    return ll


# 将数据按照部门分开
data_dep = {'du-srv': [], 'du-da': [], 'du-ad': [], 'du-fe': [], 'du-op': []}
#       云端        大数据    广告      前段      运维


@func_try
def data_per_dep(dd):
    db = DBUtil()
    for d in dd:
        dep = db.query(d['inst_id'])
        if dep:  # 如果查出的有结果，部门
            if dep in data_dep:  # 如果在 data_dep 里就追加
                data_dep[dep].append(d)

        else:  # 这个示例没有部门就查下一个
            continue
    db.close()


aliyun_zabbix = {
    'host': '172.17.146.238',
    'port': 3306,
    'user': 'root',
    'password': 'Sui@911120',
    'database': 'zabbix',
    'charset': 'utf8'
}

time_stamp = time.time() - 3600 * 24 * 7
time_stamp_now = time.time()


@func_try
def idc_query():
    # conn = pymysql.connect(**aliyun_zabbix)
    # cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    db2 = DBUtil()

    # ------------查询私有云组的 机器的名字和 监控项id-----------------
    sql = """select a.host, item_name, itemid from
        (select hosts.hostid, hosts.name host_name, hosts.host
        from hosts_groups
        left join hosts
        on hosts_groups.hostid = hosts.hostid
        where hosts_groups.groupid = '29') a
    left join
        (select host, hosts.hostid, hosts.name, items.itemid, items.name item_name
        from hosts
        right join items
        on hosts.hostid = items.hostid
        where items.name in ('CPU-空闲百分比', '内存-可用百分比', '硬盘-剩余百分比（/）',
        '硬盘-剩余百分比（/data00）', '硬盘-剩余百分比（/data01）', '硬盘-剩余百分比（/data02）',
         '硬盘-剩余百分比（/data03）', '硬盘-剩余百分比（/data04）', '硬盘-剩余百分比（/data05）',
         '网络-内网进流量', '网络-内网出流量')
        ) b
    on a.hostid = b.hostid
    order by host, item_name
    ;"""
    metrics = ('CPU-空闲百分比', '内存-可用百分比', '硬盘-剩余百分比（/）',
               '硬盘-剩余百分比（/data00）', '硬盘-剩余百分比（/data01）', '硬盘-剩余百分比（/data02）',
               '硬盘-剩余百分比（/data03）', '硬盘-剩余百分比（/data04）', '硬盘-剩余百分比（/data05）',
               '网络-内网进流量', '网络-内网出流量'
               )

    host_itemid = db2.query_zabbix(sql)
    if not host_itemid:  # 机器的名字和监控项的对应的表
        db2.close()
        return 0
    else:
        # print('host_itemid', host_itemid)
        # 查询值
        for i in host_itemid:  # i 是里面的字典
            # name = i['host']
            item_name = i['item_name']  # 监控项的名字
            sql = "select itemid, avg(value) avg_value from history where {0} < clock and itemid = {1};" \
                if item_name not in ('网络-内网进流量', '网络-内网出流量') \
                else "select itemid, (max_value-min_value)/({2}-{0}) avg_value from \
                (select itemid, max(value) max_value, min(value) min_value from history_uint \
                where {0} < clock and clock < {2} and itemid = {1}) a;"
            sql = sql.format(time_stamp, i['itemid'], time_stamp_now)  # 监控项的id
            # print('sql', sql)

            item_value = db2.query_zabbix(sql)  # 查询这个监控项
            # print('item_value', item_value)
            if item_value:
                i['value'] = item_value[0]['avg_value'] if item_name not in ('网络-内网进流量', '网络-内网出流量') \
                    else float(item_value[0]['avg_value']) \
                    if isinstance(item_value[0]['avg_value'], (Decimal, float, int)) else 0
            else:
                i['value'] = 110
                # print('host_itemid', host_itemid)
        db2.close()
        # 分组
        d = {}  # 所有主机的字典，键是host名字， 值是 记录的列表 {name:[{},{}], name2:[{},{}]}
        for i in host_itemid:
            if i['host'] not in d:
                d[i['host']] = []
                d[i['host']].append(i)
            else:
                d[i['host']].append(i)
        # print('d', d)
        # 转换
        l = []
        for key in d:  # key 是主机的host
            # key是一个主机
            temp_d = {}  # 一个主机的字典
            for j in d[key]:  # j是里面的一个字典  d[key]: [{},{},{}]
                # print('j', j)
                temp_d['name'] = j['host']
                if j['item_name'] == 'CPU-空闲百分比':
                    temp_d['cpu_total'] = 100 - j['value'] if j['value'] else -10  # 防止监控项的得到值是None
                elif j['item_name'] == '内存-可用百分比':
                    temp_d['memory_usedutilization'] = 100 - j['value'] if j['value'] else -10
                elif j['item_name'] == '硬盘-剩余百分比（/）':
                    temp_d['/_usage'] = 100 - j['value'] if j['value'] else -10
                elif j['item_name'] == '硬盘-剩余百分比（/data00）':
                    temp_d['data_usage'] = 100 - j['value'] if j['value'] else -10
                elif j['item_name'] == '硬盘-剩余百分比（/data01）':
                    temp_d['data1_usage'] = 100 - j['value'] if j['value'] else -10
                elif j['item_name'] == '硬盘-剩余百分比（/data01）':
                    temp_d['data1_usage'] = 100 - j['value'] if j['value'] else -10
                elif j['item_name'] == '硬盘-剩余百分比（/data02）':
                    temp_d['data2_usage'] = 100 - j['value'] if j['value'] else -10
                elif j['item_name'] == '硬盘-剩余百分比（/data03）':
                    temp_d['data3_usage'] = 100 - j['value'] if j['value'] else -10
                elif j['item_name'] == '网络-内网进流量':
                    temp_d['IntranetInRate'] = j['value'] if j['value'] else -10
                elif j['item_name'] == '网络-内网出流量':
                    temp_d['IntranetOutRate'] = j['value'] if j['value'] else -10
                
            l.append(temp_d)
            # print('temp_d', temp_d)
        return l


figsize = (6.8, 3.75)
xlabel = 8
ylabel = 10
tick_label = 8
title_size = 14
rotation = 349
tick_size = 8
width = 0.6


@func_try
def make_bar_chart(ll, folder='ecs_picture', mode='total'):
    # print('ll, folder, mode', ll, folder, mode)
    '''此函数生成 cpu、内存、磁盘消耗率最大的前6台机器的 柱状图'''

    keys = ('top_cpu_usage', 'top_mem_usage',
            'top_networkin_rate', 'top_networkout_rate',
            'top_/_usage', 'top_data_usage',
            'top_data1_usage', 'top_data2_usage',
            'top_data3_usage')

    def make_bar_chart10(key, l, inde=None):
        # print('key, len(l), inde', key, l, inde)
        x_ticks = [i['name'] for i in l]
        x = list(range(len(x_ticks)))

        plt.figure(key, figsize=figsize, dpi=120)  # 背景色
        # plt.title(key, fontsize=title_size)

        if key in ('top_networkin_rate', 'top_networkout_rate'):
            plt.ylabel('Mbit/s', fontsize=ylabel)
            plt.yticks(fontsize=tick_size)
            y = [round((i[key] if isinstance(i[key], float) or isinstance(i[key], int) else 0) / 10 ** 6, 2) for i in l]
            # print(y)
        else:
            y = [round((i[key] if isinstance(i[key], float) or isinstance(i[key], int) else 0), 2) for i in l]
            plt.ylabel('percent(%)', fontsize=ylabel)  # y轴标签
            plt.yticks(fontsize=tick_size)

        plt.xticks(np.arange(0, len(x_ticks)), list(range(1, len(x_ticks) + 1)), fontsize=tick_size)

        plt.tick_params(labelsize=tick_label)
        plt.grid(axis='y', linestyle=':')

        plt.xlim(-0.8, max(x) + 7)  # 设置x轴范围

        ax = plt.gca()  # 设置顶轴，和右边轴消失
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        label = []
        for i in range(1, len(x_ticks) + 1):
            ii = str(i) + ':%s'
            label.append(ii)
        label = (' \n'.join(label)) % tuple(x_ticks)
        # label = '1:%s \n2:%s \n3:%s \n4:%s \n5:%s \n6:%s \n7:%s \n8:%s \n9:%s \n10:%s' % tuple(x_ticks)

        plt.bar(x, y, width=width, color=['deepskyblue', '#8497B0'],
                label=label, )
        plt.legend(markerscale=0, handlelength=0)
        key = key if '/' not in key else key.replace('/', '')
        if not os.path.exists('%s' % folder):
            os.mkdir('%s' % folder)
        if inde:
            plt.savefig('%s/%s_%s.png' % (folder, key, inde))
            # 文件夹/监控项_第几组
        else:
            plt.savefig('%s/%s.png' % (folder, key))
        plt.close()

    for key in keys:
        l_key = ll.get(key)
        # print(l_key)
        if l_key:
            length = len(l_key)  # 求长度
            if mode == 'total':  # 如果是总共的，就不传索引，存储的文件文没有序号后缀的
                if length <= 10:
                    make_bar_chart10(key, l_key)
                else:
                    make_bar_chart10(key, l_key[:10])
            elif mode == 'dep':
                if length <= 10:  # 主机个数小于10，传个1，保存的时候价格后缀 _1
                    make_bar_chart10(key, l_key, inde=1)
                else:  # 按10个分组，看有几个组，把第几个组传进去，再把不够10个的分成最后一个组
                    groups = int(length / 10)  # 求按10分能分几组
                    remain = length % 10  # 求按10分之后的余数
                    for g in range(groups):  # 分成10个一组，送入 make_bar_chart10 进行制图
                        make_bar_chart10(key, l_key[g*10:(10+g*10)], g+1)  # 监控项， 数据， 序号

                    make_bar_chart10(key, l_key[groups*10: (groups*10+remain)], groups+1)  # 对不够10的余数进行制图,是第groups组


def get_ecs_week_main():
    begin = time.time()
    print('get_ecs_week_main begin', time.ctime())

    l_1 = get_ecs_beijing()
    # l_2 = get_ecs_qingdao()
    # if l_1 and l_2:
    #     ll = l_1 + l_2
    ll = []
    if l_1:
        ll += l_1
    else:
        string = 'get_ecs_beijing() 和 get_ecs_qingdao() 获取的值不位空'
        write_log(string)
        send_alarm_v2(alert_data, string)
        return
    # pprint(ll)

    t1 = time.time()
    print(time.ctime(), 'get_ecs_final used', t1-begin)
    data_per_dep(ll)  # 把这些ll根据id，分不到不同的部门里
    t2 = time.time()
    print(time.ctime(), 'data_per_dep used', t2-t1)

    idc_l = idc_query()
    # print('idc_l', idc_l)
    if idc_l:
        data_dep['du-da'] += idc_l
    t3 = time.time()
    print(time.ctime(), 'idc_query used', t3 - t2)

    ll_total = data_process(ll)
    make_bar_chart(ll_total, mode='total')  # 设置模式是总共的，不分部门

    t4 = time.time()
    print(time.ctime(), 'll_total', t4 - t3)

    for j in data_dep:
        if data_dep[j]:  # 如果这个部门有数据， 就把数据放到
            ll_dep = data_process(data_dep[j], 'all')  # 把这个部门的数据处理成 {监控项：[{实例1},{实例2},{实例3},] } 的形式
            make_bar_chart(ll_dep, folder='./' + j.replace('-', '_'), mode='dep')
            print(time.ctime(), j, '部门图表格做完了', time.ctime())
    print(time.ctime(), 'get_ecs_week_main 用时', time.time() - begin)


if __name__ == '__main__':
    get_ecs_week_main()





