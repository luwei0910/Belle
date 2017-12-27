# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import datetime 

channel = "TB"
channel_CN = "淘宝"
season = "17年春季"
online_sales_data_file = "E:/Belle/ST_" + channel + ".csv"
online_sales_data = pd.read_csv(online_sales_data_file, encoding='gbk')
category_data = pd.read_excel("E:/Belle/思加图商品属性.xlsx", encoding='gbk')
tag_data = pd.read_excel("E:/Belle/17春产品标签.xlsx", sheet_name="2017春")
tag_data.loc[tag_data['款型'] == '满帮', '款型'] = '满帮鞋'
tag_data.loc[tag_data['款型'] == '浅口', '款型'] = '浅口鞋'
tag_data.loc[tag_data['款型'] == '中空', '款型'] = '中空凉鞋'
tag_data.loc[tag_data['款型'] == '后空', '款型'] = '后空凉鞋'
tag_data.loc[tag_data['款型'] == '前空', '款型'] = '鱼嘴鞋'
plot_path = "E:/Belle/Plots/ST/" + channel + "/"
plot_path1 = plot_path + "Exclude_Peak/"
plot_path2 = plot_path + "Original/"
if not os.path.exists(plot_path1):
    os.makedirs(plot_path1)
if not os.path.exists(plot_path2):
    os.makedirs(plot_path2)
    
### 预处理 ###
# 到手价指记入优惠券提供的优惠并扣除礼品卡抵扣的金额后单品的价格
sale_category_merge_full = pd.merge(online_sales_data, category_data, how='left', left_on='商品编码', right_on='商品编号', suffixes=['','_1'])
sale_category_merge = sale_category_merge_full[['日期','供应商款色编号','商品编码','品牌名称','一级分类','二级分类','三级分类','成交金额','成交件数','牌价','促销活动金额','商品优惠总金额','优惠券金额','礼品卡金额','运费均摊','省','市','商品销售季']]

# 仅分析2017年春季款
intermediate_master = sale_category_merge[sale_category_merge['商品销售季'] == season]
data = pd.merge(intermediate_master, tag_data, how='left', left_on='供应商款色编号', right_on='货号', suffixes=['','_1'])
data['营收金额'] = data['成交金额'] + data ['礼品卡金额']
data['到手价'] = data['营收金额'] / data['成交件数']
max_pricetag = data.groupby('商品编码').max()['牌价']
data['最高牌价'] = max_pricetag[data['商品编码']].values
data['折扣'] = round(1 - data['到手价'] / data['最高牌价'],2)
data.loc[:,'折扣'] = data['折扣'].round(3)

# 剔除赠品
data_clean = data[data['牌价'] != 0]
data_women = data_clean[data_clean['一级分类'] == '女鞋']
data_men = data_clean[data_clean['一级分类'] == '男鞋']
data_kid = data_clean[data_clean['一级分类'] == '童鞋']

### 报表 ###
pivot_women_cnt = pd.pivot_table(data_women, values='成交件数', index='日期', aggfunc=np.sum)
#pivot_men_amt = pd.pivot_table(data_men, values='营收金额',  index='日期', aggfunc=np.sum)
pivot_women_dscnt = pd.pivot_table(data_women, values='折扣',  index='日期')
#pivot_men_dscnt = pd.pivot_table(data_men, values='折扣',  index='日期')
pivot_women_combine = pd.concat([pivot_women_cnt,pivot_women_dscnt],axis=1)

# 按销量计算线上活动日期
#women_cnt_top10pct_dates = []
#for pid in data_women['商品编码'].unique():
#    data_women_by_pid = data_women[data_women['商品编码'] == pid]
#    pivot_women_by_pid = pd.pivot_table(data_women_by_pid, values='成交件数', index='日期', aggfunc=np.sum)
#    top10pct_cnt = int(len(pivot_women_by_pid)/10)
#    women_cnt_top10pct_dates.extend(pivot_women_by_pid.sort_values('成交件数',ascending=False).head(top10pct_cnt).index)
#peak_dates = pd.Series(women_cnt_top10pct_dates).value_counts()

