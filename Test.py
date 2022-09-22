# import requests
# import http.cookiejar 
# import pickle
# from fake_useragent import UserAgent
# import browser_cookie3
# ua = UserAgent()
# header = {
#     'User-Agent':str(ua.chrome),
#     'x-Requested-With': 'XMLHttpRequest'
# }
# cj = http.cookiejar.MozillaCookieJar('shopee.vn_cookies.txt')
# cj.load()
# def save_cookies(requests_cookiejar, filename):
#     with open(filename, 'wb') as f:
#         pickle.dump(requests_cookiejar, f)

# def load_cookies(filename):
#     with open(filename, 'rb') as f:
#         return pickle.load(f)

# #save cookies
# session = requests.Session()

# # cj = browser_cookie3.chrome(domain_name='shopee.vn')
# # r = session.get('https://shopee.vn/product/3064018/399188377/')
# # cookies= r.cookies
# # print(r.cookies.get_dict())
# # #load cookies and do a request

# # for cookie in cj:
# #    print (cookie.name, cookie.value, cookie.domain)
# for cookie in cj:
#    print (cookie.name, cookie.value, cookie.domain)
# url ='https://shopee.vn/api/v4/item/get?itemid=399188377&shopid=3064018'
# res= session.get( url ,headers = header, cookies=cj)
# print(res.content)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()))
driver.get("https://shopee.vn/Th%E1%BB%9Di-Trang-Nam-cat.11035567")
print(driver.get_cookies())
driver.get("https://shopee.vn/api/v4/item/get?itemid=399188377&shopid=3064018")