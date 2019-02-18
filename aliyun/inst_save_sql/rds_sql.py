# -*- coding:utf-8 -*-
import copy
import json
import traceback
from pprint import pprint
from functools import partial
import requests
from urllib import parse
import uuid
import time
import schedule
from config import write_log, send_alarm_v2, sign_gen, aliyun_monitor, duxin_db, AccessKeyId, AccessKeySecret, DBUtil

'''此模块的任务是10分钟一次，调用云监控的接口，把监控数据存入数据库'''

LOG = './log/rds_sql_error.log'
write_log = partial(write_log, LOG)

minitue = 10

# 获取监控数据开始和结束时间
start_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime(time.time() - 60 * minitue * 1 * 1))
end_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime())


# 告警数据
alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        # 'alert_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'alert_business': '阿里云mongo详情统计',
        'alert_function': '告警功能',
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
        return 0

    else:
        return resp_list


metrics = ('CpuUsage', 'MemoryUsage', 'DiskUsage', 'IOPSUsage', 'ConnectionUsage',
           'MySQL_ActiveSessions', 'MySQL_NetworkInNew', 'MySQL_NetworkOutNew')
metrics_sql = ('cpu_usage', 'mem_usage', 'disk_usage', 'iops_usage', 'conn_usage',
               'active_sesion', 'networkin_rate', 'networkout_rate')


def rds_sql_main():
    db = DBUtil()
    inst_l = []
    data_l = []
    rds_list = get_rds_list()
    if not rds_list:
        return 0
    id_list = [x['DBInstanceId'] for x in rds_list]

    # 描述的列表
    desc_list = [x.get('DBInstanceDescription') if x.get('DBInstanceDescription') else x['DBInstanceId'] for x in
                 rds_list]

    # 数据库类型和版本 单位 string
    engine_list = [x['Engine'] for x in rds_list]
    enginev_list = [x['EngineVersion'] for x in rds_list]

    attr_list = get_rds_attr(','.join(id_list))

    # 实例状态 单位 string
    status_list = [x['DBInstanceStatus'] for x in attr_list]
    # 锁表状态 单位string
    lock_mode = [x['LockMode'] for x in attr_list]
    max_conn = [x['MaxConnections'] for x in attr_list]
    max_iops = [x['MaxIOPS'] for x in attr_list]

    for index, inst_id in enumerate(id_list):
        # 获取这个实例id的监控信息的列表
        rds_d = {'rds_id': inst_id, 'rds_desc': desc_list[index],
                 'status': status_list[index],
                 'lock_mode': lock_mode[index],
                 'engine_v': str(engine_list[index]) + str(enginev_list[index]),
                 'max_iops': max_iops[index], 'max_conn': max_conn[index],
                 'time': time.strftime('%Y-%m-%d %H:%M:00', time.localtime())
                 }
        # 字典放到 inst_l
        print('实例名=', rds_d['rds_desc'], 'begin')
        inst_l.append(rds_d)
        for ind, metric in enumerate(metrics):
            # 获取该监控项的列表
            metric_l = get_rds_metric(inst_id, metric)
            if not metric_l:
                # 如果这个监控项没有值
                continue
            else:
                for j in metric_l:
                    data_string = j.get('timestamp')
                    data_string = time.strftime('%Y-%m-%d %H:%M:00', time.localtime(data_string / 1000))

                    d = {'rds_id': inst_id, 'metric': metrics_sql[ind], 'value_num': j.get('Average'),
                         'time': data_string}

                    data_l.append(d)

        print('实例名=', rds_d['rds_desc'], 'over')

    db.insert_rds_attr(inst_l)
    print('实例入库成功')
    db.insert_rds_data(data_l)
    print('数据入库成功')
    db.close()


if __name__ == '__main__':
    try:
        rds_sql_main()
    except Exception:
        string = str(traceback.format_exc())
        send_alarm_v2(alert_data, string)
    else:
        pass
    # rds_sql_main()




