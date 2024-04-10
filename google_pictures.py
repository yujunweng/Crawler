import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv
import time
import os
import selenium




if __name__ == '__main__':
    url = 'https://www.google.com.tw/imghp?hl=zh-TW&tab=wi'
    findWords = ('青蛙', '蟾蜍', '螞蟻', '蟻象')
    
    
    # 取消網頁中的彈出視窗，避免妨礙網路爬蟲的執行
    options = Options()
    
    options.add_argument("--disable-notifications")        #阻擋彈跳式視窗
    #options.add_argument('--headless')         # 使用headless無介面瀏覽器模式
    options.add_argument('--disable-gpu')     #如果不加這個選項，有時定位會出現問題    
    
    # 建立webdriver物件，傳入下載的「瀏覽器驅動程式路徑」及「瀏覽器設定(chrome_options)」
    # selenium4.9.0 above could find chromedriver by itself
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    searchEntry = browser.find_element(By.CSS_SELECTOR, '[name="q"]')
    searchEntry.send_keys(findWords[0])
    searchEntry.send_keys(Keys.ENTER)
    
    browser.implicitly_wait(5) # seconds
    # 取得圖檔路徑
    # Find the parent <a> element that contains the image
    parent_element = browser.find_element(By.XPATH, '//div[@class="fR600b islir"]')

    # Get the href attribute of the parent <a> element
    href_attribute = parent_element.get_attribute('href')

    # Extract the imgurl parameter from the href attribute
    imgurl_param = href_attribute.split('imgurl=')[1].split('&')[0]

    # Print or use the imgurl_param as needed
    print(imgurl_param)

    os._exit(0)








