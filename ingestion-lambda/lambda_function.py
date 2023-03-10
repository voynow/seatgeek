import json
import datetime
import utils

def lambda_handler(event, context):
    """
    """
    title = event['title']
    url = event['url']
    datetime_utc = event['datetime_utc']

    try:
        raw_data = utils.extract(url)
        clean_data = utils.cleanse(raw_data)
        structured_data = utils.apply_schema(clean_data)
    except Exception as err:
        structured_data = str(err)

    response = {
        "title": title,
        "url": url,
        "datetime_utc": datetime_utc,
        "data": structured_data
    }

    return response
