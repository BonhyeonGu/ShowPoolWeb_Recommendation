from pymongo import MongoClient
from secret.db import mongo_dbid, mongo_dbpw, mongo_dbaddr, mongo_dbport


client = MongoClient(host=mongo_dbaddr, port=mongo_dbport, username=mongo_dbid, password=mongo_dbpw)
db = client['showpool']

def dbInit():
    oldCol = db['users']
    oldCol.drop()
    newCol = db['users']
    for i in range(1, 4):
        user = {
            "id" : "user0%d" % (i),
            "pw" : "1234"
        }
        newCol.insert_one(user)

def main():
    print("a")

if __name__ == '__main__':
    #?
    dbInit()
    main()