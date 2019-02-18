# -*- coding:utf-8 -*-
import copy
import json
import os
from pprint import pprint
from functools import partial
import requests
from urllib import parse
import uuid
import time
import numpy as np
import matplotlib.pyplot as plt
from config import AccessKeyId, AccessKeySecret, send_alarm_v2, write_log, sign_gen, alert_data, func_try


LOG = './rds_error.log'
write_log = partial(write_log, LOG)

# 获取监控数据开始和结束时间
start_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime(time.time() - 3600 * 24 * 7))
end_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime())

alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        'alert_business': '阿里云ECS情况统计',
        'alert_function': 'get_rds',
        # 'exception_spec' : '异常说明',
    }


def get_rds_list(PageNumber=1):
    params = {
        'Action': 'DescribeDBInstances',
        'RegionId': 'cn-beijing',
        'PageSize': 100,
        'PageNumber': PageNumber,
        'Format': 'JSON',
        'Version': '2014-08-15',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://rds.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        desc_list = resp_dict['Items']['DBInstance']
    except Exception as e:
        string = 'get_rds_list 获取rds列表失败，e:%s' % str(e)
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return desc_list


def get_rds_attr(DBInstanceId):
    '''
    测试用数据
    'DBInstanceId': 'rm-2zewy8sohv5a02jqv,rm-2zer1w1qt6k5nr163,rm-2ze6532xsiepgx84r',
    '''
    params = {
        'Action': 'DescribeDBInstanceAttribute',
        'DBInstanceId': DBInstanceId,
        # 'RegionId': 'cn-beijing',
        'Format': 'JSON',
        'Version': '2014-08-15',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://rds.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        attr_list = resp_dict['Items']['DBInstanceAttribute']
        # pprint(resp_dict)
    except Exception as e:
        string = 'get_rds_attr 获取rds属性失败，e:%s' % str(e)
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return attr_list


def get_rds_metric(instanceId, Metric):
    params = {
        'Action': 'QueryMetricLast',
        'Project': 'acs_rds_dashboard',
        'Metric': Metric,
        'Period': '60',
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
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        resp_list = resp_dict['Datapoints']
    except Exception as e:
        string = 'get_rds_metric 获取rds监控数据失败，e:%s' % str(e)
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0

    else:
        return resp_list


metrics = ('CpuUsage', 'MemoryUsage', 'DiskUsage', 'IOPSUsage', 'ConnectionUsage',
           'MySQL_ActiveSessions', 'MySQL_NetworkInNew', 'MySQL_NetworkOutNew')
#          cpu使用率      内存使用率       磁盘使用率     iops使用率    连接数使用率
#          活跃连接数      流入流量               流出流量bit/s


def get_rds_final():
    rds_list = get_rds_list()
    if not rds_list:
        return 0

    # id的列表
    id_list = [x['DBInstanceId'] for x in rds_list]
    # pprint(id_list)

    # 描述的列表
    desc_list = [x.get('DBInstanceDescription') if x.get('DBInstanceDescription') else x['DBInstanceId'] for x in rds_list]

    # 数据库类型和版本 单位 string
    engine_list = [x['Engine'] for x in rds_list]
    enginev_list = [x['EngineVersion'] for x in rds_list]

    attr_list = get_rds_attr(','.join(id_list))

    # 实例状态 单位 string
    status_list = [x['DBInstanceStatus'] for x in attr_list]

    # 锁表状态 单位string
    lock_mode = [x['LockMode'] for x in attr_list]

    rdss_l = []  # 所有实例的列表
    for index, inst_id in enumerate(id_list):
        # 每个实例

        # 获取这个实例id的监控信息的列表
        rds_d = {'rds_id': inst_id, 'rds_desc': desc_list[index],
                 'status': status_list[index],
                 'lock_mode': lock_mode[index],
                 'engine_v': str(engine_list[index])+str(enginev_list[index]),
                 }

        print(time.ctime(), '实例名=', rds_d['rds_desc'], 'begin')
        for metric in metrics:
            # 获取该监控项的列表
            metric_l = get_rds_metric(inst_id, metric)
            rds_d[metric] = 0
            if not metric_l:
                # 如果这个监控项没有值
                continue
            else:
                rds_d[metric] = metric_l[0]['Average']

        # 追加到实例列表
        rdss_l.append(rds_d)

        print(time.ctime(), '实例名=', rds_d['rds_desc'], 'over')

    # pprint(rdss_l)
    return rdss_l


@func_try
def data_process(rdss_l):
    keys = ('top_cpu_usage', 'top_mem_usage', 'top_disk_usage',
            'top_iops_usage', 'top_conn_usage', 'top_active_sessions',
            'top_networkin_rate', 'top_networkout_rate'
            )

    ll = {}
    for ind, metric in enumerate(metrics):
        # 排序
        def sorted_key(n):
            temp = n.get(metric)
            if isinstance(temp, int) or isinstance(temp, float):
                return temp
            else:
                return 0
        sorted_metric = sorted(rdss_l, key=sorted_key, reverse=True)
        # pprint(sorted_metric)
        # 取值
        l = []  # 是监控项的值
        length = 4
        if len(sorted_metric) < 4:
            length = len(sorted_metric)
        for i in range(length):
            temp_d = sorted_metric[i]
            l.append({'name': temp_d['rds_desc'], keys[ind]: temp_d.get(metric)})
        # 赋值
        ll[keys[ind]] = l

    # pprint(ll)
    return ll


figsize = (6.8, 3.75)
xlabel = 8
ylabel = 10
tick_label = 8
title_size = 14
rotation = 349
tick_size = 8
width = 0.6


@func_try
def make_bar_chart(ll):
    '''此函数生成 cpu、内存、磁盘消耗率最大的前6台机器的 柱状图'''

    # 百分比指标 （cpu、内存、磁盘）
    keys = ('top_cpu_usage', 'top_mem_usage', 'top_disk_usage',
            'top_iops_usage', 'top_conn_usage', 'top_active_sessions',
            'top_networkin_rate', 'top_networkout_rate'
            )
    for index, key in enumerate(keys):
        l = ll.get(key)
        if l:
            plt.figure(key, figsize=figsize, dpi=120, )  # 背景色

            if key in ('top_networkin_rate', 'top_networkout_rate'):
                y = [ round( (i[key] if isinstance(i[key], float) or isinstance(i[key], int) else 0 ) / 10 ** 6, 2) for i in l]
                plt.ylabel('Mbit/s', fontsize=ylabel)
                plt.yticks(fontsize=tick_size)
            elif key == 'top_active_sessions':
                y = [round((i[key] if isinstance(i[key], float) or isinstance(i[key], int) else 0), 2) for i in l]
                plt.ylabel('count', fontsize=ylabel)  # y周标签
                plt.yticks(fontsize=tick_size)
            else:
                y = [ round( (i[key] if isinstance(i[key], float) or isinstance(i[key], int) else 0 ), 2) for i in l]
                plt.ylabel('percent(%)', fontsize=ylabel)  # y周标签
                plt.yticks(fontsize=tick_size)

            x_ticks = [i['name'] for i in l]
            x = list(range(len(x_ticks)))

            # plt.title(key, fontsize=title_size)

            plt.xticks(np.arange(0, len(x_ticks)), list(range(1, len(x_ticks) + 1)), fontsize=tick_size)

            plt.tick_params(labelsize=tick_label)
            plt.grid(axis='y', linestyle=':')

            plt.xlim(-0.8, max(x) + 7)

            ax = plt.gca()
            ax.spines['top'].set_color('none')
            ax.spines['right'].set_color('none')

            label_rds = []
            for i in range(1, len(x_ticks)+1):
                ii = str(i) + ':%s'
                label_rds.append(ii)
            label = (' \n'.join(label_rds)) % tuple(x_ticks)
            # print(label)
            plt.bar(x, y, width=width, color=['deepskyblue', '#8497B0'],
                    label=label)

            plt.legend(markerscale=0, handlelength=0)
            if not os.path.exists('./rds_picture'):
                os.mkdir('./rds_picture')
            plt.savefig('./rds_picture/%s.png' % key)
            plt.close()


def get_rds_week_main():
    begin = time.time()
    print('get_rds_week_main begin', time.ctime())
    ll = get_rds_final()
    if ll:
        ll = data_process(ll)
        make_bar_chart(ll)
    else:
        string = 'get_rds_final 返回值为0'
        write_log(string)
        send_alarm_v2(alert_data, string)
    print('get_rds_week_main end', time.time() - begin)


if __name__ == '__main__':
    try:
        get_rds_week_main()
    except Exception as e:
        print(e)
        write_log(str(e))


