# -*- coding: utf-8 -*-
import pandas as pd
import xlwings as xw
import numpy as np

home_dir = "E:/Belle/Staccato/"

master_tb = pd.read_csv(home_dir+"Master_TB_1617.csv", encoding='gbk')
master_yg = pd.read_csv(home_dir+"Master_YG_1617.csv", encoding='gbk')
master_jd = pd.read_csv(home_dir+"Master_JD_1617.csv", encoding='gbk')
master_vip = pd.read_csv(home_dir+"Master_VIP_1617.csv", encoding='gbk')
master_all = pd.concat([master_tb, master_yg, master_jd, master_vip], axis=0)

filter_condition = []
for i in range(4):
    filter_condition.append(pd.read_excel(home_dir+"报表.xlsx", sheetname=i, encoding='gbk'))

wb = xw.Book(home_dir+"报表.xlsx")
sht = []
for i in range(1,5):
    sht.append(wb.sheets['Sheet'+str(i)])
    
filter_res = master_all[(master_all['商品季'] == filter_condition[0]['季节'].values[0]) & (master_all['三级分类'] == filter_condition[0]['款式'].values[0]) & (pd.to_datetime(master_all['日期']) <= pd.to_datetime(filter_condition[0]['检查日期'].values[0]))]
sht[0].range('A7:A10').options(transpose=True).value = ['常青', '畅销', '平销', '滞销']
sht[0].range('B6:J6').value = ['建议动作', '款式数', 'SKU数', '销量', '销额', '平均折扣',	'毛利率', '售罄率']
i = 0
for category in ['常青款','畅销款','平销款','滞销款']:
    filter_category = filter_res[filter_res['类别'] == category]
    spu = len(filter_category['商品款号'].unique())
    sku = len(filter_category['供应商款色编号'].unique())
    sale_cnt = int(sum(filter_category['成交件数']))
    sale_amt = int(sum(filter_category['成交金额']))
    dscnt = round(sum(filter_category['折扣率'])/len(filter_category['折扣率']),2)
    sht[0].range('C'+str(7+i)+':G'+str(7+i)).value = [spu, sku, sale_cnt, sale_amt, dscnt]
    i += 1


# 粒度设定 = 周
tw_list_2016 = pd.date_range(start="2016-01-01",end="2016-12-31",freq='W')
tw_list_2017 = pd.date_range(start="2017-01-01",end="2017-12-31",freq='W')

sht[1].range('A33:J33').value = ['周数',	'起始日期', '2016月销量',	'2017月销量'	, '2016期末库存', '2017期末库存','2016累计售罄率', '2017累计售罄率', '2016平均折扣', '2017平均折扣']
sht[1].range('A132:C132').value = ['周数', '2016月销售额', '2017月销售额']
sht[1].range('H132:J132').value = ['周数', '2016月毛利率', '2017月毛利率']

# 继续按照类别筛选（常青，畅销，平销，滞销）
filter_res = filter_res[filter_res['类别'] == filter_condition[1]['类别'].values[0]]

# 2016加总
tw_sale_cnt_2016 = {}
tw_dscnt_2016 = {}
tw_sale_amt_2016 = {}
for tw_number in range(1,len(tw_list_2016)):
    tw_start = tw_list_2016[tw_number - 1]
    tw_end = tw_list_2016[tw_number]
    tw_sale_cnt_2016[tw_start] = int(np.sum(filter_res['成交件数'][(pd.to_datetime(filter_res['日期']) >= tw_start) & (pd.to_datetime(filter_res['日期']) < tw_end)]))
    tw_dscnt_2016[tw_start] = np.average(filter_res['折扣率'][(pd.to_datetime(filter_res['日期']) >= tw_start) & (pd.to_datetime(filter_res['日期']) < tw_end)])*100
    tw_sale_amt_2016[tw_start] = int(np.sum(filter_res['成交金额'][(pd.to_datetime(filter_res['日期']) >= tw_start) & (pd.to_datetime(filter_res['日期']) < tw_end)]))

# 2017加总
tw_sale_cnt_2017 = {}
tw_dscnt_2017 = {}
tw_sale_amt_2017 = {}
for tw_number in range(1,len(tw_list_2017)):
    line_number = tw_number + 33
    line_number2 = tw_number + 109
    tw_start = tw_list_2017[tw_number - 1]
    tw_end = tw_list_2017[tw_number]
    tw_sale_cnt_2017[tw_start] = int(np.sum(filter_res['成交件数'][(pd.to_datetime(filter_res['日期']) >= tw_start) & (pd.to_datetime(filter_res['日期']) < tw_end)]))
    tw_dscnt_2017[tw_start] = np.average(filter_res['折扣率'][(pd.to_datetime(filter_res['日期']) >= tw_start) & (pd.to_datetime(filter_res['日期']) < tw_end)])*100
    tw_sale_amt_2017[tw_start] = int(np.sum(filter_res['成交金额'][(pd.to_datetime(filter_res['日期']) >= tw_start) & (pd.to_datetime(filter_res['日期']) < tw_end)]))
    sht[1].range('A'+str(line_number)).value = tw_number
    sht[1].range('A'+str(line_number2)).value = tw_number                      
    sht[1].range('F'+str(line_number2)).value = tw_number
    sht[1].range('B'+str(line_number)).value = tw_start
    if tw_number < len(tw_list_2016):
        sht[1].range('C'+str(line_number)).value = list(tw_sale_cnt_2016.values())[tw_number-1]
        sht[1].range('I'+str(line_number)).value = str(list(tw_dscnt_2016.values())[tw_number-1]) + '%'
        sht[1].range('I'+str(line_number)).number_format = '0%'
        if sht[1].range('I'+str(line_number)).value == 'nan%':
            sht[1].range('I'+str(line_number)).value = ""
        sht[1].range('B'+str(line_number2)).value = list(tw_sale_amt_2016.values())[tw_number-1]
        sht[1].range('B'+str(line_number2)).number_format = "0"
    sht[1].range('D'+str(line_number)).value = list(tw_sale_cnt_2017.values())[tw_number-1]
    sht[1].range('J'+str(line_number)).value = str(list(tw_dscnt_2017.values())[tw_number-1]) + '%'
    sht[1].range('J'+str(line_number)).number_format = '0%'
    if sht[1].range('J'+str(line_number)).value == 'nan%':
        sht[1].range('J'+str(line_number)).value = ""
    sht[1].range('C'+str(line_number2)).value = list(tw_sale_amt_2017.values())[tw_number-1]
    sht[1].range('C'+str(line_number2)).number_format = "0"
        
