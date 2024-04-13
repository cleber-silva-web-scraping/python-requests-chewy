import time
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome( options=chrome_options)

driver.get("https://medium.com")
print(driver.page_source)

driver.quit()
print("Finished!")

time.sleep(10)
