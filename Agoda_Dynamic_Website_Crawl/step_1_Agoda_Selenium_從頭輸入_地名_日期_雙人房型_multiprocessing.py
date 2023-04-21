from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , TimeoutException , WebDriverException , StaleElementReferenceException , ElementNotInteractableException
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import multiprocessing as mp
import pandas as pd
import numpy as np
import time
import datetime
import sys
import re
import random
import os


class agoda_crawl(object):
    def __init__(self , city , start_date , end_date , pos_x = 0 , pos_y = 0 , size_x = 500 , size_y = 500):
        self.city = city
        self.start_date = datetime.date(start_date[0] , start_date[1] , start_date[2])
        self.end_date = datetime.date(end_date[0] , end_date[1] , end_date[2])
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        
    # 把括號中(包含括號)的文字去除掉
    @staticmethod
    def simplification(x):
        ret = re.finditer("\(.*\)" , x)
        for m in ret:
            remove_idx = m.span()
            
        list_x = list(x)
        try:
            for i in range(remove_idx[0] , remove_idx[1]):
                list_x[i] = ''
        except:
            pass        
        x = ''.join(list_x)
        
        return x       

    def num_confirm(self):
        if self.room_num < 1: sys.exit('Please reselect number of room!!')
        if self.adults_num < 1: sys.exit('Please reselect number of adult!!')
        if self.adults_num < self.room_num: sys.exit('Please reselect number of room & adult!!')

    def date_confirm(self):
        if (self.start_date - datetime.date.today()).days < 0:
            sys.exit('Please reselect departrue date!!')
                    
    def get_web(self , driver):
        self.driver = driver
        self.driver.set_window_position(self.pos_x , self.pos_y)
        self.driver.set_window_size(self.size_x , self.size_y)
        self.driver.get("https://www.agoda.com/zh-tw/")
        time.sleep(random.randint(50 , 60)) 
 
    # 按掉彈出式廣告
    def delete_pop_ad(self):
        try:
            self.driver.find_element_by_class_name('ab-close-button').click()
        except NoSuchElementException:
            pass 
    
    def select_city(self):
        print('city : {} , step1.輸入城市、區域、景點或住宿名稱 → 開始'.format(self.city))
        try:
            self.delete_pop_ad()
            self.driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").click()
            self.driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").send_keys(u"{}".format(self.city))
            while True:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
                except NoSuchElementException:
                    break
                except StaleElementReferenceException:
                    self.driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
                    
        except WebDriverException:
            time.sleep(2)
            self.delete_pop_ad()
            self.driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").click()
            self.driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").send_keys(u"{}".format(self.city))
            while True:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
                except NoSuchElementException:
                    break
                except StaleElementReferenceException:
                    self.driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
        print('city : {} , step1.輸入城市、區域、景點或住宿名稱 → 結束'.format(self.city))
        
    def month_delta(self):
        localtime = time.localtime()
        result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime)
        current_year = int(result.split(' ')[0].split('-')[0])
        current_month = int(result.split(' ')[0].split('-')[1])
        count = 0
        while True:
            current_month = current_month + 1
            if current_month == 13:
                current_month = 1
                current_year = current_year + 1
            count = count + 1    
            if current_year == self.start_date.year and current_month == self.start_date.month:
                break   
        self.month_moving = count 
    
    def select_date(self):
        print('city : {} , step2.選擇日期 → 開始'.format(self.city))
        month_first_day = datetime.date(self.start_date.year , self.start_date.month , day = 1) # 當月第一天
        add_day = month_first_day.weekday()
        if (self.start_date.day + add_day) % 7 == 0: 
            input_start_day = 7
            input_start_week = (self.start_date.day + add_day) // 7
        else: 
            input_start_day = (self.start_date.day + add_day) % 7  
            input_start_week = (self.start_date.day + add_day) // 7 + 1
        if (self.end_date.day + add_day) % 7 == 0: 
            input_end_day = 7
            input_end_week = (self.end_date.day + add_day) // 7
        else: 
            input_end_day = (self.end_date.day + add_day) % 7 
            input_end_week = (self.end_date.day + add_day) // 7 + 1        
        self.delete_pop_ad()
        time.sleep(1)
        for i in range(0 , self.month_moving): # 選擇日期的窗格滑動4次，ex:現在12月，若想選擇4月的房間，就滑動4次；而日期挑在4/10~4/17
            try:
                self.driver.find_element(By.CSS_SELECTOR , ".DayPicker-NavButton--next").click()
            except ElementNotInteractableException:
                element = self.driver.find_element(By.CSS_SELECTOR , ".DayPicker-NavButton--next")
                self.driver.implicitly_wait(10)
                ActionChains(self.driver).move_to_element(element).click(element).perform()
        time.sleep(1)
        self.driver.find_element_by_xpath("//div[@id='SearchBoxContainer']/div/div/div[2]/div/div/div[5]/div/div/div[2]/div/div[2]/div/div[3]/div[{}]/div[{}]/div/div/span".format(input_start_week , input_start_day)).click()
        self.driver.find_element_by_xpath("//div[@id='SearchBoxContainer']/div/div/div[2]/div/div/div[5]/div/div/div[2]/div/div[2]/div/div[3]/div[{}]/div[{}]/div/div/span".format(input_end_week , input_end_day)).click()
        self.driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextDescription--occupancy > .SearchBoxTextDescription__title").click()
        print('city : {} , step2.選擇日期 → 結束'.format(self.city))
        time.sleep(5)
        
    def select_room_type(self):
        print('city : {} , step3.選擇旅遊形式 → 開始'.format(self.city))
        self.delete_pop_ad()
        # 選擇雙人旅遊
        try:
            self.driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextDescription--occupancy > .SearchBoxTextDescription__title").click()
            self.driver.find_element(By.CSS_SELECTOR, ".TravellerSegment--active > .TravellerSegment__title").click()
        except NoSuchElementException:
            pass
        print('city : {} , step3.選擇旅遊形式 → 結束'.format(self.city))
        time.sleep(2)

    def press_search_button(self):
        print('city : {} , step4.開始查詢 → 開始'.format(self.city))
        self.delete_pop_ad()
        self.driver.find_element_by_xpath("//div[@id='SearchBoxContainer']/div[2]/button/div").click()
        try:
            # self.driver.find_element_by_css_selector("svg.SvgIconstyled__SvgIconStyled-sc-1i6f60b-0.RBeKP > path").click()
            element = self.driver.find_element_by_css_selector("svg.SvgIconstyled__SvgIconStyled-sc-1i6f60b-0.RBeKP > path")
            ActionChains(self.driver).move_to_element(element).click(element).perform()
        except NoSuchElementException:
            pass 
        print('city : {} , step4.開始查詢 → 結束'.format(self.city))
        time.sleep(5)
        
    def price_range(self): 
        print('city : {} , step5.決定價格區間 → 開始'.format(self.city))
        self.driver.find_element_by_id("price_box_0").click()
        self.driver.find_element_by_id("price_box_0").clear()
        self.driver.find_element_by_id("price_box_0").send_keys("0")
        self.driver.find_element_by_id("price_box_1").click()
        self.driver.find_element_by_id("price_box_1").clear()
        self.driver.find_element_by_id("price_box_1").send_keys("5000")
        self.driver.find_element_by_id("price_box_1").send_keys(Keys.ENTER)
        print('city : {} , step5.決定價格區間 → 結束'.format(self.city))
        time.sleep(5)

    def start_crawl(self):
        self.data_pd = pd.DataFrame(columns = ['旅店名稱' , '鄰近地區' , '旅客評分' , '旅客評鑑數目' , '旅店當天價格'])
        while True:
            time.sleep(5 + np.random.randint(0 , 5))
            soup = BeautifulSoup(self.driver.page_source , 'html.parser')
        
            current_page = soup.select("[data-selenium='pagination-text']")[0].text.split('/')[0]
            total_page = soup.select("[data-selenium='pagination-text']")[0].text.split('/')[1]
            current_page = int(current_page.replace('第' , '').replace('頁' , ''))
            total_page = int(total_page.replace(' 共' , '').replace('頁' , ''))
            print('\ncity : {} , current page : {} , total page : {}'.format(self.city , current_page , total_page))

            # 必須將網頁慢慢往下滾動，才能獲得全部旅店的資訊
            # 網頁往下滾動時，y_location會慢慢變大，當停止變大時，代表網頁已經滾動到最下面
            # 接下來即可使用BeautifulSoup獲取網頁內容
            y_location_set = []
            count_rolldown = 0
            y_current = 0
            while True:
                # 若跳出其他網頁，則將目前頁面轉回目標頁面
                handles = self.driver.window_handles
                if len(handles) == 2:
                    self.driver.switch_to_window(handles[1])
                    self.driver.close()
                    self.driver.switch_to_window(handles[0])
                        
                y_location = self.driver.find_element_by_xpath("//span[@id='paginationPageCount']").location['y']
                print('city : {} , page : {} , y_location : {} , count : {}'.format(self.city , current_page , y_location , count_rolldown))
                y_location_set.append(y_location)
                y_location_set = np.array(y_location_set)
                if y_location_set[-1] != y_current:
                    y_current = y_location_set[-1]
                    count_rolldown = 0
                elif y_location_set[-1] == y_current:
                    count_rolldown += 1
        
                if count_rolldown > 200:
                    y_location_set = []
                    count_rolldown = 0
                    y_current = 0
                    break
                y_location_set = list(y_location_set)
        
                # 每次往下滾動200
                self.driver.execute_script("window.scrollBy(0,100)")

            # 使用BeautifulSoup獲取網頁內容
            time.sleep(10)
            soup = BeautifulSoup(self.driver.page_source , 'html.parser')
            temp_name , temp_loc , temp_rate , temp_evaluation_num , temp_price = [] , [] , [] , [] , []
            for step , all_part in enumerate(soup.select("[class='Box-sc-kv6pi1-0 hRUYUu JacketContent JacketContent--Empty']")):
        
                # 獲取旅店名稱
                if len(all_part.select("[data-selenium='hotel-name']")) != 0:
                    temp_name.append(all_part.select("[data-selenium='hotel-name']")[0].text.strip())
                else:
                    temp_name.append('no info')
            
                # 獲取鄰近地區
                if len(all_part.select("[data-selenium='area-city-text']")) != 0:
                    if all_part.select("[data-selenium='area-city-text']")[0].text.rstrip(' - 查看地圖').split(',')[0] == '台北車站':
                        temp_loc.append('中正區')
                    else:
                        temp_loc.append(all_part.select("[data-selenium='area-city-text']")[0].text.rstrip(' - 查看地圖').split(',')[0])
                else:
                    temp_loc.append('no info')
        
                # 獲取旅客評分
                if len(all_part.select("[class='Box-sc-kv6pi1-0 ggePrW']")) != 0:
                    rate = float(all_part.select("[class='Box-sc-kv6pi1-0 ggePrW']")[0].text)
                    temp_rate.append(rate)
                else :
                    temp_rate.append('no info')

                # 獲取旅客評鑑數目
                if len(all_part.select("[class='Spanstyled__SpanStyled-sc-16tp9kb-0 jYmZbG kite-js-Span Box-sc-kv6pi1-0 jjmSNA']")) != 0:
                    evaluation_num = int(''.join(filter(str.isdigit , all_part.select("[class='Spanstyled__SpanStyled-sc-16tp9kb-0 jYmZbG kite-js-Span Box-sc-kv6pi1-0 jjmSNA']")[0].text)))
                    temp_evaluation_num.append(evaluation_num)
                else: temp_evaluation_num.append('no info')

                # 獲取旅店當天價格
                if len(all_part.select("[class='PropertyCardPrice__Value']")) != 0:
                    price = int(all_part.select("[class='PropertyCardPrice__Value']")[0].text.replace(',' , ''))
                    temp_price.append(price)
                elif len(all_part.select("[data-element-name='final-price']")) != 0:
                    price = int(all_part.select("[data-element-name='final-price']")[0].text.split(' ')[-1].replace(',' , ''))
                    temp_price.append(price)
                else: temp_price.append('no info')
    
            
            data_pd_temp = pd.concat([pd.DataFrame(temp_name) , 
                                      pd.DataFrame(temp_loc) ,
                                      pd.DataFrame(temp_rate) ,
                                      pd.DataFrame(temp_evaluation_num) ,
                                      pd.DataFrame(temp_price)] , axis = 1)
            if len(data_pd_temp) != 0:
                data_pd_temp.columns = ['旅店名稱' , '鄰近地區' , '旅客評分' , '旅客評鑑數目' , '旅店當天價格']
                self.data_pd = pd.concat([self.data_pd , data_pd_temp] , axis = 0)


            # 當找不到"paginationNext"這個元素，代表很可能已經到了最後一頁，即可停止爬蟲
            try:
                self.driver.find_element_by_id("paginationNext").click()
                print('\ncity : {} , NOT YET!!!'.format(self.city))
            except NoSuchElementException:
                try:
                    # 在5秒內看"paginationNext"這個元素有沒有出現，如果沒有出現，代表已經到了最後一頁，即可停止爬蟲
                    wait = ui.WebDriverWait(self.driver , 5)
                    wait.until(lambda driver: self.driver.find_element_by_id("paginationNext"))
                except TimeoutException:
                    print('\ncity : {} , FINSH CRAWLING!!!'.format(self.city))
                    break
                
    def save_crawl_result(self):
        self.data_pd.reset_index(inplace = True , drop = True)
        self.data_pd['旅店名稱'] = self.data_pd['旅店名稱'].apply(self.simplification) 
        self.data_pd.to_csv(os.path.join('./crawl_result' , '{}_crawl_result.csv'.format(self.city)) , encoding = 'utf_8_sig')
       
        
