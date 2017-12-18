# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

data = pd.read_csv("E:/Belle/Yougou.csv",encoding='gbk')

### 预处理 ###
data['成交额'] = data['成交金额'] * data['成交件数']
data['折扣'] = data['成交金额'] / data['牌价']
data.loc[:,'折扣'] = data['折扣'].round(3)

# 剔除赠品
data_clean = data[data['牌价'] != 0]

data_women = data_clean[data_clean['一级分类'] == '女鞋']
data_men = data_clean[data_clean['一级分类'] == '男鞋']
data_kid = data_clean[data_clean['一级分类'] == '童鞋']

### 报表 ###
pivot_women = pd.pivot_table(data_women, values = ['成交额'], index = ['日期'],aggfunc=np.sum)
pivot_men = pd.pivot_table(data_men, values = ['成交额'], index = ['日期'],aggfunc=np.sum)
pivot_combine = pd.concat([pivot_women,pivot_men],axis=1)
pivot_combine.plot(kind='line', title='2017百丽男女鞋销量曲线_优购平台')
women_dscnt_by_dt = pd.pivot_table(data_women, values = ['折扣'], index = ['日期'])
women_cnt_by_dt = pd.pivot_table(data_women, values = ['成交件数'], index = ['日期'], aggfunc = np.sum)
women_cnt_vs_dscnt = pd.concat([women_dscnt_by_dt, women_cnt_by_dt], axis = 1)
women_cnt_vs_dscnt.plot(kind='line', title='女鞋销量与折扣的关系')
women_cnt_by_pid = pd.pivot_table(data_women, values = ['成交件数'], index = ['商品编号'],aggfunc=np.sum).sort_values('成交件数',ascending=False)
women_top10 = women_cnt_by_pid.head(10)