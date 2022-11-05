import operator
import pickle as pic
import numpy as np
from scipy.stats import norm

from math import log2
def getBacklinks(fileName):
        with open(fileName,'rb') as f:
            ret = pic.load(f)
        return ret
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

    def RWR(self):
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

        kcList = sorted(kcDict.items(), key=operator.itemgetter(1), reverse=True)

        kcGraph = self._graph(kcList)
        kcDict = dict()
        if len(kcGraph) > 0:
            nowNode = kcGraph[0]
            for i in range(len(kcGraph)):
                p = np.random.rand()
                sum = 0
                for j in kcGraph:
                    sum+= j[1] / (segNum*5)
                    if p < sum:
                        nowNode = j
                        break;

                while(True):
                    try:
                        kcDict[nowNode[0]]+=1
                    except KeyError:
                        kcDict[nowNode[0]]=1

                    if np.random.rand() < 0.1:
                        break;
                    sum = 0
                    p=np.random.rand()
                    for j in nowNode[2]:
                        sum+=j[0]
                        if p < sum:
                            nowNode = kcGraph[j[1]]
                            break;
        #
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

    def _graph(self, s:list):
        if len(s) == 0:
            return []
        N=1633324#전체 아이디 개수
        backlink_list = list()
        kcList = list()
        #backlink집합을 가지는 튜플을 만든다
        with open("C:/Users/MY/.vscode/tt/Wikification_web/Wikification_web/ComTittleToID.pkl",'rb') as f:
            title2Id = pic.load(f)
        
        for kc in s:
            kcList.append((kc[0], kc[1],[]))
            backlink_list.append(getBacklinks("C:/Users/MY/.vscode/tt/Wikification_web/Wikification_web/backlinks/"+str(title2Id[kc[0].encode()]) + "_backlinks.pickle"))
        
        backlink_tuple = tuple(backlink_list)
        del(title2Id)
        i = -1
        for startVertex in kcList:
            i+=1
            j=i
            for endVertex in kcList[i+1:]:
                j+=1
                if(i == j):#자기자신을 가리키는 간선 안생김
                    continue
                #i에서 j로
                SR = self._calcSR(backlink_tuple[i],backlink_tuple[j],N)

                if(SR > 0):#SR값이 0보다커야 간선 추가함
                    startVertex[2].append([SR, j])
                    endVertex[2].append([SR, i])

        #SR 값을 각 노드에 대해 정규화
        for vertex in kcList:
            sumSR = 0
            vertex[2].sort(reverse = True)
            for n in vertex[2]:
                sumSR += n[0]

            for n in range(len(vertex[2])):
                vertex[2][n][0] = vertex[2][n][0] / sumSR

        return kcList

    def _calcSR(self, start_set:set, end_set:set, N:int) -> float:
            
        sameNum = len(start_set & end_set)
            
        #집합 사이즈 저장
        startLen = len(start_set)
        endLen = len(end_set)

        #수식 계산
        SR = 0
        if sameNum == 0:#log2에 0이 들어가면 에러뜸
            return 0
        denominator = (log2(N) - log2(min(startLen,endLen)))
        numerator = (log2(max(startLen,endLen)) - log2(sameNum)) #분자
        #분모가 0인 경우가 발생할 수 있음. 임시로 0으로 처리하는걸로 해놓음
        if denominator == 0:
            SR = 0
        else:
            SR = 1- numerator / denominator
        
        return SR 