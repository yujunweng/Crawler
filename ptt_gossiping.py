from bs4 import BeautifulSoup
import requests
import re
import os
import time
import json

def get_web_page(url):
	resp = requests.get(url = url, cookies = {'over18':'1'})	#告知server已回答過滿18歲的問題
	if resp.status_code != 200:
		print('Invalid url:', resp.url)
		return None
	else:
		return resp.text


def get_articles(dom, date):
	soup = BeautifulSoup(dom, 'html5lib')

	# 取得上一頁的連結
	paging_div = soup.find('div', 'btn-group btn-group-paging')
	pre_url = paging_div.find_all('a')[1]['href']
	
	articles = []	# 儲存取得的文章資料
	divs = soup.find_all('div', 'r-ent')
	
	for d in divs:
		if d.find('div', 'date').text.strip() == date:	# 發文日期正確
			# 取得推文數
			push_count = 0
			push_str = d.find('div', 'nrec').text
			if push_str:
				try:
					push_count = int(push_str)	# 轉換字串為數字
				except ValueError:
					# 若轉換失敗, 可能是 ' 爆 ' 或 'X1', 'X2', ....
					# 若不是, 不做任何事, push_count 保持為 0
					if push_str == '爆':
						push_count = 99
					elif push_str.startswith('X'):
						push_count = -10
			
			#取得文章連結及標題
			if d.find('a'):		# 有超連結, 表示文章存在, 未被刪除	
				href = d.find('a')['href']
				title = d.find('a').text
				author = d.find('div', 'author').text if d.find('div', 'author') else ''
				articles.append({
					'title': title,
					'href': href,
					'push_count': push_count,
					'author': author
				})
	return articles, pre_url				

PTT_URL = 'https://www.ptt.cc'

current_page = get_web_page(PTT_URL + '/bbs/Gossiping/index.html')
if current_page:
	articles = []	#全部的今日文章
	
	# 今天日期, 去掉開頭的 0 以符合 PTT 網站格式
	today = time.strftime("%m/%d").lstrip('0')
	
	# 目前頁面的今日文章
	current_articles, prev_url = get_articles(current_page, today)
	
	# 若目前頁面有今日文章則加入 articles, 並回到上一頁繼續尋找是否有今日文章
	while current_articles:
		articles += current_articles
		current_page = get_web_page(PTT_URL + prev_url)
		current_articles, prev_url = get_articles(current_page, today)
		
	# 儲存或處理文章資訊
	print('今天有', len(articles), '篇文章')
	threshold = 50
	print('熱門文章 (> %d 推 ):' %threshold)
	
	for a in articles:
		if int(a['push_count']) > threshold:
			print(a)
	
	with open('gossiping.json', 'w', encoding='UTF-8') as f:
		json.dump(articles, f, indent=2, sort_keys = True, ensure_ascii=False)