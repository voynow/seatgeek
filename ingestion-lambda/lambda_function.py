import json
import utils

def lambda_handler(event, context):
    """
    """
    url = event['url']
    raw_data = utils.extract(url)
    clean_data = utils.cleanse(raw_data)
    structured_data = utils.apply_schema(clean_data)

    response = {
        "url": url,
        "raw_data": structured_data
    }

    return response
