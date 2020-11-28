f = open("199801_seg&pos.txt", "r")
ss = f.read()
ss = ss.split()
f.close()

def _key(x):
    return x[0]

f = open("dic.txt", "w")
dic_tmp = []
for i in ss:
    tmp = i
    tmp = tmp[tmp.find('[')+1 : len(tmp)]
    if(tmp.find(']') != -1):
        tmp = tmp[:tmp.find(']')]
    first = tmp[:tmp.find('/')]
    second = tmp[tmp.find('/')+1:len(tmp)]
    if second != "m":
        dic_tmp.append([first, second])
dic_tmp.sort()
dic = [dic_tmp[0]]
for i in range(1, len(dic_tmp)):
    if dic_tmp[i-1] != dic_tmp[i]:
        dic.append(dic_tmp[i])
for i in dic:
    f.write(str(i[0]) + " " + str(i[1]) +"\n")
f.close()