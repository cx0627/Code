f = open("199801_seg&pos.txt", "r")
s = f.read().split('\n')
f.close()
f = open("seg_FMM.txt", "r")
s1 = f.read().split('\n')
f.close()
f = open("seg_BMM.txt", "r")
s2 = f.read().split('\n')
f.close()

f = open("score.txt","w")
tp = fp = tn = fn = 0
fl = []
for i in range(len(s)):
    fl.append([])
    for j in s[i].split():
        tmp = j
        tmp = tmp[tmp.find('[')+1 : len(tmp)]
        if(tmp.find(']') != -1):
            tmp = tmp[:tmp.find(']')]
        first = tmp[:tmp.find('/')]
        second = tmp[tmp.find('/')+1:len(tmp)]
        sj = first
        for k in range(len(sj)-1):
            fl[i].append(0)
        fl[i].append(1)
fl1 = []
for i in range(len(s1)):
    fl1.append([])
    for j in s1[i].split():
        tmp = j
        tmp = tmp[tmp.find('[')+1 : len(tmp)]
        if(tmp.find(']') != -1):
            tmp = tmp[:tmp.find(']')]
        first = tmp[:tmp.find('/')]
        second = tmp[tmp.find('/')+1:len(tmp)]
        sj = first
        for k in range(len(sj)-1):
            fl1[i].append(0)
        fl1[i].append(1)
fl2 = []
for i in range(len(s2)):
    fl2.append([])
    for j in s2[i].split():
        tmp = j
        tmp = tmp[tmp.find('[')+1 : len(tmp)]
        if(tmp.find(']') != -1):
            tmp = tmp[:tmp.find(']')]
        first = tmp[:tmp.find('/')]
        second = tmp[tmp.find('/')+1:len(tmp)]
        sj = first
        for k in range(len(sj)-1):
            fl2[i].append(0)
        fl2[i].append(1)

tp = fp = tn = fn = 0
for i in range(len(fl)):
    for j in range(len(fl[i])):
        if(fl[i][j]==1)and(fl1[i][j]==1):
            tp = tp + 1
        if(fl[i][j]==1)and(fl1[i][j]==0):
            fn = fn + 1
        if(fl[i][j]==0)and(fl1[i][j]==1):
            fp = fp + 1
        if(fl[i][j]==0)and(fl1[i][j]==0):
            tn = tn + 1
f.write(str((tp/(tp+fp) , tp/(tp+fn) , 2*tp/(2*tp+fp+fn))) + '\n')
tp = fp = tn = fn = 0
for i in range(len(fl)):
    for j in range(len(fl[i])):
        if(fl[i][j]==1)and(fl2[i][j]==1):
            tp = tp + 1
        if(fl[i][j]==1)and(fl2[i][j]==0):
            fn = fn + 1
        if(fl[i][j]==0)and(fl2[i][j]==1):
            fp = fp + 1
        if(fl[i][j]==0)and(fl2[i][j]==0):
            tn = tn + 1
f.write(str((tp/(tp+fp) , tp/(tp+fn) , 2*tp/(2*tp+fp+fn))) + '\n')