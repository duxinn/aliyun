# -*- coding:utf-8 -*-
import re
from collections import OrderedDict
from pprint import pprint
import traceback
from functools import partial
import copy
import json
import requests
from urllib import parse
import uuid
import time
from config import DBUtil, write_log, send_alarm_v2, sign_gen, AccessKeyId, AccessKeySecret

'''此模块的任务是10分钟一次，调用云监控的接口，把监控数据存入数据库'''

LOG = './log/mongo_sql_error.log'
write_log = partial(write_log, LOG)

minitue = 10

start_time = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(time.time() - 60 * minitue * 1 * 1))
end_time = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())

start_time_metric = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 60 * minitue * 1 * 1))
end_time_metric = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

alert_data = {
        'id': 'ggzh',
        'level': '13',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        'alert_business': '阿里云监控统计',
        'alert_function': 'mongodb 每天的数据入库',
        # 'exception_spec' : '异常说明',
    }

perf_keys = ('CpuUsage', 'MemoryUsage', 'DiskUsage', 'MongoDB_IOPS', 'IOPSUsage', 'MongoDB_Connections', 'MongoDB_Network')
metric_keys = ('CPUUtilization', 'MemoryUtilization', 'DiskUtilization', 'IOPSUtilization',
               'ConnectionAmount', 'ConnectionUtilization', 'QPS',
               'IntranetIn', 'IntranetOut')

shard_perf_keys = ('CpuUsage', 'MemoryUsage', 'DiskUsage', 'IOPSUsage', 'MongoDB_IOPS')
mongo_perf_keys = ('CpuUsage', 'MemoryUsage', 'MongoDB_Connections')

# 入库变换字段名
metric_keys_sql = ('cpu_usage', 'mem_usage', 'disk_usage', 'iops_usage',
                   'connection', 'connection_usage', 'qps',
                   'traffic_in', 'traffic_out')
shard_perf_keys_sql = ('cpu_usage', 'mem_usage', 'disk_usage', 'iops_usage', 'iops')
mongo_perf_keys_sql = ('cpu_usage', 'mem_usage', 'connection')


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
        string = 'get_mongo_list 获取失败，' + str(traceback.format_exc())
        # print(string)
        write_log(string)
        return 0
    else:
        return resp_list


def inst_perf(DBInstanceId, NodeId, Key, start_time, end_time):
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
        'StartTime': start_time,
        'EndTime': end_time,
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
        resp = requests.get(url, timeout=5)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        perf_list = resp_dict['PerformanceKeys']['PerformanceKey']
    except Exception as e:
        string = 'gest_rds_list 获取rds失败，' + str(traceback.format_exc())
        # print(string)
        write_log(string)
        return 0
    else:
        return perf_list


