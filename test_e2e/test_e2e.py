import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class E2ETestDesktop(unittest.TestCase):
    def setUp(self):
        """Sets up the browser driver and parameters."""
        # Set up a browser.
        browser_option = Options()
        browser_option.driver_path = "./"
        browser_option.headless = False
        self.browser = webdriver.Chrome(options=browser_option)
        self.browser.set_window_size(1920, 1080)

        # Set up parameters.
        self.url = "http://127.0.0.1:8000/"
        self.test_user = "test"
        self.test_password = 'peppytest45'

    def test_collection_creation(self):
        """Tests usual steps taken in a collection creation process"""
        # Open beattosetto.
        self.browser.get(self.url)

        # Open collapse menu to login
        self.browser.find_element(By.CSS_SELECTOR, '#profile-picture').click()
        # Need to sleep due to need the collapse animation
        time.sleep(1)
        self.browser.find_element(By.CSS_SELECTOR, '#profile-picture-login').click()
        time.sleep(1)

        # Login
        self.browser.find_element(By.NAME, 'login').send_keys(self.test_user)
        self.browser.find_element(By.NAME, 'password').send_keys(self.test_password)
        self.browser.find_element(By.CSS_SELECTOR, '.btn-beattosetto').click()
        self.assertIn(f"Successfully signed in as {self.test_user}", self.browser.page_source)

        # Create collection
        self.browser.find_element(By.CSS_SELECTOR, '#create-collection').click()
        self.browser.find_element(By.NAME, 'name').send_keys('peppy dance')
        self.browser.find_element(By.CSS_SELECTOR, '#id_description').send_keys('peppy dance and more')
        self.browser.find_element(By.NAME, 'tags').send_keys('peppy,dance')
        # Sometime selenium say "the button cannot click" but it's still clickable, so I use JS executor
        # on the element instead.
        self.browser.execute_script("arguments[0].click()", self.browser.find_element(By.CSS_SELECTOR, '.btn-success'))
        self.assertIn("peppy dance", self.browser.page_source)

        # Comment
        self.browser.find_element(By.CSS_SELECTOR, '#id_comment').send_keys('Wow, peppy dance!')
        self.browser.execute_script("arguments[0].click()", self.browser.find_element(By.CSS_SELECTOR, '.btn-success'))
        self.assertIn("Add comment successfully!", self.browser.page_source)
        self.assertIn("Wow, peppy dance!", self.browser.page_source)

    def test_click_list(self):
        """Check whether clicking on the list link leads to the listing page."""
        self.browser.get(self.url)
        list_link_element = self.browser.find_element(by=By.CSS_SELECTOR, value=".nav-link.px-2.nav-text"
                                                                                ".hvr-underline-from-center")
        list_link_element.click()
        self.assertEqual(self.url + "listing", self.browser.current_url)

    def test_click_collection_card(self):
        """Check whether clicking on the collection card on the landing page or the listing page
        leads to its designated page.
        """
        # Click the first card on the landing page.
        self.browser.get(self.url)
        time.sleep(1)
        collection_name_element = self.browser.find_element(by=By.CSS_SELECTOR, value=".card-title.text-primary")
        # Store the clicked collection's name for further comparison.
        collection_name_text = collection_name_element.text
        collection_name_element.click()
        time.sleep(1)
        collection_page_title = self.browser.find_element(by=By.CSS_SELECTOR,
                                                          value=".display-5.fw-bold.text-break.aos-init.aos-animate")
        self.assertEqual(collection_name_text, collection_page_title.text)

        # Click the first card on the listing page.
        self.browser.get(self.url + "listing")
        time.sleep(1)
        collection_name_element = self.browser.find_element(by=By.CSS_SELECTOR, value=".card-title.text-primary")
        collection_name_text = collection_name_element.text
        collection_name_element.click()
        time.sleep(1)
        collection_page_title = self.browser.find_element(by=By.CSS_SELECTOR,
                                                          value=".display-5.fw-bold.text-break.aos-init.aos-animate")
        self.assertEqual(collection_name_text, collection_page_title.text)

    def test_click_collection_card_user(self):
        """Check whether clicking on the collection card's owner name leads to the user's profile page."""
        # Click the first card's owner on the landing page.
        self.browser.get(self.url)
        time.sleep(1)
        collection_owner_element = self.browser.find_element(by=By.CSS_SELECTOR,
                                                             value=".hvr-picture-bounce.text-decoration-none"
                                                                   ".spacing-hover")
        # Store the clicked collection owner's name for further comparison.
        collection_owner_text = collection_owner_element.text
        collection_owner_element.click()
        time.sleep(1)
        collection_owner_page_title = self.browser.find_element(by=By.XPATH, value="/html/body/main/div[2]/div/div["
                                                                                   "2]/h1")
        self.assertEqual(collection_owner_text, collection_owner_page_title.text)

        # Click the first card's owner on the listing page.
        self.browser.get(self.url)
        time.sleep(1)
        collection_owner_element = self.browser.find_element(by=By.CSS_SELECTOR,
                                                             value=".hvr-picture-bounce.text-decoration-none"
                                                                   ".spacing-hover")
        collection_owner_text = collection_owner_element.text
        collection_owner_element.click()
        time.sleep(1)
        collection_owner_page_title = self.browser.find_element(by=By.XPATH, value="/html/body/main/div[2]/div/div["
                                                                                   "2]/h1")
        self.assertEqual(collection_owner_text, collection_owner_page_title.text)

    def tearDown(self):
        """Closes the browser."""
        self.browser.quit()


