# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os
from datetime import datetime
import random
import csv
import time
import re
import time
import json

def writeCsv(i, hotel_name, hotel_addr, source):
	# 存檔路徑
	sFilepath = "./%s.csv" %source
	
	# 開啟要寫入的檔案
	f = open(sFilepath, 'a+', encoding = 'UTF-8', newline ='')
	f_writer = csv.writer(f, dialect = 'excel')
	
	hotel_dict = {}
	fields = ['sequence', 'hotel name', 'hotel address', 'source']

	hotel_dict = {'sequence':i, 'hotel name':hotel_name, 'hotel address':hotel_addr, 'source':source}
	if i == 1:
		f_writer.writerow(hotel_dict.keys())
	f_writer.writerow(hotel_dict.values())
	
	# 關閉檔案
	f.close()	

def getBookingHotel(link_to_hotel, i):	# 傳入參數為 booking.com 的 hotel 連結網址
	# 在各個 hotel 頁面取得名稱與地址
	resp_hotel = requests.get(link_to_hotel)
	
	if resp_hotel.status_code == 200:
		soup_hotel = BeautifulSoup(resp_hotel.text, 'html.parser')
		
		for jsoncontent in soup_hotel.find_all('script', type = 'application/ld+json'):
			#print(jsoncontent)
			jsoncontent = str(jsoncontent).strip('}')
			
			if jsoncontent is not None:
				# 取得名稱
				if jsoncontent.find("name") > -1:
					name_start = str(jsoncontent).find("name")+9
					name_end = jsoncontent.find('"', name_start)
					hotel_name = jsoncontent[name_start:name_end].strip()
				
				# 取得地址 
				if jsoncontent.find("streetAddress") > -1:
					addr_start = str(jsoncontent).find("streetAddress")+18
					addr_end = jsoncontent.find('"', addr_start)
					hotel_addr = jsoncontent[addr_start:addr_end].strip().replace('\\t', '')
					
					# 改成高雄市
					areas = ['橋頭', '梓官', '田寮', '岡山', '燕巢', '茄萣', '永安', '路竹', '阿蓮', '彌陀', '湖內',
							 '大寮', '大樹', '鳥松', '仁武', '大社', '林園',
							 '旗山', '美濃','六龜','杉林', '那瑪夏', '茂林', '內門', '甲仙', '桃源'
							] 
					for area in areas: 
						if hotel_addr.find(area) > -1:
							if hotel_addr.find('高雄') == -1:
								hotel_addr = '高雄市' + hotel_addr
					if hotel_addr.find('高雄') > -1: 
						if hotel_addr.find('高雄市') == -1:
							hotel_addr = hotel_addr.replace('高雄', '高雄市')
				
				# 地址在高雄才寫入檔案
				if (hotel_addr.find('高雄') > -1):	
					writeCsv(i, hotel_name, hotel_addr, 'booking')
					i += 1
				
				print(i-1, hotel_name, hotel_addr)
				time.sleep(0.5)
				
	return i 		

def getBookingHotelLink(page_allHotel, i):
	# 定義nextPage避免錯誤
	nextPage = None
	
	# 在總覽頁面取得各個 hotel 的網址
	resp = requests.get(page_allHotel)
	if resp.status_code == 200:
		
		# 解析頁面取得各 hotel 連結網址
		soup = BeautifulSoup(resp.text, 'html.parser')
		#for hotelLink in soup.find_all(sr_item_photo_link sr_hotel_preview_track, {'href':re.compile('/hotel/tw.*')}):		
		for hotelLink in soup.find_all('a', class_ = 'sr_item_photo_link sr_hotel_preview_track'):
			hotelLink = 'https://www.booking.com/' + hotelLink['href']
			
			# 呼叫函數取得各個hotel的資料
			i = getBookingHotel(hotelLink, i)

		# 頁面中 hotel 資料取得完成換下一頁 
		# 取得下一頁的連結網址
		try:
			nextPage = soup.find('li', class_ = 'bui-pagination__item bui-pagination__next-arrow').a['href']
		except Exception as e:
			print('Exception: %s' %(e))
		
		# 如果還有下一頁就繼續
		if nextPage is None:
			pass	
		else:
			i = getBookingHotelLink(nextPage, i)
	return i
	
