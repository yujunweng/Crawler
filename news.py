import requests
from bs4 import BeautifulSoup



print('自由今日焦點')
dom = requests.get('https://www.ltn.com.tw/').text
soup = BeautifulSoup(dom, 'html5lib')
today = soup.find('div', class_ = 'datebox').p.text.strip()
print(today)

title = soup.find('div', class_ = 'swiper-slide').a.b.text.strip()
print(title)



'''	
print('---------------------')

print('蘋果今日焦點')
dom = requests.get('http://www.appledaily.com.tw/appledaily/hotdaily/headline').text
soup = BeautifulSoup(dom, 'html5lib')

for ele in soup.find('ul', 'all').find_all('li'):
	print(
		ele.find('div', 'aht_title_num').text,
		ele.find('div', 'aht_title').text,
		ele.find('div', 'aht_pv_num').text	
		)
'''		