def get_facebook():
	# 取消網頁中的彈出視窗，避免妨礙網路爬蟲的執行
	options = Options()
	options.add_argument("--disable-notifications")
	
	# 建立webdriver物件，傳入下載的「瀏覽器驅動程式路徑」及「瀏覽器設定(chrome_options)」
	# 其中的「瀏覽器驅動程式路徑」一定要傳入，而「瀏覽器設定(chrome_options)」則選擇性視情況傳入
	chrome = webdriver.Chrome('./chromedriver', chrome_options = options)
	
	# 前往要爬取的網頁網址
	chrome.get("https://www.facebook.com/")
	
	# 建立「電子郵件」及「密碼」的物件
	email = chrome.find_element_by_id("email")
	password = chrome.find_element_by_id("pass")
	
	# 模擬使用者輸入資料，利用submit()方法送出，進行登入
	email.send_keys('example@gmail.com')
	password.send_keys('******')
	password.submit()
	
	# 讓網頁利用這段時間載入元素，再前往粉絲專頁，避免直接執行時，如果網頁還沒有載入完成，就會發生讀取不到所要爬取的元素或網頁卡住等例外情況
	time.sleep(3)
	chrome.get('https://www.facebook.com/learncodewithmike')
	
	for x in range(1, 4):
		chrome.execute_script("window.scrollTo(0, document.body.scrollHeight)")
		time.sleep(5)
	
	soup = BeautifulSoup(chrome.page_source, 'html.parser')
	
	
	titles = soup.find_all('span', {'class_': 'a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7'}) 
 	
	for title in titles:
		print(title.getText())
			
	# 關閉瀏覽器
	chrome.quit()