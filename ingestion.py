
import boto3
import utils.data_collection as data_collection
import utils.data_storage as data_storage
import json


bucket = "seatgeek-tickets"
success = False

while not success:
    try:
        data = data_collection.etl()
        success = True
    except Exception as e:
        print(f"Exiting data_collcetion ETL with the following exception: \n{e}")

resp = data_storage.put_object(data, bucket)