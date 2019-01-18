# -*- coding:utf-8 -*-
import os
import copy
import json
from pprint import pprint
from functools import partial
import requests
from urllib import parse
import uuid
import time
import numpy as np
import matplotlib.pyplot as plt
from config import AccessKeyId, AccessKeySecret, send_alarm_v2, write_log, sign_gen, alert_data, func_try

LOG = './mongodb_error.log'
write_log = partial(write_log, LOG)

# 起止时间
start_time_perf = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(time.time() - 3600 * 24 * 1))
# start_time_perf = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(time.time() - 60 * 5))
end_time_perf = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())


perf_keys = ['CpuUsage', 'MemoryUsage', 'DiskUsage', 'MongoDB_IOPS', 'IOPSUsage', 'MongoDB_Connections', 'MongoDB_Network']
#              cpu使用率    内存适使用率     磁盘使用率      iops 使用量       iops使用率      连接数    网络
metric_keys = ['CPUUtilization', 'MemoryUtilization', 'DiskUtilization', 'IOPSUtilization',
               'ConnectionAmount', 'ConnectionUtilization', 'QPS', 'IntranetIn', 'IntranetOut']
#       cpu使用率   内存使用率    磁盘使用率     iops使用率    连接数量   连接使用率    qps   net_in  net_in

shard_perf_keys = ('CpuUsage', 'MemoryUsage', 'DiskUsage', 'IOPSUsage', 'MongoDB_IOPS')
#  cpu 使用率  内存使用率   磁盘使用率   iops使用率   iops数
mongo_perf_keys = ('CpuUsage', 'MemoryUsage', 'MongoDB_Connections')
#  CPU使用率   内存使用率   连接数

alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        'alert_business': '阿里云ECS情况统计',
        'alert_function': 'get_mongo',
        # 'exception_spec' : '异常说明',
    }


