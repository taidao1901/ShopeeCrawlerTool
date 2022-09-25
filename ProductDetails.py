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
def GetProductData(url:str) -> dict:
    
    def process_browser_log_entry(entry):
        response = json.loads(entry['message'])['message']
        return response
    data=[]
    driver = CreateService()
    try:
        driver.get(f"{url}")
        time.sleep(10)
        '''Test Bypass
        try:
            actions = ActionChains(driver)
            sliderContainer = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]')
            slider = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div')
            for x in range(10000):
                actions.move_to_element(slider).click_and_hold().move_by_offset(x, 0).release().perform()
                time.sleep(0.1)
        except:
            print("Sai đâu đó!")
        actions = ActionChains(driver)
        for x in range(10000):
            # if not check_exists_by_xpath(driver, xpath='/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div'):
            #     break
            try:
                slider = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div')
                sliderContainer = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]')
                # actions.move_to_element(slider).click_and_hold().move_by_offset(sliderContainer.size['width'], 0).release().perform()
                actions.move_to_element(slider).click_and_hold().move_by_offset(236, 0).release().perform()
                time.sleep(0.5)
            except:
                continue'''
        browser_log = driver.get_log('performance') 
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.response' in event['method']]
    except Exception() as e:
        print("Không vào được links")
        print(e)
        return data
    for i in range(len(events)):
        try:
            if  "https://shopee.vn/api/v4/item/get?itemid" in events[i]["params"]["response"]["url"]:
                response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': events[i]["params"]["requestId"]})
                data = (json.loads(response['body']))['data']
        except:
            pass
    driver.execute_script("window.stop();")
    return data
def GetProductsDetails(data: dict) -> list:
    result = {}
    if data is not None:
        
        try:
            result={
                    'ItemId': data['itemid'],
                    "PriceMin": data["price_min"] if "price_min" in data.keys() else 0 ,
                    'PriceMax': data['price_max']if "price_max" in data.keys() else 0 , 
                    "Status": data["status"] if "status" in data.keys() else 1,
                    "Description": data["description"] if "description" in data.keys() else ""  ,
                    'Attributes': [{"Name":attr["name"],"Value": attr["value"],"Id":attr["id"]} for attr in data["attributes"]] if "attributes" in data.keys() else [] ,
                    'FetchedTime': datetime.timestamp(datetime.utcnow())
                }         
        except Exception as e:
            # logger.error(e)
            pass
    return result
data = GetProductData("https://shopee.vn/Qu%E1%BA%A7n-Black-Funoff-Short-Biker-Short-D%C3%A1ng-Ng%E1%BA%AFn-N%E1%BB%AF-N%C3%A2ng-M%C3%B4ng-M%C3%B9a-H%C3%A8-N%C4%83ng-%C4%90%E1%BB%99ng-i.267034657.13454004194?sp_atk=49122a6b-ebd1-4888-ac3c-7b816271e6f9&xptdk=49122a6b-ebd1-4888-ac3c-7b816271e6f9")
details = GetProductsDetails(data)
with open('productdetail.json', 'w', encoding='utf-8') as f:
    json.dump(details, f, ensure_ascii=False, indent=4)
