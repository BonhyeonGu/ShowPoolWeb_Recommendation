import operator

class Recomm():
    def __init__(self, allID:list, allData:dict, clickdID:list, resultNum=6):
        self.allID = allID
        self.allData = allData
        self.clickdID = clickdID
        self.resultNum = resultNum
    def run(self):
        segNum = 0
        kcDict = dict()
        clickedSet = set(self.clickdID)

        #시청한 영상의 세그먼트에 있는 각각의 kc의 개수를 센다.
        for vidID in self.clickdID:
            segNum += len(self.allData[vidID])
            for segment in self.allData[vidID]:
                for kc in segment:
                    try:
                        kcDict[kc] += 1
                    except KeyError:
                        kcDict[kc] = 1

        weightDict = dict()

        #전체 영상의 kc를 확인하여 각 가중치를 더한다.
        for vidID in self.allID:
            if vidID in clickedSet:
                continue
            segCount = 0
            for segment in self.allData[vidID]:
                
                for kc in segment:
                    weightDict[vidID+" ~ "+str(segCount)] = 0.0
                    try:
                        weightDict[vidID+" ~ "+str(segCount)] += kcDict[kc]/(segNum*5)
                    except KeyError:
                        continue

                segCount += 1            

        #가중치가 큰 순으로 정렬 후 self.resultNum 개의 결과 반환
        s = sorted(weightDict.items(), key=operator.itemgetter(1), reverse=True)
        
        result = []
        for i in s:
            idx = i[0].find(" ~ ")
            result.append((i[0][:idx],i[0][idx+3:],i[1]))
        return result[:self.resultNum]