# 绘制总销量相关图
plot_by_class3_name = season + "思加图各类别女鞋" + channel_CN + "销量"
plot_by_class3 = pd.pivot_table(data_women, values='成交件数', index='三级分类', aggfunc=np.sum).sort_values('成交件数', ascending=False).plot(kind='bar', title=plot_by_class3_name, rot=0, fontsize=12, figsize=(10,6))
plot_by_class3.get_figure().savefig(plot_path + plot_by_class3_name + ".png")
plot_by_sale_amt_name = season + "思加图女鞋" + channel_CN + "营收额及平均折扣力度曲线"
plot_by_sale_amt = pivot_women_combine.plot(subplots=True, title=plot_by_sale_amt_name)

# 仅分析春季的5个鞋款
class3_list = {'浅口鞋','满帮鞋','鱼嘴鞋','中空凉鞋','后空凉鞋'}
pivot_array = {'浅口鞋':[], '满帮鞋':[], '鱼嘴鞋':[], '中空凉鞋':[], '后空凉鞋':[]}
pivot_array_full_ind = {'浅口鞋':False, '满帮鞋':False, '鱼嘴鞋':False, '中空凉鞋':False, '后空凉鞋':False}
#class3_list = {'浅口鞋','满帮鞋'}
#pivot_array = {'浅口鞋':[], '满帮鞋':[]}
#pivot_array_full_ind = {'浅口鞋':False, '满帮鞋':False}
women_cnt_by_pid = pd.pivot_table(data_women, values='成交件数', index='商品编码', aggfunc=np.sum).sort_values('成交件数',ascending=False)
for pid in women_cnt_by_pid.index:
    data_by_pid = data_clean[data_clean['商品编码']==pid]
    class2 = data_by_pid.iloc[0,5]
    class3 = data_by_pid.iloc[0,6]
    max_pricetag = data_by_pid.iloc[0,-2]
    if not class3 in class3_list:
        continue
    else:
        if pivot_array_full_ind[class3] == True:
            continue
    pivot_amt_by_pid = pd.pivot_table(data_by_pid, values='成交件数', index='日期', aggfunc=np.sum)
    pivot_price_by_pid = pd.pivot_table(data_by_pid, values=['到手价'], index='日期')
    pivot_dscnt_by_pid = pd.pivot_table(data_by_pid, values=['折扣'], index='日期')
    cnt_by_pid = int(women_cnt_by_pid[women_cnt_by_pid.index == pid].iloc[0,0])
    title_str = str(class3) + ' 销量' + str(cnt_by_pid) + ' 编号' + str(pid) + ' 最高牌价' + str(int(max_pricetag))
    pivot_by_pid = pd.concat([pivot_amt_by_pid,pivot_price_by_pid,pivot_dscnt_by_pid], axis=1)

    # 找出各品类销量TOP5的
    if len(pivot_array[class3]) < 10:
        pivot_array[class3].append([pivot_by_pid,title_str])
    else: 
        pivot_array_full_ind[class3] = True
    if False in pivot_array_full_ind.values():
        continue
    break  

# 定义活动日期
peak_dates_list = ['2017-02-20','2017-03-06','2017-03-07','2017-03-08','2017-03-21','2017-03-31','2017-04-14','2017-04-15','2017-04-21','2017-04-22','2017-05-02','2017-05-03','2017-05-17','2017-05-18','2017-06-06','2017-06-18','2017-06-19','2017-06-20','2017-07-11','2017-07-21','2017-07-31','2017-08-11','2017-08-05','2017-08-27','2017-09-09','2017-09-10','2017-11-11']
major_fest_list = ['2017-03-06','2017-03-07','2017-03-08','2017-06-18','2017-06-19','2017-06-20','2017-11-11']

