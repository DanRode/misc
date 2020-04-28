from selenium import webdriver
import time

PATH = "/Users/drode/git/misc/sandbox/chromedriver"
driver = webdriver.Chrome(PATH)

driver.get("http://techwithtim.net")

time.sleep(9)

driver.quit()
