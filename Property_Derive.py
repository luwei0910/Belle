# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import datetime 

prop = pd.read_excel("E:/Belle/思加图商品属性.xlsx", encoding='gbk')

for i in range(len(prop['首次上架时间'])):
    if type(prop['首次上架时间'][i]) == str:
        actual_time = datetime.datetime.strptime(prop['首次上架时间'][i], '%Y-%m-%d %H:%M:%S')
        prop.loc[i, '首次上架年份'] = actual_time.year
        prop.loc[i, '首次上架月份'] = actual_time.month
        if actual_time.day <= 10:
            prop.loc[i, '详细上架月份'] = str(actual_time.month) + '月上'
        elif actual_time.day <= 20:
            prop.loc[i, '详细上架月份'] = str(actual_time.month) + '月中'
        else:
            prop.loc[i, '详细上架月份'] = str(actual_time.month) + '月下'