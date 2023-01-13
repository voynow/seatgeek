import json
import requests
import secrets_manager

secrets = secrets_manager.get_secrets()
clientid = secrets['clientid']
secret = secrets['secret']

url = "https://api.seatgeek.com/2/venues?city=philadelphia"
params = {
    'client_id': clientid,
    'client_secret': secret,
}

res = requests.get(url=url, params=params)
philly_venues = res.json()['venues']

found = False
wells_fargo = "wells fargo"
for venue in philly_venues:
    if wells_fargo in venue['name'].lower():
        wells_fargo_id = venue['id']
        found = True
if not found:
    raise ValueError(f"Did not find venue: {wells_fargo}")

url = f"https://api.seatgeek.com/2/events?venue.id={wells_fargo_id}&per_page=20&taxonomies.name=nba"
res = requests.get(url=url, params=params)
json.dump(res.json()['events'], open('test.json', 'w'))