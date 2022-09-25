import undetected_chromedriver.v2 as uc
import time

if __name__ == "__main__":
    driver = uc.Chrome()
    driver.get('https://shopee.vn/%C3%81o-Kho%C3%A1c-cat.11035567.11035568')
    time.sleep(10)
    driver.close()