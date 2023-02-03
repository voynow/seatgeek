
import boto3
import datetime
import json



s3 = boto3.resource('s3')

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
        "fn": lambda x: x.split(" ")[2],
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

sections_of_interest = ['101', '113', '114', '112', '124', '102']
max_price = 200

def get_object(event):
    """ Use event info to access s3 data
    """
    bucket = event['bucket']
    key = f"{event['key']}.json"

    obj = s3.Object(bucket, key)
    return json.loads(obj.get()['Body'].read())

def transform(data):

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


def check_price(obj):
    deal = obj[obj['score'] > 9.4]
    section = deal[deal['section'].apply(lambda x: x in sections_of_interest)]
    price = section[section['price'] < max_price]

    if not price.empty:
        return price.to_json(orient="records")
