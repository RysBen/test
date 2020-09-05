import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#read
cost=pd.read_csv('/biocluster/data/biobk/user_test/renshuaibing/aliyun_cost/202008_detail.csv')

#prepare
cost.replace('-',np.nan,inplace=True)   #np.nan vs. 'NaN'
cost['date']=cost['账单开始时间'].fillna(cost['消费时间']).astype('str').str.split(' ',expand=True)[0]

#total-day
total=cost['应付金额'].groupby(cost['date']).sum()
total.index=pd.to_datetime(total.index)
#bar
fig, ax = plt.subplots(figsize=(10, 6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
ax.bar(total.index, total, align='center')

#product
product=cost['应付金额'].groupby(cost['产品明细']).sum()
#pie
fig,ax = plt.subplots()
product.plot(kind='pie',autopct='%.2f%%',ax=ax,radius=1,textprops={'fontsize':7})
ax.set_aspect('equal')
ax.set_title('xxx')

#product-day



'''
#cost['产品明细'].drop_duplicates()
##########################################################################################
# 计算
### 云服务器ECS-包年包月
### 云服务器ECS-按量付费
# 存储
### 文件存储NAS按量付费：用于存储流程使用database数据，临时存放分析使用的原始数据和结果数据；
### 云盘：在ECS上挂载的云盘，按使用的节点数目和使用时间计费，用于存储计算节点计算过程中使用数据；
### 对象存储OSS：用于存储上传用来计算的原始数据和分析结果，分析完成并下载后即删除；
# 服务
### 日志服务：日志数据采集和查询服务；
### NAT网关（按量付费）：为网络专线提供高性能网络服务；
### 弹性公网IP：跟使用的ECS服务器数目有关（为每个服务器分配公网IP地址的服务）；
### 负载均衡：根据集群服务器健康情况以及异常情况（自动隔离）来分配任务；
##########################################################################################
#cost.to_csv('/biocluster/data/biobk/user_test/renshuaibing/aliyun_cost/202008_detail_check.csv',encoding='utf_8_sig')
'''
