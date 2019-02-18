# -*- coding:utf-8 -*-
import traceback
from functools import partial
from pprint import pprint
import copy
import json
import requests
from urllib import parse
import uuid
import time
import schedule
from config import write_log, send_alarm_v2, sign_gen, aliyun_monitor, duxin_db, AccessKeyId, AccessKeySecret, DBUtil

'''此模块的任务是10分钟一次，调用云监控的接口，把监控数据存入数据库'''

LOG = './log/slb_sql_error.log'
write_log = partial(write_log, LOG)

mintinue = 10

start_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime(time.time() - 60 * mintinue * 1 * 1))
end_time = time.strftime('%Y-%m-%dT%H:%M:00Z', time.gmtime())


# 告警数据
alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '低',
        'alert_business': '阿里云mongo详情统计',
        'alert_function': '告警功能',
        # 'exception_spec' : '异常说明',
    }

name_l = ('du-ddi_slb', 'du-dna-slb', 'du-iddi_slb',
          'du-pixel-bj-slb', 'du-rtb_slb',
          'du-dcc-slb', 'du-dai_slb', 'du-idna-slb',
          'du-idaa-slb', 'du-daa-slb')

id_l = ('lb-2zeco0382sr00h9yfrsb1', 'lb-2zegrhxfptym9ot1ve6zo', 'lb-2ze4wm4a4bgptkkfq2rrv',
            'lb-2zep9dqdb42drtcz51dad', 'lb-2zewsoc4lbdi9xq8zmzih',
            'lb-2zeliy8kebtk62ukrtu94', 'lb-2zejw0hmknp4etnojc2t9', 'lb-2zeanyim1j82k7e664tkz',
            'lb-2zeb10qn5xu5youx1lx0p', 'lb-2ze3tq78xyn1jsruzilxs')

metrics = ('InstanceTrafficRX', 'InstanceTrafficTX',
           # 每秒流入\流出流量  bit/s
           'InstancePacketRX', 'InstancePacketTX',
           # 每秒入包数\出包数
           'InstanceActiveConnection', 'InstanceInactiveConnection',
           # 每秒活跃连接数\非活跃连接数
           'InstanceMaxConnection', 'InstanceNewConnection',
           # 每秒最大并发数\新建连接数
           'InstanceDropConnection'
           # 丢弃连接数
           )

metrics_sql = ('networkin_rate', 'networkout_rate', 'packet_in', 'packet_in',
               'active_conn', 'inactive_conn', 'max_conn', 'new_conn',
               'drop_conn')


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
        resp = requests.get(url)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
    except Exception as e:
        string = 'gest_rds_list 获取rds失败，e:' + str(e) + str(traceback.format_exc())
        # print(string)
        write_log(string)
        return 0
    else:
        return resp_dict


def get_metric(instanceId, Metric):
    '''
    功能 对某个实例获取她的监控项的值
    参数 instanceId 表示实例id
        Metric 表示监控项
    测试参数如下
    get_metric('lb-2zep9dqdb42drtcz51dad', 'InstanceTrafficRX')
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
        resp = requests.get(url)
        resp_dict = json.loads(resp.text)
        # pprint(resp_dict)
        resp_list = resp_dict['Datapoints']
    except Exception as e:
        string = 'gest_rds_list 获取rds失败，e:' + str(e) + str(traceback.format_exc())
        # print(string)
        write_log(string)
        return 0
    else:
        return resp_list


def slb_sql_main():
    db = DBUtil()
    inst_l = []
    data_l = []
    for sid in id_l:
        attr_list = slb_attr(sid)  # 属性列表
        if not attr_list:
            string = 'slb_attr 函数返回值为 0'
            write_log(string)
            send_alarm_v2(alert_data, string)
        else:
            slb_name = attr_list.get('LoadBalancerName')  # 名字
            print(slb_name, '开始')
            slb_status = attr_list.get('LoadBalancerStatus')  # 状态
            addr = attr_list.get('Address')  # 服务地址
            port_list = attr_list.get('ListenerPorts').get('ListenerPort')  # 端口列表 [443, 80]
            port_list = ','.join([str(i) for i in port_list])
            spec = attr_list.get('LoadBalancerSpec')  # 实例规格
            bandwidth = attr_list.get('Bandwidth')  # 带宽
            region = attr_list.get('RegionId')  # 带宽
            # 构造实例的字典
            slb_d = {'slb_id': sid, 'name': slb_name, 'status': slb_status, 'addr': addr,
                     'bandwidth': bandwidth,
                     'port_list': port_list, 'spec': spec, 'region': region,
                     'time': time.strftime('%Y-%m-%d %H:%M:00', time.localtime())}
            # 属性追加到属性列表
            inst_l.append(slb_d)

            # 构建含有该id的偏函数
            metric_id = partial(get_metric, sid)
            # 获取实例该监控项的数据
            for ind, metric in enumerate(metrics):
                metric_list = metric_id(metric)
                if not metric_list:
                    continue
                for j in metric_list:
                    data_string = j.get('timestamp')
                    data_string = time.strftime('%Y-%m-%d %H:%M:00', time.localtime(data_string / 1000))

                    d = {'slb_id': sid, 'metric': metrics_sql[ind],
                         'value_num': j.get('Average'),
                         'time': data_string}
                    data_l.append(d)
            print(slb_d['name'], 'over')

    if inst_l:
        db.insert_slb_attr(inst_l)
        print('实例入库成功')
    if data_l:
        db.insert_slb_data(data_l)
        print('数据入库成功')
    db.close()


if __name__ == '__main__':
    try:
        slb_sql_main()
    except Exception:
        string = str(traceback.format_exc())
        send_alarm_v2(alert_data, string)
    else:
        pass
    # slb_sql_main()


