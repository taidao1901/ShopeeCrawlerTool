# import os
# import zipfile
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# import time

# PROXY_HOST = '116.109.77.230'  # rotating proxy or host
# PROXY_PORT = 12005 # port
# PROXY_USER = 'lKlqnWQk' # username
# PROXY_PASS = 'd1qyHypY' # password

# manifest_json = """
# {
#     "version": "1.0.0",
#     "manifest_version": 2,
#     "name": "Chrome Proxy",
#     "permissions": [
#         "proxy",
#         "tabs",
#         "unlimitedStorage",
#         "storage",
#         "<all_urls>",
#         "webRequest",
#         "webRequestBlocking"
#     ],
#     "background": {
#         "scripts": ["background.js"]
#     },
#     "minimum_chrome_version":"22.0.0"
# }
# """

# background_js = """
# var config = {
#         mode: "fixed_servers",
#         rules: {
#         singleProxy: {
#             scheme: "http",
#             host: "%s",
#             port: parseInt(%s)
#         },
#         bypassList: ["localhost"]
#         }
#     };
# chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
# function callbackFn(details) {
#     return {
#         authCredentials: {
#             username: "%s",
#             password: "%s"
#         }
#     };
# }
# chrome.webRequest.onAuthRequired.addListener(
#             callbackFn,
#             {urls: ["<all_urls>"]},
#             ['blocking']
# );
# """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

# def get_chromedriver(use_proxy=False, user_agent=None):
#     path = os.path.dirname(os.path.abspath(__file__))
#     service = Service(executable_path=ChromeDriverManager().install())
#     caps = DesiredCapabilities.CHROME
#     caps['goog:loggingPrefs'] = {'performance': 'ALL'}
#     chrome_options = webdriver.ChromeOptions()
#     if use_proxy:
#         pluginfile = 'proxy_auth_plugin.zip'

#         with zipfile.ZipFile(pluginfile, 'w') as zp:
#             zp.writestr("manifest.json", manifest_json)
#             zp.writestr("background.js", background_js)
#         chrome_options.add_extension(pluginfile)
#     if user_agent:
#         chrome_options.add_argument('--user-agent=%s' % user_agent)
#     driver = webdriver.Chrome(
#         desired_capabilities=caps,service = service,
#         chrome_options=chrome_options)
#     return driver

# def main():
#     driver = get_chromedriver(use_proxy=True)
#     #driver.get('https://www.google.com/search?q=my+ip+address')
#     driver.get('https://shopee.vn/%C3%81o-Kho%C3%A1c-cat.11035567.11035568')
#     time.sleep(10)


# if __name__ == '__main__':
#     main()

