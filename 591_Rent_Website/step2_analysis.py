import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import os
import re
import seaborn as sns 
from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.font_manager as fm
import numpy as np
from scipy import stats
import geopandas as gpd
import json
# 設定字體的檔案位置，並放到fm.FontProperties裡
fontPath = os.path.join('.' , 'NotoSansTC-Regular.otf')
font = fm.FontProperties(fname = fontPath , size = 12)

with open(os.path.join('.' , 'response_1647008060817.json') , 'r' , encoding = 'utf-8') as f:
    stations = json.loads(f.read())
station_district = {station['StationName']['Zh_tw'] : station['LocationTown'] for station in stations if station['LocationCity'] == '臺北市'}   
    
raw_data = pd.DataFrame()
for file in os.listdir('./crawl_result/Taipei_City'):
    if 'csv' in file:
        raw_data = pd.concat([raw_data , pd.read_csv(os.path.join('./crawl_result/Taipei_City' , file) , index_col = 0 , encoding = 'utf-8')] , axis = 0)
raw_data.columns = ['title' , 'style_set' , 'district' , 'subway_distance' , 'rent']
raw_data.reset_index(inplace = True , drop = True)
raw_data = raw_data.astype(str)

shape_path = os.path.join('./Taiwan_Town_Shape' , 'TOWN_MOI_1091016.shp')
town_shp = gpd.read_file(shape_path , encoding = 'utf8')
taipei_districts = list(town_shp.query("COUNTYNAME=='臺北市'")['TOWNNAME'].unique())


def fun_district(inp):
    return re.findall('([\u4e00-\u9fa5_a-zA-Z0-9]{2}區)-' , inp)[0]

# 找出台北市的行政區
def fun_district_in_taipei(inp):
    if inp not in taipei_districts:
        return False
    elif inp in taipei_districts:
        return True
    
def fun_subway_district_confirm(inp):
    try:
        if inp['subway'] != 'no info':
            if station_district[inp['subway']] != inp['district']:
                print(inp['district'] , inp['subway'])
                inp['district'] = station_district[inp['subway']]
    except:
        pass            
    return inp

def fun_rent(inp):
    if '~' in inp: 
        return (int(inp.split('~')[0]) + int(inp.split('~')[1])) / 2
    else:
        return float(inp)   

def fun_area_floor(inp):
    if '樓中樓' in inp: return inp[1:]
    else: return inp

def fun_maisonette(inp):
    if '樓中樓' in inp: return True
    else: return False

def fun_subway(inp):
    index_set = re.finditer('[0-9]*$'  , inp)
    for i , index in enumerate(index_set):
        if i == 0: break
    return inp[:index.span()[0]]    

def fun_subway_map(inp):
    if inp == '台北車': return '台北車站'
    elif inp == '臺北市政府松德辦公大樓': return '市政府'
    elif inp == '樂炸特區FUNNYFRIEDZONE': return '忠孝復興'
    elif inp == '松山機場2號出口': return '松山機場'
    else: return inp

def fun_distance(inp):
    index_set = re.finditer('[0-9]*$'  , inp)
    for i , index in enumerate(index_set):
        if i == 0: break
    if index.span()[0] != index.span()[1]:
        return inp[index.span()[0]:index.span()[1]]
    elif index.span()[0] == index.span()[1]:
        return 'no info'

style = raw_data['style_set'].apply(lambda x : x.split(' ')[0])
rent = raw_data['rent'].apply(lambda x : fun_rent(x)) 
district =  raw_data['district'].apply(lambda x : fun_district(x))  
district_in_taipei =  district.apply(lambda x : fun_district_in_taipei(x))


area_floor = raw_data['style_set'].apply(lambda x : x.split(' ')[1:])   
area_floor = area_floor.apply(lambda x : fun_area_floor(x))    
area = area_floor.apply(lambda x : float(x[0].replace('坪' , '')))
floor = area_floor.apply(lambda x : x[1].split('/')[0].replace('F' , ''))
total_floor = area_floor.apply(lambda x : x[1].split('/')[1].replace('F' , ''))
maisonette = area_floor.apply(lambda x : fun_maisonette(x))   

subway_distance = raw_data['subway_distance'].apply(lambda x : x.replace('距' , '').replace('公尺' , '').replace('站' , ''))
subway = subway_distance.apply(lambda x : fun_subway(x))
subway = subway.apply(lambda x : fun_subway_map(x))
distance = subway_distance.apply(lambda x : fun_distance(x))

data_clean = pd.concat([raw_data['title'] , style , area , floor , total_floor , district , rent , subway , distance , maisonette] , axis = 1)
data_clean.columns = ['title' , 'style' , 'area' , 'floor' , 'total_floor' , 'district' , 'rent' , 'subway' , 'distance' , 'maisonette']
data_clean.drop_duplicates(inplace = True)
data_clean = data_clean.loc[district_in_taipei]
data_clean.drop_duplicates(inplace = True)      
temp = data_clean.apply(lambda x : fun_subway_district_confirm(x) , axis = 1)




data_mean_rent = data_clean.copy(deep = True)
data_mean_rent['mean_rent'] = data_mean_rent['rent'] / data_mean_rent['area']
data_mean_rent = data_mean_rent.query("subway!='no info'")
data_mean_rent = data_mean_rent.groupby(['district'] , as_index = False).agg({'mean_rent' : lambda x : x.mean()}) 
data_mean_rent.sort_values('mean_rent' , ascending = False , inplace = True)
main_districts = list(data_house_num['district'][:4])
colors = ['salmon' , 'tan' , 'gold' , 'violet']

data_mean_rent = data_clean.copy(deep = True)
data_mean_rent['mean_rent'] = data_mean_rent['rent'] / data_mean_rent['area']
data_mean_rent = data_mean_rent.query("subway!='no info'")
data_mean_rent = data_mean_rent.groupby(['district' , 'subway'] , as_index = True).agg({'mean_rent' : lambda x : x.mean()}) 
data_mean_rent = data_mean_rent.reset_index()