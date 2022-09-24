import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime
import concurrent.futures
def CreateService():
    service = Service(executable_path=ChromeDriverManager().install())
    caps = DesiredCapabilities.CHROME   
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps,service = service)
    return driver

def GetItems(url:str, page: int) -> dict:
    
    def process_browser_log_entry(entry):
        response = json.loads(entry['message'])['message']
        return response
    items=[]
    driver = CreateService()
    try:
        driver.get(f"{url}?page={page}")
        time.sleep(10)
        browser_log = driver.get_log('performance') 
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.response' in event['method']]
    except Exception() as e:
        print("Không vào được links")
        print(e)
        return items
    for i in range(len(events)):
        try:
            if  "https://shopee.vn/api/v4/search/search_items?by=relevancy" in events[i]["params"]["response"]["url"]:
                response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': events[i]["params"]["requestId"]})
                items = (json.loads(response['body'])["items"])
        except:
            pass
    driver.execute_script("window.stop();")
    return items
def GetProductsDetails(items: list,customerCategoryId: str) -> list:
    result = []
    for item in items:
        try:
            item =item["item_basic"]
            result.append(
                {
                    'ItemId': item['itemid'],
                    "ShopId": item["shopid"],
                    'Name': item['name'],
                    'Images': [f"https://cf.shopee.vn/file/{image}" for image in item['images']],
                    'ProductURL': f"https://shopee.vn/{item['name']}-i.{item['shopid']}.{item['itemid']}",
                    'CustomerCategoryId':customerCategoryId,
                    "SellerId":  item['catid'],
                    'LabelIds': item['label_ids'],
                    'Brand': item['brand'],
                    'Price': item['price'] if item['raw_discount'] == 0 else item['price_before_discount'],
                    'IsOfficialShop': item['is_official_shop'],
                    'FetchedTime': datetime.timestamp(datetime.utcnow()),
                    'Description':''
                }
            )
        except Exception as e:
            # logger.error(e)
            pass
    return result
def CrawlByCategory(url,customerCategoryId, pageQuantity: int, maxWorkers=2) -> list:
    futures =[]
    items = []
    with concurrent.futures.ThreadPoolExecutor(max_workers= maxWorkers) as executor:
        for page in range(pageQuantity):
            futures.append(executor.submit(GetItems,url,page))

    for future in concurrent.futures.as_completed(futures):
        items.extend(future.result())
    
    result = GetProductsDetails(items, customerCategoryId)
    return result

result = CrawlByCategory("https://shopee.vn/%C3%81o-Kho%C3%A1c-cat.11035567.11035568", '11035568', 8)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)