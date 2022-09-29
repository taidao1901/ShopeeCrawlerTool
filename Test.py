import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime
import concurrent.futures
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from seleniumwire import webdriver
from HelpTools.ReadCategories import Categories
from TinProxyService import GetProxyIP
import logging
import pandas as pd 

def CreateService():
    service = Service(executable_path=ChromeDriverManager().install())
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    # Get random user agent
    softwareNames = [SoftwareName.CHROME.value]
    operatingSystems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    userAgentRotator = UserAgent(software_names=softwareNames, operating_systems=operatingSystems, limit=100)
    userAgent = userAgentRotator.get_random_user_agent()
    # Options
    chromeOptions = Options()
    chromeOptions.add_argument(f'user-agent={userAgent}')
    chromeOptions.add_argument('--disable-blink-features=AutomationControlled')
    chromeOptions.add_argument("--incognito")
    chromeOptions.add_argument("--private")
    chromeOptions.add_argument('--disable-notifications')
    chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
    chromeOptions.add_experimental_option('useAutomationExtension', False)
    # Proxy
    result = GetProxyIP.GetProxyIps()
    # result = {
    #     "proxyIp": "116.109.19.55:10006",
    #     "username": "tmABbQHD",
    #     "password": "sQ0zgbj5"
    # }
    proxyIp = result["proxyIp"]
    username = result["username"]
    password = result["password"]
    options = {
        'disable_capture': True,
        'proxy': {
            'http': f'http://{username}:{password}@{proxyIp}', 
            'https': f'https://{username}:{password}@{proxyIp}',
            'no_proxy': 'localhost,127.0.0.1' # excludes
            }
    }
    driver = webdriver.Chrome(desired_capabilities=caps,service = service, options=chromeOptions, seleniumwire_options=options)
    return driver

def GetItems(url:str, page: int, patient = 0) -> dict:

    def process_browser_log_entry(entry):
        response = json.loads(entry['message'])['message']
        return response
    items=[]
    if patient >= 5:
        print(f"Không vào được link sau {patient} lần tải lại!")
        return items
    driver = CreateService()
    try:
        time.sleep(3)
        driver.get(f"{url}?page={page}")
        time.sleep(10)
        browser_log = driver.get_log('performance')
        for entry in browser_log:
            event = process_browser_log_entry(entry)
            try:
                if  "https://shopee.vn/api/v4/search/search_items?by=relevancy" in event["params"]["response"]["url"]:
                    response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': event["params"]["requestId"]})
                    items = (json.loads(response['body'])["items"])
                    break
            except:
                pass
        # events = [process_browser_log_entry(entry) for entry in browser_log]
        # events = [event for event in events if 'Network.response' in event['method']]
    # except Exception() as e:
    except:
        driver.close()
        print(f"###################Không vào được links page {page}. Tải lại...")
        return GetItems(url, page, patient + 1)

    driver.execute_script("window.stop();")
    return items, page

def GetProductsDetails(items: list,customerCategoryId: str) -> list:
    result = []
    if len(items)>0:
        for item in items:
            try:
                item = item["item_basic"]
                result.append(
                    {
                        'ItemId': item['itemid'],
                        "ShopId": item["shopid"],
                        'Name': item['name'],
                        'Images': [f"https://cf.shopee.vn/file/{image}" for image in item['images']],
                        'ProductURL': f"https://shopee.vn/product/{item['shopid']}/{item['itemid']}",
                        'CustomerCategoryId':customerCategoryId,
                        "SellerId":  item['catid'],
                        # 'LabelIds': item['label_ids'],
                        'Brand': item['brand'],
                        'Price': item['price'] if item['raw_discount'] == 0 else item['price_before_discount'],
                        'IsOfficialShop': item['is_official_shop'],
                        'FetchedTime': datetime.now().timestamp(),
                    }
                )
            except Exception as e:
                # logger.error(e)
                pass
    return result

def CrawlByCategory(url, pageRange = (0,20), maxWorkers=8) -> list:
    futures =[]
    items = []
    pages = []
    log = {"CategoryLink": url}
    with concurrent.futures.ThreadPoolExecutor(max_workers= maxWorkers) as executor:
        for page in range(pageRange[0],pageRange[1]):
            futures.append(executor.submit(GetItems,url,page))
    customerCategoryId = url.split(".")[-1]
    for future in concurrent.futures.as_completed(futures):
        res, page = future.result()
        if len(res)>0:
            pages.append(page)
            items.extend(res)
    log["IsCompelete"] = 1 if len(items)>=2000 else 0
    log["ProductQuantity"] = len(items)
    log["PagesAreCrawled"] = pages
    log["CrawlTime"] = datetime.now()
    result = GetProductsDetails(items, customerCategoryId)
    return result,log
def SaveLog(log,filePath =r"tmp\CrawlByCategory.csv"):
    logs = pd.read_csv(filePath)
    try:
        logs= logs.drop(logs[logs.CategoryLink == log["CategoryLink"]].index)
    except: 
        pass
    logs = pd.concat([logs,pd.DataFrame([log])],ignore_index=True,axis=0)
    logs.to_csv(filePath, index= False)
if __name__=="__main__":
    # https://httpbin.org/ip
    # result = CrawlByCategory("https://httpbin.org/ip", 16)
    logging.basicConfig(filename=r'tmp\CrawlByCategory.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s',datefmt='%H:%M:%S', level=logging.DEBUG)
    categories = Categories("Categories.json")
    allPaths =categories.GetAllPaths()
    # print(allPaths)
    result,log = CrawlByCategory(allPaths[0], (0,1))
    SaveLog(log)
    # print(result)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    # print(GetProxyIP.LoadApiKeyAndAllowIp())
    # print(GetProxyIP.GetProxyIps())
