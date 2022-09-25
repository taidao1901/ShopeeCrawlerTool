import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime
import concurrent.futures
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from selenium_stealth import stealth
import undetected_chromedriver as uc
from selenium.webdriver.common.proxy import Proxy, ProxyType

def CheckExistsByXpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def CreateService():
    service = Service(executable_path=ChromeDriverManager().install())
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    # Get random user agent
    softwareNames = [SoftwareName.CHROME.value]
    operatingSystems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    userAgentRotator = UserAgent(software_names=softwareNames, operating_systems=operatingSystems, limit=100)
    userAgent = userAgentRotator.get_random_user_agent()
    Options
    chromeOptions = Options()
    chromeOptions.add_argument(f'user-agent={userAgent}')
    chromeOptions.add_argument('--disable-blink-features=AutomationControlled')
    chromeOptions.add_argument("--incognito")
    chromeOptions.add_argument("--private")
    chromeOptions.add_argument('--disable-notifications')
    chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
    chromeOptions.add_experimental_option('useAutomationExtension', False)
    # Proxy
    # PROXY = "116.109.77.129:9009"
    # prox = Proxy()
    # prox.proxy_type = ProxyType.MANUAL
    # prox.auto_detect = False
    # prox.http_proxy = PROXY
    # prox.ssl_proxy = PROXY
    # prox.add_to_capabilities(caps)
    driver = webdriver.Chrome(desired_capabilities=caps,service = service, options=chromeOptions)
    # Bypass captcha
    # stealth(driver,
    #     languages=["en-US", "en"],
    #     vendor="Google Inc.",
    #     platform="Win32",
    #     webgl_vendor="Intel Inc.",
    #     renderer="Intel Iris OpenGL Engine",
    #     fix_hairline=True,
    #     )
    # driver = uc.Chrome(options=chromeOptions)
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
        # Test Bypass
        # try:
        #     actions = ActionChains(driver)
        #     sliderContainer = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]')
        #     slider = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div')
        #     for x in range(10000):
        #         actions.move_to_element(slider).click_and_hold().move_by_offset(x, 0).release().perform()
        #         time.sleep(0.1)
        # except:
        #     print("Sai đâu đó!")
        # actions = ActionChains(driver)
        # for x in range(10000):
        #     # if not check_exists_by_xpath(driver, xpath='/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div'):
        #     #     break
        #     try:
        #         slider = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div')
        #         sliderContainer = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]')
        #         # actions.move_to_element(slider).click_and_hold().move_by_offset(sliderContainer.size['width'], 0).release().perform()
        #         actions.move_to_element(slider).click_and_hold().move_by_offset(236, 0).release().perform()
        #         time.sleep(0.5)
        #     except:
        #         continue
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
                print(items)
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

def CrawlByCategory(url, customerCategoryId, pageQuantity: int, maxWorkers=2) -> list:
    futures =[]
    items = []
    with concurrent.futures.ThreadPoolExecutor(max_workers= maxWorkers) as executor:
        for page in range(pageQuantity):
            futures.append(executor.submit(GetItems,url,page))

    for future in concurrent.futures.as_completed(futures):
        items.extend(future.result())
    
    result = GetProductsDetails(items, customerCategoryId)
    return result

if __name__=="__main__":
    result = CrawlByCategory("https://shopee.vn/%C3%81o-Kho%C3%A1c-cat.11035567.11035568", '11035568', 4)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)