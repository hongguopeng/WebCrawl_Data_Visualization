from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , TimeoutException , WebDriverException , StaleElementReferenceException
import selenium.webdriver.support.ui as ui
from bs4 import BeautifulSoup
import requests
import re
import json
import time
import pandas as pd
import random

driver = webdriver.Chrome()
driver.set_window_position(2000 , 0)
driver.maximize_window()
driver.get("https://www.amazon.com/s?k=sexy+lingerie&language=en_US&crid=2HKWU10901ND2&sprefix=sexy+lingerie")
time.sleep(5)

# 蒐集每個商品的資訊
soup = BeautifulSoup(driver.page_source , 'html.parser')
total_page = int(soup.select("[class='s-pagination-item s-pagination-disabled']")[0].text)
page = 1
lingeries = []
while True:
    print('\rpage : {}/{}'.format(page , total_page) , end = '')
    soup = BeautifulSoup(driver.page_source , 'html.parser')
    items = soup.select("[class='a-section a-spacing-base']")
    
    for i , item in enumerate(items):
        # 商品名稱
        name = item.select("[class='a-size-base-plus a-color-base a-text-normal']")[0].text
        
        # 商品星數
        try:
            stars = item.select("[class='a-icon-alt']")[0].text
        except IndexError:
            stars = 'no info'
        
        # 商品評價數目
        try:
            reviews = item.select("[class='a-size-base s-underline-text']")[0].text
        except IndexError:
            reviews = 'no info'
        
        # 是否為Best Seller
        try:
            if item.select("[class='a-badge-text']")[0].text == 'Best Seller':
                best_seller = True
            else:
                best_seller = False
        except IndexError:
            best_seller = False
        
        # 商品連結
        item_link = 'https://www.amazon.com/{}'.format(item.select("[class='a-link-normal s-no-outline']")[0]['href'])
        
        lingerie = [name , stars , reviews , best_seller , item_link]
        lingeries.append(lingerie)
    
    try:
        driver.find_element_by_link_text("Next").click()
    except NoSuchElementException:
        try:
            # 在5秒內看"paginationNext"這個元素有沒有出現，如果沒有出現，代表已經到了最後一頁，即可停止爬蟲
            wait = ui.WebDriverWait(driver , 5)
            wait.until(lambda driver: driver.find_element_by_link_text("Next"))
        except TimeoutException:
            print('\nFINSH CRAWLING!!!')
            break
    page += 1 
    time.sleep(random.randint(1 , 3))   

lingeries = pd.DataFrame(lingeries)
lingeries.columns = ['product' , 'stars' , 'reviews' , 'best_seller' , 'item_link']


# 針對商品連結蒐集更詳細的商品資訊
lingeries = pd.read_csv('lingeries_raw.csv')
driver = webdriver.Chrome()
total_price , total_shop , total_comments , total_size_color = [] , [] , [] , []
for i , item_link in enumerate(lingeries['item_link']):
    print('\rprogress : {}/{}'.format(i + 1 , len(lingeries)) , end = '')
    driver.get(item_link + '&language=en_US')
    soup = BeautifulSoup(driver.page_source , 'html.parser')
    
    # 賣商
    try:    
        shop = soup.select("[id='bylineInfo']")[0].text      
    except IndexError:
        try:
            shop = soup.select("[class='a-color-base a-link-normal a-text-bold']")[0].text 
        except IndexError:    
            shop = 'no info'
    total_shop.append(shop)
    
    # 商品價格
    try:
        price = soup.select("[class='a-price-range']")[0].text  # 價格區間
    except IndexError:
        try:
            price = soup.select("[class='a-price a-text-price a-size-medium apexPriceToPay']")[0].text  # 單一價格
        except IndexError:
            price = 'no info'
    total_price.append(price) 
        
    # 商品評論內容
    try:
        comment_list = soup.select("[data-hook='review-collapsed']") 
        comments = []
        for comment in comment_list:
            comments.append(comment.text)
        if len(comments) == 0:
            comments = 'no info'
    except IndexError:
        comments = 'no info'         
    total_comments.append(comments)  
    
    # 商品尺寸&顏色
    try:
        size_color_list = soup.select("[data-hook='format-strip-linkless']")  
        size_colors = []
        for size_color in size_color_list:
            size_colors.append(size_color.text)
        if len(size_colors) == 0:
            size_colors = 'no info'
    except IndexError:
        size_colors = 'no info'
    total_size_color.append(size_colors) 
      
    time.sleep(random.randint(1 , 7))


# 存入csv檔再讀取會讓原本的list變成沒有分隔的字串，因此在這裡預先做分隔字符
total_comments_new , total_size_color_new = [] , []
for comments , size_color in zip(total_comments , total_size_color):
    if comments != 'no info':
        total_comments_new.append('||||||||||||||||||||||||'.join(comments))
    else:
        total_comments_new.append('no info')
    if comments != 'size_color':    
        total_size_color_new.append('||||||||||||||||||||||||'.join(size_color))
    else:
        total_size_color_new.append('no info')

lingeries['shop'] , lingeries['price'] , lingeries['comments'] , lingeries['size_color'] = total_shop , total_price , total_comments_new , total_size_color_new
lingeries.to_csv('lingeries_raw.csv' , index = False)