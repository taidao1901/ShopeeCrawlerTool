import requests
import random
import time
import pandas as pd

def LoadApiKeyAndAllowIp():
    # Load api key list
    with open("TinProxyService/ApiKeyList.txt", "r", encoding="UTF-8") as f:
        lstApiKey = [key.strip() for key in f.read().split("\n")]
    # Load Allow ip list
    with open("TinProxyService/AllowIpList.txt", "r", encoding="UTF-8") as f:
        lstAllowIp = [ip.strip() for ip in f.read().split("\n")]
    # Get random api key
    return random.choice(lstApiKey), lstAllowIp

def GetProxyIps(count=0):
    if count >= 20:
        print(f"Quá {count} lần request lấy proxy cho 1 request!")
        return {"proxyIp":":", "username": "", "password":""}
    # Load info
    apiKey, lstAllowIp = LoadApiKeyAndAllowIp()
    # Check status apiKey
    if not CheckRenewProxyPackage(apiKey=apiKey, renew=True):
        return GetProxyIps(count + 1)
    strAllowIp = ",".join(lstAllowIp)
    # Request to get proxy ip
    url = f"https://api.tinproxy.com/proxy/get-new-proxy?api_key={apiKey}&authen_ips={strAllowIp}&location=random"
    r = requests.get(url=url)
    print("Status code of request get proxy ip: " + str(r.status_code))
    # Check status request
    if r.status_code != 200:
        return GetProxyIps(count + 1)
    data = r.json()
    try:
        status = data["status"]
    except:
        GetProxyIps(count + 1)
    ###################################
    print(f"Proxy ip {data['data']['http_ipv4']} status: {status}")
    # Auto renew package
    if status not in ["active", "expired", "waiting"]:
        print(f"Proxy api key {apiKey} chưa active!")
        time.sleep(1)
        return GetProxyIps(count + 1)
    proxyIp = data["data"]["http_ipv4"]
    username = data["data"]["authentication"]["username"]
    password = data["data"]["authentication"]["password"]
    result = {"proxyIp":proxyIp, "username": username, "password":password}
    return result
        
def CheckRenewProxyPackage(apiKey, renew=False, time_=1):
    with open("TinProxyService/Token.txt", "r", encoding="UTF-8") as f:
        token = [token.strip() for token in f.read().split("\n")][0]
    url = f"https://api.tinproxy.com/user/get-list-proxy?token={token}&status=active,expired"
    r = requests.get(url)
    data = r.json()
    try:
        lstKey = data["data"]
    except:
        print("Token không hợp lệ!")
        return False
    for key in lstKey:
        ######################################
        # print(f"{key['api_key']} status: {key['status']}")
        if key["api_key"] == apiKey:
            print(f"{key['api_key']} status: {key['status']}")
            if key["status"] in ["active", "waiting"]:
                # print("API Key đã active!")
                return True
            else:
                # print(key["status"])
                # print("API Key đã hết hạn!")
                if renew:
                    # Thực hiện gia hạn
                    urlRenew = f"https://api.tinproxy.com/user/renew-proxy?token={token}"
                    dataRenew = {"api_key": apiKey, "time": time_}
                    rRenew = requests.post(url=urlRenew, data=dataRenew)
                    time.sleep(2)
                    if rRenew.status_code == 200:
                        resultRenew = rRenew.json()
                        print(resultRenew["message"])
                        return True
                    else:
                        print("#####\n#####Gia hạn thất bại. Kiểm tra đường truyền, website đăng ký.")
                        return False
                else:
                    print("Không chọn renew=True...")
                    return False
    print("API Key không tồn tại hoặc đã bị xóa!")
    return False


if __name__ == "__main__":
    print(LoadApiKeyAndAllowIp())
    # print(GetProxyIps())
    GetProxyIps()