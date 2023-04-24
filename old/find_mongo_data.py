from pymongo import MongoClient
from pymongo.server_api import ServerApi


def mongo_init():
    uri = "mongodb+srv://ehcws333:ehcws333@manifesto.tpyq8xn.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['manifesto']
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return db


db = mongo_init()
collection = db.get_collection('propositions')

