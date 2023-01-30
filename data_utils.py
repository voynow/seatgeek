import boto3
import json
import pandas as pd
import numpy as np
import time

import matplotlib.pyplot as plt
plt.style.use('seaborn')


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


bucket_name = "seatgeek-tickets"
table = "2023-01-16-09-26-43-941432.json"
s3 = boto3.resource('s3')


def get_obj_keys():
    # get all data from s3
    s3_objs = s3.Bucket(bucket_name).objects.all()
    return [obj.key for obj in s3_objs]


def collect(obj_keys):
    data = {}
    for key in obj_keys:
        obj = s3.Object(bucket_name, key)
        json_obj = json.loads(obj.get()['Body'].read())
        key_stem = key.replace(".json", "")
        data[key_stem] = json_obj
    return data


def transform(data):
    # concatenate data
    dfs = []
    for datetime, dataset in data.items():
        if isinstance(dataset, list):
            for tickets in dataset:
                if not isinstance(tickets['data'], str):
                    df = pd.DataFrame(tickets['data'])
                    df['title'] = tickets['title']
                    df['game_ts'] = tickets['datetime_utc']
                    df['ingestion_ts'] = datetime
                    dfs.append(df)
    return pd.concat(dfs)



def etl():
    """ Convert raw data into pandas DF
    """
    object_keys = get_obj_keys()
    raw_json_objects = collect(object_keys)
    df = transform(raw_json_objects)

    # data preprocessing
    for p in preprocessing:
        df[p['update_col']] = df[p['from_col']].apply(p['fn'])

    return df