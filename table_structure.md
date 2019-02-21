
建表指令如下：
ecs：

create table ecs_data(
id int(11) primary key auto_increment,
host varchar(100) default null,
metric varchar(100) default null,
value_num int(11) default null,
value_attr varchar(100) default null,
time datetime default null,
note text default null
)default charset=utf8;

create table ecs_dep (
id int(11) primary key auto_increment,
inst_id varchar(100) not null,
name varchar(100) default null,
department varchar(100) default null,
note text default null
)default charset=utf8;

create table idc_dep (
id int(11) primary key auto_increment,
sn_id varchar(100) default null,
name varchar(100) not null,
department varchar(100) default null,
note text default null
)default charset=utf8;

字段说明：

inst_id 实例id
name 实例名字
host 实例名字
status 实例状态
metric 监控项的名字
‘CPU-空闲百分比’, ‘内存-可用百分比’,
‘硬盘-剩余百分比（/）’,
‘硬盘-剩余百分比（/data）’,
‘硬盘-剩余百分比（/data1）’, ‘硬盘-剩余百分比（/data2）’,
‘硬盘-剩余百分比（/data3）’, ‘硬盘-剩余百分比（/data4）’, ‘硬盘-剩余百分比（/data5）’,
‘硬盘-剩余百分比（/data00）’,
‘硬盘-剩余百分比（/data01）’, ‘硬盘-剩余百分比（/data02）’,
‘硬盘-剩余百分比（/data03）’, ‘硬盘-剩余百分比（/data04）’, ‘硬盘-剩余百分比（/data05）’
value_num 数值类型的值
value_attr 属性类型的值
time 时间戳，和metric一起表示某个时间某个监控项的值
rds：

create table rds_attr(
id int primary key auto_increment,
rds_id varchar(100) default null,
desc varchar(100) default null,
status char(20) default null,
lock_mode char(20) default null,
max_iops varchar(100) default null,
max_conn varchar(100) default null,
engine_v varchar(100) default null,
time datetime default null,
note text default null
)default charset=utf8;

create table rds_data(
id int primary key auto_increment,
rds_id varchar(100) default null,
metric varchar(100) default null,
value_num int(11) default null,
value_attr varchar(100) default null,
time datetime default null,
note text default null
)default charset=utf8;

字段说明：

rds_id 实例id
descr 实例描述
status 实例状态
lock_mode 实例锁定模式：


 

    Unlock：正常；
    ManualLock：手动触发锁定；
    LockByExpiration：实例过期自动锁定；
    LockByRestoration：实例回滚前的自动锁定；
    LockByDiskQuota：实例空间满自动锁定。

metric 监控项的名字，取值为
‘cpu_usage’, ‘mem_usage’, ‘disk_usage’, ‘iops_usage’, ‘conn_usage’,
‘active_sesion’, ‘networkin_rate’, ‘networkout_rate’
value_num 数值类型的值
value_attr 属性类型的值
time 时间戳，和metric一起表示某个时间某个监控项的值
mongo：

create table mongo_attr (
id int primary key auto_increment,
mongodb_id varchar(100) default null,
engine_v varchar(100) default null,
descr varchar(100) default null,
status varchar(100) default null,
mongo_id text default null,
shard_id text default null,
time datetime default null,
note text default null
)default charset=utf8;

create table mongo_data(
id int primary key auto_increment,
mongodb_id varchar(100),
metric varchar(100) default null,
value_num int(11) default null,
value_attr varchar(100) default null,
time datetime default null,
note text default null
)default charset=utf8;

create table mongo_node_data(
id int primary key auto_increment,
node_id varchar(100),
metric varchar(100) default null,
value_num int(11) default null,
value_attr varchar(100) default null,
time datetime default null,
note text default null
)default charset=utf8;

字段说明：

mongodb_id MongoDB实例id
status 实例状态
engine_v 机器类型机器及其版本
descr 描述
mongo_id 路由 mongo 的id， MongoDB 实例的话会存其所有 mongo 的的id
shard_id 分片 shared 的id，MongoDB 实例的话会存其所有 shard 的的id
metric 监控项的名字，取值为
‘cpu_usage’, ‘mem_usage’, ‘disk_usage’, ‘iops_usage’,
‘connection’, ‘connection_usage’, ‘qps’

value_num 数值类型的值
value_attr 属性类型的值
time 时间戳，和metric一起表示某个时间某个监控项的值
slb：

create table slb_attr(
id int primary key auto_increment,
slb_id varchar(100) default null,
name varchar(100) default null,
status varchar(100) default null,
addr varchar(100) default null,
bandwidth varchar(100) default null,
spec varchar(100) default null,
port_list varchar(100) default null,
region varchar(100) default null,
time datetime default null,
note text default null
)default charset=utf8;

create table slb_data(
id int primary key auto_increment,
slb_id varchar(100) default null,
metric varchar(100) default null,
value_num int(11) default null,
value_attr varchar(100) default null,
time datetime default null,
note text default null
)default charset=utf8;

字段说明

slb_id 负暂均衡的实例id
name 实例的名字
status 实例的状态
addr 实例的ip地址
bandwidth slb的带宽（程序运行时候）
spec slb实例的描述
port_list 实例端口的列表，格式为 ‘’端口1,端口2’’
region 区域
metric 监控项，取值为 ‘networkin_rate’, ‘networkout_rate’,
‘packet_in’, ‘packet_out’,
‘active_conn’, ‘inactive_conn’,
‘max_conn’, ‘new_conn’, ‘drop_conn’

value_num 数值类型的值
value_attr 属性类型的值
time 时间戳，和metric一起表示某个时间某个监控项的值

