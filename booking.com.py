import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time
import os
import re
import time
import json

def getHotel(link_to_hotel, i):	# 傳入參數為 booking.com 的 hotel 連結網址
	# 在各個 hotel 頁面取得名稱與地址
	resp_hotel = requests.get(link_to_hotel)
	if resp_hotel.status_code == 200:
		soup_hotel = BeautifulSoup(resp_hotel.text, 'html.parser')
		for jsoncontent in soup_hotel.find_all('script', type = 'application/ld+json'):
			#print(jsoncontent)
			jsoncontent = str(jsoncontent).strip('}')
			if jsoncontent is not None:
				print(i, end = ' ')
				
				# 取得名稱
				if jsoncontent.find("name") > -1:
					name_start = str(jsoncontent).find("name")+9
					name_end = jsoncontent.find('"', name_start)
					name = jsoncontent[name_start:name_end].strip()
					print(name, end = ' ')
				
				# 取得地址 
				if jsoncontent.find("streetAddress") > -1:
					addr_start = str(jsoncontent).find("streetAddress")+18
					addr_end = jsoncontent.find('"', addr_start)
					addr = jsoncontent[addr_start:addr_end].strip().replace('\\t', '')
					print(addr)
			i += 1	
	return i 		

def getHotelLink(page_allHotel, i):
	# 在總覽頁面取得各個 hotel 的網址
	resp = requests.get(page_allHotel)
	if resp.status_code == 200:
		
		# 解析頁面取得各 hotel 連結網址
		soup = BeautifulSoup(resp.text, 'html.parser')
		for hotelLink in soup.find_all('a', class_ = 'sr_item_photo_link sr_hotel_preview_track'):
			hotelLink = 'https://www.booking.com/' + hotelLink['href']
			
			# 呼叫函數取得各個hotel的資料
			i = getHotel(hotelLink, i)

		# 頁面中 hotel 資料取得完成換下一頁 
		# 取得下一頁的連結網址
		try:
			nextPage = soup.find('li', class_ = 'bui-pagination__item bui-pagination__next-arrow').a['href']
		except Exception as e:
			print('Exception: %s' %(e))
		
		# 如果還有下一頁就繼續
		while nextPage:
			getHotelLink(nextPage, i)

booking_kaohsiung = 'https://www.booking.com/searchresults.zh-tw.html?label=gen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKdpp78BcACAdICJGQxNzUxYmY5LThjZDMtNDlhNS05NWUzLWQ0NzA4Yjg1ZTRlN9gCBeACAQ&sid=91e841923acc46ce764795397a35b949&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.zh-tw.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIMFgEaOcBiAEBmAEwuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKdpp78BcACAdICJGQxNzUxYmY5LThjZDMtNDlhNS05NWUzLWQ0NzA4Yjg1ZTRlN9gCBeACAQ%3Bsid%3D91e841923acc46ce764795397a35b949%3Bsb_price_type%3Dtotal%26%3B&ss=%E9%AB%98%E9%9B%84%2C+%E5%8F%B0%E6%B9%BE&is_ski_area=&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&dest_id=-2632378&dest_type=city&search_pageview_id=70cb010efe5e00a5&search_selected=true&is_popular_nearby=1'

if __name__ == '__main__':
	# 連結booking.com 高雄取得頁面
	getHotelLink(booking_kaohsiung, 1)
	

	
	#for hotelLink in soup.find_all(sr_item_photo_link sr_hotel_preview_track, {'href':re.compile('/hotel/tw.*')}):