#    for sheet in wb.sheets:
#        sheet.autofit()    

master_id_cate = master_all[['商品款号','类别']].drop_duplicates()
    
item_effect = pd.read_csv('E:/Belle/Sycm/items_effect_staccato_GBK.csv', encoding='GBK')
item_effect['title'] = item_effect['title'].str.replace('STACCATO','')
item_effect['title'] = item_effect['title'].str.replace('staccato','')
item_effect['title'] = item_effect['title'].str.replace('Staccato','')
item_effect['product_id'] = item_effect['title'].str.extract("([A-Za-z0-9]{8})", expand=False)
item_effect = item_effect[['itemuv', 'payrate', 'avgstaytime', 'addcartitemcnt', 'select_date_begin', 'product_id']]
item_effect = item_effect[item_effect['product_id'].notnull()]
prop = pd.read_excel(home_dir+"思加图商品属性.xlsx", encoding='gbk')
prop = prop[['商品编号', '货号', '商品款号', '三级分类', '商品销售季', '商品季', '首次上架时间', '首次上架年份', '首次上架月份']]
prop.drop_duplicates('商品款号', keep='first', inplace=True)
master = pd.merge(item_effect, prop, how='left', left_on='product_id', right_on='商品款号', suffixes=['','_1']).drop('商品款号', axis=1)
master = pd.merge(master, master_id_cate, how='left', left_on='product_id', right_on='商品款号', suffixes=['','_1']).drop('商品款号', axis=1)
master_filter = master[(master['商品季'] == filter_condition[1]['季节'].values[0]) & (master['三级分类'] == filter_condition[1]['款式'].values[0]) & (master['类别'] == filter_condition[1]['类别'].values[0]) & (pd.to_datetime(master['select_date_begin']) <= pd.to_datetime(filter_condition[1]['检查日期'].values[0]))]

addcartitemcnt = []
itemuv = []
avgstaytime = []
payrate = []
def calculate_item_effect(today):
    thirty_days_before = today + pd.Timedelta('-30 days')
    for date in pd.date_range(start=thirty_days_before, end=today):
        master_filter_today = master_filter[pd.to_datetime(master_filter['select_date_begin']) == date]
        filter_res_today = filter_res[pd.to_datetime(filter_res['日期']) == date]
        join_res = pd.merge(master_filter_today, filter_res_today, how='left', left_on = 'product_id', right_on = '商品款号', suffixes=['','_1'])
        addcartitemcnt.append(np.average(master_filter_today['addcartitemcnt']))
        itemuv.append(np.average(master_filter_today['itemuv']))
        avgstaytime.append(round(np.average(master_filter_today['avgstaytime']),1))
        total = 0
        for pid in master_filter_today['product_id']:
            total += (sum(join_res[join_res['product_id'] == pid]['成交件数']) / master_filter_today[master_filter_today['product_id'] == pid]['itemuv']).values[0]
            payrate.append(round(total/len(master_filter_today['product_id'])*100,2))
        
today = pd.to_datetime(filter_condition[1]['检查日期'].values[0])
calculate_item_effect(today)
for i in range(-7,0):
    line_number1 = 215
    line_number2 = 245
    sht[1].range('A'+str(line_number1+i)).value = itemuv[52+i]
    sht[1].range('B'+str(line_number1+i)).value = int(np.average(itemuv[45:52]))
    sht[1].range('C'+str(line_number1+i)).value = int(np.average(itemuv[0:52]))
    sht[1].range('H'+str(line_number1+i)).value = str(payrate[30+i]) + '%'
    payrate_one_week_nonan = [x for x in payrate[23:30] if str(x) != 'nan']
    payrate_one_month_nonan = [x for x in payrate[0:30] if str(x) != 'nan']
    sht[1].range('I'+str(line_number1+i)).value = str(round(np.average(payrate_one_week_nonan),2)) + '%'
    sht[1].range('J'+str(line_number1+i)).value = str(round(np.average(payrate_one_month_nonan),2)) + '%'
    sht[1].range('A'+str(line_number2+i)).value = avgstaytime[52+i]
    sht[1].range('B'+str(line_number2+i)).value = int(np.average(avgstaytime[45:52]))
    sht[1].range('C'+str(line_number2+i)).value = int(np.average(avgstaytime[0:52]))
    sht[1].range('H'+str(line_number2+i)).value = addcartitemcnt[52+i]
    sht[1].range('I'+str(line_number2+i)).value = int(np.average(addcartitemcnt[45:52]))
    sht[1].range('J'+str(line_number2+i)).value = int(np.average(addcartitemcnt[0:52]))
     
#today = today + pd.Timedelta('-365 days')
#addcartitemcnt = []
#itemuv = []
#avgstaytime = []
#payrate = []
#calculate_item_effect(today)