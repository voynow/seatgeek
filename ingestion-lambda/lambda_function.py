import json
import utils

def lambda_handler(event, context):
    """
    """
    driver = utils.create_driver_helper()
    raw_data = utils.extract(driver, event['url'])

    return raw_data
