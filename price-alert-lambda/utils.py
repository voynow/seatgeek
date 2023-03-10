
import boto3
import datetime
import json
import pandas as pd


s3 = boto3.resource('s3')
sns = boto3.client('sns')

def custom_num_tickets_fn(x):
    x_split = x.split(" ")
    try:
        num = x_split[2]
    except IndexError:
        num = x
    return num


preprocessing = [
    {
        "update_col": "price", 
        "from_col": "price",
        "fn": lambda x: int(x.split(" ")[0].replace("$", "").replace(",", "")),
    },
    {
        "update_col": "score", 
        "from_col": "score",
        "fn": lambda x: float(x),
    },
    {
        "update_col": "num_tickets", 
        "from_col": "num_tickets",
        "fn": lambda x: custom_num_tickets_fn(x),
    },
    {
        "update_col": "section", 
        "from_col": "section",
        "fn": lambda x: x.replace("Section ", "").replace("Row ", "") + ", NA",
    },
    {
        "update_col": "row", 
        "from_col": "section",
        "fn": lambda x: x.split(", ")[1],
    },
    {
        "update_col": "section", 
        "from_col": "section",
        "fn": lambda x: x.split(", ")[0],
    },
]

min_score = 9.9
sections_of_interest = ['101', '113', '114', '112', '124', '102']
max_price = 200

def get_object(event):
    """ Use event info to access s3 data
    """
    bucket = event['bucket']
    key = event['key']

    obj = s3.Object(bucket, key)
    return json.loads(obj.get()['Body'].read())

def transform(data):
    """
    """
    dfs = []
    for game in data:
        if not isinstance(game['data'], str):
            df = pd.DataFrame(game['data'])
            df['title'] = game['title']
            df['game_ts'] = game['datetime_utc']
            dfs.append(df)
    df = pd.concat(dfs)

    for p in preprocessing:
        df[p['update_col']] = df[p['from_col']].apply(p['fn'])
    return df


def check_for_deals(obj):
    """
    """
    deal = obj[obj['score'] >= min_score]
    section = deal[deal['section'].apply(lambda x: x in sections_of_interest)]
    price = section[section['price'] < max_price]

    if not price.empty:
        return json.loads(price.to_json(orient="records"))
    else:
        return [None]


def price_alert(obj):
    """
    """
    deals = check_for_deals(obj)

    resps = []
    for deal in deals:
        if deal:
            response = sns.publish(
                TargetArn="arn:aws:sns:us-east-1:498969721544:seatgeek-tickets",
                Message=json.dumps({'default': json.dumps(deal)}),
                MessageStructure='json',
            )
            resps.append(response)
    return resps