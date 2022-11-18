import numpy as np
import pickle
index_dict = dict()
li = list()
len = 0
count =0
with open("backlinksZip", "r", encoding="utf-8") as f:
    ReadLine = f.readline
    while(True):
        count += 1
        line = ReadLine()
        if not line:
            break
        
       
        line = line.replace("\n","")
        lines = line.split("\t")

        try:
            idx = index_dict[lines[1]]
            li[idx].add(lines[2])
        except KeyError:
            index_dict[lines[1]] = len
            li.append(set())
            len += 1

            idx = index_dict[lines[1]]
            li[idx].add(lines[2])

    print("end find")

for i in index_dict.keys():
    with open("./backlinks/"+i+'_backlinks.pickle', 'wb') as outf:
        index = index_dict[i]
        pickle.dump(li[index],outf,pickle.HIGHEST_PROTOCOL)
print("all_clear")