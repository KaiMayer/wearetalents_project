import os
import time
from django.test import TestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

MAX_WAIT = 10


class SeleniumTestCase(TestCase):

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                time.sleep(0.5)
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(1)

    def wait_for_row_in_list(self, row_text):
        start_time = time.time()
        while True:
            try:
                list = self.browser.find_element_by_class_name('list-group')
                rows = list.find_elements_by_tag_name('li')
                self.assertIn(row_text, [row.text for row in rows][0])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def setUp(self):
        self.browser = webdriver.Chrome()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = 'http://' + staging_server

    def tearDown(self):
        self.browser.refresh()
        self.browser.quit()

    def get_item_input_box(self):
        return self.browser.find_element_by_name('q')

    def test_admin_home_page_and_make_post(self):
        # navigate to home page
        self.browser.get('http://localhost:8000/')

        self.get_item_input_box().send_keys('Java developer')
        self.wait_for(lambda: self.get_item_input_box().send_keys(Keys.ENTER))

        self.wait_for_row_in_list('Java developer')

