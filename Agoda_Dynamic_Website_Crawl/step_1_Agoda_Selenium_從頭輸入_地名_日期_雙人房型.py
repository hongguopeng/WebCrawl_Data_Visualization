from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , TimeoutException , WebDriverException , StaleElementReferenceException
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

# 按掉彈出式廣告
def delete_pop_ad():
    try:
        driver.find_element_by_class_name('ab-close-button').click()
    except NoSuchElementException:
        pass

# 若跳出其他網頁，則將目前頁面轉回目標頁面
def delete_webpage():
    handles = driver.window_handles
    if len(handles) == 2:
        driver.switch_to_window(handles[1])
        driver.close()
        driver.switch_to_window(handles[0])

driver = webdriver.Chrome()
driver.set_window_position(2000 , 0)
driver.maximize_window()
driver.get("https://www.agoda.com/zh-tw/")
time.sleep(5)
city = 'Taipei'

print('1.輸入城市、區域、景點或住宿名稱 → 開始')
try:
    delete_pop_ad()
    driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").click()
    driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").send_keys(city)
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
        except NoSuchElementException:
            break
        except StaleElementReferenceException:
            driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
            
except WebDriverException:
    time.sleep(2)
    delete_pop_ad()
    driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").click()
    driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextEditor").send_keys("台北")
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
        except NoSuchElementException:
            break
        except StaleElementReferenceException:
            driver.find_element(By.CSS_SELECTOR, ".Suggestion:nth-child(1)").click()
print('1.輸入城市、區域、景點或住宿名稱 → 結束\n')


print('2.選擇日期 → 開始')
travel_start_day = datetime(year = 2022 , month = 6 , day = 11)
travel_end_day = datetime(year = 2022 , month = 6 , day = 12)
travel_month_first_day = datetime(year = 2022 , month = 6 , day = 1) # 當月第一天
add_day = travel_month_first_day.weekday()
moving_month = travel_start_day.month - datetime.today().month
if (travel_start_day.day + add_day) % 7 == 0: 
    input_start_day = 7
    input_start_week = (travel_start_day.day + add_day) // 7
else: 
    input_start_day = (travel_start_day.day + add_day) % 7  
    input_start_week = (travel_start_day.day + add_day) // 7 + 1
    
if (travel_end_day.day + add_day) % 7 == 0: 
    input_end_day = 7
    input_end_week = (travel_end_day.day + add_day) // 7
else: 
    input_end_day = (travel_end_day.day + add_day) % 7 
    input_end_week = (travel_end_day.day + add_day) // 7 + 1
delete_pop_ad()
time.sleep(1)
for i in range(0 , moving_month): # 選擇日期的窗格滑動4次，ex:現在12月，若想選擇4月的房間，就滑動4次；而日期挑在4/10~4/17
    driver.find_element(By.CSS_SELECTOR, ".DayPicker-NavButton--next").click()
    time.sleep(1)
driver.find_element_by_xpath("//div[@id='SearchBoxContainer']/div/div/div[2]/div/div/div[5]/div/div/div[2]/div/div[2]/div/div[3]/div[{}]/div[{}]/div/div/span".format(input_start_week , input_start_day)).click()
driver.find_element_by_xpath("//div[@id='SearchBoxContainer']/div/div/div[2]/div/div/div[5]/div/div/div[2]/div/div[2]/div/div[3]/div[{}]/div[{}]/div/div/span".format(input_end_week , input_end_day)).click()
driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextDescription--checkOut > .SearchBoxTextDescription__title").click()
print('2.選擇日期 → 結束\n')
time.sleep(2)


print('3.選擇旅遊形式 → 開始')
delete_pop_ad()
# 選擇雙人旅遊
try:
    driver.find_element(By.CSS_SELECTOR, ".SearchBoxTextDescription--occupancy > .SearchBoxTextDescription__title").click()
    driver.find_element(By.CSS_SELECTOR, ".TravellerSegment--active > .TravellerSegment__title").click()
except NoSuchElementException:
    pass
print('3.選擇旅遊形式 → 結束\n')
time.sleep(2)


print('4.開始查詢 → 開始')
delete_pop_ad()
driver.find_element_by_xpath("//div[@id='SearchBoxContainer']/div[2]/button/div").click()
try:
    driver.find_element_by_css_selector("svg.SvgIconstyled__SvgIconStyled-sc-1i6f60b-0.RBeKP > path").click()
except NoSuchElementException:
    pass    
print('4.開始查詢 → 結束\n')


print('5.選擇價格 → 開始')
driver.find_element_by_id("price_box_0").click()
driver.find_element_by_id("price_box_0").clear()
driver.find_element_by_id("price_box_0").send_keys("0")
driver.find_element_by_id("price_box_1").click()
driver.find_element_by_id("price_box_1").clear()
driver.find_element_by_id("price_box_1").send_keys("6000")
driver.find_element_by_id("price_box_1").send_keys(Keys.ENTER)
print('5.選擇價格→ 結束\n')

