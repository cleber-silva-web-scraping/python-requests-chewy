from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://medium.com")
print(driver.page_source)

driver.quit()
print("Finished!")
