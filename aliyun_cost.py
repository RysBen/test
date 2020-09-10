import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#read
cost=pd.read_csv('/biocluster/data/biobk/user_test/renshuaibing/aliyun_cost/202008_detail.csv')

#prepare
cost.replace('-',np.nan,inplace=True)   #np.nan vs. 'NaN'
cost['date']=cost['账单开始时间'].fillna(cost['消费时间']).astype('str').str.split(' ',expand=True)[0]

date_product=cost.groupby(['date','产品明细Code'])['应付金额'].sum().unstack()
date_product.index=pd.to_datetime(date_product.index)

##################
#概览
##################
labels=['ecs','vm','naspost','oss','yundisk','sls','nat_gw','slb','eip']
colors=['tomato','salmon','yellowgreen','lightgreen','limegreen','lightskyblue','orange','gold','yellow']
patches,l_text,p_text=plt.pie(date_product.sum().sort_values(ascending=False), explode=(0,0,0,0,0,0,0.2,0.4,0.6), autopct='%1.2f%%', \
labels=labels,colors=colors,\
textprops={'fontsize': 6})
plt.title("Cost overview")

for t in l_text:
    t.set_size(6)

plt.axis('equal')
plt.legend()
plt.gcf().set_size_inches(6, 6)
plt.subplots_adjust(left=0,bottom=0,right=0.95,top=0.93)
plt.gcf().savefig('overview.png', dpi=100)
#plt.show()
plt.clf()

##################
#计算：2 Y-axis
##################
fig,ax1=plt.subplots()
ax2=ax1.twinx()
date_product.drop(['vm','sls','eip','slb','nat_gw','oss','naspost','yundisk'],axis=1).plot.area(stacked=False,ax=ax1)
date_product.drop(['ecs','sls','eip','slb','nat_gw','oss','naspost','yundisk'],axis=1).plot.area(stacked=False,ax=ax2,color='salmon')
ax1.set_title('Cloud Computering Cost')
ax1.set_ylabel('cost(ecs)')
ax2.set_ylabel('cost(vm)')
ax1.legend(loc=2, prop={'size': 8})
ax2.legend(loc=1, prop={'size': 8})
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))
plt.xticks(rotation=0)
plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
ax1.grid()
plt.gcf().set_size_inches(10, 6)
plt.subplots_adjust(left=0.08,bottom=0.09,right=0.9,top=0.93)
plt.gcf().savefig('comp.png', dpi=100)
#plt.show()
plt.clf()

##################
#存储
##################
date_product.drop(['vm','sls','eip','slb','nat_gw','ecs'],axis=1).plot.area(stacked=False,title='Cloud Storage Cost')
plt.legend(loc=1, prop={'size': 8})
plt.ylabel('cost')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))
plt.xticks(rotation=0)
plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
plt.grid()
plt.gcf().set_size_inches(10, 6)
plt.subplots_adjust(left=0.07,bottom=0.08,right=0.97,top=0.93)
plt.gcf().savefig('storage.png', dpi=100)
#plt.show()
plt.clf()


##################
#其它
##################
date_product.drop(['ecs','vm','oss','naspost','yundisk'],axis=1).plot.area(stacked=False,title='Other Services Cost')
plt.legend(loc=1, prop={'size': 8})
plt.ylabel('cost')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))
plt.xticks(rotation=0)
plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
plt.grid()
plt.gcf().set_size_inches(10, 6)
plt.subplots_adjust(left=0.07,bottom=0.08,right=0.97,top=0.93)
plt.gcf().savefig('others.png', dpi=100)
#plt.show()
plt.clf()


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
