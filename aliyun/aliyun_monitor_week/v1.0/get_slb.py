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

LOG = './slb_error.log'
write_log = partial(write_log, LOG)

start_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime(time.time() - 3600 * 24 * 7))
end_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime())

alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        'alert_business': '阿里云ECS情况统计',
        'alert_function': 'get_slb',
        # 'exception_spec' : '异常说明',
    }


def get_slb_list():
    params = {
        'Action': 'DescribeLoadBalancers',
        'RegionId': 'cn-beijing',
        'Format': 'JSON',
        'Version': '2014-05-15',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://slb.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        resp_list = resp_dict['LoadBalancers']['LoadBalancer']
    except Exception as e:
        string = 'get_slb_list 获取rds列表失败，e:%s' % str(e)
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return resp_list


def slb_attr(LoadBalancerId):
    '''
    :param LoadBalancerId:
    :return:
    测试数据如下,有的id没有'LoadBalancerSpec'属性
    t = slb_attr('lb-2zeliy8kebtk62ukrtu94')
    pprint(t)
    '''
    params = {
        'Action': 'DescribeLoadBalancerAttribute',
        'RegionId': 'cn-beijing',
        'LoadBalancerId': LoadBalancerId,
        'Format': 'JSON',
        'Version': '2014-05-15',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://slb.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
    except Exception as e:
        string = 'slb_attr 获取rds属性失败，e:%s' % str(e)
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return resp_dict


def slb_metric(instanceId, Metric):
    '''
    功能 对某个实例获取她的监控项的值
    参数 instanceId 表示实例id
        Metric 表示监控项
    测试参数如下
    slb_metric('lb-2zep9dqdb42drtcz51dad', 'InstanceTrafficRX')
    '''
    params = {
        'Action': 'QueryMetricLast',
        'Project': 'acs_slb_dashboard',
        'Period': '60',
        'Metric': Metric,
        'StartTime': start_time,
        'EndTime': end_time,
        'Dimensions': '{"instanceId":"%s"}' % instanceId,
        # 'Length': 1000,
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'Format': 'JSON',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': str(uuid.uuid1()),
        'Version': '2017-03-01',
        'SignatureVersion': '1.0',
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
        string = 'slb_metric, 获取slb监控值失败, e:%s' % str(e)
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return resp_list


# 端口监控项
port_metrics = [
                'TrafficRXNew', 'TrafficTXNew',
                # 每秒流入\流出数据量 bit/s
                'PacketRX', 'PacketTX',
                # 每秒流入,每秒流出的数据报 Count/Second
                'ActiveConnection', 'InactiveConnection',
                # 活跃\非活跃 连接数
                'MaxConnection', 'NewConnection',
                # 端口并发连接数 新建连接数
                'DropPacketRX', 'DropPacketTX',
                # 每秒丢失入\出流量数
                'DropTrafficRX', 'DropTrafficTX',
                # 每秒丢失入\丢出包数
                'DropConnection'
                # 每秒丢失连接数
                ]

# 实例监控项
metrics = ['InstanceTrafficRX', 'InstanceTrafficTX',
           # 每秒流入\流出流量  bit/s
           'InstancePacketRX', 'InstancePacketTX',
           # 每秒入包数\出包数
           'InstanceActiveConnection', 'InstanceInactiveConnection',
           # 每秒活跃连接数\非活跃连接数
           'InstanceMaxConnection', 'InstanceNewConnection',
           # 每秒最大并发数\新建连接数
           'InstanceDropTrafficRX', 'InstanceDropTrafficTX',
           # 每秒丟入流量\丢出流量
           'InstanceDropPacketRX', 'InstanceDropPacketTX',
           # 每秒丢入包数\丢出包数
           'InstanceDropConnection'
           # 丢弃连接数
           ]


def get_slb_final():
    slb_list = get_slb_list()
    # 返回的是列表,里面是每个实例的字典,列表是有序的,所以里面的实例也是有序的
    if not slb_list:
        return 0
    else:
        insts_list = []
        slb_ids = [x['LoadBalancerId'] for x in slb_list]  # slb 的id
        slb_names = [x['LoadBalancerName'] for x in slb_list]  # slb 的名字
        slb_status = [x['LoadBalancerStatus'] for x in slb_list]  # slb 的状态

        for index, sid in enumerate(slb_ids):
            # 一个实例

            attr_list = slb_attr(sid)  # 属性列表

            addr = attr_list.get('Address')  # 服务地址

            port_list = attr_list.get('ListenerPorts').get('ListenerPort')  # 端口列表 [443, 80]

            spec = attr_list.get('LoadBalancerSpec')  # 实例规格
            # 设置的带宽
            bandwidth = attr_list.get('Bandwidth')
            # 构造实例的字典
            slb_d = {'slb_id': sid, 'name': slb_names[index], 'status': slb_status[index], 'addr': addr,
                     'port_list': port_list, 'spec': spec, 'bandwidth': bandwidth}

            print(time.ctime(), slb_d['name'], '开始')

            # 构建含有该id的偏函数
            metric_id = partial(slb_metric, sid)

            # 获取实例该监控项的数据
            for metric in metrics:
                # 生程该监控项的列表
                slb_d[metric] = 0
                # 获取该监控项的数据的列表
                metric_list = metric_id(metric)
                if not metric_list:
                    continue
                slb_d[metric] = metric_list[0]['Average']
            print(time.ctime(), slb_d['name'], 'over')
            # 把这个实例的字典
            insts_list.append(slb_d)
        return insts_list


def data_process(insts_list):
    '''每个实例的第一个监控项， 列出成一个序列，去除前10 的最大值和其实例名字'''

    keys = ('top_networkin_rate', 'top_networkout_rate',
            'top_packetin', 'top_packetout',
            'top_active_conn', 'top_inactive_conn',
            'top_max_conn', 'top_new_conn',
            'top_drop_networkin_rate', 'top_drop_networkout_rate',
            'top_drop_packetin', 'top_drop_packetout',
            'top_drop_conn'
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

        sorted_metric = sorted(insts_list, key=sorted_key, reverse=True)
        # pprint(sorted_metric)
        # 取值
        l = []  # 是监控项的值
        length = 10
        if len(sorted_metric) < 10:
            length = len(sorted_metric)
        for i in range(length):
            temp_d = sorted_metric[i]
            l.append({'name': temp_d['name'], keys[ind]: temp_d.get(metric)})
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
width = 0.7
color = ['deepskyblue', '#8497B0']


@func_try
def make_bar_chart(ll):
    '''此函数生成 cpu、内存、磁盘消耗率最大的前6台机器的 柱状图'''

    keys = ('top_networkin_rate', 'top_networkout_rate',
            'top_packetin', 'top_packetout',
            'top_active_conn', 'top_inactive_conn',
            'top_max_conn', 'top_new_conn',
            'top_drop_networkin_rate', 'top_drop_networkout_rate',
            'top_drop_packetin', 'top_drop_packetout',
            'top_drop_conn'
            )
    for index, key in enumerate(keys):
        l = ll.get(key)
        if l:
            if key in ('top_networkin_rate', 'top_networkout_rate', 'top_drop_networkin_rate', 'top_drop_networkout_rate'):
                # 对 网络流量数据 做 Mbit/s 的处理
                y = [float(i[key])/10**6 for i in l]
            else:
                y = [round(float(i[key]), 2) for i in l]
            x_ticks = [i['name'] for i in l]
            x = list(range(len(x_ticks)))

            plt.figure(key, figsize=figsize, dpi=120, )  # 背景色

            if key in ('top_networkin_rate', 'top_networkout_rate', 'top_drop_networkin_rate', 'top_drop_networkout_rate'):
                plt.ylabel('Mbit/s', fontsize=ylabel)
            else:
                plt.ylabel('count', fontsize=ylabel)

            plt.xticks(np.arange(0, len(x_ticks)), list(range(1, len(x_ticks) + 1)), fontsize=tick_size)
            plt.yticks(fontsize=tick_size)

            plt.tick_params(labelsize=tick_label)
            plt.grid(axis='y', linestyle=':')

            plt.xlim(-0.8, max(x) + 7)

            ax = plt.gca()
            ax.spines['top'].set_color('none')
            ax.spines['right'].set_color('none')

            label = []
            for i in range(1, len(x_ticks)+1):
                ii = str(i) + ':%s'
                label.append(ii)
            label = (' \n'.join(label)) % tuple(x_ticks)
            # print(label)
            plt.bar(x, y, width=width, color=color,
                    label=label)

            # 柱子上不放数字
            # for i, j in zip(x, y):
            #     plt.text(i, j, '%s' % j, ha='center', va='bottom', size=8)
            plt.legend(markerscale=0, handlelength=0)
            if not os.path.exists('./slb_picture'):
                os.mkdir('./sib_picture')
            plt.savefig('./slb_picture/%s.png' % key)
            plt.close()


def get_slb_week_main():
    begin = time.time()
    print('get_slb_week_main 开始', time.ctime())
    ll = get_slb_final()
    if ll:
        ll = data_process(ll)
        make_bar_chart(ll)
    else:
        string = 'get_slb_final() 返回值为0'
        print(time. ctime(), string)
        write_log(string)
        send_alarm_v2(alert_data, string)
    print('get_slb_week_main 结束', time.time() - begin)


if __name__ == '__main__':
    try:
        get_slb_week_main()
    except Exception as e:
        print(e)
        write_log(str(e))
        send_alarm_v2()

