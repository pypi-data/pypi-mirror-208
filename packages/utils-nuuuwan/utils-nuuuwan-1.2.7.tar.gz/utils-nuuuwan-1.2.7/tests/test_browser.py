import tempfile
from unittest import TestCase

from selenium.webdriver.common.by import By

from utils import Browser

TEST_URL = '/'.join(
    [
        'https://nuuuwan.github.io',
        'utils',
    ]
)


class TestBrowser(TestCase):
    def test_find_element_etc(self):
        browser = Browser()
        browser.open(TEST_URL)
        elem_h1 = browser.find_element(By.TAG_NAME, 'h1')
        self.assertEqual('Heading 1', elem_h1.text)

        elem_h2_2 = browser.find_elements(By.TAG_NAME, 'h2')[1]
        self.assertEqual('Heading 1.2', elem_h2_2.text)

        elem_h2_1 = browser.wait_for_element(By.TAG_NAME, 'h2')
        self.assertEqual('Heading 1.1', elem_h2_1.text)

        browser.quit()

    def test_source(self):
        browser = Browser()
        browser.open(TEST_URL)
        self.assertIn('This is a test', browser.source)
        browser.quit()

    def test_all_others(self):
        browser = Browser()
        browser.open(TEST_URL)
        browser.set_window_dim((100, 200))
        browser.scroll_to_bottom()
        browser.downloadScreenshot(
            tempfile.NamedTemporaryFile(
                prefix="screenshot.", suffix=".png"
            ).name
        )
        browser.sleep(1)
        browser.quit()
