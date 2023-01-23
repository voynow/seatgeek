
import utils.seatgeek_api as seatgeek_api
import json
import requests
import time

from headless_chrome import create_driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


def create_driver_helper():
    """
    Handles Chrome failed to start error
    """
    driver = None
    while driver is None:
        try:
            driver = create_driver()
        except WebDriverException:
            create_driver_helper()
            
    return driver


def extract(driver, url):
    """ Get seatgeek urls from api, collect text from each webpage
    """
    driver.get(url)
    driver.maximize_window()
    driver.execute_script("document.body.style.zoom='5%'")
    driver.implicitly_wait(10)
    time.sleep(1)

    text = driver.find_element(By.ID, '__next').text
    return text.split("\n")