def get_mongo_list(PageNumber=1):
    params = {
        'Action': 'DescribeDBInstances',
        'RegionId': 'cn-beijing',
        'DBInstanceType': 'sharding',
        'PageSize': 100,
        'PageNumber': PageNumber,
        'Format': 'JSON',
        'Version': '2015-12-01',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://mongodb.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        resp_list = resp_dict['DBInstances']['DBInstance']
    except Exception as e:
        string = 'get_mongo_list 获取失败，e:%s' % str(e)
        print(string)
        write_log(string)
        send_alarm_v2(alert_data, string)
        return 0
    else:
        return resp_list


def get_attr(DBInstanceId):
    '''
    参数: 实例id,类型:字符串
    测试用 get_attr('dds-2ze9a59287cde624')
    '''
    params = {
        'Action': 'DescribeDBInstanceAttribute',
        'DBInstanceId': DBInstanceId,
        'Format': 'JSON',
        'Version': '2015-12-01',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://mongodb.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        perf_list = resp_dict['DBInstances']['DBInstance']
    except Exception as e:
        string = 'get_attr 获取失败，e:%s' % str(e)
        print(string)
        write_log(string)
        return 0
    else:
        return perf_list


def inst_perf(DBInstanceId, NodeId, Key):
    '''
    功能: 返回该实例的所有监控项的列表
    参数: DBInstanceId: 实例id, NodeId:节点id, Key: 监控项,可以','来连接多项
    性能指标如下
    CPU 使用率 	CpuUsage
    内存 使用率 	MemoryUsage
    IOPS 使用量 	MongoDB_IOPS
    IOPS 使用率 	IOPSUsage
    磁盘空间使用量 	MongoDB_DetailedSpaceUsage
    磁盘空间使用率 	DiskUsage
    测试用:
    inst_perf('dds-2ze9a59287cde624', 's-2ze6c71dc69d0fc4', ','.join(keys))
    '''
    params = {
        'Action': 'DescribeDBInstancePerformance',
        'DBInstanceId': DBInstanceId,
        'NodeId': NodeId,
        'StartTime': start_time_perf,
        'EndTime': end_time_perf,
        'Key': Key,
        'Format': 'JSON',
        'Version': '2015-12-01',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'SignatureVersion': '1.0',
        'SignatureNonce': str(uuid.uuid1()),
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://mongodb.aliyuncs.com/?' + parse.urlencode(data)
    try:
        resp = requests.get(url, timeout=16)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        perf_list = resp_dict['PerformanceKeys']['PerformanceKey']

    except Exception as e:
        string = 'inst_perf 失败，e:%s' % str(e)
        print(string)
        write_log(string)
        return 0
    else:
        return perf_list


def get_mongo_final():
    # 获取 mongo 的id
    inst_id_list = get_mongo_list()
    inst_list = []
    for ind, inst in enumerate(inst_id_list):

        # 对于一个mongodb 的 id
        inst_id = inst['DBInstanceId']
        print(time.ctime(), inst_id, 'begin')
        inst_desc = inst.get('DBInstanceDescription')  # 这个键表示对这个描述的描述,有时候没有这个键
        inst_status = inst['DBInstanceStatus']
        engine_v = str(inst['Engine'])+str(inst['EngineVersion'])
        attr_list = get_attr(inst_id)  # 里面有他的 mongo列表 和 shard 列表

        if not attr_list:
            return 0

        max_iops = attr_list[ind]['MaxIOPS']

        mongo_l = inst['MongosList']['MongosAttribute']
        shard_l = inst['ShardList']['ShardAttribute']

        # mongo的id列表
        mongo_ids = [i['NodeId'] for i in mongo_l]
        # mongo_maxiops_list = [ x['MaxIOPS'] for x in attr_list[0]['MongosList']['MongosAttribute'] ]
        # mongo_nodedescr = [ x.get('NodeDescription') for x in attr_list[0]['MongosList']['MongosAttribute'] ]

        # shard的id列表  和 存储容量列表
        shard_ids = [i['NodeId'] for i in shard_l]
        # shard_maxiops_list = [x['MaxIOPS'] for x in attr_list[0]['ShardList']['ShardAttribute'] ]
        # shard_storages = [i['NodeStorage'] for i in shard_l]  # 磁盘使用量，未启用
        # shard_nodedescr = [ x.get('NodeDescription') for x in attr_list[0]['ShardList']['ShardAttribute'] ]

        # 该实例的 字典
        inst_d = {'inst_id': inst_id, 'inst_desc': inst_desc, 'inst_status': inst_status, 'engine_v': engine_v,
                  'mongo_ids': mongo_ids, 'shard_ids': shard_ids, 'max_iops': max_iops,
                  'mongo_perfs': [], 'shard_perfs': [],
                  }

        print(time.ctime(), '-------实例结束， mongo 和 分片开始------')

        shard_list = []  # 分片的 所有实例的监控项的集合
        # 构建 内含该id的 偏函数
        shard_perf = partial(inst_perf, inst_id, Key=','.join(shard_perf_keys))
        # 'CpuUsage', 'MemoryUsage', 'DiskUsage', 'IOPSUsage', 'MongoDB_IOPS'
        for shard_id in shard_ids:
            perf_list = shard_perf(shard_id)
            # print('perf_list', perf_list)
            if perf_list:  # 一个 shard_id 的所有监控项
                d = {'shard_id': shard_id}
                print(time.ctime(), 'shard_id', shard_id, 'begin')
                for i in perf_list:  # i 是每一个监控项的字典
                    value_data = i['PerformanceValues']['PerformanceValue']
                    # print('value_data', value_data)
                    # value_list = [float( j.get('Value', '0').split('&')[0] ) if '&' in j.get('Value', '0')
                    #               else float(j.get('Value', '0')) for j in value_data]
                    value_list = []
                    for j in value_data:
                        if '&' in j.get('Value'):
                            try:
                                temp = float( j.get('Value').split('&')[0] )
                            except Exception as e:
                                pass
                            else:
                                value_list.append(float(temp))
                        else:
                            try:
                                temp2 = eval(j.get('Value'))
                            except Exception as e:
                                pass
                            else:
                                value_list.append(float(temp2))
                    value = sum(value_list) / len(value_list)
                    d[i['Key']] = value
                print(time.ctime(), 'shard_id', shard_id, 'over')
                shard_list.append(d)
            else:
                string = 'shard_id:%s 获取 inst_per 返回值为0' % shard_id
                write_log(string)
                send_alarm_v2(alert_data, string)
        # pprint(shard_list)

        mongo_list = []
        # 构建 内含该id的 偏函数
        shard_perf = partial(inst_perf, inst_id, Key=','.join(mongo_perf_keys))
        # 'CpuUsage', 'MemoryUsage', 'MongoDB_Connections'
        for mongo_id in mongo_ids:
            perf_list = shard_perf(mongo_id)
            # print('perf_list2', perf_list)
            if perf_list:  # 一个 mongo_id 的所有监控项
                d = {'mongo_id': mongo_id}
                print(time.ctime(), 'mongo_id', mongo_id, 'begin')
                for i in perf_list:  # i 是每一个监控项的字典
                    value_data = i['PerformanceValues']['PerformanceValue']  # 值和时间戳的字典
                    # value_list = [float( j.get('Value', '0').split('&')[0] ) if '&' in j.get('Value', '0')
                    #               else float(j.get('Value', '0')) for j in value_data]
                    value_list = []
                    for j in value_data:
                        if '&' in j.get('Value'):
                            try:
                                temp = float( j.get('Value').split('&')[0] )
                            except Exception as e:
                                pass
                            else:
                                value_list.append(float(temp))
                        else:
                            try:
                                temp2 = eval(j.get('Value'))
                            except Exception as e:
                                pass
                            else:
                                value_list.append(float(temp2))
                    value = sum(value_list) / len(value_list)
                    d[i['Key']] = value
                print(time.ctime(), 'mongo_id', mongo_id, 'over')
                mongo_list.append(d)
        # pprint(mongo_list)

        inst_d['mongo_perfs'] = mongo_list
        inst_d['shard_perfs'] = shard_list
        inst_list.append(inst_d)

    return inst_list


@func_try
def data_process(inst_list):
    mongo_list = inst_list[0]['mongo_perfs']
    shard_list = inst_list[0]['shard_perfs']
    shard_keys = ('top_cpu_usage', 'top_mem_usage', 'top_shard_disk_usage',
                  'top_shard_iops_usage', 'top_shard_iops')
    mongo_keys = ('top_cpu_usage', 'top_mem_usage', 'top_mongo_conn')

    def sorted_key(n):
        temp = n.get(metric)
        if isinstance(temp, int) or isinstance(temp, float):
            return temp
        else:
            return 0

    shard_ll = {}
    for ind, metric in enumerate(shard_perf_keys):
        # 排序
        sorted_metric = sorted(shard_list, key=sorted_key, reverse=True)
        # pprint(sorted_metric)
        # 取值
        l = []  # 是监控项的值
        length = 8
        if len(sorted_metric) < 8:
            length = len(sorted_metric)
        for i in range(length):
            temp_d = sorted_metric[i]
            l.append({'name': temp_d['shard_id'], shard_keys[ind]: temp_d.get(metric)})
        # 赋值
        shard_ll[shard_keys[ind]] = l

    mongo_ll = {}
    for ind, metric in enumerate(mongo_perf_keys):
        # 排序
        def sorted_key(n):
            temp = n.get(metric)
            if isinstance(temp, int) or isinstance(temp, float):
                return temp
            else:
                return 0

        sorted_metric = sorted(mongo_list, key=sorted_key, reverse=True)
        # pprint(sorted_metric)
        # 取值
        l = []  # 是监控项的值
        length = 2
        if len(sorted_metric) < 2:
            length = len(sorted_metric)
        for i in range(length):
            temp_d = sorted_metric[i]
            l.append({'name': temp_d['mongo_id'], mongo_keys[ind]: temp_d.get(metric)})
        # 赋值
        mongo_ll[mongo_keys[ind]] = l

    return shard_ll, mongo_ll


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
def make_bar_chart(shard_ll, mongo_ll):
    '''
    shard_keys = ('top_cpu_usage', 'top_mem_usage', 'top_shard_disk_usage',
                  'top_shard_iops_usage', 'top_shard_iops')
    mongo_keys = ('top_cpu_usage', 'top_mem_usage', 'top_mongo_conn')
    '''

    keys = ('top_cpu_usage', 'top_mem_usage', 'top_shard_disk_usage',
            'top_shard_iops_usage', 'top_shard_iops',
            'top_mongo_conn')

    for key in keys:
        if key in ('top_cpu_usage', 'top_mem_usage'):
            l = shard_ll.get(key)
            m = mongo_ll.get(key)
            if l and m:
                plt.figure(key, figsize=figsize, dpi=120, )  # 背景色

                y = [round(float(i[key]), 2) for i in l]
                y2 = [round(float(i[key]), 2) for i in m]
                plt.ylabel('percent(%)', fontsize=ylabel)
                plt.yticks(np.arange(-99, 99, 10), fontsize=tick_size)

                x_ticks = [i['name'] for i in l]
                x2_ticks = [i['name'] for i in m]

                x = list(range(len(x_ticks)))
                x2 = list(range(len(x2_ticks)))

                # 设置标题
                # plt.title(key, fontsize=title_size)

                plt.xticks(np.arange(0, len(x_ticks)), list(range(1, len(x_ticks) + 1)), fontsize=tick_size)

                plt.tick_params(labelsize=tick_label)
                plt.grid(axis='y', linestyle=':')

                plt.xlim(-0.8, max(x) + 7)

                ax = plt.gca()
                ax.spines['top'].set_color('none')
                ax.spines['right'].set_color('none')
                ax.spines['bottom'].set_position(('data', 0))

                label_mongo = []
                for i in range(1, len(x_ticks) + 1):
                    ii = str(i) + ':%s'
                    label_mongo.append(ii)
                label = (' \n'.join(label_mongo)) % tuple(x_ticks)

                label2_mongo = []
                for i in range(1, len(x2_ticks) + 1):
                    ii = str(i) + ':%s'
                    label2_mongo.append(ii)
                label2 = (' \n'.join(label2_mongo)) % tuple(x2_ticks)

                # print('x,y',x,y)
                plt.bar(x, y, width=width, color=color,
                        label=label)

                y2 = [-i for i in y2]

                plt.bar(x2, y2, width=width, color=color,
                        label=label2)

                plt.legend(markerscale=0, handlelength=0)
                if not os.path.exists('./mongo_picture'):
                    os.mkdir('./mongo_picture')
                plt.savefig('./mongo_picture/%s.png' % key)
                plt.close()

        elif key in ('top_shard_disk_usage', 'top_shard_iops_usage', 'top_shard_iops'):
            l = shard_ll.get(key)
            if l:
                x_ticks = [i['name'] for i in l]
                y = [round(float(i[key]), 2) for i in l]
                x = list(range(len(x_ticks)))

                plt.figure(key, figsize=figsize, dpi=120, )  # 背景色

                if key in ('top_shard_disk_usage', 'top_shard_iops_usage'):
                    plt.yticks(fontsize=tick_size)
                    plt.ylabel('percent(%)', fontsize=ylabel)
                else:
                    plt.yticks(fontsize=tick_size)
                    plt.ylabel('count', fontsize=ylabel)

                # plt.title(key, fontsize=title_size)
                plt.xticks(np.arange(0, len(x_ticks)), list(range(1, len(x_ticks) + 1)), fontsize=tick_size)

                plt.tick_params(labelsize=tick_label)
                plt.grid(axis='y', linestyle=':')

                plt.xlim(-0.8, max(x) + 7)

                ax = plt.gca()
                ax.spines['top'].set_color('none')
                ax.spines['right'].set_color('none')
                ax.spines['bottom'].set_position(('data', 0))

                label = []
                for i in range(1, len(x_ticks) + 1):
                    ii = str(i) + ':%s'
                    label.append(ii)
                label = (' \n'.join(label)) % tuple(x_ticks)

                plt.bar(x, y, width=width, color=color,
                        label=label, )

                plt.legend(markerscale=0, handlelength=0)
                plt.savefig('./mongo_picture/%s.png' % key)
                plt.close()

        elif key == 'top_mongo_conn':
            l = mongo_ll.get(key)
            x_ticks = [i['name'] for i in l]
            y = [round(float(i[key]), 2) for i in l]
            x = list(range(len(x_ticks)))

            plt.figure(key, figsize=figsize, dpi=120, )  # 背景色

            plt.yticks(fontsize=tick_size)
            plt.ylabel('count', fontsize=ylabel)

            # plt.title(key, fontsize=title_size)
            plt.xticks(np.arange(0, len(x_ticks)), list(range(1, len(x_ticks) + 1)), fontsize=tick_size)

            plt.tick_params(labelsize=tick_label)
            plt.grid(axis='y', linestyle=':')

            plt.xlim(-0.8, max(x) + 7)

            ax = plt.gca()
            ax.spines['top'].set_color('none')
            ax.spines['right'].set_color('none')
            ax.spines['bottom'].set_position(('data', 0))

            label = []
            for i in range(1, len(x_ticks) + 1):
                ii = str(i) + ':%s'
                label.append(ii)
            label = (' \n'.join(label)) % tuple(x_ticks)

            plt.bar(x, y, width=width, color=color,
                    label=label, )

            plt.legend(markerscale=0, handlelength=0)
            if not os.path.exists('./mongo_picture'):
                os.mkdir('./mongo_picture')
            plt.savefig('./mongo_picture/%s.png' % key)
            plt.close()
        else:
            pass


def get_mongo_week_main():
    begin = time.time()
    print(time.ctime(), 'get_mongo_week begin')
    ll = get_mongo_final()
    if ll:
        l1, l2 = data_process(ll)
        make_bar_chart(l1, l2)
    else:
        string = 'get_mongo_final 返回值为0'
        write_log(string)
        send_alarm_v2(alert_data, string)
    print('get_mongo_week_main 用时', time.time()-begin)


if __name__ == '__main__':
    # try:
    #     get_mongo_week_main()
    # except Exception as e:
    #     print(str(e))
    #     write_log(e)
    # get_mongo_week_main()
    temp = inst_perf('dds-2ze9a59287cde624', 's-2ze6c71dc69d0fc4', ','.join(shard_perf_keys) )
