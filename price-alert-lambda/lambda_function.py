import utils

def lambda_handler(event, context):

    obj = utils.get_object(event)
    df = utils.transform(obj)
    resp = utils.price_alert(df)
    
    return resp
