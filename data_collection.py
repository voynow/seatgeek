import api_utils
import json
import pandas as pd
import requests
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')


def create_driver(link=None):
    """ Create chrome driver, get link if available
    """
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    if link:
        driver.get(link)

    return driver


def extract_data_from_urls():
    """ Get seatgeek urls from api, collect text from each webpage
    """
    data = []
    resp = api_utils.get_76ers_games()
    urls = [event['url'] for event in resp['events']]

    driver = create_driver()
    for i, url in enumerate(urls):
        print(f"({i}/{len(urls)}) {url}")

        driver.get(url)
        driver.maximize_window()
        driver.execute_script("document.body.style.zoom='5%'")
        driver.implicitly_wait(10)
        time.sleep(1)

        text = driver.find_element(By.ID, '__next').text
        data.append(text.split("\n"))

    driver.quit()
    return data


def cleanse(raw_data):
    """ Cleaning raw text extracted from seatgeek
    """
    title_string = " at Philadelphia 76ers"
    remove_strings = [
        "Aisle Seats",
        "Private Restrooms",
        "Includes access to a buffet, Includes Parking",
        "Limited view"
    ]

    data = {}
    for dataset in raw_data:

        # remove excess data
        for string in remove_strings:
            while string in dataset:
                dataset.remove(string)
        # get game title
        for row in dataset:
            if title_string in row:
                title = row.replace(title_string, "")
                break
        # handling for duplicate title
        while title in data:
            title += "(1)"
        data[title] = dataset

    # trim data
    for k, v in data.items():
        while v[0][0] != "$":
            v = v[1:]
        data[k] = v
        namefrmt = k.replace(" ", "-")
        print(f"game={namefrmt} data-size={len(v)}")

    return data


def apply_schema(clean_data):
    """
    Structuring data, consistent format across games
    """
    cols = ["price", "score", "deal", "num_tickets", "section"]
    failure = False

    dfs = {}
    for k, v in clean_data.items():
        data_collection = {col: [] for col in cols}
        for i, item in enumerate(v):
            col = cols[i % 5]
            data_collection[col].append(item)
        
        try:
            dfs[k] = pd.DataFrame(data_collection)
        except ValueError as e:
            failure = True
            print(f"Failed on {k}")

    if not failure:
        print("Applied schemas successfully!")

    return dfs


def etl():
    """ pipeline for data extraction and transformation
    """
    raw_data = extract_data_from_urls()
    clean_data = cleanse(raw_data)
    structured_data = apply_schema(clean_data)

    return {key: df.to_json() for key, df in structured_data.items()}
    