def getAgodaHotel_switchwindow(browser):
	# 取得當前網址
	page_allHotel = browser.current_url	 
	print(page_allHotel)
	
	# 在總覽頁面取得各個 hotel 的網址
	soup = BeautifulSoup(browser.page_source, 'html5lib')

	i = 0
	while i < 100:
		# 點入個別 hotel 網頁
		browser.find_element(By.CSS_SELECTOR, ".PropertyCard__HotelName:nth-child(%d)" %i).click()
		time.sleep(5)
		
		# 將當前視窗改為點入後的新視窗
		handles = browser.window_handles
		browser.switch_to.window(handles[1])
		
		# 取得當前新視窗網址
		url = browser.current_url 
		print(url)
		
		# 取得 hotel 名稱與地址
		soup = BeautifulSoup(browser.page_source, 'html.parser')
		name = soup.find('h1', class_ = 'HeaderCerebrum__Name')
		addr = soup.find('div', class_ = 'HeaderCerebrum__Location').find('span')
		print(name.text, addr.text)
		
		# 頁面拉到最下方
		browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
		time.sleep(2)
		
		# 取得頁面高度
		page_height = browser.get_window_position().get('y')
		print(page_height)
		
		# 頁面拉回最上方
		browser.execute_script("window.scrollTo(0,0);")
		i += 1
	
def getAgodaHotel(browser, i):
	#print(page_allHotel)
	time.sleep(5)

	# 往下捲動讀取資料
	for x in range(1,25):
		browser.execute_script('window.scrollTo(0, 800*%d);' %x)
		time.sleep(random.randint(1, 4))
	
	# 在總覽頁面取得各個 hotel 的網址
	soup = BeautifulSoup(browser.page_source, 'html5lib')

	# 設定第2個瀏覽器
	options = Options()
	# 取消網頁中的彈出視窗，避免妨礙網路爬蟲的執行
	options.add_argument("--disable-notifications")
	# 設定瀏覽器背景執行
	options.add_argument("--headless")
	browser_gethotel = webdriver.Chrome('./chromedriver', options=options)
	k = 1
	for hotel in soup.find_all('h3', class_ = 'PropertyCard__HotelName'):
		print(k, hotel.text)
		k += 1
	j = 1	
	for tag in soup.ol.find_all('li', class_ = "PropertyCard PropertyCardItem"):
		hotelLink = 'https://www.agoda.com'+tag.find('a')['href']	
		print(j, hotelLink)
		j += 1
	#browser.find_element_by_link_text(hotel.text).click()
	
	
	# 取得各 hotel 網址抓取資料並對 hotel 計數
	print("取得各 hotel 網址")
	try:
		for i in range (1, 100):
			browser.find_element(By.CSS_SELECTOR, ".PropertyCard__HotelName:nth-child(%d)" %i).click()
			time.sleep(2)
			# 獲取當前視窗控制代碼（視窗A）
			handle = browser.current_window_handle		
			# 獲取當前所有視窗控制代碼（視窗A、B）
			handles = browser.window_handles
			# 對視窗進行遍歷
			for newhandle in handles:
				# 篩選新開啟的視窗B
				if newhandle!=handle:
				# 切換到新開啟的視窗B
					browser.switch_to.window(newhandle)		
					# 解析頁面以尋找名稱與地址
					soup = BeautifulSoup(browser.page_source, 'html5lib')
					
					# 取得名稱
					hotel_name = soup.find('div', class_ = 'HeaderCerebrum').find('h1', class_ = 'HeaderCerebrum__Name').text
					# 取得地址
					hotel_addr = soup.find('div', class_ = 'HeaderCerebrum__Location').find('span').text
					# 寫入檔案
					writeCsv(i, hotel_name, hotel_addr, 'agoda')
					print(i, hotel_name, hotel_addr)
					#browser.switch_to.window(vars["root"])
					time.sleep(2)
					# 關閉當前視窗B
					browser.close()
					#切換回視窗A
					browser.switch_to.window(handles[0]) 
					time.sleep(2)
	except:
		pass
	
	for tag in soup.ol.find_all('li', class_ = "PropertyCard PropertyCardItem"):
		hotelLink = 'https://www.agoda.com'+tag.find('a')['href']
		#print(hotelLink)
		# 前往要爬取的網頁網址
		browser_gethotel.get(hotelLink)
		
		# 隨意捲動網頁
		for x in range(3):
			browser_gethotel.execute_script('window.scrollTo(0, %d*%d);' %(random.randint(3,8), random.randint(500,2000)))
			time.sleep(random.randint(2,3))
		
		# 解析頁面以尋找名稱與地址
		soup2 = BeautifulSoup(browser_gethotel.page_source, 'html5lib')
		
		# 取得名稱
		hotel_name = soup2.find('div', class_ = 'HeaderCerebrum').find('h1', class_ = 'HeaderCerebrum__Name').text
		# 取得地址
		hotel_addr = soup2.find('div', class_ = 'HeaderCerebrum__Location').find('span').text
		# 寫入檔案
		writeCsv(i, hotel_name, hotel_addr, 'agoda')
		print(i, hotel_name, hotel_addr)
		
		i += 1

	# 結束browser_gethotel
	browser_gethotel.quit()
	
	# browser點選下一頁
	i = click_nextPage(browser, i)
	
	return i
	
	
