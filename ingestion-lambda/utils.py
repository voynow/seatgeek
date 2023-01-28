
import json
import requests
import time

from headless_chrome import create_driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

cols = [
    "price", 
    "score", 
    "deal", 
    "num_tickets", 
    "section"
]

remove_strings = [
    "Aisle Seats",
    "Private Restrooms",
    "Includes access to a buffet, Includes Parking",
    "Limited view",
    "In-Seat Wait Service, Private Restrooms"
]


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
    driver = create_driver_helper()
    driver.get(url)
    
    driver.maximize_window()
    driver.execute_script("document.body.style.zoom='5%'")
    driver.implicitly_wait(10)
    time.sleep(1)

    text = driver.find_element(By.ID, '__next').text
    return text.split("\n")


def cleanse(dataset):
    """ Cleaning raw text extracted from seatgeek
    """
    # remove excess data
    for string in remove_strings:
        while string in dataset:
            dataset.remove(string)

    # trim data
    while dataset[0][0] != "$":
        dataset = dataset[1:]

    return dataset


def validate_data(data):
    """ Check that all columns are the same length
    """
    lens = [len(v) for _, v in data.items()]

    for l in lens:
        if l != lens[0]:
            raise ValueError("(Validation Failure) Column length mismatch")
    return data


def apply_schema(dataset):
    """
    Structuring data, consistent format across games
    """
    data_collection = {col: [] for col in cols}
    for i, row in enumerate(dataset):
        col = cols[i % 5]
        data_collection[col].append(row)
    
    return validate_data(data_collection)
