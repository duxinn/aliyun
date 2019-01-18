import os
import smtplib
import time
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from functools import partial
from config import AccessKeyId, AccessKeySecret, send_alarm_v2, write_log, sign_gen, alert_data, aliyun_monitor
from collections import OrderedDict


mail_host = "xx"
mail_sender = "xx"
mail_username = "xx"
mail_password = "xx"

LOG = './monitor_dep_error.log'
write_log = partial(write_log, LOG)

technical_department = [12993126, 74448429, 48804840, 48806835, 48815834, 48828847, 48879846]
#                       技术中心     技术部     业务保障部 云端       终端       前端      大数据

deps = ('du_srv', 'du_ad', 'du_da', 'du_fe')
emails = ('zhoucj@shuzilm.cn', 'wanght@shuzilm.cn', 'liuwei@shuzilm.cn', 'fangcl@shuzilm.cn')


def addimg(src, imgid):  # 文件路径、图片id
    fp = open(src, 'rb')  # 打开文件
    msg_image = MIMEImage(fp.read())  # 读入msg_image中
    fp.close()  # 关闭文件
    msg_image.add_header('Content-ID', imgid)
    return msg_image


def send_email(email_list, subject="阿里云监控周报", dep='部门'):
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = mail_sender
    msg['To'] = ', '.join(email_list) if isinstance(email_list, list) else email_list

    title = '云端部门' if dep == 'du_srv' \
        else '广告部门' if dep == 'du_ad' \
        else '大数据部门' if dep == 'du_da' \
        else '前端部门' if dep == 'du_fe' \
        else dep
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
        <title>""" + title + """阿里云ECS监控周报</title>
    </head>
    <body>
        <div class="contain">
            <h1>""" + title + """阿里云ECS监控周报</h1>
            <br>"""

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

    # 云端部门
    if dep == 'du_srv':
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
        content = content_head + du_srv + content_foot
        msg_text = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(msg_text)

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

    # -------------广告 du_ad--------------------------------
    elif dep == 'du_ad':
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
        content = content_head + du_ad + content_foot
        msg_text = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(msg_text)

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

    # -----du_da  大数据----------------------------------
    elif dep == 'du_da':
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
        content = content_head + du_da + content_foot
        msg_text = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(msg_text)

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

    # --------前端 du_fe---------------------
    elif dep == 'du_fe':
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
        content = content_head + du_fe + content_foot
        msg_text = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(msg_text)

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

    else:
        content = 'send_email() dep参数错误'
        msg_text = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(msg_text)

    try:
        server = smtplib.SMTP(mail_host, 25)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(mail_username, mail_password)
        server.sendmail(mail_sender, email_list, msg.as_string())
        server.quit()
    except Exception as e:
        string = 'aliun_week_dep 给各个部门发送邮件异常 e:%s' % str(e)
        print(string)
        write_log(string + str(traceback.format_exc()))
        send_alarm_v2(alert_data, traceback.format_exc())
        return 0
    else:
        return 1


def send_dep():
    for dep, email in zip(deps, emails):
        send_email(email_list=email, dep=dep)


if __name__ == '__main__':
    print(time.ctime())
    begin0 = time.time()
    send_dep()
    print('total used time', time.time() - begin0)



