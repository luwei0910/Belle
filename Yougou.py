# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

yg = pd.read_csv("E:/Belle/Yougou.csv",encoding='gbk')

yg['成交额'] = yg['成交金额']*yg['成交件数']
# 剔除赠品
yg_clean = yg[yg['牌价'] != 0]
yg_women = yg_clean[yg_clean['一级分类'] == '女鞋']
yg_men = yg_clean[yg_clean['一级分类'] == '男鞋']
yg_kid = yg_clean[yg_clean['一级分类'] == '童鞋']
pivot_women = pd.pivot_table(yg_women, values = ['成交额'], index = ['日期'],aggfunc=np.sum)
pivot_men = pd.pivot_table(yg_men, values = ['成交额'], index = ['日期'],aggfunc=np.sum)
pivot_combine = pd.concat([pivot_women,pivot_men],axis=1)
pivot_combine.plot(kind='line',title='2017百丽男女鞋销量曲线_优购平台')
women_top10 = pivot_women = pd.pivot_table(yg_women, values = ['成交额'], index = ['日期'],aggfunc=np.sum)