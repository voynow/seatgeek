import json
import utils

def lambda_handler(event, context):

    bucket = "seatgeek-tickets"
    resp = utils.put_object(event, bucket)
    
    return resp
