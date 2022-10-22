from pymongo import MongoClient
from secret.db import dbid, dbpw, dbaddr, dbport


client = MongoClient(host=dbaddr, port=dbport, username=dbid, password=dbpw)
db = client['showpool']

def dbInit():
    oldCol = db['users']
    oldCol.drop()
    newCol = db['users']
    for i in range(1, 4):
        user = {
            "id" : "user%d" % (i),
            "pw" : "1234"
        }
        newCol.insert(user)

def main():
    print("a")

if __name__ == '__main__':
    #?
    dbInit()
    main()