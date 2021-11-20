"""Program for running E2E test via Selenium"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Configuration on test
url = "http://127.0.0.1:8000/"
browser = webdriver.Chrome('chromedriver.exe')
test_username = 'test'
test_password = 'peppytest45'

# Before run the test, don't forget to run the server

# Set the browser size to mobile size
browser.set_window_size(480, 1000)
browser.get(url)
navbar_collapse = browser.find_element(By.CSS_SELECTOR, '.navbar-toggler')
navbar_collapse.click()
time.sleep(1)
login_button = browser.find_element(By.CSS_SELECTOR, '#collapse-sign-in')
login_button.click()

# Login
browser.find_element(By.NAME, 'login').send_keys(test_username)
browser.find_element(By.NAME, 'password').send_keys(test_password)
browser.find_element(By.CSS_SELECTOR, '.btn-beattosetto').click()
assert f"Successfully signed in as {test_username}" in browser.page_source

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
