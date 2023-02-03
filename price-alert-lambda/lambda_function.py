import utils

def lambda_handler(event, context):

    obj = utils.get_object(event)
    df = utils.transform(obj)
    resp = utils.check_price(df)
    
    return resp
