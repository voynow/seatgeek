import json
import utils

def lambda_handler(event, context):
    """
    """
    url = event['url']
    driver = utils.create_driver_helper()
    raw_data = utils.extract(driver, url)

    response = {
        "url": url,
        "raw_data": raw_data
    }

    return response