def crawl_fun(agoda_crawler , city_name):
    agoda_crawler.date_confirm()
    driver = webdriver.Chrome()
    agoda_crawler.get_web(driver)
    agoda_crawler.select_city()
    agoda_crawler.month_delta()
    agoda_crawler.select_date()
    agoda_crawler.select_room_type()
    agoda_crawler.press_search_button()
    agoda_crawler.price_range()
    agoda_crawler.start_crawl()
    agoda_crawler.save_crawl_result()

if __name__ == '__main__':
    city_name_list = ['Taipei' , 'Taichung' , 'Miaoli' , 'Tainan' , 'Kaohsiung' , 'Pingtung' , 'Yilan' , 'Hualien']
    crawl_list = []
    for i , city in enumerate(city_name_list):
        crawl_list.append(agoda_crawl(city = city ,                    
                                      start_date = [2022 , 6 , 11] ,  
                                      end_date = [2022 , 6 , 12] ,    
                                      pos_x = 100 * i ,
                                      pos_y = 0 ,
                                      size_x = 1000 ,
                                      size_y = 900))
    
    processes = []
    for i in range(0 , len(crawl_list)):
        processes = []
        p = mp.Process(target = crawl_fun , args = [crawl_list[i] , city_name_list[i]])
        p.start()
        processes.append(p)

    for process in processes:
        process.join()