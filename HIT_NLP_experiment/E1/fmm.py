#Forward maximum matching
#正向最大匹配

def find(x):
    # 顺序遍历 事实证明并不可信 时间开销过大 没有一丁点实际意义
    # for i in range(dic_len):
    #     if(dic[i][0] == x):
    #         return i
    # return -1
    # 使用朴素的二分搜索
    l = int(0)
    r = int(dic_len-1)
    while l < r -1 :
        m = int ((l+r)/2)
        if dic[m][0] == x:
            return m
        if dic[m][0] > x:
            r = m - 1
        if dic[m][0] < x:
            l = m + 1
    if dic[l][0] == x:
        return l
    if dic[r][0] == x:
        return r
    return -1

f = open("dic.txt", "r")
dic_data = f.read().split()
dic = []
dic_len = int(len(dic_data) / 2)
max_len = 0
for i in range(0, len(dic_data), 2):
    dic.append([dic_data[i], dic_data[i+1]])
    max_len = max(max_len, len(dic_data[i]))
f.close()
# print(type(dic[0][0]))
f = open("199801_sent.txt", "r")
ss = f.read().split('\n')
fc = []
for i in range(len(ss)):
    fc.append([])
    start = 0
    flag = 0
    cnt = ""
    for j in range(len(ss[i])):
        if j < start :
            continue
        flag = 0
        for k in range(min(max_len, len(ss[i]) - j), 0, -1):
            _find = find(ss[i][j:j+k])
            if _find != -1:
                if(cnt != ""):
                    fc[i].append(cnt + '/uk')
                    cnt = ""
                start = j + k
                for l in range(k):
                    cnt = cnt + ss[i][j+l]
                cnt = cnt + '/' + dic[_find][1]
                flag = 1
                fc[i].append(cnt)
                cnt = ""
                break
        if flag == 0:
            cnt = cnt + ss[i][j]
    if(cnt != ""):
        fc[i].append(cnt + '/uk')
    if i % 100 == 0:
        print(i)
f.close()
f = open("seg_FMM.txt", "w")
for i in range(len(fc)):
    for j in range(len(fc[i])):
        f.write(fc[i][j] + ' ')
    f.write("\n")
f.close()