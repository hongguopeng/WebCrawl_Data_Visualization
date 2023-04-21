import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException , TimeoutException , WebDriverException
from bs4 import BeautifulSoup
import time
import re
import os

# raw_data = pd.read_csv(os.path.join('./crawl_result' , '{}_crawl_result.csv'.format(city))  , index_col = 0)
# raw_data.replace({'【初登場】尚無評價' : np.nan , 'no info' : np.nan} , inplace = True)

# raw_data['行政區'] = raw_data['鄰近地區'].apply(lambda x : x.split(',')[0])
# raw_data['行政區'] = raw_data['行政區'].replace({'台北車站' : '中正區' , '西門町' : '萬華區' , '九份' : '瑞芳區'})
# raw_data.drop(columns = ['鄰近地區'] , inplace = True)

# raw_data['旅客評分'] = raw_data['旅客評分'].str.replace(',' , '').astype(float)
# raw_data['旅客評鑑數目'] = raw_data['旅客評鑑數目'].str.replace(',' , '').astype(float)
# raw_data['旅店當天價格'] = raw_data['旅店當天價格'].str.replace(',' , '').astype(float)

## 搜尋所有旅店的地址
city = 'Taipei'
raw_data = pd.read_csv(os.path.join('./crawl_result' , '{}_crawl_result.csv'.format(city))  , index_col = 0)
raw_data['旅店地址'] = [0 for _ in range(0 , len(raw_data))]
driver = webdriver.Chrome()
driver.get("https://www.google.com.tw/")
driver.set_window_size(500 , 500)
for index , hotel in enumerate(raw_data['旅店名稱']):
    driver.find_element_by_name("q").click()
    driver.find_element_by_name("q").clear()
    driver.find_element_by_name("q").send_keys(u"{} {} 地址".format(raw_data['行政區'].loc[index] , hotel))
    driver.find_element_by_id("tsf").submit()
    
    soup = BeautifulSoup(driver.page_source , 'html5lib')
    try:
        address = soup.select("[class='LrzXr']")[0].text
        address = re.sub(r'^\d{3,10}' , '' , address) # 把地址前的郵遞區號去掉
    except IndexError:
        driver.back()
        driver.find_element_by_name("q").click()
        driver.find_element_by_name("q").clear()
        try:
            # 取括號裡面的名稱
            condition = re.compile(r'[(](.*?)[)]' , re.S)
            hotel_another = re.findall(condition , hotel)[0]
        except IndexError:
            # 若有沒括號或者還是搜尋不到地址的情況，就讓hotel_another = 'no info'，直接進行查詢
            # 反正後面soup.select("[class='LrzXr']")一定找不到任何東西，所以直接讓address = raw_data['行政區'][index]
            # 就像是raw_data['旅店名稱']中有一家叫做yummy就是會碰到這種情況
            hotel_another = 'no info'
        driver.find_element_by_name("q").send_keys(u"{} {} 地址".format(raw_data['行政區'].loc[index] , hotel_another))
        driver.find_element_by_id("tsf").submit()

        try:
            soup = BeautifulSoup(driver.page_source , 'html5lib')
            address = soup.select("[class='LrzXr']")[0].text
            address = re.sub(r'^\d{3,10}' , '' , address)
        except IndexError:
            address = raw_data['行政區'][index]

    raw_data['旅店地址'].loc[index] = address
    print('Process : {} / {} {}'.format(index , len(raw_data) , address))
    driver.back()
driver.quit()
raw_data.to_csv('Taipei_crawl_result.csv')

# 藉由旅店地址，查詢所有旅店的經緯度
raw_data['lat'] = [0 for _ in range(0 , len(raw_data))]
raw_data['log'] = [0 for _ in range(0 , len(raw_data))]
driver = webdriver.Chrome()
driver.get("https://www.map.com.tw/")
driver.set_window_size(500 , 500)
for index , address in enumerate(raw_data['旅店地址']):
    driver.find_element_by_xpath("//input[@id='searchWord']").clear()
    driver.find_element_by_xpath("//input[@id='searchWord']").send_keys(u"{}".format(address))
    driver.find_element_by_xpath("//img[@onclick='search()']").click()
    time.sleep(2)
    iframe = driver.find_elements_by_tag_name("iframe")[1]
    driver.switch_to.frame(iframe)
    try:
        driver.find_element_by_xpath("//td[@onclick='showLocation()']").click()
    except WebDriverException:
        # 若碰到地址的寫法不是傳統寫法時，就直接用該地址所屬行政區重新查詢
        driver.switch_to.default_content()
        driver.find_element_by_xpath("//input[@id='searchWord']").clear()
        driver.find_element_by_xpath("//input[@id='searchWord']").send_keys(u"{}".format(raw_data['行政區'].loc[index]))
        driver.find_element_by_xpath("//img[@onclick='search()']").click()
        time.sleep(2)
        iframe = driver.find_elements_by_tag_name("iframe")[1]
        driver.switch_to.frame(iframe)
    
    soup = BeautifulSoup(driver.page_source , 'html5lib')
    coord = soup.select("[id='location']")[0].text.split('\n')[7].strip().split(' ')
    lat = coord[0].replace('\xa0' , ' ').split(' ')[0].split('：')[-1]
    log = coord[0].replace('\xa0' , ' ').split(' ')[-1].split('：')[-1]
    raw_data['lat'].loc[index] , raw_data['log'].loc[index] = float(lat) , float(log)
    print('Process : {} / {} {}'.format(index , len(raw_data) , address))
    driver.switch_to.default_content()
driver.quit()

raw_data.reset_index(inplace = True , drop = True)   
raw_data.to_csv(os.path.join('./crawl_result' , '{}_crawl_result_lat_log_v1.csv'.format(city)) , encoding = 'utf_8_sig')