### 绘制曲线
for class3 in pivot_array.keys():
    for top_n in range(len(pivot_array[class3])):
        original = pivot_array[class3][top_n][0]
        cnt_sum = np.sum(original['成交件数'])
        # 除去成交件数大于3倍75%百分点值的outlier并计算outlier占比
        #quartile3 = original['成交件数'].describe()[6]
        #peak = original[original['成交件数'] > quartile3*3]
        #exclude_peak = original[original['成交件数'] <= quartile3*2.5]
        exclude_peak = original.copy()
        peak = pd.DataFrame(columns = ['成交件数','到手价','折扣'])
        fest = pd.DataFrame(columns = ['成交件数','到手价','折扣'])
        for date in original.index:
            if date in peak_dates_list:
                sum = 0
                non_peak_day_cnt = 0
                peak = peak.append(original.loc[date,:])
                if date in major_fest_list:
                    fest = fest.append(original.loc[date,:])
                peak_day = datetime.datetime.strptime(date,'%Y-%m-%d')            
                for day_diff in range(-3,4):
                    day = datetime.datetime.strftime(peak_day + datetime.timedelta(days = day_diff), '%Y-%m-%d')
                    if (day not in peak_dates_list):
                        non_peak_day_cnt += 1
                        if day in original.index:
                            sum += original.loc[day,'成交件数']
                exclude_peak.loc[date,'成交件数'] = round(np.average(sum/non_peak_day_cnt))
        peak_cnt_sum = np.sum(peak['成交件数'])
        peak_pct = round(peak_cnt_sum / cnt_sum * 100, 1)
        plot_title = pivot_array[class3][top_n][1] + ' 峰值占比' + str(peak_pct) + '%'
        fest_cnt_sum = np.sum(fest['成交件数'])
        fest_pct = round(fest_cnt_sum / cnt_sum * 100, 1)
        plot_title = plot_title + ' 三大节占比' + str(fest_pct) + '%'
        
        # 加总到周Level
        week_list= pd.date_range(start="2017-01-01",end="2017-12-31",freq='MS')
        week_agg_exclude_peak = {}
        week_agg_original = {}
        week_avg_dscnt = {}
        for week_number in range(len(week_list)-1):
            week_start = week_list[week_number]
            week_end = week_list[week_number + 1]
            week_avg_dscnt[week_start] = (np.average(original['折扣'][(original.index >= week_start.to_pydatetime().strftime('%Y-%m-%d')) & (original.index < week_end.to_pydatetime().strftime('%Y-%m-%d'))]))  * 10 # 单位：折
            week_agg_original[week_start] = int(np.sum(original['成交件数'][(original.index >= week_start.to_pydatetime().strftime('%Y-%m-%d')) & (original.index < week_end.to_pydatetime().strftime('%Y-%m-%d'))]))
            week_agg_exclude_peak[week_start] = int(np.sum(exclude_peak['成交件数'][(exclude_peak.index >= week_start.to_pydatetime().strftime('%Y-%m-%d')) & (exclude_peak.index < week_end.to_pydatetime().strftime('%Y-%m-%d'))]))
        week_agg_dscnt_df = pd.DataFrame(pd.Series(week_avg_dscnt))    
        week_agg_dscnt_df.fillna(method='pad', inplace=True) # 用前一项填补折扣空缺值
        week_agg_original_df = pd.DataFrame(pd.Series(week_agg_original))
        week_agg_exclude_peak_df = pd.DataFrame(pd.Series(week_agg_exclude_peak))
#        if (class3 == '浅口鞋') and (top_n == 3):
#            print(week_agg_dscnt_df)
        plots_original = week_agg_original_df.plot(title=plot_title, legend=False, fontsize=14, figsize=(10,6))
        plots_original.get_figure().savefig(plot_path2 + plot_title + ".png")
#        week_dscnt_cnt = pd.concat([week_agg_exclude_peak_df,week_agg_dscnt_df], axis = 1)
#        week_dscnt_cnt.columns = ['成交件数', '折扣']
#        plots_exclude_peak = week_dscnt_cnt.plot(title=plot_title, legend=False, fontsize=14, figsize=(10,6), subplots=True)
        plots_exclude_peak = week_agg_exclude_peak_df.plot(title=plot_title, legend=False, fontsize=14, figsize=(10,6))
        plots_exclude_peak.get_figure().savefig(plot_path1 + plot_title + ".png")
        
original = pivot_women_cnt.copy()
exclude_peak = original.copy()
for date in original.index:
    if date in peak_dates_list:
        sum = 0
        non_peak_day_cnt = 0
        peak_day = datetime.datetime.strptime(date,'%Y-%m-%d')            
        for day_diff in range(-6,7):
            day = datetime.datetime.strftime(peak_day + datetime.timedelta(days = day_diff), '%Y-%m-%d')
            if (day not in peak_dates_list):
                non_peak_day_cnt += 1
                if day in original.index:
                    sum += original.loc[day,'成交件数']
            exclude_peak.loc[date,'成交件数'] = round(np.average(sum/non_peak_day_cnt))            