import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import csv
import time
import os
import selenium
import urllib
import traceback


if __name__ == '__main__':
    url = 'https://www.google.com.tw/imghp?hl=zh-TW&tab=wi'
    findWords = ('frog', '蟾蜍', '螞蟻', '蟻象')
    
    
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
    
    # 模擬滾動視窗瀏覽更多圖片
    pos = 0  
    count = 0 # 圖片編號 
    
    for i in range(10):  
        pos += i*500 # 每次下滾500  
        js = "document.documentElement.scrollTop=%d" % pos  
        browser.execute_script(js)
        time.sleep(3)

        #WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Q4LuWd')))
    
    
    savePath = "./imgs"
    if not os.path.isdir(savePath):
        os.mkdir(savePath)
    reightXPath = False    
    j = 1
    k = 4
    while 1:
        try:
            img = browser.find_element(By.XPATH, '/html/body/div[%d]/div/div[13]/div/div[2]/div[2]/div/div/div/div/div[1]/div/div/div[%d]/div[2]/h3/a/div/div/div/g-img/img' %(k, j)) 
            #imgs = browser.find_elements(By.CLASS_NAME,'Q4LuWd')
        except selenium.common.exceptions.NoSuchElementException:
            if not rightXPath:
                k += 1
                print('k=', k)
            else:
                j += 1
                print('j=', j)
            img = browser.find_element(By.XPATH, '/html/body/div[%d]/div/div[13]/div/div[2]/div[2]/div/div/div/div/div[1]/div/div/div[%d]/div[2]/h3/a/div/div/div/g-img/img' %(k, j))
        
        except:
            traceback.print_exc()
            os._exit(0)
            
        # 取得圖檔路徑
        #os.makedirs('./imgs')
        rightXPath = True
        imgUrl = img.get_attribute("src")
        if imgUrl is not None:
            save_img = os.path.join(savePath, findWords[0]+str(count)+'.jpg')
            #圖片之開啟並儲存
            with urllib.request.urlopen(imgUrl) as r:
                data = r.read()
                with open(save_img, "wb") as f:
                    f.write(data)
            count += 1        
            j += 1            
            time.sleep(0.5)