class E2ETestMobile(unittest.TestCase):
    def setUp(self):
        """Sets up the browser driver and parameters."""
        # Set up a browser.
        browser_option = Options()
        browser_option.driver_path = "./"
        browser_option.headless = False
        self.browser = webdriver.Chrome(options=browser_option)
        self.browser.set_window_size(1920, 1080)

        # Set up parameters.
        self.url = "http://127.0.0.1:8000/"
        self.test_user = "test"
        self.test_password = 'peppytest45'

    def test_collection_creation(self):
        """Tests usual steps taken in a collection creation process"""
        # Open beattosetto.
        self.browser.get(self.url)

        # Open collapse menu to login
        self.browser.find_element(By.CSS_SELECTOR, '#profile-picture').click()
        # Need to sleep due to need the collapse animation
        time.sleep(1)
        self.browser.find_element(By.CSS_SELECTOR, '#profile-picture-login').click()
        time.sleep(1)

        # Login
        self.browser.find_element(By.NAME, 'login').send_keys(self.test_user)
        self.browser.find_element(By.NAME, 'password').send_keys(self.test_password)
        self.browser.find_element(By.CSS_SELECTOR, '.btn-beattosetto').click()
        self.assertIn(f"Successfully signed in as {self.test_user}", self.browser.page_source)

        # Create collection
        self.browser.find_element(By.CSS_SELECTOR, '#create-collection').click()
        self.browser.find_element(By.NAME, 'name').send_keys('peppy dance')
        self.browser.find_element(By.CSS_SELECTOR, '#id_description').send_keys('peppy dance and more')
        self.browser.find_element(By.NAME, 'tags').send_keys('peppy,dance')
        # Sometime selenium say "the button cannot click" but it's still clickable, so I use JS executor
        # on the element instead.
        self.browser.execute_script("arguments[0].click()", self.browser.find_element(By.CSS_SELECTOR, '.btn-success'))
        self.assertIn("peppy dance", self.browser.page_source)

        # Comment
        self.browser.find_element(By.CSS_SELECTOR, '#id_comment').send_keys('Wow, peppy dance!')
        self.browser.execute_script("arguments[0].click()", self.browser.find_element(By.CSS_SELECTOR, '.btn-success'))
        self.assertIn("Add comment successfully!", self.browser.page_source)
        self.assertIn("Wow, peppy dance!", self.browser.page_source)

    def test_click_list(self):
        """Check whether clicking on the list link leads to the listing page."""
        self.browser.get(self.url)
        list_link_element = self.browser.find_element(by=By.CSS_SELECTOR, value=".nav-link.px-2.nav-text"
                                                                                ".hvr-underline-from-center")
        list_link_element.click()
        self.assertEqual(self.url + "listing", self.browser.current_url)

    def test_click_collection_card(self):
        """Check whether clicking on the collection card on the landing page or the listing page
        leads to its designated page.
        """
        # Click the first card on the landing page.
        self.browser.get(self.url)
        time.sleep(1)
        collection_name_element = self.browser.find_element(by=By.CSS_SELECTOR, value=".card-title.text-primary")
        # Store the clicked collection's name for further comparison.
        collection_name_text = collection_name_element.text
        collection_name_element.click()
        time.sleep(1)
        collection_page_title = self.browser.find_element(by=By.CSS_SELECTOR,
                                                          value=".display-5.fw-bold.text-break.aos-init.aos-animate")
        self.assertEqual(collection_name_text, collection_page_title.text)

        # Click the first card on the listing page.
        self.browser.get(self.url + "listing")
        time.sleep(1)
        collection_name_element = self.browser.find_element(by=By.CSS_SELECTOR, value=".card-title.text-primary")
        collection_name_text = collection_name_element.text
        collection_name_element.click()
        time.sleep(1)
        collection_page_title = self.browser.find_element(by=By.CSS_SELECTOR,
                                                          value=".display-5.fw-bold.text-break.aos-init.aos-animate")
        self.assertEqual(collection_name_text, collection_page_title.text)

    def test_click_collection_card_user(self):
        """Check whether clicking on the collection card's owner name leads to the user's profile page."""
        # Click the first card's owner on the landing page.
        self.browser.get(self.url)
        time.sleep(1)
        collection_owner_element = self.browser.find_element(by=By.CSS_SELECTOR,
                                                             value=".hvr-picture-bounce.text-decoration-none"
                                                                   ".spacing-hover")
        # Store the clicked collection owner's name for further comparison.
        collection_owner_text = collection_owner_element.text
        collection_owner_element.click()
        time.sleep(1)
        collection_owner_page_title = self.browser.find_element(by=By.XPATH, value="/html/body/main/div[2]/div/div["
                                                                                   "2]/h1")
        self.assertEqual(collection_owner_text, collection_owner_page_title.text)

        # Click the first card's owner on the listing page.
        self.browser.get(self.url)
        time.sleep(1)
        collection_owner_element = self.browser.find_element(by=By.CSS_SELECTOR,
                                                             value=".hvr-picture-bounce.text-decoration-none"
                                                                   ".spacing-hover")
        collection_owner_text = collection_owner_element.text
        collection_owner_element.click()
        time.sleep(1)
        collection_owner_page_title = self.browser.find_element(by=By.XPATH, value="/html/body/main/div[2]/div/div["
                                                                                   "2]/h1")
        self.assertEqual(collection_owner_text, collection_owner_page_title.text)

    def tearDown(self):
        """Closes the browser."""
        self.browser.quit()
