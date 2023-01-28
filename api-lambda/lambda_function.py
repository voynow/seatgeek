import json

import utils

def lambda_handler(event, context):

    keys = ["title", "url", "datetime_utc"]
    event_data = []

    resp = utils.get_76ers_games()
    for obj in resp['events']:
        event_data.append({key: obj[key] for key in keys})

    return event_data