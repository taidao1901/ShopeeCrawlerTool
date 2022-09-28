import requests
import selenium
import seleniumwire

if __name__=="__main__":
    # token = ""
    # url = f"https://api.tinproxy.com/user/renew-proxy?token={token}"
    # data = {"api_key": "MrIVnojEv4OqdBDTZB2BFnzLdah0IaOz", "time": 1}
    # r = requests.post(url=url, data=data)
    # result = r.json()
    # print(result, r.status_code)
    print(selenium.__version__)
    print(seleniumwire.__version__)