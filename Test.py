import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime

def GetResponse(url: str, page: int) -> dict:
    def process_browser_log_entry(entry):
        response = json.loads(entry['message'])['message']
        return response
    items=[]
    service = Service(executable_path=ChromeDriverManager().install())
    caps = DesiredCapabilities.CHROME   
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps,service = service)
    try:
        driver.get(f"{url}?page={page}")
        time.sleep(10)
        browser_log = driver.get_log('performance') 
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.response' in event['method']]
    except:
        print("Không vào được links")
        return items
    for i in range(len(events)):
        try:
            if  "https://shopee.vn/api/v4/search/search_items?by=relevancy" in events[i]["params"]["response"]["url"]:
                response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': events[i]["params"]["requestId"]})
                items = (json.loads(response['body'])["items"])
        except:
            pass
    return items
def GetProductsDetails(items,customerCategoryId):
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

items= GetResponse("https://shopee.vn/Vải-len-cat.11035639.11035713.11035717", 0)
result = GetProductsDetails(items, "11035717")
with open('items.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=4)
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)