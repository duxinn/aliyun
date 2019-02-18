import os
import smtplib
import time
import traceback
from collections import OrderedDict
from functools import partial
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from get_ecs import get_ecs_week_main
from get_rds import get_rds_week_main
from get_mongo import get_mongo_week_main
from get_slb import get_slb_week_main
from monitor_dep import send_dep
from config import AccessKeyId, AccessKeySecret, send_alarm_v2, write_log, sign_gen, alert_data, aliyun_monitor


LOG = './monitor_all_error.log'
write_log = partial(write_log, LOG)

mail_host = ""
mail_sender = ""
mail_username = ""
mail_password = ""

email_list = ['xx@shuzilm.cn', 'xx@shuzilm.cn']
cc_list = ['xx@shuzilm.cn']

technical_department = [12993126, 74448429, 48804840, 48806835, 48815834, 48828847, 48879846]
#                       技术中心     技术部     业务保障部 云端       终端       前端      大数据


def addimg(src, imgid):  # 文件路径、图片id
    fp = open(src, 'rb')  # 打开文件
    msg_image = MIMEImage(fp.read())  # 读入msg_image中
    fp.close()  # 关闭文件
    msg_image.add_header('Content-ID', imgid)
    return msg_image


def send_email(email_list, subject="阿里云监控周报"):
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = mail_sender
    msg['To'] = ', '.join(email_list)
    msg['Cc'] = ', '.join(cc_list)

    # 总共的资源
    content_head = """
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <style>
                h1{text-align:center}
                h2{text-align:center}
                .contain{
                    margin-left:3%
                }
                fieldset {
                    margin-left:4%;
                    margin-right:4%;
                }
                .line{
                    align:center;
                    margin-left:3%;
                    width: 110%;
                }
                .line div{
                    display: inline-block;
                    width: 45%;
                    margin-left: 0%;
                }
                .line h5{
                    margin-left: 33%;
                }
                .line_title{
                    margin-left:5%;
                    font-weight: 550;
                }
                .main-footer{
                    margin-left: 50px !important;
                    z-index: 845;
                    display: block;
                    box-sizing: border-box;
                    background: #fff;
                    padding: 15px;
                    color: #444;
                    border-top: 1px solid #d2d6de;
                    transition: transform .3s ease-in-out,margin .3s ease-in-out;
                }
            </style>
            <meta charset="UTF-8">
            <title>阿里云监控周报</title>
        </head>
        <body>
            <div class="contain">
                <h1>阿里云监控周报</h1>
    """

    # total_t = ('./ecs_picture/top_cpu_usage.png', './ecs_picture/top_mem_usage.png',
    #            './ecs_picture/top__usage.png', './ecs_picture/top_data_usage.png', './ecs_picture/top_data1_usage.png',
    #            './ecs_picture/top_data2_usage.png', './ecs_picture/top_data3_usage.png',
    #            './ecs_picture/top_networkin_rate.png', './ecs_picture/top_networkout_rate.png',
    #            './rds_picture/top_cpu_usage.png', './rds_picture/top_mem_usage.png', './rds_picture/top_disk_usage.png',
    #            './rds_picture/top_iops_usage.png', './rds_picture/top_conn_usage.png',
    #            './rds_picture/top_networkin_rate.png', './rds_picture/top_networkout_rate.png',
    #            './mongo_picture/top_cpu_usage.png', './mongo_picture/top_mem_usage.png',
    #            './mongo_picture/top_mongo_conn.png', './mongo_picture/top_shard_disk_usage.png',
    #            './mongo_picture/top_shard_iops.png', './mongo_picture/top_shard_iops_usage.png',
    #            './slb_picture/top_networkin_rate.png', './slb_picture/top_networkout_rate.png',
    #            './slb_picture/top_packetin.png', './slb_picture/top_packetout.png', './slb_picture/top_active_conn.png',
    #            './slb_picture/top_inactive_conn.png', './slb_picture/top_max_conn.png', './slb_picture/top_new_conn.png',
    #            './slb_picture/top_drop_networkin_rate.png', './slb_picture/top_drop_networkout_rate.png',
    #            './slb_picture/top_drop_packetin.png', './slb_picture/top_drop_packetout.png',
    #            './slb_picture/top_drop_conn.png')
    # total = OrderedDict()
    # for file in total_t:
    #     total[file] = True if os.path.exists(file) else False

    content_head += """
        <!--ecs-->
        <fieldset>
        <legend class="line_title">ECS 资源消耗 top 10</legend>
        <div class="line">
            <div>
                <h5>CPU使用率</h5>
                <img src="cid:ecs_top_cpu_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>内存使用率</h5>
                <img src="cid:ecs_top_mem_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>磁盘根目录使用率</h5>
                <img src="cid:ecs_top__usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>磁盘data目录使用率</h5>
                <img src="cid:ecs_top_data_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>磁盘data1目录使用率</h5>
                <img src="cid:ecs_top_data1_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>磁盘data2目录使用率</h5>
                <img src="cid:ecs_top_data2_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>磁盘data3目录使用率</h5>
                <img src="cid:ecs_top_data3_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>上行带宽（每秒流入流量）</h5>
                <img src="cid:ecs_top_networkin_rate" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>下行带宽（每秒流出流量）</h5>
                <img src="cid:ecs_top_networkout_rate" alt="" width="85%" height="85%">
            </div>
        </div>
        </fieldset>
        <br>

        <!--rds-->
        <fieldset>
        <legend class="line_title">RDS 资源消耗</legend>
        <div class="line">
            <div>
                <h5>CPU使用率</h5>
                <img src="cid:rds_top_cpu" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>内存使用率</h5>
                <img src="cid:rds_top_mem" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>磁盘使用率</h5>
                <img src="cid:rds_top_disk" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>IOPS</h5>
                <img src="cid:rds_top_iops" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>连接数</h5>
                <img src="cid:rds_top_conn" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>上行带宽（每秒流入流量）</h5>               
                <img src="cid:rds_top_netin" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>下行带宽（每秒流出流量)</h5>
                <img src="cid:rds_top_netout" alt="" width="85%" height="85%">
            </div>
        </div>
        </fieldset>
        <br>

        <!--mongo-->
        <fieldset>
        <legend class="line_title">MongoDB 资源消耗</legend>
        <div class="line">
            <div>
                <h5>CPU使用率</h5>
                <img src="cid:mongo_top_cpu_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>内存使用率</h5>
                <img src="cid:mongo_top_mem_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒连接数</h5>
                <img src="cid:mongo_top_conn" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>磁盘使用率</h5>
                <img src="cid:mongo_top_disk_usage" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>IOPS</h5>
                <img src="cid:mongo_top_iops" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>IOPS使用率</h5>
                <img src="cid:mongo_top_iops_usage" alt="" width="85%" height="85%">
            </div>
        </div>
        </fieldset>
        <br>

        <!--slb-->
        <fieldset>
        <legend class="line_title">SLB 资源消耗</legend>
        <div class="line">
            <div>
                <h5>活跃连接数</h5>
                <img src="cid:slb_top_active_conn" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>非活跃连接数</h5>
                <img src="cid:slb_top_inactive_conn" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>上行带宽（每秒流入流量）</h5>
                <img src="cid:slb_top_netin" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>下行带宽（每秒流出流量）</h5>
                <img src="cid:slb_top_netout" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒最大连接数</h5>
                <img src="cid:slb_top_max_conn" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒新建连接数</h5>
                <img src="cid:slb_top_new_conn" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒入包数</h5>
                <img src="cid:slb_top_packetin" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒出包数</h5>
                <img src="cid:slb_top_packetout" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒丢失连接数</h5>
                <img src="cid:slb_top_drop_conn" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒丢入流量数</h5>
                <img src="cid:slb_top_drop_netin" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒丢出流量数</h5>
                <img src="cid:slb_top_drop_netout" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒丢入包数</h5>
                <img src="cid:slb_top_drop_packetin" alt="" width="85%" height="85%">
            </div>
            <div>
                <h5>每秒丢出包数</h5>
                <img src="cid:slb_top_drop_packetout" alt="" width="85%" height="85%">
            </div>
        </div>
        </fieldset>
"""

    # 云端部门
    du_srv_cpu_usage = OrderedDict()
    du_srv_mem_usage = OrderedDict()
    du_srv__usage = OrderedDict()
    du_srv_data_usage = OrderedDict()
    du_srv_data1_usage = OrderedDict()
    du_srv_data2_usage = OrderedDict()
    du_srv_data3_usage = OrderedDict()
    du_srv_networkin_rate = OrderedDict()
    du_srv_networkout_rate = OrderedDict()
    for i in range(1, 8):
        du_srv_cpu_usage[i] = True if os.path.exists('./du_srv/top_cpu_usage_%s.png' % i) else False
        du_srv_mem_usage[i] = True if os.path.exists('./du_srv/top_mem_usage_%s.png' % i) else False
        du_srv__usage[i] = True if os.path.exists('./du_srv/top__usage_%s.png' % i) else False
        du_srv_data_usage[i] = True if os.path.exists('./du_srv/top_data_usage_%s.png' % i) else False
        du_srv_data1_usage[i] = True if os.path.exists('./du_srv/top_data1_usage_%s.png' % i) else False
        du_srv_data2_usage[i] = True if os.path.exists('./du_srv/top_data2_usage_%s.png' % i) else False
        du_srv_data3_usage[i] = True if os.path.exists('./du_srv/top_data3_usage_%s.png' % i) else False
        du_srv_networkin_rate[i] = True if os.path.exists('./du_srv/top_networkin_rate_%s.png' % i) else False
        du_srv_networkout_rate[i] = True if os.path.exists('./du_srv/top_networkout_rate_%s.png' % i) else False
    # 广告部门
    du_ad_cpu_usage = OrderedDict()
    du_ad_mem_usage = OrderedDict()
    du_ad__usage = OrderedDict()
    du_ad_data_usage = OrderedDict()
    du_ad_data1_usage = OrderedDict()
    du_ad_data2_usage = OrderedDict()
    du_ad_data3_usage = OrderedDict()
    du_ad_networkin_rate = OrderedDict()
    du_ad_networkout_rate = OrderedDict()
    for i in range(1, 8):
        du_ad_cpu_usage[i] = True if os.path.exists('./du_ad/top_cpu_usage_%s.png' % i) else False
        du_ad_mem_usage[i] = True if os.path.exists('./du_ad/top_mem_usage_%s.png' % i) else False
        du_ad__usage[i] = True if os.path.exists('./du_ad/top__usage_%s.png' % i) else False
        du_ad_data_usage[i] = True if os.path.exists('./du_ad/top_data_usage_%s.png' % i) else False
        du_ad_data1_usage[i] = True if os.path.exists('./du_ad/top_data1_usage_%s.png' % i) else False
        du_ad_data2_usage[i] = True if os.path.exists('./du_ad/top_data2_usage_%s.png' % i) else False
        du_ad_data3_usage[i] = True if os.path.exists('./du_ad/top_data3_usage_%s.png' % i) else False
        du_ad_networkin_rate[i] = True if os.path.exists('./du_ad/top_networkin_rate_%s.png' % i) else False
        du_ad_networkout_rate[i] = True if os.path.exists('./du_ad/top_networkout_rate_%s.png' % i) else False
    # du_da 大数据
    du_da_cpu_usage = OrderedDict()
    du_da_mem_usage = OrderedDict()
    du_da__usage = OrderedDict()
    du_da_data_usage = OrderedDict()
    du_da_data1_usage = OrderedDict()
    du_da_data2_usage = OrderedDict()
    du_da_data3_usage = OrderedDict()
    du_da_networkin_rate = OrderedDict()
    du_da_networkout_rate = OrderedDict()
    for i in range(1, 8):
        du_da_cpu_usage[i] = True if os.path.exists('./du_da/top_cpu_usage_%s.png' % i) else False
        du_da_mem_usage[i] = True if os.path.exists('./du_da/top_mem_usage_%s.png' % i) else False
        du_da__usage[i] = True if os.path.exists('./du_da/top__usage_%s.png' % i) else False
        du_da_data_usage[i] = True if os.path.exists('./du_da/top_data_usage_%s.png' % i) else False
        du_da_data1_usage[i] = True if os.path.exists('./du_da/top_data1_usage_%s.png' % i) else False
        du_da_data2_usage[i] = True if os.path.exists('./du_da/top_data2_usage_%s.png' % i) else False
        du_da_data3_usage[i] = True if os.path.exists('./du_da/top_data3_usage_%s.png' % i) else False
        du_da_networkin_rate[i] = True if os.path.exists('./du_da/top_networkin_rate_%s.png' % i) else False
        du_da_networkout_rate[i] = True if os.path.exists('./du_da/top_networkout_rate_%s.png' % i) else False
    # du_fe 前端
    du_fe_cpu_usage = OrderedDict()
    du_fe_mem_usage = OrderedDict()
    du_fe__usage = OrderedDict()
    du_fe_data_usage = OrderedDict()
    du_fe_data1_usage = OrderedDict()
    du_fe_data2_usage = OrderedDict()
    du_fe_data3_usage = OrderedDict()
    du_fe_networkin_rate = OrderedDict()
    du_fe_networkout_rate = OrderedDict()
    for i in range(1, 8):
        du_fe_cpu_usage[i] = True if os.path.exists('./du_fe/top_cpu_usage_%s.png' % i) else False
        du_fe_mem_usage[i] = True if os.path.exists('./du_fe/top_mem_usage_%s.png' % i) else False
        du_fe__usage[i] = True if os.path.exists('./du_fe/top__usage_%s.png' % i) else False
        du_fe_data_usage[i] = True if os.path.exists('./du_fe/top_data_usage_%s.png' % i) else False
        du_fe_data1_usage[i] = True if os.path.exists('./du_fe/top_data1_usage_%s.png' % i) else False
        du_fe_data2_usage[i] = True if os.path.exists('./du_fe/top_data2_usage_%s.png' % i) else False
        du_fe_data3_usage[i] = True if os.path.exists('./du_fe/top_data3_usage_%s.png' % i) else False
        du_fe_networkin_rate[i] = True if os.path.exists('./du_fe/top_networkin_rate_%s.png' % i) else False
        du_fe_networkout_rate[i] = True if os.path.exists('./du_fe/top_networkout_rate_%s.png' % i) else False

    # 云端部门
    du_srv = """<fieldset>
        <legend class="line_title">云端部门ECS资源消耗</legend>
        <div class="line">"""
    for i in du_srv_cpu_usage:
        if du_srv_cpu_usage[i]:
            du_srv += """<div><h5>CPU使用率({})</h5><img src="cid:du_srv_ecs_cpu_usage_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv_mem_usage:
        if du_srv_cpu_usage[i]:
            du_srv += """<div><h5>内存使用率({})</h5><img src="cid:du_srv_ecs_mem_usage_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv__usage:
        if du_srv__usage[i]:
            du_srv += """<div><h5>磁盘根目录使用率({})</h5><img src="cid:du_srv_ecs__usage_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv_data_usage:
        if du_srv_data_usage[i]:
            du_srv += """<div><h5>磁盘data目录使用率({})</h5><img src="cid:du_srv_ecs_data_usage_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv_data1_usage:
        if du_srv_data1_usage[i]:
            du_srv += """<div><h5>磁盘data1目录使用率({})</h5><img src="cid:du_srv_ecs_data1_usage_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv_data2_usage:
        if du_srv_data2_usage[i]:
            du_srv += """<div><h5>磁盘data2目录使用率({})</h5><img src="cid:du_srv_ecs_data2_usage_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv_data3_usage:
        if du_srv_data3_usage[i]:
            du_srv += """<div><h5>磁盘data3目录使用率({})</h5><img src="cid:du_srv_ecs_data3_usage_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv_networkin_rate:
        if du_srv_networkin_rate[i]:
            du_srv += """<div><h5>上行带宽({})</h5><img src="cid:du_srv_ecs_networkin_rate_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_srv_networkout_rate:
        if du_srv_networkout_rate[i]:
            du_srv += """<div><h5>下行带宽({})</h5><img src="cid:du_srv_ecs_networkout_rate_{}" \
            alt="" width="85%" height="85%"></div>""".format(i, i)
    du_srv += """</div>
        </fieldset>"""

    # -------------广告 du_ad--------------------------------
    du_ad = """<fieldset>
            <legend class="line_title">广告部门ECS资源消耗</legend>
            <div class="line">"""
    for i in du_ad_cpu_usage:
        if du_ad_cpu_usage[i]:
            du_ad += """<div><h5>CPU使用率({})</h5><img src="cid:du_ad_ecs_cpu_usage_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad_mem_usage:
        if du_ad_cpu_usage[i]:
            du_ad += """<div><h5>内存使用率({})</h5><img src="cid:du_ad_ecs_mem_usage_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad__usage:
        if du_ad__usage[i]:
            du_ad += """<div><h5>磁盘根目录使用率({})</h5><img src="cid:du_ad_ecs__usage_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad_data_usage:
        if du_ad_data_usage[i]:
            du_ad += """<div><h5>磁盘data目录使用率({})</h5><img src="cid:du_ad_ecs_data_usage_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad_data1_usage:
        if du_ad_data1_usage[i]:
            du_ad += """<div><h5>磁盘data1目录使用率({})</h5><img src="cid:du_ad_ecs_data1_usage_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad_data2_usage:
        if du_ad_data2_usage[i]:
            du_ad += """<div><h5>磁盘data2目录使用率({})</h5><img src="cid:du_ad_ecs_data2_usage_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad_data3_usage:
        if du_ad_data3_usage[i]:
            du_ad += """<div><h5>磁盘data3目录使用率({})</h5><img src="cid:du_ad_ecs_data3_usage_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad_networkin_rate:
        if du_ad_networkin_rate[i]:
            du_ad += """<div><h5>上行带宽({})</h5><img src="cid:du_ad_ecs_networkin_rate_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_ad_networkout_rate:
        if du_ad_networkout_rate[i]:
            du_ad += """<div><h5>下行带宽({})</h5><img src="cid:du_ad_ecs_networkout_rate_{}" \
                alt="" width="85%" height="85%"></div>""".format(i, i)
    du_ad += """</div>
            </fieldset>"""

    # -----du_da  大数据----------------------------------
    du_da = """<fieldset>
                <legend class="line_title">大数据部门ECS资源消耗</legend>
                <div class="line">"""
    for i in du_da_cpu_usage:
        if du_da_cpu_usage[i]:
            du_da += """<div><h5>CPU使用率({})</h5><img src="cid:du_da_ecs_cpu_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da_mem_usage:
        if du_da_cpu_usage[i]:
            du_da += """<div><h5>内存使用率({})</h5><img src="cid:du_da_ecs_mem_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da__usage:
        if du_da__usage[i]:
            du_da += """<div><h5>磁盘根目录使用率({})</h5><img src="cid:du_da_ecs__usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da_data_usage:
        if du_da_data_usage[i]:
            du_da += """<div><h5>磁盘data目录使用率({})</h5><img src="cid:du_da_ecs_data_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da_data1_usage:
        if du_da_data1_usage[i]:
            du_da += """<div><h5>磁盘data1目录使用率({})</h5><img src="cid:du_da_ecs_data1_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da_data2_usage:
        if du_da_data2_usage[i]:
            du_da += """<div><h5>磁盘data2目录使用率({})</h5><img src="cid:du_da_ecs_data2_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da_data3_usage:
        if du_da_data3_usage[i]:
            du_da += """<div><h5>磁盘data3目录使用率({})</h5><img src="cid:du_da_ecs_data3_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da_networkin_rate:
        if du_da_networkin_rate[i]:
            du_da += """<div><h5>上行带宽({})</h5><img src="cid:du_da_ecs_networkin_rate_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_da_networkout_rate:
        if du_da_networkout_rate[i]:
            du_da += """<div><h5>下行带宽({})</h5><img src="cid:du_da_ecs_networkout_rate_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    du_da += """</div>
                </fieldset>"""

    # --------前端 du_fe---------------------
    du_fe = """<fieldset>
                <legend class="line_title">前端部门ECS资源消耗</legend>
                <div class="line">"""
    for i in du_fe_cpu_usage:
        if du_fe_cpu_usage[i]:
            du_fe += """<div><h5>CPU使用率({})</h5><img src="cid:du_fe_ecs_cpu_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe_mem_usage:
        if du_fe_cpu_usage[i]:
            du_fe += """<div><h5>内存使用率({})</h5><img src="cid:du_fe_ecs_mem_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe__usage:
        if du_fe__usage[i]:
            du_fe += """<div><h5>磁盘根目录使用率({})</h5><img src="cid:du_fe_ecs__usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe_data_usage:
        if du_fe_data_usage[i]:
            du_fe += """<div><h5>磁盘data目录使用率({})</h5><img src="cid:du_fe_ecs_data_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe_data1_usage:
        if du_fe_data1_usage[i]:
            du_fe += """<div><h5>磁盘data1目录使用率({})</h5><img src="cid:du_fe_ecs_data1_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe_data2_usage:
        if du_fe_data2_usage[i]:
            du_fe += """<div><h5>磁盘data2目录使用率({})</h5><img src="cid:du_fe_ecs_data2_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe_data3_usage:
        if du_fe_data3_usage[i]:
            du_fe += """<div><h5>磁盘data3目录使用率({})</h5><img src="cid:du_fe_ecs_data3_usage_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe_networkin_rate:
        if du_fe_networkin_rate[i]:
            du_fe += """<div><h5>上行带宽({})</h5><img src="cid:du_fe_ecs_networkin_rate_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    for i in du_fe_networkout_rate:
        if du_fe_networkout_rate[i]:
            du_fe += """<div><h5>下行带宽({})</h5><img src="cid:du_fe_ecs_networkout_rate_{}" \
                    alt="" width="85%" height="85%"></div>""".format(i, i)
    du_fe += """</div>
                </fieldset>"""

    content_foot = """        
            <br>  
        </div>
            <footer class="main-footer">
                <div class="pull-right hidden-xs">
                    <p style="font-size:10px;color: #999">版本 v1.0</p>
                </div>
                <p style="font-size:10px;color: #999">© Copyright 2018.版权所有 <a href="https://www.shuzilm.cn/" style="font-size:10px;">北京数字联盟网络科技有限公司</a></p>
            </footer>
        </body>
        </html>"""

    content = content_head + du_srv + du_ad + du_da + du_fe + content_foot
    msg_text = MIMEText(content, _subtype='html', _charset='utf-8')
    msg.attach(msg_text)

    # 这是总共的
    if os.path.exists('./ecs_picture/top_cpu_usage.png'):
        msg.attach(addimg('./ecs_picture/top_cpu_usage.png', 'ecs_top_cpu_usage'))
    if os.path.exists('./ecs_picture/top_mem_usage.png'):
        msg.attach(addimg('./ecs_picture/top_mem_usage.png', 'ecs_top_mem_usage'))
    if os.path.exists('./ecs_picture/top__usage.png'):
        msg.attach(addimg('./ecs_picture/top__usage.png', 'ecs_top__usage'))
    if os.path.exists('./ecs_picture/top_data_usage.png'):
        msg.attach(addimg('./ecs_picture/top_data_usage.png', 'ecs_top_data_usage'))
    if os.path.exists('./ecs_picture/top_data1_usage.png'):
        msg.attach(addimg('./ecs_picture/top_data1_usage.png', 'ecs_top_data1_usage'))
    if os.path.exists('./ecs_picture/top_data2_usage.png'):
        msg.attach(addimg('./ecs_picture/top_data2_usage.png', 'ecs_top_data2_usage'))
    if os.path.exists('./ecs_picture/top_data3_usage.png'):
        msg.attach(addimg('./ecs_picture/top_data3_usage.png', 'ecs_top_data3_usage'))
    if os.path.exists('./ecs_picture/top_networkin_rate.png'):
        msg.attach(addimg('./ecs_picture/top_networkin_rate.png', 'ecs_top_networkin_rate'))
    if os.path.exists('./ecs_picture/top_networkout_rate.png'):
        msg.attach(addimg('./ecs_picture/top_networkout_rate.png', 'ecs_top_networkout_rate'))

    if os.path.exists('./ecs_picture/top_networkout_rate.png'):
        msg.attach(addimg('./rds_picture/top_cpu_usage.png', 'rds_top_cpu'))
    if os.path.exists('./rds_picture/top_mem_usage.png'):
        msg.attach(addimg('./rds_picture/top_mem_usage.png', 'rds_top_mem'))
    if os.path.exists('./rds_picture/top_disk_usage.png'):
        msg.attach(addimg('./rds_picture/top_disk_usage.png', 'rds_top_disk'))
    if os.path.exists('./rds_picture/top_iops_usage.png'):
        msg.attach(addimg('./rds_picture/top_iops_usage.png', 'rds_top_iops'))
    if os.path.exists('./rds_picture/top_conn_usage.png'):
        msg.attach(addimg('./rds_picture/top_conn_usage.png', 'rds_top_conn'))
    if os.path.exists('./rds_picture/top_networkin_rate.png'):
        msg.attach(addimg('./rds_picture/top_networkin_rate.png', 'rds_top_netin'))
    if os.path.exists('./rds_picture/top_networkout_rate.png'):
        msg.attach(addimg('./rds_picture/top_networkout_rate.png', 'rds_top_netout'))

    if os.path.exists('./mongo_picture/top_cpu_usage.png'):
        msg.attach(addimg('./mongo_picture/top_cpu_usage.png', 'mongo_top_cpu_usage'))
    if os.path.exists('./mongo_picture/top_mem_usage.png'):
        msg.attach(addimg('./mongo_picture/top_mem_usage.png', 'mongo_top_mem_usage'))
    if os.path.exists('./mongo_picture/top_mongo_conn.png'):
        msg.attach(addimg('./mongo_picture/top_mongo_conn.png', 'mongo_top_conn'))
    if os.path.exists('./mongo_picture/top_shard_disk_usage.png'):
        msg.attach(addimg('./mongo_picture/top_shard_disk_usage.png', 'mongo_top_disk_usage'))
    if os.path.exists('./mongo_picture/top_shard_iops.png'):
        msg.attach(addimg('./mongo_picture/top_shard_iops.png', 'mongo_top_iops'))
    if os.path.exists('./mongo_picture/top_shard_iops_usage.png'):
        msg.attach(addimg('./mongo_picture/top_shard_iops_usage.png', 'mongo_top_iops_usage'))

    if os.path.exists('./slb_picture/top_networkin_rate.png'):
        msg.attach(addimg('./slb_picture/top_networkin_rate.png', 'slb_top_netin'))
    if os.path.exists('./slb_picture/top_networkout_rate.png'):
        msg.attach(addimg('./slb_picture/top_networkout_rate.png', 'slb_top_netout'))
    if os.path.exists('./slb_picture/top_packetin.png'):
        msg.attach(addimg('./slb_picture/top_packetin.png', 'slb_top_packetin'))
    if os.path.exists('./slb_picture/top_packetout.png'):
        msg.attach(addimg('./slb_picture/top_packetout.png', 'slb_top_packetout'))
    if os.path.exists('./slb_picture/top_active_conn.png'):
        msg.attach(addimg('./slb_picture/top_active_conn.png', 'slb_top_active_conn'))
    if os.path.exists('./slb_picture/top_inactive_conn.png'):
        msg.attach(addimg('./slb_picture/top_inactive_conn.png', 'slb_top_inactive_conn'))
    if os.path.exists('./slb_picture/top_max_conn.png'):
        msg.attach(addimg('./slb_picture/top_max_conn.png', 'slb_top_max_conn'))
    if os.path.exists('./slb_picture/top_new_conn.png'):
        msg.attach(addimg('./slb_picture/top_new_conn.png', 'slb_top_new_conn'))
    if os.path.exists('./slb_picture/top_drop_networkin_rate.png'):
        msg.attach(addimg('./slb_picture/top_drop_networkin_rate.png', 'slb_top_drop_netin'))
    if os.path.exists('./slb_picture/top_drop_networkout_rate.png'):
        msg.attach(addimg('./slb_picture/top_drop_networkout_rate.png', 'slb_top_drop_netout'))
    if os.path.exists('./slb_picture/top_drop_packetin.png'):
        msg.attach(addimg('./slb_picture/top_drop_packetin.png', 'slb_top_drop_packetin'))
    if os.path.exists('./slb_picture/top_drop_packetout.png'):
        msg.attach(addimg('./slb_picture/top_drop_packetout.png', 'slb_top_drop_packetout'))
    if os.path.exists('./slb_picture/top_drop_conn.png'):
        msg.attach(addimg('./slb_picture/top_drop_conn.png', 'slb_top_drop_conn'))

    for i in du_srv_cpu_usage:
        if du_srv_cpu_usage[i]:
            msg.attach(addimg('./du_srv/top_cpu_usage_%s.png' % i, 'du_srv_ecs_cpu_usage_%s' % i))
    for i in du_srv_mem_usage:
        if du_srv_mem_usage[i]:
            msg.attach(addimg('./du_srv/top_mem_usage_%s.png' % i, 'du_srv_ecs_mem_usage_%s' % i))
    for i in du_srv__usage:
        if du_srv__usage[i]:
            msg.attach(addimg('./du_srv/top__usage_%s.png' % i, 'du_srv_ecs__usage_%s' % i))
    for i in du_srv_data_usage:
        if du_srv_data_usage[i]:
            msg.attach(addimg('./du_srv/top_data_usage_%s.png' % i, 'du_srv_ecs_data_usage_%s' % i))
    for i in du_srv_data_usage:
        if du_srv_data1_usage[i]:
            msg.attach(addimg('./du_srv/top_data1_usage_%s.png' % i, 'du_srv_ecs_data1_usage_%s' % i))
    for i in du_srv_data2_usage:
        if du_srv_data2_usage[i]:
            msg.attach(addimg('./du_srv/top_data2_usage_%s.png' % i, 'du_srv_ecs_data2_usage_%s' % i))
    for i in du_srv_data3_usage:
        if du_srv_data3_usage[i]:
            msg.attach(addimg('./du_srv/top_data3_usage_%s.png' % i, 'du_srv_ecs_data3_usage_%s' % i))
    for i in du_srv_networkin_rate:
        if du_srv_networkin_rate[i]:
            msg.attach(addimg('./du_srv/top_networkin_rate_%s.png' % i, 'du_srv_ecs_networkin_rate_%s' % i))
    for i in du_srv_networkout_rate:
        if du_srv_networkout_rate[i]:
            msg.attach(addimg('./du_srv/top_networkout_rate_%s.png' % i, 'du_srv_ecs_networkout_rate_%s' % i))

    #  -----du_ad----------
    for i in du_ad_cpu_usage:
        if du_ad_cpu_usage[i]:
            msg.attach(addimg('./du_ad/top_cpu_usage_%s.png' % i, 'du_ad_ecs_cpu_usage_%s' % i))
    for i in du_ad_mem_usage:
        if du_ad_mem_usage[i]:
            msg.attach(addimg('./du_ad/top_mem_usage_%s.png' % i, 'du_ad_ecs_mem_usage_%s' % i))
    for i in du_ad__usage:
        if du_ad__usage[i]:
            msg.attach(addimg('./du_ad/top__usage_%s.png' % i, 'du_ad_ecs__usage_%s' % i))
    for i in du_ad_data_usage:
        if du_ad_data_usage[i]:
            msg.attach(addimg('./du_ad/top_data_usage_%s.png' % i, 'du_ad_ecs_data_usage_%s' % i))
    for i in du_ad_data_usage:
        if du_ad_data1_usage[i]:
            msg.attach(addimg('./du_ad/top_data1_usage_%s.png' % i, 'du_ad_ecs_data1_usage_%s' % i))
    for i in du_ad_data2_usage:
        if du_ad_data2_usage[i]:
            msg.attach(addimg('./du_ad/top_data2_usage_%s.png' % i, 'du_ad_ecs_data2_usage_%s' % i))
    for i in du_ad_data3_usage:
        if du_ad_data3_usage[i]:
            msg.attach(addimg('./du_ad/top_data3_usage_%s.png' % i, 'du_ad_ecs_data3_usage_%s' % i))
    for i in du_ad_networkin_rate:
        if du_ad_networkin_rate[i]:
            msg.attach(addimg('./du_ad/top_networkin_rate_%s.png' % i, 'du_ad_ecs_networkin_rate_%s' % i))
    for i in du_ad_networkout_rate:
        if du_ad_networkout_rate[i]:
            msg.attach(addimg('./du_ad/top_networkout_rate_%s.png' % i, 'du_ad_ecs_networkout_rate_%s' % i))

    # -----du_da------------
    for i in du_da_cpu_usage:
        if du_da_cpu_usage[i]:
            msg.attach(addimg('./du_da/top_cpu_usage_%s.png' % i, 'du_da_ecs_cpu_usage_%s' % i))
    for i in du_da_mem_usage:
        if du_da_mem_usage[i]:
            msg.attach(addimg('./du_da/top_mem_usage_%s.png' % i, 'du_da_ecs_mem_usage_%s' % i))
    for i in du_da__usage:
        if du_da__usage[i]:
            msg.attach(addimg('./du_da/top__usage_%s.png' % i, 'du_da_ecs__usage_%s' % i))
    for i in du_da_data_usage:
        if du_da_data_usage[i]:
            msg.attach(addimg('./du_da/top_data_usage_%s.png' % i, 'du_da_ecs_data_usage_%s' % i))
    for i in du_da_data_usage:
        if du_da_data1_usage[i]:
            msg.attach(addimg('./du_da/top_data1_usage_%s.png' % i, 'du_da_ecs_data1_usage_%s' % i))
    for i in du_da_data2_usage:
        if du_da_data2_usage[i]:
            msg.attach(addimg('./du_da/top_data2_usage_%s.png' % i, 'du_da_ecs_data2_usage_%s' % i))
    for i in du_da_data3_usage:
        if du_da_data3_usage[i]:
            msg.attach(addimg('./du_da/top_data3_usage_%s.png' % i, 'du_da_ecs_data3_usage_%s' % i))
    for i in du_da_networkin_rate:
        if du_da_networkin_rate[i]:
            msg.attach(addimg('./du_da/top_networkin_rate_%s.png' % i, 'du_da_ecs_networkin_rate_%s' % i))
    for i in du_da_networkout_rate:
        if du_da_networkout_rate[i]:
            msg.attach(addimg('./du_da/top_networkout_rate_%s.png' % i, 'du_da_ecs_networkout_rate_%s' % i))

    # -----du_fe-------------------
    for i in du_fe_cpu_usage:
        if du_fe_cpu_usage[i]:
            msg.attach(addimg('./du_fe/top_cpu_usage_%s.png' % i, 'du_fe_ecs_cpu_usage_%s' % i))
    for i in du_fe_mem_usage:
        if du_fe_mem_usage[i]:
            msg.attach(addimg('./du_fe/top_mem_usage_%s.png' % i, 'du_fe_ecs_mem_usage_%s' % i))
    for i in du_fe__usage:
        if du_fe__usage[i]:
            msg.attach(addimg('./du_fe/top__usage_%s.png' % i, 'du_fe_ecs__usage_%s' % i))
    for i in du_fe_data_usage:
        if du_fe_data_usage[i]:
            msg.attach(addimg('./du_fe/top_data_usage_%s.png' % i, 'du_fe_ecs_data_usage_%s' % i))
    for i in du_fe_data_usage:
        if du_fe_data1_usage[i]:
            msg.attach(addimg('./du_fe/top_data1_usage_%s.png' % i, 'du_fe_ecs_data1_usage_%s' % i))
    for i in du_fe_data2_usage:
        if du_fe_data2_usage[i]:
            msg.attach(addimg('./du_fe/top_data2_usage_%s.png' % i, 'du_fe_ecs_data2_usage_%s' % i))
    for i in du_fe_data3_usage:
        if du_fe_data3_usage[i]:
            msg.attach(addimg('./du_fe/top_data3_usage_%s.png' % i, 'du_fe_ecs_data3_usage_%s' % i))
    for i in du_fe_networkin_rate:
        if du_fe_networkin_rate[i]:
            msg.attach(addimg('./du_fe/top_networkin_rate_%s.png' % i, 'du_fe_ecs_networkin_rate_%s' % i))
    for i in du_fe_networkout_rate:
        if du_fe_networkout_rate[i]:
            msg.attach(addimg('./du_fe/top_networkout_rate_%s.png' % i, 'du_fe_ecs_networkout_rate_%s' % i))

    try:
        server = smtplib.SMTP(mail_host, 25)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(mail_username, mail_password)
        server.sendmail(mail_sender, email_list + cc_list, msg.as_string())
        server.quit()
    except Exception as e:
        string = 'aliun_monitor_week 发送总共邮件异常 e:%s' % str(e)
        write_log(string + str(traceback.format_exc()))
        send_alarm_v2(alert_data, traceback.format_exc())


if __name__ == '__main__':
    print(time.ctime())
    begin0 = time.time()

    paths = ('./du_srv', './du_ad', './du_da', './du_fe', './du_op',
             './ecs_picture', './rds_picture', './mongo_picture', './slb_picture')
    for path in paths:
        # 如果文件夹存在, 删除里面的全部文件,
        if os.path.exists(path):
            for i in os.listdir(path):
                path_file = os.path.join(path, i)  # 取文件路径
                if os.path.isfile(path_file):
                    os.remove(path_file)
        # 不存在,创建文件夹
        else:
            os.mkdir(path)

    # 生成图片
    for j in (get_ecs_week_main, get_rds_week_main, get_mongo_week_main, get_slb_week_main):
        try:
            j()
            print(time.ctime(), '{},图片生成结束'.format(j.__qualname__))
        except Exception as e:
            print(str(e), traceback.format_exc())
            write_log(str(traceback.format_exc()))
            send_alarm_v2(alert_data, str(traceback.format_exc()))

    # 发全部的
    # email_list = ['xx@shuzilm.cn', 'xx@shuzilm.cn']  # 测试用
    send_email(email_list)

    # 发各个部门的
    send_dep()

    # 保存图片
    paths = ('./du_srv', './du_ad', './du_da', './du_fe', './du_op',
             './ecs_picture', './rds_picture', './mongo_picture', './slb_picture')
    for path in paths:
        os.rename(path,
                  '../aliyun_monitor_data/' + path.replace('./', '') + '_' + time.strftime('%Y-%m-%d', time.localtime()))

    print('total used time', time.time() - begin0)