#-----------------------crawl_part-----------------------#
data_pd = pd.DataFrame(columns = ['旅店名稱' , '鄰近地區' , '旅客評分' , '旅客評鑑數目' , '旅店當天價格'])

while True:
    time.sleep(5 + np.random.randint(0 , 5))
    soup = BeautifulSoup(driver.page_source , 'html.parser')

    current_page = soup.select("[data-selenium='pagination-text']")[0].text.split('/')[0]
    total_page = soup.select("[data-selenium='pagination-text']")[0].text.split('/')[1]
    current_page = int(current_page.replace('第' , '').replace('頁' , ''))
    total_page = int(total_page.replace(' 共' , '').replace('頁' , ''))
    print('\ncurrent page : {} , total page : {}'.format(current_page , total_page))

    # 必須將網頁慢慢往下滾動，才能獲得全部旅店的資訊
    # 網頁往下滾動時，y_location會慢慢變大，當停止變大時，代表網頁已經滾動到最下面
    # 接下來即可使用BeautifulSoup獲取網頁內容
    y_location_set = []
    count_rolldown = 0
    y_current = 0
    while True:
        delete_webpage()

        y_location = driver.find_element_by_xpath("//span[@id='paginationPageCount']").location['y']
        print('page : {} , y_location : {} , count : {}'.format(current_page , y_location , count_rolldown))
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

        # 每次將網頁往下滾動200
        driver.execute_script("window.scrollBy(0,100)")

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") # 讓網頁頁面滾動到最底部

    # 使用BeautifulSoup獲取網頁內容
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source , 'html.parser')
    temp_name , temp_loc , temp_rate , temp_evaluation_num , temp_price = [] , [] , [] , [] , []
    for step , all_part in enumerate(soup.select("[class='Box-sc-kv6pi1-0 hRUYUu JacketContent JacketContent--Empty']")):     
        # 獲取旅店名稱
        if len(all_part.select("[data-selenium='hotel-name']")) != 0:
            name = all_part.select("[data-selenium='hotel-name']")[0].text
            name = name.split('/')[0]
            temp_name.append(name)
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
        if len(all_part.select("[class='Typographystyled__TypographyStyled-sc-j18mtu-0 Hkrzy kite-js-Typography ']")) != 0:
            rate = float(all_part.select("[class='Typographystyled__TypographyStyled-sc-j18mtu-0 Hkrzy kite-js-Typography ']")[0].text)
            temp_rate.append(rate)
        else :
            temp_rate.append('no info')

        # 獲取旅客評鑑數目
        if len(all_part.select("[class='Spanstyled__SpanStyled-sc-16tp9kb-0 jYmZbG kite-js-Span Box-sc-kv6pi1-0 jjmSNA']")) != 0:
            evaluation_num = int(all_part.select("[class='Spanstyled__SpanStyled-sc-16tp9kb-0 jYmZbG kite-js-Span Box-sc-kv6pi1-0 jjmSNA']")[0].text.split(' ')[0].replace(',' , ''))
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
        data_pd = pd.concat([data_pd , data_pd_temp] , axis = 0)

    # 當找不到"paginationNext"這個元素，代表很可能已經到了最後一頁，即可停止爬蟲
    try:
        driver.find_element_by_id("paginationNext").click()
        print('\nNOT YET!!!')
    except NoSuchElementException:
        try:
            # 在5秒內看"paginationNext"這個元素有沒有出現，如果沒有出現，代表已經到了最後一頁，即可停止爬蟲
            wait = ui.WebDriverWait(driver , 5)
            wait.until(lambda driver: driver.find_element_by_id("paginationNext"))
        except TimeoutException:
            print('\nFINSH CRAWLING!!!')
            break
        
data_pd.reset_index(inplace = True , drop = True)
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
data_pd['旅店名稱'] = data_pd['旅店名稱'].apply(simplification) 
data_pd['旅客評分'] = pd.to_numeric(data_pd['旅客評分']  , errors = 'coerce')
data_pd['旅客評鑑數目'] = pd.to_numeric(data_pd['旅客評鑑數目']  , errors = 'coerce')
data_pd['旅店當天價格'] = pd.to_numeric(data_pd['旅店當天價格']  , errors = 'coerce')
data_pd.to_csv(os.path.join('./crawl_result' , '{}_crawl_result.csv'.format(city)) , encoding = 'utf_8_sig')
#-----------------------crawl_part-----------------------#


#-----------------------demo-----------------------#
#driver.execute_script("window.scrollBy(0,50)") # 模擬網頁往下滾動，每次滾動距離50
#driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") # 讓網頁頁面滾動到最底部
#driver.execute_script("window.scrollTo(0,0)") # 讓網頁頁面滾動到最上方     
#-----------------------demo-----------------------#