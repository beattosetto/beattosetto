"""Program for running E2E test via Selenium on collection creation on desktop or big browser screen"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Configuration on test
URL = "http://127.0.0.1:8000/"
TEST_USERNAME = 'test'
TEST_PASSWORD = 'peppytest45'
browser = webdriver.Chrome('chromedriver.exe')

# Before run the test, don't forget to run the server

# Set the browser size to mobile size
browser.set_window_size(1920, 1080)
browser.get(URL)

# Open collapse menu to login
browser.find_element(By.CSS_SELECTOR, '#profile-picture').click()
# Need to sleep due to need the collapse animation
time.sleep(1)
browser.find_element(By.CSS_SELECTOR, '#profile-picture-login').click()
time.sleep(1)

# Login
browser.find_element(By.NAME, 'login').send_keys(TEST_USERNAME)
browser.find_element(By.NAME, 'password').send_keys(TEST_PASSWORD)
browser.find_element(By.CSS_SELECTOR, '.btn-beattosetto').click()
assert f"Successfully signed in as {TEST_USERNAME}" in browser.page_source

# Create collection
browser.find_element(By.CSS_SELECTOR, '#create-collection').click()
browser.find_element(By.NAME, 'name').send_keys('peppy dance')
browser.find_element(By.CSS_SELECTOR, '#id_description').send_keys('peppy dance and more')
browser.find_element(By.NAME, 'tags').send_keys('peppy,dance')
# Sometime selenium say "the button cannot click" but it's still clickable so I use JS executor on the element instead.
browser.execute_script("arguments[0].click()", browser.find_element(By.CSS_SELECTOR, '.btn-success'))
assert "peppy dance" in browser.page_source

# Comment
browser.find_element(By.CSS_SELECTOR, '#id_comment').send_keys('Wow, peppy dance!')
browser.execute_script("arguments[0].click()", browser.find_element(By.CSS_SELECTOR, '.btn-success'))
assert "Add comment successfully!" in browser.page_source
assert "Wow, peppy dance!" in browser.page_source