def click_nextPage(browser, i):
	# browser跳到browser_gethotel搜尋的頁面
	
	# 當前頁往下捲以尋找下一頁的按鈕
	for x in range(12):
		browser.execute_script('window.scrollTo(0, %d*3000);' %x)
		time.sleep(random.randint(1, 3))
	
	# 尋找下一頁的按鈕
	try:
		element = browser.find_element(By.ID, "paginationNext")

	# 發生了NoSuchElementException異常，說明頁面中未找到該元素
	except NoSuchElementException as e:
		# 打印異常信息
		print(e)
		# 如果找不到到下一頁的按鈕就再讀取一次網頁然後往下拉
		browser.get(page_allHotel)
	else:
		# 沒有發生異常，表示在頁面中找到了該元素，點擊下一頁
		browser.find_element(By.ID, "paginationNext").click()
		print("next page")
		time.sleep(5)
		# 呼叫 getAgodaHotel 繼續抓資料
		i = getAgodaHotel(browser, i)

	return i


def getAgodaHotelLink(url, hand):
	options = Options()
	
	# 取消網頁中的彈出視窗，避免妨礙網路爬蟲的執行
	options.add_argument("--disable-notifications")
	# 設定瀏覽器背景執行
	#options.add_argument("--headless")

	# 建立webdriver物件，傳入下載的「瀏覽器驅動程式路徑」及「瀏覽器設定(chrome_options)」
	# 其中的「瀏覽器驅動程式路徑」一定要傳入，而「瀏覽器設定(chrome_options)」則選擇性視情況傳入	 
	browser = webdriver.Chrome('./chromedriver', options=options)
	#browser = webdriver.Firefox('./geckodriver', options=options)
	# 前往 Agoda 高雄
	browser.get(url)
	time.sleep(10)	
	
	# 取得Agoda資料
	getAgodaHotel(browser, 1)
	#getAgodaHotel_switchwindow(browser)
	# 關閉瀏覽器
	browser.quit()
		
	
