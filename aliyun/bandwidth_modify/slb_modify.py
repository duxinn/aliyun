# -*- coding:utf-8 -*-
import copy
import json
import traceback
import requests
from hashlib import sha1
import hashlib
import base64
import hmac
from urllib import parse
import uuid
import time
import datetime
import schedule
from collections import OrderedDict

AccessKeyId = 'xxx'
AccessKeySecret = 'xxx'

# du-daa-slb
LoadBalancerId = 'xxx'

# 设置最大带宽
max_band_width = 186
# 调整倍数
multiple = 1.2

# 记录日志的文件
LOG = 'daa_bandwidth_modify_2.log'

alert_data = {
        'id': 'ggzh',
        'level': '11',
        'dep': 'du-op',
        'env': 'prod',
        'alert_level': '中',
        # 'alert_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'alert_business' : '负载均衡带宽调节',
        'alert_function' : 'daa负载均衡带宽调节',
        # 'exception_spec' : '异常说明',
    }


def write_log(string):
    with open(LOG, 'a') as f:
        now_time = datetime.datetime.now().strftime("[ %Y-%m-%d %H:%M:%S ] ")
        f.write(now_time + str(string) + '\n')


def send_alarm_v2(string):
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
        code = eval(resp.text).get('code')
    except Exception as e:
        write_log('send_alarm_v2发送告警异常, e=' + str(e))
    else:
        if code not in (0, 1010):
            write_log('send_alarm_v2发送告警异常, code=' + str(code))


def sign_gen(params):
    """
    params :请求参数，类型为字典
    此函数功能是生成签名，
    先进行百分号编码，将生成的字符串，进行拼接和编码，生成签名。
    """
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
    signature_hmac = hmac.new((AccessKeySecret+'&').encode(), string_to_sign.encode(), sha1).digest()
    signature = base64.encodebytes(signature_hmac).strip().decode()
    return signature


def modify(band_width):
    """
    params :请求参数，类型为字典
    生成签名，构建请求参数，发起调节
    """
    params = {
        'Action': 'ModifyLoadBalancerInternetSpec',
        'LoadBalancerId': LoadBalancerId,
        # 'InternetChargeType': 'paybybandwidth',
        'Bandwidth': band_width,
        'RegionId': 'cn-beijing',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'Format': 'JSON',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': str(uuid.uuid1()),
        'Version': '2014-05-15',
        'SignatureVersion': '1.0',
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://slb.aliyuncs.com/?' + parse.urlencode(data)
    resp = requests.get(url)
    if 'error' not in resp.text:
        return 1
    else:
        return resp.text


def query():
    """此函数用于查询 流出流量，即实例每秒出bit数
    params：请求参数，类型为字典"""
    params = {
        'Action': 'QueryMetricLast',
        'Project': 'acs_slb_dashboard',
        'Metric': 'InstanceTrafficTX',
        'Period': '60',
        'Dimensions': '{"instanceId":"%s"}' % LoadBalancerId,
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
    url = 'http://metrics.cn-beijing.aliyuncs.com/?'+parse.urlencode(data)

    resp = requests.get(url)
    if 'error' in resp.text:
        # 如果发生了异常，返回resp.text字符串
        return resp.text
    else:
        # 没有发生异常，获取查询指标之 实例每秒出bit数
        try:
            resp_dict = json.loads(resp.text)
            InstanceTrafficTX = resp_dict["Datapoints"][0]["Average"]
            # InstanceTrafficTX = int(InstanceTrafficTX)
        except Exception as e:
            # print(e)
            return str(e)+'\n解析出现异常\n'+str(resp.text)
        else:
            InstanceTrafficTX = InstanceTrafficTX / 10 ** 6
            return InstanceTrafficTX


def desc():
    """此函数用于查询实例信息 的带宽设置值
    params：请求参数，类型为字典"""
    params = {
        'Action': 'DescribeLoadBalancerAttribute',
        'LoadBalancerId': LoadBalancerId,
        'RegionId': 'cn-beijing',
        'Timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'Format': 'JSON',
        'AccessKeyId': AccessKeyId,
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': str(uuid.uuid1()),
        'Version': '2014-05-15',
        'SignatureVersion': '1.0',
    }
    signature = sign_gen(params)
    data = copy.deepcopy(params)
    data['Signature'] = signature
    url = 'https://slb.aliyuncs.com/?'+parse.urlencode(data)
    resp = requests.get(url)
    if 'error' in resp.text:
        return resp.text
    else:
        try:
            result = json.loads(resp.text)["Bandwidth"]
            result = int(result)
        except Exception as e:
            return str(e)+'\n解析出现异常\n'+str(resp.text)
        else:
            return result


def modify_once():
    string = str(time.ctime()) + ' 开始调节'
    print(string)
    write_log(string)
    # 检测 实例每秒出bit数  取不到值，返回是response.text
    band_width = query()
    if not (isinstance(band_width, float) or isinstance(band_width, int)):
        # 检测 实例每秒出bit数 异常
        string = str(time.ctime()) + ' 检测实例每秒出bit数异常,返回的值是{}, 将调节至最大{}'.format(str(band_width), str(max_band_width))
        print(string)
        write_log(string)
        # 调节到最高值
        band_width = max_band_width
        send_alarm_v2(string)
    else:
        # 检测 实例每秒出bit数 正常
        string = str(time.ctime()) + ' 现在获取到的流出流量是' + str(band_width)
        print(string)
        write_log(string)

        band_width = int(band_width * multiple)
        string = str(time.ctime()) + ' 将要设置为的带宽峰值是' + str(band_width)
        print(string)
        write_log(string)

    time.sleep(1)
    modify_result = modify(band_width)
    if modify_result != 1:
        # 修改失败
        string = str(time.ctime()) + ' 修改带宽峰值失败,返回的是：' + str(modify_result)
        print(string)
        write_log(string)
        send_alarm_v2(string)
    else:
        # 修改成功
        time.sleep(1)
        # 获取设置值
        desc_result = desc()
        if isinstance(desc_result, int):
            # 获取成功
            string = str(time.ctime()) + ' 修改带宽成功，现在设置的峰值带宽是' + str(desc_result)
            print(string)
            write_log(string)
        else:
            # 获取失败
            string = str(time.ctime()) + ' 修改带宽成功，获取修改后的带宽值失败,获取的值是' + str(desc_result)
            print(string)
            write_log(string)


if __name__ == '__main__':
    try:
        modify_once()
    except Exception as e:
        print(str(e), repr(str(traceback.format_exc())))
        # send_alarm_v2(str(e)+'\nr\"\"\"' + str(traceback.format_exc()) + '\n\"\"\"')
        send_alarm_v2(str(e) + repr(traceback.format_exc()))
    else:
        pass



