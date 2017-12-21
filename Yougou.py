# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

channel = "TB"
channel_CN = "淘宝"
season = "17年春季"
online_sales_data_file = "E:/Belle/ST_" + channel + ".csv"
online_sales_data = pd.read_csv(online_sales_data_file, encoding='gbk')
online_category_data = "E:/Belle/思加图商品属性.xlsx"
category_data = pd.read_excel(online_category_data, encoding='gbk')
plot_path = "E:/Belle/Plots/ST/" + channel + "/"
plot_path1 = plot_path + "Exclude_Peak/"
plot_path2 = plot_path + "Include_Peak/"
if not os.path.exists(plot_path1):
    os.makedirs(plot_path1)
if not os.path.exists(plot_path2):
    os.makedirs(plot_path2)
    
### 预处理 ###
# 到手价指记入优惠券提供的优惠并扣除礼品卡抵扣的金额后单品的价格
sale_category_merge_full = pd.merge(online_sales_data, category_data, how='left', left_on='商品编码', right_on='商品编号', suffixes=['','_1'])
sale_category_merge = sale_category_merge_full[['日期','供应商款色编号','商品编码','品牌名称','一级分类','二级分类','三级分类','成交金额','成交件数','牌价','促销活动金额','商品优惠总金额','优惠券金额','礼品卡金额','运费均摊','省','市','商品销售季']]

# 只处理2017年春季款
data = sale_category_merge[sale_category_merge['商品销售季'] == season]
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
pivot_women_cnt = pd.pivot_table(data_women, values='成交件数', index='日期', aggfunc=np.sum)
#pivot_men_amt = pd.pivot_table(data_men, values='营收金额',  index='日期', aggfunc=np.sum)
pivot_women_dscnt = pd.pivot_table(data_women, values='折扣',  index='日期')
#pivot_men_dscnt = pd.pivot_table(data_men, values='折扣',  index='日期')
pivot_women_combine = pd.concat([pivot_women_cnt,pivot_women_dscnt],axis=1)

# 绘制总销量相关图
plot_by_class3_name = season + "思加图各类别女鞋" + channel_CN + "销量"
plot_by_class3 = pd.pivot_table(data_women, values='成交件数', index='三级分类', aggfunc=np.sum).sort_values('成交件数', ascending=False).plot(kind='bar', title=plot_by_class3_name, rot=0, fontsize=12, figsize=(10,6))
plot_by_class3.get_figure().savefig(plot_path + plot_by_class3_name + ".png")
plot_by_sale_amt_name = season + "思加图女鞋" + channel_CN + "营收额及平均折扣力度曲线"
plot_by_sale_amt = pivot_women_combine.plot(subplots=True, title=plot_by_sale_amt_name)
#plot_by_sale_amt.get_figure().savefig(plot_path + plot_by_sale_amt_name + ".png")

