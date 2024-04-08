# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import time
import os
import selenium



def writeCsv(i, name, address, source):
    # 存檔路徑
    sFilepath = "./%s.csv" %source
    
    # 開啟要寫入的檔案
    f = open(sFilepath, 'a+', encoding = 'UTF-8', newline ='')
    f_writer = csv.writer(f, dialect = 'excel')
    
    house_dict = {}
    fields = ['sequence', 'name', 'address', 'source']

    house_dict = {'sequence':i, 'name':name, 'address':address, 'source':source}
    if i == 1:
        f_writer.writerow(house_dict.keys())
    f_writer.writerow(house_dict.values())
    
    # 關閉檔案
    f.close()    
    
    
def getRentHouseLink(page, i):
    # 取消網頁中的彈出視窗，避免妨礙網路爬蟲的執行
    options = Options()
    
    options.add_argument("--disable-notifications")        #阻擋彈跳式視窗
    #options.add_argument('--headless')         # 使用headless無介面瀏覽器模式
    options.add_argument('--disable-gpu')     #如果不加這個選項，有時定位會出現問題
        
    # 建立webdriver物件，傳入下載的「瀏覽器驅動程式路徑」及「瀏覽器設定(chrome_options)」
    # 其中的「瀏覽器驅動程式路徑」一定要傳入，而「瀏覽器設定(chrome_options)」則選擇性視情況傳入
    #chrome = webdriver.Chrome('./chromedriver'), options=options)
    chrome = webdriver.Chrome(options=options) # selenium4.9.0 above could find chromedriver by itself
    
    # 在總覽頁面取得各個出租房屋的網址
    resp = requests.get(page)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        #print(soup)
        #for hotelLink in soup.find_all(sr_item_photo_link sr_hotel_preview_track, {'href':re.compile('/hotel/tw.*')}):        
        
        # 連結到該學校出租房屋頁面
        for school in soup.find_all('a', class_= 'btn btn-outline-info btn-block btn-sm mb-2'):    
            if school.text.strip().find('高雄市') > -1:
                print(school.text.strip())
                chrome.get(school['href'])
                time.sleep(4)
                i = getRentHouse(chrome, i)
                time.sleep(10)
            
        
def getRentHouse(browser, i):
    # 將當前視窗改為點入後的新視窗
    handles = browser.window_handles
    browser.switch_to.window(handles[0])
    
    # 取得當前新視窗網址
    url = browser.current_url

    # 取得出租房屋名稱與地址
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    for a in soup.find_all('a', 'page-link'):
        if a.text.replace(" ", "").find("共0頁") > -1:
            print(a.text.replace(" ", "").replace('\n', ''))   
            return i

    for tag in soup.find_all('div', class_='row p-1 m-0 rh-house'):
        house = tag.find_all('div', class_='mb-1')
        print(i, house[1].text, house[2].text)
        writeCsv(i, house[1].text, house[2].text, '雲端出租網')        
        i += 1
        
    # 頁面資料取得完成 換下一頁 
    try:
        browser.find_element('xpath', "//*[contains(text(), '下一頁')]").click()
        time.sleep(6)
        i = getRentHouse(browser, i)
    except selenium.common.exceptions.ElementClickInterceptedException:
        pass
    finally:
        return i


# 租賃服務資訊網首頁
rent_house = 'https://house.nfu.edu.tw/' 

if __name__ == '__main__':
    getRentHouseLink(rent_house, 1)