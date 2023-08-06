import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils.Log import Log

DEFAULT_WINDOW_DIM = (1920, 1080)
TIME_DEFAULT_WAIT = 10
TIME_DEFAULT_SLEEP = 1

log = Log('Browser')


class Browser:
    """Browser."""

    def __init__(self):
        """Construct."""
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(
            options=options,
        )
        self.set_window_dim(DEFAULT_WINDOW_DIM)

    def set_window_dim(self, dim: tuple):
        width, height = dim
        self.driver.set_window_size(width, height)

    def open(self, url: str):
        self.driver.get(url)
        log.debug(f'Opened "{url}".')

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        SCRIPT_SCROLL = 'window.scrollTo(0, document.body.scrollHeight);'
        self.driver.execute_script(SCRIPT_SCROLL)

    @property
    def source(self):
        """Get page source."""
        return self.driver.page_source

    def downloadScreenshot(self, image_file_name):
        self.driver.save_screenshot(image_file_name)
        log.debug(f'Downloaded screenshot to "{image_file_name}".')

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def wait_for_element(self, by, value, timeout: int = TIME_DEFAULT_WAIT):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def sleep(self, timeout=TIME_DEFAULT_SLEEP):
        time.sleep(timeout)

    def quit(self):
        self.driver.close()
        self.driver.quit()