# 仅分析春季鞋款
class3_list = {'浅口鞋','满帮鞋','鱼嘴鞋','中空凉鞋','后空凉鞋'}
pivot_array = {'浅口鞋':[], '满帮鞋':[], '鱼嘴鞋':[], '中空凉鞋':[], '后空凉鞋':[]}
pivot_array_full_ind = {'浅口鞋':False, '满帮鞋':False, '鱼嘴鞋':False, '中空凉鞋':False, '后空凉鞋':False}
women_cnt_by_pid = pd.pivot_table(data_women, values='成交件数', index='商品编码', aggfunc=np.sum).sort_values('成交件数',ascending=False)
for pid in women_cnt_by_pid.index:
    data_by_pid = data_clean[data_clean['商品编码']==pid]
    class2 = data_by_pid.iloc[0,5]
    class3 = data_by_pid.iloc[0,6]
    if not class3 in class3_list:
        continue
    else:
        if pivot_array_full_ind[class3] == True:
            continue
    pivot_amt_by_pid = pd.pivot_table(data_by_pid, values='成交件数', index='日期', aggfunc=np.sum)
    pivot_price_by_pid = pd.pivot_table(data_by_pid, values=['到手价'], index='日期')
    pivot_pricetag_by_pid = pd.pivot_table(data_by_pid, values=['牌价'], index='日期')
    cnt_by_pid = int(women_cnt_by_pid[women_cnt_by_pid.index == pid].iloc[0,0])
    pricetag_by_pid = int(data_by_pid['牌价'].iloc[0])
    title_str = str(class3) + ' 销量' + str(cnt_by_pid) + ' 编号' + str(pid) + ' 牌价'
    #' 时间段' + str(data_by_pid['日期'].values[0])[5:] + '至' + str(data_by_pid['日期'].values[-1])[5:]
    if (data_by_pid['牌价'].describe().iloc[2] == 0):
        title_str = title_str + str(pricetag_by_pid) 
        pivot_by_pid = pd.concat([pivot_amt_by_pid,pivot_price_by_pid], axis=1)
    else: 
        title_str = title_str + '有过变动'
        pivot_by_pid = pd.concat([pivot_amt_by_pid,pivot_price_by_pid,pivot_pricetag_by_pid], axis=1)
    # 找出各品类销量TOP5的
    if len(pivot_array[class3]) < 5:
        pivot_array[class3].append([pivot_by_pid,title_str])
    else: 
        pivot_array_full_ind[class3] = True
    if False in pivot_array_full_ind.values():
        continue
    break  

# 绘制曲线
for class3 in pivot_array.keys():
    for top_n in range(len(pivot_array[class3])):
        # 除去成交件数大于3倍75%百分点值的outlier并计算outlier占比
        quartile3 = pivot_array[class3][top_n][0]['成交件数'].describe()[6]
        cnt_sum = np.sum(pivot_array[class3][top_n][0]['成交件数'])
        include_peak = pivot_array[class3][top_n][0]
        peak = pivot_array[class3][top_n][0][pivot_array[class3][top_n][0]['成交件数'] > quartile3*3]
        peak_cnt_sum = np.sum(peak['成交件数'])
        peak_pct = round(peak_cnt_sum / cnt_sum * 100, 1)
        plot_title = pivot_array[class3][top_n][1] + ' 峰值占比' + str(peak_pct) + '%'
        exclude_peak = pivot_array[class3][top_n][0][pivot_array[class3][top_n][0]['成交件数'] <= quartile3*3]
        # 加总到周Level
        week_list= pd.date_range(start="2017-01-01",end="2017-12-31",freq='W')
        week_agg_exclude_peak = {}
        week_agg_include_peak = {}
        for week_number in range(len(week_list)-1):
            week_start = week_list[week_number]
            week_end = week_list[week_number + 1]
            week_agg_exclude_peak[week_start] = int(np.sum(exclude_peak['成交件数'][(exclude_peak.index >= week_start.to_pydatetime().strftime('%Y-%m-%d')) & (exclude_peak.index < week_end.to_pydatetime().strftime('%Y-%m-%d'))]))
            week_agg_include_peak[week_start] = int(np.sum(include_peak['成交件数'][(include_peak.index >= week_start.to_pydatetime().strftime('%Y-%m-%d')) & (include_peak.index < week_end.to_pydatetime().strftime('%Y-%m-%d'))]))
        plots_exclude_peak = pd.DataFrame(pd.Series(week_agg_exclude_peak)).plot(title=plot_title, legend=False, fontsize=14, figsize=(10,6))
        plots_exclude_peak.get_figure().savefig(plot_path1 + plot_title + ".png")
        plots_include_peak = pd.DataFrame(pd.Series(week_agg_include_peak)).plot(title=plot_title, legend=False, fontsize=14, figsize=(10,6))
        plots_include_peak.get_figure().savefig(plot_path2 + plot_title + ".png")
        #pivot_array[class3][top_n][0].plot(subplots=True, title=pivot_array[class3][top_n][1])
