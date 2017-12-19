# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

data = pd.read_csv("E:/Belle/Taobao.csv",encoding='gbk')

### 预处理 ###
# 到手价指记入优惠券提供的优惠并扣除礼品卡抵扣的金额后单品的价格
data['营收金额'] = data['成交金额'] + data ['礼品卡金额']
data['到手价'] = data['营收金额'] / data['成交件数']
data['折扣'] = data['到手价'] / data['牌价']
data.loc[:,'折扣'] = data['折扣'].round(3)

# 剔除赠品
data_clean = data[data['牌价'] != 0]
data_women = data_clean[data_clean['一级分类'] == '女鞋']
data_men = data_clean[data_clean['一级分类'] == '男鞋']
data_kid = data_clean[data_clean['一级分类'] == '童鞋']

### 报表 ###
pivot_women = pd.pivot_table(data_women, values = ['营收金额'], index = ['日期'],aggfunc=np.sum)
pivot_men = pd.pivot_table(data_men, values = ['营收金额'], index = ['日期'],aggfunc=np.sum)
pivot_combine = pd.concat([pivot_women,pivot_men],axis=1)
pivot_combine.plot(kind='line', title='2017百丽男女鞋销量曲线_优购平台')
women_cnt_by_pid = pd.pivot_table(data_women, values = ['成交件数'], index = ['商品编号'],aggfunc=np.sum).sort_values('成交件数',ascending=False)
women_cnt_top = women_cnt_by_pid.head(10)
for pid in women_cnt_top.index:
    data_by_pid = data_clean[data_clean['商品编号']==pid]
    pivot_amt_by_pid = pd.pivot_table(data_by_pid, values='营收金额', index='日期', aggfunc=np.sum)
    pivot_price_by_pid = pd.pivot_table(data_by_pid, values='到手价', index='日期')
    pivot_by_pid = pd.concat([pivot_amt_by_pid,pivot_price_by_pid], axis=1)
    cnt_by_pid = int(women_cnt_top[women_cnt_top.index == pid].iloc[0,0])
    title_str = str(pid) + ' ' + str(data_by_pid.iloc[0,5]) + ' '+ str(data_by_pid.iloc[0,6]) + ' 销量' + str(cnt_by_pid)
    pivot_by_pid.plot(title=title_str)