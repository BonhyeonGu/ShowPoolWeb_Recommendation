from neo4j import GraphDatabase
from secret.db import neo_dbid, neo_dbpw, neo_dbaddr, neo_dbport
class Neo:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri=f"neo4j://{neo_dbaddr}:{neo_dbport}", auth=(neo_dbid, neo_dbpw))
    
    def __del__(self):
        self.driver.close()    

    #DB 전체 비디오들 각 아이디 조회
    def getVideos(self, tx):
        rets = []
        result = tx.run("MATCH (n : Video) RETURN (n)")
        for record in result:
            rets.append(record[0]["data"])
        return rets

    #원하는 비디오, 세그먼트의 컴포넌트들 조회 in=>brU5yLm9DZM ret=>
    #[('2', 'Tangent'), ('2', 'Intelligence_quotient'), ('2', 'Laser'),
    # ('2', 'Momentum'), ('2', 'Computer_scientist'), ('1', 'Friction'), ('1', 'Kinetic_energy'), ('1', 'Optics'), ('1', 'Beam_(nautical)'), ('1', 'Sine_and_cosine'), ('0', 'Geometry'), ('0', 'Croquet'), ('0', 'Kaleidoscope'), ('0', 'Optics'), ('0', 'Beam_(nautical)')]
    #였는데 바꿈, [[],[]..]
    def getVideo_Seg_KCS(self, tx, yid):
        result = tx.run("MATCH (c: KnowledgeComponent) --> (s: Segment) --> (v: Video {data: $yid}) RETURN c, s",
        yid=yid
        )
        ans = list(reversed([(row["s"]["data"], row["c"]["data"])for row in result]))
        compsCount = len(ans) // 5
        tempRet = dict()
        for i in ans:
            try:
                tempRet[i[0]].append(i[1])
            except KeyError:
                tempRet[i[0]] = [i[1]]
        ret = []
        for i in range(0, compsCount):
            ret.append(tempRet[str(i)])
        return ret

    #해당 컴포넌트가 포함되어있는 비디오 조회 in=>Tangent, ret=>
    #[('jsYwFizhncE', '1'), ('brU5yLm9DZM', '2'), ('jsYwFizhncE', '2'), ('d-o3eB9sfls', '1')]
    def getKC_Videos(self, tx, kc):
        result = tx.run("MATCH (c: KnowledgeComponent {data: $kc}) --> (s: Segment) --> (v: Video) RETURN s, v",
        kc=kc
        )
        return [(row["v"]["data"], row["s"]["data"])for row in result]

    #실행부 이것만 쓸 예정
    def runQuery(self, q, arg1 = 0):
        with self.driver.session() as session:
            if q == 0:
                rets = session.read_transaction(self.getVideos)
            if q == 1:
                rets = session.read_transaction(self.getVideo_Seg_KCS, arg1)
            if q == 2:
                rets = session.read_transaction(self.getKC_Videos, arg1)
        return rets

    def runAll(self):
        allDict = dict()
        ids = self.runQuery(0)
        for id in ids:
            allDict[id] = self.runQuery(1, id)
        return ids, allDict
            
#N = Neo()
#a1 = N.runQuery(1, "GqmQg-cszw4")
#print(a1)