def get_mongo_metric(instanceId, Metric, start_time_metric, end_time_metric):
    params = {
        'Action': 'QueryMetricList',
        'Project': 'acs_mongodb',
        'Metric': Metric,
        'Period': '300',
        # 'Period': '60', 无数据
        'StartTime': start_time_metric,
        'EndTime': end_time_metric,
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
        # print(resp_dict)
        resp_list = resp_dict['Datapoints']
    except Exception as e:
        string = 'get_inst_metric 获取监控数据失败，' + str(traceback.format_exc())
        write_log(string)
        # print(string)
        return 0

    else:
        return resp_list


def mongo_sql_main():
    mongodb_l = get_mongo_list()
    inst_l = []
    mongodb_data_l = []
    node_data_l = []
    # 每个监控项的 数据，  处理、入库

    def node_sql(perf_list, node_id, node_type):
        print('node_id', node_id, 'begin')
        for i in perf_list:  # i 是每一个监控项的字典
            metric = 'cpu_usage' if i['Key'] == 'CpuUsage' \
                else 'mem_usage' if i['Key'] == 'MemoryUsage' \
                else 'disk_usage' if i['Key'] == 'DiskUsage' \
                else 'iops_usage' if i['Key'] == 'IOPSUsage' \
                else 'iops' if i['Key'] == 'MongoDB_IOPS' \
                else 'connection' if i['Key'] == 'MongoDB_Connections' \
                else i['Key']
            performance_value = i['PerformanceValues']['PerformanceValue']
            for j in performance_value:  # j 是时间和日期的字典
                data_string = re.sub(r':\d\dZ$', ':00', j['Date'].replace('T', ' '))  # 替换j['Date']
                data_string = time.strftime('%Y-%m-%d %H:%M:00', time.localtime(time.mktime(time.strptime(data_string, '%Y-%m-%d %H:%M:%S') ) + 8 * 3600))
                d = {'node_id': node_id,
                     'metric': metric,
                     'time': data_string,
                     }
                if '&' in j.get('Value'):
                    try:
                        temp = float(j.get('Value').split('&')[0])  # 得到值
                    except Exception:
                        pass
                    else:
                        d['value_num'] = temp
                        node_data_l.append(d)
                else:
                    try:
                        temp2 = float(j.get('Value'))
                    except Exception:
                        pass
                    else:
                        d['value_num'] = temp2
                        node_data_l.append(d)
        print('node_id', node_id, 'over')

    if mongodb_l:  # 获取实例列表的值
        for mongodb in mongodb_l:
            mongodb_id = mongodb['DBInstanceId']
            mongodb_desc = mongodb.get('DBInstanceDescription')  # 这个键表示对这个描述的描述,有时候没有这个键
            mongodb_status = mongodb['DBInstanceStatus']
            engine_v = str(mongodb['Engine']) + str(mongodb['EngineVersion'])
            mongo_l = mongodb['MongosList']['MongosAttribute']
            shard_l = mongodb['ShardList']['ShardAttribute']
            # 构造两个列表，让以后使用
            mongo_ids = [i['NodeId'] for i in mongo_l]
            shard_ids = [i['NodeId'] for i in shard_l]

            mongodb_d = {'mongodb_id': mongodb_id, 'desc': mongodb_desc,
                         'status': mongodb_status, 'engine_v': engine_v,
                         'time': time.strftime('%Y-%m-%d %H:%M:00', time.localtime(time.time())),
                         'mongo_id': ','.join(mongo_ids), 'shard_id': ','.join(shard_ids)
                         }
            inst_l.append(mongodb_d)

            # 入库实例 的监控值  mongo_data
            for ind, Metric in enumerate(metric_keys):
                # 获取 mongodb 的每个监控项
                metric_data = get_mongo_metric(mongodb_id, Metric, start_time_metric, end_time_metric)
                if metric_data:
                    for k in metric_data:  # k 含有时间戳和数据的字典
                        if k['role'] == 'Primary':
                            mongodb_d = {'mongodb_id': mongodb_id,
                                         'metric': metric_keys_sql[ind],
                                         'value_num': k['Average'],
                                         'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(k['timestamp'] / 1000)))
                                         }
                            mongodb_data_l.append(mongodb_d)
                else:
                    string = 'get_mongo_metric({}, {}) 获取 mongodb 监控项返回值为0'.format(mongodb_id, Metric)
                    print(string)
                    write_log(string)
                    send_alarm_v2(alert_data, string)

            print('mongodb实例结束，路由和分片开始')
            # 构建 内含该id的 监控项的偏函数
            shard_perf = partial(inst_perf, mongodb_id, Key=','.join(shard_perf_keys),
                                 start_time=start_time, end_time=end_time)
            for shard_id in shard_ids:
                # 每一个分片的 请求
                perf_list = shard_perf(shard_id)
                if perf_list:  # 一个 shard_id 的所有监控项
                    # print('perf_list', perf_list)
                    node_sql(perf_list, shard_id, node_type='shard')
                else:
                    string = 'shard_id:%s 获取 inst_per 返回值为0' % shard_id
                    write_log(string)
                    send_alarm_v2(alert_data, string)

            # 构建 内含该id的 监控项的偏函数
            mongos_perf = partial(inst_perf, mongodb_id, Key=','.join(mongo_perf_keys),
                                  start_time=start_time, end_time=end_time)
            for mongo_id in mongo_ids:
                # 每一个分片的请求
                perf_list = mongos_perf(mongo_id)
                if perf_list:  # 一个 mongo_id 的所有监控项
                    node_sql(perf_list, mongo_id, node_type='mongo')
                else:
                    string = 'mongo_id:%s 获取 inst_per 返回值为0' % mongo_id
                    write_log(string)
                    send_alarm_v2(alert_data, string)
    else:  # 没有获取到值
        string = 'get_mongo_list 获取 mongodb 列表返回值为0'
        write_log(string)
        send_alarm_v2(alert_data, string)

    # 关闭游标
    db = DBUtil()
    if inst_l:
        # db.insert_mongo_attr(inst_l)
        print('inst_l 入库成功')
    if mongodb_data_l:
        # db.insert_mongo_data(mongodb_data_l)
        print('mongodb_data_l 入库成功')
    if node_data_l:
        print(node_data_l)
        m = OrderedDict()
        for k in node_data_l:
            # k['metric'], k['node_id'], k['time'] 构成的元组为键， k['value_num']的列表为值
            # m.setdefault((k['metric'], k['node_id'], k['time']), [])
            # m[(k['metric'], k['node_id'], k['time'])].append(k['value_num'])
            if (k['metric'], k['node_id'], k['time']) not in m:
                m[(k['metric'], k['node_id'], k['time'])] = []
                m[(k['metric'], k['node_id'], k['time'])].append(k['value_num'])
            else:
                m[(k['metric'], k['node_id'], k['time'])].append(k['value_num'])
        node_data_l2 = []
        for n in m:
            print('m[n]', m[n])
            node_data_l2.append({'metric': n[0], 'node_id': n[1],
                                 'time': n[2], 'value_num': sum(m[n]) / len(m[n])})
        if node_data_l2:
            # pprint(node_data_l2)
            db.insert_mongo_node_data(node_data_l2)
            print('node_data_l2 入库成功')

    db.close()


if __name__ == '__main__':
    # try:
    #     mongo_sql_main()
    # except Exception:
    #     string = str(traceback.format_exc())
    #     send_alarm_v2(alert_data, string)
    # else:
    #     pass
    mongo_sql_main()


