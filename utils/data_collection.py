import utils.seatgeek_api as seatgeek_api
import json
import pandas as pd
import requests
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('log-level=3')

title_string = " at Philadelphia 76ers"
remove_strings = [
    "Aisle Seats",
    "Private Restrooms",
    "Includes access to a buffet, Includes Parking",
    "Limited view",
    "In-Seat Wait Service, Private Restrooms"
]
cols = ["price", "score", "deal", "num_tickets", "section"]


def create_driver(link=None):
    """ Create chrome driver, get link if available
    """
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    if link:
        driver.get(link)

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


def cleanse(dataset):
    """ Cleaning raw text extracted from seatgeek
    """

    # remove excess data
    for string in remove_strings:
        while string in dataset:
            dataset.remove(string)

    # get game title
    for row in dataset:
        if title_string in row:
            title = row.replace(title_string, "")
            break

    # trim data
    while dataset[0][0] != "$":
        dataset = dataset[1:]
    namefrmt = title.replace(" ", "-")
    print(f"game={namefrmt} data-size={len(dataset)}")

    return title, dataset


def validate_title(title, data):
    """ Handle duplicate titles
    """
    while title in data:
        title += "(1)"
    return title


def apply_schema(dataset):
    """
    Structuring data, consistent format across games
    """
    data_collection = {col: [] for col in cols}
    for i, row in enumerate(dataset):
        col = cols[i % 5]
        data_collection[col].append(row)
    
    return data_collection


def validate_data(data):
    """ Check that all columns are the same length
    """
    lens = [len(v) for _, v in data.items()]

    for l in lens:
        if l != lens[0]:
            raise ValueError("(Validation Failure) Column length mismatch")
    return data

def etl():
    """ pipeline for data extraction and transformation
    """
    resp = seatgeek_api.get_76ers_games()
    urls = [event['url'] for event in resp['events']]

    driver = create_driver()
    master_data = {}

    for i, url in enumerate(urls):
        print(f"({i+1}/{len(urls)}) {url}")

        raw_data = extract(driver, url)
        title, clean_data = cleanse(raw_data)
        title = validate_title(title, master_data)
        structured_data = validate_data(apply_schema(clean_data))
        master_data[title] = structured_data

    driver.quit()
    return master_data