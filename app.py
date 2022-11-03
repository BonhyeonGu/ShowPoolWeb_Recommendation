from pymongo import MongoClient
from datetime import datetime
from hashlib import sha256

from secret.db import mongo_dbid, mongo_dbpw, mongo_dbaddr, mongo_dbport
from recomm import Recomm
#-------------------------------------------------------------
client = MongoClient(host=mongo_dbaddr, port=mongo_dbport, username=mongo_dbid, password=mongo_dbpw)
db = client['showpool']
doc = db['users']
#-------------------------------------------------------------
userLastClick = dict()
#-------------------------------------------------------------
REF_NUM = 10 #참고할 영상 개수, 웹사이트와 동일하게 할 것
#-------------------------------------------------------------

def dbInit():
    oldCol = doc
    oldCol.drop()
    newCol = doc
    for i in range(1, 4):
        user = {
            "id" : "user0%d" % (i),
            "pw" : "1234",
            "clickedID" : (),
            "clickedInfo" : (),
            "recommID" : (),
            "time_lastclick" : "x",
            "time_lastupdate" : "x"
        }
        newCol.insert_one(user)

def mainRoutine():
    while True:
        for user_info in doc.find():
            if (user_info['id'] not in userLastClick) or \
                (userLastClick[user_info['id']] != sha256(user_info['time_lastclick'].decode('utf-8'))):
                print("%s is changed, update start"%(user_info['id']))
                recomm = Recomm(user_info['clickedID'], user_info['clickedInfo']).run()
                userLastClick['id'] = sha256(user_info['time_lastclick'].encode('utf-8'))
                nowDate = datetime.today().strftime("%Y%m%d%H%M%S")
                doc.update_one({"id" : user_info['id']}, {"$set":{"time_lastupdate" : nowDate}})
            else:
                print("%s is not changed, update skip"%(user_info['id']))

def main():
    print("start")
    mainRoutine()

if __name__ == '__main__':
    dbInit()
    main()