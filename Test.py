import requests
import pickle
from fake_useragent import UserAgent
ua = UserAgent()
header = {
    'User-Agent':str(ua.chrome),
    'x-Requested-With': 'XMLHttpRequest'
}
def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

#save cookies
r = requests.get('https://shopee.vn/product/3064018/399188377/')
save_cookies(r.cookies, 'cookies.pkl')
print(r.cookies)
#load cookies and do a request
url ='https://shopee.vn/api/v4/item/get?itemid=399188377&shopid=3064018'
res=requests.get( url ,headers = header, cookies=load_cookies('cookies.pkl'))
print(res.content)