from asyncio import as_completed
import json
from sqlite3 import Row
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import concurrent.futures
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from seleniumwire import webdriver
from HelpTools.ReadCategories import Categories
from TinProxyService import GetProxyIP
import pandas as pd 

def CreateService(patient = 0):
    if patient >= 5:
        print("Lỗi IP! Create Service đã khởi chạy 5 lần.")
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
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument(f'user-agent={userAgent}')
    chromeOptions.add_argument('--disable-blink-features=AutomationControlled')
    chromeOptions.add_argument("--incognito")
    chromeOptions.add_argument("--private")
    chromeOptions.add_argument('--disable-notifications')
    chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
    chromeOptions.add_experimental_option('useAutomationExtension', False)
    # Proxy
    result = GetProxyIP.GetProxyIps()
    '''result = {
    #     "proxyIp": "116.108.241.218:7001",
    #     "username": "YTRHGBuR",
    #     "password": "v5WXaTij"
    # }'''
    proxyIp = result["proxyIp"]
    if proxyIp == ":":
        return CreateService(patient + 1)
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

    
def GetProductData(url:str, patient = 0) -> dict:
    def process_browser_log_entry(entry):
        response = json.loads(entry['message'])['message']
        return response
    data=[]
    if url is not None:
        if patient >= 5:
            print(f"Không vào được link sau {patient} lần tải lại!")
            return data
        driver = CreateService()
        try:
            driver.get(f"{url}")
            time.sleep(10)
            browser_log = driver.get_log('performance')
            for entry in browser_log:
                event = process_browser_log_entry(entry)
                try:
                    if  "https://shopee.vn/api/v4/item/get?itemid" in event["params"]["response"]["url"]:
                        response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': event["params"]["requestId"]})
                        data = (json.loads(response['body']))['data']
                        if len(data)==0:
                            continue
                        break
                except:
                    pass

        except Exception() as e:
            driver.quit()
            print(f"Không vào được links page {url} lần {patient + 1}. Tải lại...")
            return GetProductData(url, patient + 1)
        driver.quit()
    return data

def GetProductDetails(data: dict) -> list:
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
def GetProductByCategory(categoryPath, coarseInfos):
    categoryProducts=pd.DataFrame()
    customerCategoryId = categoryPath.split(".")[-1]
    categoryProducts = coarseInfos[coarseInfos["CustomerCategoryId"]==int(customerCategoryId)]
    categoryProducts = categoryProducts.sort_values(by=['IsOfficialShop'], ascending=False)
    return categoryProducts
def CrawlFineGrainedByCategory(categoryProducts , categoryLink, maxWorkers= 12, maxProducts=0, step =100) ->list:
    ids = []
    log = {"CategoryLink": categoryLink}
    if categoryProducts.shape[0]>0:
        if maxProducts != 0:
            categoryProducts= categoryProducts.head(maxProducts)
        productUrls = categoryProducts["ProductURL"].tolist()
        lenProductUrls = len(productUrls)
        print(lenProductUrls)
        for start in range (0,lenProductUrls,step):
            futures =[]
            result = []
            end = (start+step) if (start+step)< lenProductUrls else lenProductUrls
            currentProductUrls= productUrls[start:end]
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers= maxWorkers) as executor:
                    for productUrl in currentProductUrls:
                        futures.append(executor.submit(GetProductData, productUrl))
                for future in concurrent.futures.as_completed(futures):
                    try:
                        data = future.result()
                        if data is not None:
                            fineGrained  = GetProductDetails(data)
                            if fineGrained is not None:
                                result.append(fineGrained)
                                ids.append(fineGrained["ItemId"])
                    except:
                        pass
            except:
                pass
            with open('FineGrainedProductInfos.json', 'r+', encoding='utf-8') as f:
                data = json.loads(f.read())
                f.seek(0)
                f.truncate()
                data.extend(result)
                json.dump(data, f, ensure_ascii=False, indent=4)
    log["IsComplete"] = 1 if len(ids) >= 1500 else 0
    log["ProductQuantity"] = len(ids)
    log["ProductsAreCrawled"] = ids
    log["CrawlTime"]= datetime.now()
    return log

def SaveLog(log,csvfilePath =r"tmp/FineGrainedInfos.csv",jsonfilePath = r"tmp/FineGrainedInfos.json"):
    logs = pd.read_csv(csvfilePath)
    try:
        logs= logs.drop(logs[logs.CategoryLink == log["CategoryLink"]].index)
    except: 
        pass
    logs = pd.concat([logs,pd.DataFrame([log])],ignore_index=True,axis=0)
    logs.to_csv(csvfilePath, index= False)
    logs.to_json(jsonfilePath, orient= "records", indent=4, force_ascii = False)

if __name__=="__main__":
    # data = GetProductData("https://shopee.vn/Qu%E1%BA%A7n-Black-Funoff-Short-Biker-Short-D%C3%A1ng-Ng%E1%BA%AFn-N%E1%BB%AF-N%C3%A2ng-M%C3%B4ng-M%C3%B9a-H%C3%A8-N%C4%83ng-%C4%90%E1%BB%99ng-i.267034657.13454004194?sp_atk=49122a6b-ebd1-4888-ac3c-7b816271e6f9&xptdk=49122a6b-ebd1-4888-ac3c-7b816271e6f9")
    # details = GetProductsDetails(data)
    # with open('productdetail.json', 'w', encoding='utf-8') as f:
    #     json.dump(details, f, ensure_ascii=False, indent=4)
    coarseInfos = pd.read_json("CoarseProductInfos.json")
    #print(coarseInfos.head())
    #result =GetProductUrls("https://shopee.vn/Áo-Khoác-cat.11035567.11035568.11035570", coarseInfos)
    #result.to_json("CategoryProducs.json", indent=4,orient ="records", force_ascii = False)
    crawlByCategoryLog = pd.read_csv(r'tmp/CrawlByCategory.csv')
    fineGrainedInfos = pd.read_csv(r'tmp/FineGrainedInfos.csv')
    fineGrainedInfos  =fineGrainedInfos["CategoryLink"].tolist()

    for index, row in crawlByCategoryLog.iterrows():
        try:
            if row['CategoryLink'] not in fineGrainedInfos:
                categoryProducts = GetProductByCategory(categoryPath=row["CategoryLink"],coarseInfos=coarseInfos)
                log = CrawlFineGrainedByCategory(categoryProducts,row["CategoryLink"])
                SaveLog(log)
        except:
            pass
