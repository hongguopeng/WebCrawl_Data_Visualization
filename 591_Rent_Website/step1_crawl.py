from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException , ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.ui as ui
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import numpy as np
import time
import random
from tqdm import tqdm 
import requests
# from fake_useragent import UserAgent
import base64
import cv2
import os
from datetime import datetime
import json
import os

with open(os.path.join('.' , 'AllData.json') , 'r' , encoding = 'utf-8') as f:
    AllData = json.loads(f.read())
chi_eng = {data['CityName'].replace('市' , '').replace('臺' , '台') : data['CityEngName'].replace(' ' , '_') for data in AllData}   
city = '新北'

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://rent.591.com.tw/?keywords={}".format(city))
driver.find_element(By.CSS_SELECTOR, ".new-search-region").click()
driver.find_element(By.LINK_TEXT, "{}市".format(city)).click()


time.sleep(5)
driver.find_element(By.CSS_SELECTOR, ".vue-filter-container > .vue-filter-list-item:nth-child(3) .vue-filter-item:nth-child(2) > .fa").click() # 5000元以下 
driver.find_element(By.CSS_SELECTOR, ".vue-filter-container > .vue-filter-list-item:nth-child(3) .vue-filter-item:nth-child(3) > .fa").click() # 5000~10000元以下 
driver.find_element(By.CSS_SELECTOR, ".vue-filter-container > .vue-filter-list-item:nth-child(3) .vue-filter-item:nth-child(4) > .fa").click() # 10000~20000元以下 
if city == '新北' or city == '台北':
    driver.find_element(By.CSS_SELECTOR, ".vue-filter-container > .vue-filter-list-item:nth-child(5) .vue-filter-item:nth-child(3)").click() # 近捷運
    
# vue-filter-item:nth-child(3) 獨立套房
# vue-filter-item:nth-child(3) 分租套房
# vue-filter-item:nth-child(3) 雅房
driver.find_element(By.CSS_SELECTOR, ".vue-filter-container > .vue-filter-list-item:nth-child(2) .vue-filter-item:nth-child(4)").click() # 獨立套房
time.sleep(3)
driver.find_element(By.CSS_SELECTOR, ".show-more > div").click() # 展開選項
driver.find_element(By.CSS_SELECTOR, ".show-more-content > .vue-filter-list-item:nth-child(5) .vue-filter-item:nth-child(5) > .fa").click()
driver.find_element(By.CSS_SELECTOR, ".searchBtn").click() # 搜尋
time.sleep(3)

def get_data(driver):
    soup = BeautifulSoup(driver.page_source , 'html.parser') 
    selection_part = soup.select("[class='container-content-left']")
    selection_part = selection_part[0].select("[class='rent-item-right']")
    sub_title , sub_style , sub_loc , sub_subway , sub_rent = [] , [] , [] , [] , []
    for step , all_part in enumerate(selection_part):         
        if len(all_part.select("[class='item-title']")) != 0:
            sub_title.append(all_part.select("[class='item-title']")[0].text.replace(' ' , '').replace('\n' , ''))
        else:
            sub_title.append('no info')

        if len(all_part.select("[class='item-style']")) != 0:
            sub_style.append(all_part.select("[class='item-style']")[0].text.replace('  ' , ' '))
        else:
            sub_style.append('no info')
            
        if len(all_part.select("[class='item-area']")) != 0:
            sub_loc.append(all_part.select("[class='item-area']")[0].text.replace(' ' , ''))
        else:
            sub_loc.append('no info')    
            
        if len(all_part.select("[class='item-tip subway']")) != 0:
            sub_subway.append(all_part.select("[class='item-tip subway']")[0].text.replace(' ' , '').replace('\n' , '').replace('捷運' , ''))
        else:
            sub_subway.append('no info')  
        
        if len(all_part.select("[class='item-price-text']")) != 0:
            sub_rent.append(all_part.select("[class='item-price-text']")[0].text.replace(',' , '').replace(' ' , '').replace('元/月\n' , ''))
        else:
            sub_rent.append('no info') 
    return sub_title , sub_style , sub_loc , sub_subway , sub_rent        

page = 1
title , style , area , floor , loc , subway , rent = [] , [] , [] , [] , [] , [] , []
while True:
    # collect data
    # sub_title , sub_style , sub_area , sub_floor , sub_total_floor , sub_loc , sub_subway , sub_rent = get_data(driver)
    soup = BeautifulSoup(driver.page_source , 'html.parser') 
    selection_part = soup.select("[class='container-content-left']")
    selection_part = selection_part[0].select("[class='rent-item-right']")
    sub_title , sub_style , sub_loc , sub_subway , sub_rent = [] , [] , [] , [] , []
    for i , all_part in enumerate(selection_part): 

        if len(all_part.select("[class='item-title']")) != 0:
            sub_title.append(all_part.select("[class='item-title']")[0].text.replace(' ' , '').replace('\n' , ''))
        else:
            sub_title.append('no info')

        if len(all_part.select("[class='item-style']")) != 0:
            sub_style.append(all_part.select("[class='item-style']")[0].text.replace('  ' , ' '))
        else:
            sub_style.append('no info')
            
        if len(all_part.select("[class='item-area']")) != 0:
            sub_loc.append(all_part.select("[class='item-area']")[0].text.replace(' ' , ''))
        else:
            sub_loc.append('no info')    
            
        if len(all_part.select("[class='item-tip subway']")) != 0:
            sub_subway.append(all_part.select("[class='item-tip subway']")[0].text.replace(' ' , '').replace('\n' , '').replace('捷運' , ''))
        else:
            sub_subway.append('no info')  
        
        if len(all_part.select("[class='item-price-text']")) != 0:
            sub_rent.append(all_part.select("[class='item-price-text']")[0].text.replace(',' , '').replace(' ' , '').replace('元/月\n' , ''))
        else:
            sub_rent.append('no info') 

    sub_data = pd.concat([pd.DataFrame(sub_title) ,
                          pd.DataFrame(sub_style) ,
                          pd.DataFrame(sub_loc) ,
                          pd.DataFrame(sub_subway) ,
                          pd.DataFrame(sub_rent)] , axis = 1)
    sub_data.to_csv(os.path.join('./crawl_result/{}'.format(chi_eng[city]) , 'raw_data_page_{}.csv'.format(page)) , encoding = 'utf_8_sig')
    title.extend(sub_title)
    style.extend(sub_style)
    loc.extend(sub_loc)
    subway.extend(sub_subway)
    rent.extend(sub_rent) 
    time.sleep(random.randint(5 , 20))
       
    current_page = int(soup.select("[class='pageCurrent']")[-1].text)
    last_page = int(soup.select("[class='pageNum-form']")[-1].text)
    now = datetime.now()
    print('\rProgress: {}/{} , time: {}'.format(current_page , last_page  , now.strftime('%H:%M:%S')) , end = '')
    if current_page < last_page:
        # next page
        element = driver.find_element(By.CSS_SELECTOR, ".pageNext > span")
        ActionChains(driver).move_to_element(element).click(element).perform()
        time.sleep(random.randint(1 , 2))
        page += 1
    else:  
        print('已到達最後一頁 !!')
        break
    
total_data = pd.concat([pd.DataFrame(title) ,
                        pd.DataFrame(style) ,
                        pd.DataFrame(loc) , 
                        pd.DataFrame(subway) ,
                        pd.DataFrame(rent)] , axis = 1)    
total_data.to_csv(os.path.join('./crawl_result/{}'.format(chi_eng[city]) , 'raw_data.csv') , encoding = 'utf_8_sig')
