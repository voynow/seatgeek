import boto3
from botocore.exceptions import ClientError
import json
import requests


def get_secrets():
    """
    """
    secret_name = "seatgeek_configs"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return json.loads(get_secret_value_response['SecretString'])


def get_params():
    """
    """
    secrets = get_secrets()
    clientid = secrets['clientid']
    secret = secrets['secret']

    return {
        'client_id': clientid,
        'client_secret': secret,
    }


def get_wells_fargo_id():
    """
    """
    wells_fargo = "wells fargo"
    url = "https://api.seatgeek.com/2/venues?city=philadelphia"

    res = requests.get(url=url, params=get_params())
    philly_venues = res.json()['venues']

    found = False
    for venue in philly_venues:
        if wells_fargo in venue['name'].lower():
            wells_fargo_id = venue['id']
            found = True
    if not found:
        raise ValueError(f"Did not find venue: {wells_fargo}")

    return wells_fargo_id


def get_76ers_games():
    """
    """
    url = f"https://api.seatgeek.com/2/events?venue.id={get_wells_fargo_id()}&per_page=20&taxonomies.name=nba"
    return requests.get(url=url, params=get_params()).json()
