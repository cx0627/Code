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
    for j in range(len(s[i])):
        sj = s[i][j][:s[i][j].find('/')]
        for k in range(len(sj)-1):
            fl[i].append(0)
        fl[i].append(1)