booking_kaohsiung = ['https://www.booking.com/searchresults.zh-tw.html?label=gen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuALDqcP8BcACAdICJDlkNTE4YzVjLTA5NzEtNGRlMy1hYjliLTEyYWVjM2U0MjEzONgCBeACAQ&sid=d2e34ad2caabd31dbf3be45b0ed5b714&sb=1&src=searchresults&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Fsearchresults.zh-tw.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuALDqcP8BcACAdICJDlkNTE4YzVjLTA5NzEtNGRlMy1hYjliLTEyYWVjM2U0MjEzONgCBeACAQ%3Bsid%3Dd2e34ad2caabd31dbf3be45b0ed5b714%3Btmpl%3Dsearchresults%3Bac_click_type%3Db%3Bac_position%3D0%3Bcity%3D-2166199%3Bclass_interval%3D1%3Bdest_id%3D-3414440%3Bdest_type%3Dcity%3Bdtdisc%3D0%3Bfrom_sf%3D1%3Bgroup_adults%3D2%3Bgroup_children%3D0%3Biata%3DBKK%3Binac%3D0%3Bindex_postcard%3D0%3Blabel_click%3Dundef%3Bno_rooms%3D1%3Boffset%3D0%3Bpostcard%3D0%3Braw_dest_type%3Dcity%3Broom1%3DA%252CA%3Bsb_price_type%3Dtotal%3Bsearch_selected%3D1%3Bshw_aparth%3D1%3Bslp_r_match%3D0%3Bsrc%3Dsearchresults%3Bsrc_elem%3Dsb%3Bsrpvid%3Df92004acc0cb001c%3Bss%3D%25E6%259B%25BC%25E8%25B0%25B7%252C%2520%25E6%259B%25BC%25E8%25B0%25B7%252C%2520%25E6%25B3%25B0%25E5%259C%258B%3Bss_all%3D0%3Bss_raw%3D%25E3%2584%2587%3Bssb%3Dempty%3Bsshis%3D0%3Bssne%3D%25E8%25B1%2590%25E6%25B2%2599%25E7%2588%25BE%3Bssne_untouched%3D%25E8%25B1%2590%25E6%25B2%2599%25E7%2588%25BE%3Btop_ufis%3D1%26%3B&ss=%E7%BE%8E%E6%BF%83%E5%8D%80%2C+%E9%AB%98%E9%9B%84%E5%9C%B0%E5%8D%80%2C+%E8%87%BA%E7%81%A3&is_ski_area=&ssne=%E6%9B%BC%E8%B0%B7&ssne_untouched=%E6%9B%BC%E8%B0%B7&city=-3414440&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&from_sf=1&ss_raw=%E7%BE%8E%E6%BF%83+%E9%AB%98%E9%9B%84&ac_position=1&ac_langcode=xt&ac_click_type=b&dest_id=-2634181&dest_type=city&place_id_lat=22.900801&place_id_lon=120.542999&search_pageview_id=f92004acc0cb001c&search_selected=true&search_pageview_id=f92004acc0cb001c&ac_suggestion_list_length=5&ac_suggestion_theme_list_length=0',
					 'https://www.booking.com/searchresults.zh-tw.html?label=gen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuALDqcP8BcACAdICJDlkNTE4YzVjLTA5NzEtNGRlMy1hYjliLTEyYWVjM2U0MjEzONgCBeACAQ&sid=d2e34ad2caabd31dbf3be45b0ed5b714&sb=1&src=searchresults&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Fsearchresults.zh-tw.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuALDqcP8BcACAdICJDlkNTE4YzVjLTA5NzEtNGRlMy1hYjliLTEyYWVjM2U0MjEzONgCBeACAQ%3Bsid%3Dd2e34ad2caabd31dbf3be45b0ed5b714%3Btmpl%3Dsearchresults%3Bac_click_type%3Dg%3Bclass_interval%3D1%3Bdtdisc%3D0%3Bfrom_sf%3D1%3Bgroup_adults%3D2%3Bgroup_children%3D0%3Binac%3D0%3Bindex_postcard%3D0%3Blabel_click%3Dundef%3Bno_rooms%3D1%3Boffset%3D0%3Bplace_id%3DChIJi4gWi8sNbjQRZgVbWCT-c1o%3Bplace_id_lat%3D22.8016472%3Bplace_id_lon%3D120.2858846%3Bpostcard%3D0%3Braw_dest_type%3Dregion%3Broom1%3DA%252CA%3Bsb_price_type%3Dtotal%3Bsearch_selected%3D1%3Bshw_aparth%3D1%3Bslp_r_match%3D0%3Bsrc%3Dsearchresults%3Bsrc_elem%3Dsb%3Bsrpvid%3Db6d5059eefda0127%3Bss%3D%25E5%258F%25B0%25E7%2581%25A3%2520Kaohsiung%2520City%252C%2520%25E5%25B2%25A1%25E5%25B1%25B1%3Bss_all%3D0%3Bss_raw%3D%25E5%258F%25B0%25E7%2581%25A3%2520%25E5%25B2%25A1%25E5%25B1%25B1%3Bssb%3Dempty%3Bsshis%3D0%3Bssne%3D%25E5%25B2%25A1%25E5%25B1%25B1%3Bssne_untouched%3D%25E5%25B2%25A1%25E5%25B1%25B1%3Btop_ufis%3D1%26%3B&ss=%E7%94%B0%E5%AF%AE%E5%8D%80%2C+%E9%AB%98%E9%9B%84%E5%9C%B0%E5%8D%80%2C+%E8%87%BA%E7%81%A3&is_ski_area=0&ssne=%E5%8F%B0%E7%81%A3+Kaohsiung+City%2C+%E5%B2%A1%E5%B1%B1&ssne_untouched=%E5%8F%B0%E7%81%A3+Kaohsiung+City%2C+%E5%B2%A1%E5%B1%B1&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&from_sf=1&ac_position=0&ac_langcode=xt&ac_click_type=b&dest_id=-2638805&dest_type=city&place_id_lat=22.8333&place_id_lon=120.400002&search_pageview_id=b6d5059eefda0127&search_selected=true&ss_raw=%E7%94%B0%E5%AF%AE',
					 'https://www.booking.com/searchresults.zh-tw.html?label=gen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKdpp78BcACAdICJGQxNzUxYmY5LThjZDMtNDlhNS05NWUzLWQ0NzA4Yjg1ZTRlN9gCBeACAQ&sid=91e841923acc46ce764795397a35b949&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.zh-tw.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKdpp78BcACAdICJGQxNzUxYmY5LThjZDMtNDlhNS05NWUzLWQ0NzA4Yjg1ZTRlN9gCBeACAQ%3Bsid%3D91e841923acc46ce764795397a35b949%3Bsb_price_type%3Dtotal%26%3B&ss=%E9%AB%98%E9%9B%84%2C+%E5%8F%B0%E6%B9%BE&is_ski_area=&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&dest_id=-2632378&dest_type=city&search_pageview_id=70cb010efe5e00a5&search_selected=true&is_popular_nearby=1'
					]
