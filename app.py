from pymongo import MongoClient
from datetime import datetime
import pickle as pic
import time

from secret.db import mongo_dbid, mongo_dbpw, mongo_dbaddr, mongo_dbport
from neo import Neo
from recomm import Recomm
#-------------------------------------------------------------
client = MongoClient(host=mongo_dbaddr, port=mongo_dbport, username=mongo_dbid, password=mongo_dbpw)
db = client['showpool']
doc = db['users']
#-------------------------------------------------------------
userLastClick = dict()
#-------------------------------------------------------------
SLEEP_SEC = 5
REF_NUM = 3 #참고할 영상 개수, 웹사이트와 동일하게 할 것

#경로 도커파일에서 쓸 수 있는 것을 기준으로 푸시함!
LOACATION_TITLE2ID = "../rk/ComTittleToID.pkl"
LOACATION_BACKLINKS = "../rk/backlinks/"
#LOACATION_TITLE2ID = "C:/Users/8whwh/Git/Reasoning_over_Knowledge_Component_Streams/ComTittleToID.pkl"
#LOACATION_BACKLINKS = "C:/Users/8whwh/Git/Reasoning_over_Knowledge_Component_Streams/backlinks/"
#LOACATION_TITLE2ID = "C:/Users/MY/.vscode/tt/Wikification_web/Wikification_web/ComTittleToID.pkl"
#LOACATION_BACKLINKS = "C:/Users/MY/.vscode/tt/Wikification_web/Wikification_web/backlinks/"
#-------------------------------------------------------------

def dbInit():
    oldCol = doc
    oldCol.drop()
    newCol = doc

    nowDate = datetime.today().strftime("%Y%m%d%H%M%S")
    for i in range(1, 4):
        user = {
            "id" : "user0%d" % (i),
            "pw" : "1234",
            "clickedID" : (),
            "recommID1" : (),
            "recommID2" : (),
            "time_lastclick" : nowDate,
            "time_lastupdate" : "x"
        }
        newCol.insert_one(user)
        userLastClick["user0%d" % (i)] = nowDate

def mainRoutine():
    with open(LOACATION_TITLE2ID,'rb') as f:
            title2Id = pic.load(f)
    while True:
        for user_info in doc.find():
            if (user_info['id'] not in userLastClick) or \
                (userLastClick[user_info['id']] != user_info['time_lastclick']):
                print("%s is changed, update start"%(user_info['id']))
                allID, allData = Neo().runAll()
                #---------------------------------------------------------------------------------------------
                recomm = Recomm(title2Id, LOACATION_BACKLINKS, allID, allData, user_info['clickedID'], 6).run()
                doc.update_one({"id" : user_info['id']}, {"$set":{"recommID1" : recomm}})
                recomm = Recomm(title2Id, LOACATION_BACKLINKS, allID, allData, user_info['clickedID'], 6).RWR()
                doc.update_one({"id" : user_info['id']}, {"$set":{"recommID2" : recomm}})
                #---------------------------------------------------------------------------------------------
                userLastClick[user_info['id']] = user_info['time_lastclick']
                nowDate = datetime.today().strftime("%Y%m%d%H%M%S")
                doc.update_one({"id" : user_info['id']}, {"$set":{"time_lastupdate" : nowDate}})
            else:
                print("%s is not changed, update skip"%(user_info['id']))
            print("process %dsecond sleep"%(SLEEP_SEC))
            time.sleep(SLEEP_SEC)

def main():
    mainRoutine()

if __name__ == '__main__':
    dbInit()
    main()