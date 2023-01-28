import json
import utils

def lambda_handler(event, context):

    bucket = "seatgeek-tickets"
    utils.put_object(event, bucket)
    