agoda_kaohsiung = 'https://www.agoda.com/zh-tw/search?asq=NQVGXW6jsE3tbdY9S%2BqUCuD4bPdrJUFgeWG34Daq5CXRv0YPW16G3xc0oqW80Q8JwB34B8C5AY104QjjUCNELcJMH%2F%2BDjl36vWoQ3LWH6Jk5RMNY3o1v63%2BPQI8ngQ3vC2IQVGwjWisHJHwdUYn88eASvbStbZsnqlljKJ7GBBgP1t17hvYe9spGyIHfXx76CpAzJy%2BIPcIhZIlXClDyytoNXpDh7M%2FFMrm0YlxlGwg%3D&city=756&cid=1844104&tick=637387316265&languageId=20&userId=95617a16-fe82-48e3-8752-43e76f3a67b9&sessionId=uoj0pa5wtvucvlrnirbmsdiw&pageTypeId=1&origin=TW&locale=zh-TW&aid=130589&currencyCode=TWD&htmlLanguage=zh-tw&cultureInfoName=zh-TW&ckuid=95617a16-fe82-48e3-8752-43e76f3a67b9&prid=0&checkIn=2020-10-28&checkOut=2020-10-29&rooms=1&adults=2&children=0&priceCur=TWD&los=1&textToSearch=%E9%AB%98%E9%9B%84%E5%B8%82&travellerType=1&familyMode=off&productType=-1'

if __name__ == '__main__':
    print(time.ctime())
	'''
	# 連結 booking.com 高雄取得頁面
	i = 1
	for booking_link in booking_kaohsiung:
		i = getBookingHotelLink(booking_link, i)
	
	# 連結 agoda 高雄取得頁面
	'''
	#choice = input("(任意鍵)全自動搜尋agoda(失敗率高)\n(h)半自動搜尋agoda：")
	#if choice == 'h':
	#	agoda_kaohsiung = input("請輸入要擷取的agoda資料頁面網址：")
	
	choice = None
	getAgodaHotelLink(agoda_kaohsiung, choice)
	print(time.ctime())
