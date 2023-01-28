import json
import utils

def lambda_handler(event, context):
    """
    """
    title = event['title']
    url = event['url']
    datetime_utc = event['datetime_utc']

    raw_data = utils.extract(url)
    clean_data = utils.cleanse(raw_data)
    structured_data = utils.apply_schema(clean_data)

    response = {
        "title": title,
        "url": url,
        "datetime_utc": datetime_utc,
        "raw_data": structured_data
    }

    return response
