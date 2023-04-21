import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException , TimeoutException , WebDriverException , ElementNotInteractableException , ElementClickInterceptedException , InvalidElementStateException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import re
import numpy as np
import random
from urllib.parse import unquote
import os

# raw_data = pd.read_csv('Taipei_crawl_result.csv' , index_col = 0)
# raw_data = pd.read_csv('Taipei_crawl_result.csv' , index_col = 0)
# raw_data.replace({'【初登場】尚無評價' : np.nan , 'no info' : np.nan} , inplace = True)

# raw_data['行政區'] = raw_data['鄰近地區'].apply(lambda x : x.split(',')[0])
# raw_data['行政區'] = raw_data['行政區'].replace({'台北車站' : '中正區' , '西門町' : '萬華區' , '九份' : '瑞芳區'})
# raw_data.drop(columns = ['鄰近地區'] , inplace = True)

# raw_data['旅客評分'] = raw_data['旅客評分'].str.replace(',' , '').astype(float)
# raw_data['旅客評鑑數目'] = raw_data['旅客評鑑數目'].str.replace(',' , '').astype(float)
# raw_data['旅店當天價格'] = raw_data['旅店當天價格'].str.replace(',' , '').astype(float)
 
city = 'Pingtung'
raw_data = pd.read_csv(os.path.join('./crawl_result' , '{}_crawl_result.csv'.format(city)), index_col = 0)
raw_data['旅店名稱'] = raw_data['旅店名稱'].apply(lambda x : x.replace('/' , '').strip())
raw_data['lat'] = np.nan
raw_data['log'] = np.nan

page_num = 8
hotel_subsets = []
temp = []
for hotel , area in zip(list(raw_data['旅店名稱']) , list(raw_data['鄰近地區'])):
    temp.append('{}  {}'.format(hotel , area))
    if len(temp) == page_num:
        hotel_subsets.append(temp)
        temp = []
if len(temp) != page_num and len(temp) != 0: 
    hotel_subsets.append(temp)

driver = webdriver.Chrome()
driver.set_window_position(200 , 0)
driver.get('https://www.google.com.tw/maps')
driver.set_window_size(200 , 200)

js = "window.open('https://www.google.com.tw/maps')"
for _ in range(0 , page_num - 1):
    driver.execute_script(js)
time.sleep(10)

for index , hotel_subset in enumerate(hotel_subsets):    
    # 在最後一個hotel_subset，若數量不足page_num，會把一些頁面關掉
    handles = driver.window_handles
    if len(hotel_subset) != page_num:
        for i in range(0 , page_num - len(hotel_subset)):
            driver.switch_to_window(handles[i])
            driver.close()

    # 搜尋旅店位置
    handles = driver.window_handles
    for i , (handle , hotel_name) in enumerate(zip(handles , hotel_subset)):
        driver.switch_to_window(handle)
        try:
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').click()
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').clear()
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').send_keys(hotel_name)
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').send_keys(Keys.ENTER)        
        except ElementNotInteractableException:
            time.sleep(5)
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').click()
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').clear()
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').send_keys(hotel_name)
            driver.find_element_by_xpath('/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[1]/input[1]').send_keys(Keys.ENTER)        
        except ElementClickInterceptedException:
            element = driver.find_element_by_xpath("//div[@id='hoNUob-Sx9Kwc-m5SR9c']/div[2]/div/div[2]/button")
            ActionChains(driver).move_to_element(element).click(element).perform()
        time.sleep(random.randint(1 , 5))   
    time.sleep(5)

    # 獲取經緯度
    handles = driver.window_handles
    for i , (handle , hotel_name) in enumerate(zip(handles , hotel_subset)):
        driver.switch_to_window(handle)
        website = unquote(driver.current_url) # unquote可將亂碼轉成中文
        position = re.findall("https://www.google.com.tw/maps/search/.*?/.*?@(\d+.\d+).*?(\d+.\d+)" , website)
        try:
            lat , log = position[0][0] , position[0][1]
            raw_data.loc[index * page_num + i , 'lat'] = lat
            raw_data.loc[index * page_num + i , 'log'] = log
        except IndexError:
            position = re.findall("https://www.google.com.tw/maps/place/.*?/.*?@(\d+.\d+).*?(\d+.\d+)" , website)
            lat , log = position[0][0] , position[0][1]
            raw_data.loc[index * page_num + i , 'lat'] = float(lat)
            raw_data.loc[index * page_num + i , 'log'] = float(log)
        # if '/@' in website:
            # position = website.split('/@')[-1]
            # ret = re.finditer('[D]?[\d\.\,]*z' , position)
            # temp = ''
            # for m in ret:
            #     temp += position[m.span()[0] : m.span()[1]]
                
            # position = temp.split(',')[0:2]
            # lat , log = position[0] , position[1]
            # lat , log = re.sub('[\D]' , '' , lat) , re.sub('[\D]' , '' , log)
            # lat = float(lat) / 10 ** (int(np.log10(float(lat))) - 1)
            # log = float(log) / 10 ** (int(np.log10(float(log))) - 2)
            
            # raw_data.loc[index * page_num + i , 'lat'] = lat
            # raw_data.loc[index * page_num + i , 'log'] = log
        print('\rhotel_subset: {:d}/{:d} | hotel: {:d}/{:d}'.format(index , len(hotel_subsets) - 1 , i , len(hotel_subset) - 1) , end = '\n')

raw_data['lat'] = raw_data['lat'].astype(np.float)
raw_data['log'] = raw_data['log'].astype(np.float)
raw_data.to_csv(os.path.join('./crawl_result' , '{}_crawl_result_lat_log_v2.csv'.format(city)) , encoding = 'utf_8_sig')