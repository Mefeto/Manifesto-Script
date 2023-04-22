import json

from pymongo.errors import CollectionInvalid
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://ehcws333:ehcws333@manifesto.tpyq8xn.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['manifesto']
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def create_ddl(db):
    try:
        print(db.create_collection('propositions'))
    except CollectionInvalid as e:
        pass


create_ddl(db)


test_data = {
    "id": "PRC_P2O3N0C3B2Z7Y1Z4H3G9E3D1G4H3G7",
    "number": "2121190",
    "name": "관광진흥법 일부개정법률안",
    "comittee": "None",
    "committee_id": "None",
    "prop_date": "2023-04-06",
    "prop_result": "None",
    "age": "21",
    "detail": {
        "content": "제안이유 및 주요내용"
    },
    "analytics": {
        "problem": "발의안이 조명하고 있는 문제",
        "solution": "발의안이 해결하려고 하는 방식",
        "words": [
            {
                "name": "word1",
                "description": "word1 description"
            },
            {
                "name": "word2",
                "description": "word2 description"
            },
            {
                "name": "word3",
                "description": "word3 description"
            },
            {
                "name": "word4",
                "description": "word4 description"
            },
            {
                "name": "word5",
                "description": "word5 description"
            },
        ]
    },
    "members_info": "http://likms.assembly.go.kr/bill/coactorListPopup.do?billId=PRC_P2O3N0C3B2Z7Y1Z4H3G9E3D1G4H3G7",
    "rst_proposer": "이개호",
    "pub_proposer": "김남국,박광온,서삼석,신정훈,양경숙,어기구,이병훈,조오섭,허영"
}

collection = db.get_collection('propositions')
collection.insert_many([test_data])




