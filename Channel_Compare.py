# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

data_tb = pd.read_csv("E:/Belle/ST_TB.csv", encoding='gbk')
data_jd = pd.read_csv("E:/Belle/ST_JD.csv", encoding='gbk')
data_vip = pd.read_csv("E:/Belle/ST_VIP.csv", encoding='gbk')
data_yg = pd.read_csv("E:/Belle/ST_YG.csv", encoding='gbk')
online_category_data = "E:/Belle/思加图商品属性.xlsx"
category_data = pd.read_excel(online_category_data, encoding='gbk')
plot_path = "E:/Belle/Plots/ST/"

tb_merge = pd.merge(data_tb, category_data, how='left', left_on='商品编码', right_on='商品编号', suffixes=['','_1'])
tb_merge = tb_merge[tb_merge['商品销售季'] == "17年春季"]
tb_pivot = pd.pivot_table(tb_merge, values='成交件数', index='日期', aggfunc=np.sum)
tb_pivot.rename(columns={'成交件数':'淘宝'}, inplace=True)

jd_merge = pd.merge(data_jd, category_data, how='left', left_on='商品编码', right_on='商品编号', suffixes=['','_1'])
jd_merge = jd_merge[jd_merge['商品销售季'] == "17年春季"]
jd_pivot = pd.pivot_table(jd_merge, values='成交件数', index='日期', aggfunc=np.sum)
jd_pivot.rename(columns={'成交件数':'京东'}, inplace=True)

vip_merge = pd.merge(data_vip, category_data, how='left', left_on='商品编码', right_on='商品编号', suffixes=['','_1'])
vip_merge = vip_merge[vip_merge['商品销售季'] == "17年春季"]
vip_pivot = pd.pivot_table(vip_merge, values='成交件数', index='日期', aggfunc=np.sum)
vip_pivot.rename(columns={'成交件数':'唯品会'}, inplace=True)

yg_merge = pd.merge(data_yg, category_data, how='left', left_on='商品编码', right_on='商品编号', suffixes=['','_1'])
yg_merge = yg_merge[yg_merge['商品销售季'] == "17年春季"]
yg_pivot = pd.pivot_table(yg_merge, values='成交件数', index='日期', aggfunc=np.sum)
yg_pivot.rename(columns={'成交件数':'优购'}, inplace=True)

pivot_master = pd.concat([tb_pivot, jd_pivot, vip_pivot, yg_pivot], axis=1).fillna(0)
plot1 = pivot_master.plot(figsize=(10,7), title='思加图17年春款女鞋线上4种渠道销量对比')
plot1.get_figure().savefig(plot_path + "思加图17年春款女鞋线上4种渠道销量对比.png")
pivot_master['总成交件数'] = pivot_master['淘宝'] + pivot_master['京东'] + pivot_master['唯品会'] + pivot_master['优购']
pivot_percent = pd.DataFrame(columns=['淘宝','京东','唯品会','优购'])
pivot_percent['淘宝'] = pivot_master['淘宝'] / pivot_master['总成交件数'] * 100
pivot_percent['京东'] = pivot_master['京东'] / pivot_master['总成交件数'] * 100
pivot_percent['唯品会'] = pivot_master['唯品会'] / pivot_master['总成交件数'] * 100
pivot_percent['优购'] = pivot_master['优购'] / pivot_master['总成交件数'] * 100
plot2 = pivot_percent.plot(kind='area', stacked=True, figsize=(12,2), title='思加图17年春款女鞋线上4种渠道销量占比')
plot2.get_figure().savefig(plot_path + "思加图17年春款女鞋线上4种渠道销量占比.png")