import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time
import traceback
import collections
import re
import json


def get_web_page(url):
	resp = requests.get(url = url)
	if resp.status_code != 200:
		print('Invalid url:', resp.url)
		return None
	else:
		return resp.text

def get_movie_id(url):
	#e.g., 'https://movies.yahoo.com.tw/movieinfo_main/%E6%AD%BB%E4%BE%8D2-deadpool-2-7820.html'
	try:
		movie_id = url.split('.html')[0].split('-')[-1]
	except:
		movie_id = url
	return movie_id	
	
def get_date(date_str):
		pattern = '\d+-\d+-\d+'
		match = re.search(pattern, date_str)
		if match is None:
			return date_str
		else:
			return match.group(0)

def get_movies(dom):
	soup = BeautifulSoup(dom, 'html5lib')
	movies = []
	rows = soup.find_all('div', 'release_info_text')
	for row in rows:
		movie = dict()
		movie['expectation'] = row.find('div', 'leveltext').span.text.strip()
		movie['ch_name'] = row.find('div', 'release_movie_name').a.text.strip()
		movie['eng_name'] = row.find('div', 'release_movie_name').find('div', 'en').a.text.strip()
		movie['movie_id'] = get_movie_id(row.find('div', 'release_movie_name').a['href'])
		movie['poster_url'] = row.parent.find_previous_sibling('div', 'release_foto').a.img['src']
		movie['release_date'] = get_date(row.find('div', 'release_movie_time').text)
		movie['intro'] = row.find('div', 'release_text').text.replace(u'詳全文', '').strip()
		trailer_a = row.find_next_sibling('div', 'release_btn color_btnbox').find_all('a')[1]
		movie['trailer_url'] = trailer_a['href'] if 'href' in trailer_a.attrs else ''
		movies.append(movie)
	return movies


Y_MOVIE_URL = 'https://tw.movies.yahoo.com/movie_thisweek.html'

page = get_web_page(Y_MOVIE_URL)
if page:
	movies = get_movies(page)
	for movie in movies:
		print(movie)
	
	with open('movie.json', 'w', encoding = 'UTF-8') as f:
		json.dump(movies, f, indent=2, sort_keys=True, ensure_ascii=False)