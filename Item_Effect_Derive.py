# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 17:51:04 2018

@author: BELLE
"""

import pandas as pd

item_effect = pd.read_csv('E:/Belle/Sycm/items_effect_staccato_GBK.csv', encoding='GBK')
item_effect['title'] = item_effect['title'].str.replace('STACCATO','')
item_effect['title'] = item_effect['title'].str.replace('staccato','')
item_effect['title'] = item_effect['title'].str.replace('Staccato','')
item_effect['product_id'] = item_effect['title'].str.extract("([A-Za-z0-9]{8})", expand=False)
item_effect = item_effect[['itemuv', 'payrate', 'avgstaytime', 'addcartitemcnt', 'select_date_begin', 'product_id']]
item_effect = item_effect[item_effect['product_id'].notnull()]

