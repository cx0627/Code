import numpy as np

cnt = 0
B = int(0)
E = int(1)
M = int(2)
S = int(3)

def find(x):
    if(x in char):
        return char[x]
    return char["unknown"]

def viterbi(a, b, pi, o):
    T = len(o)
    N = 4
    weight = np.ndarray(shape=(T,N),dtype=float)
    path = np.ndarray(shape=(T,N),dtype=int)
    p = np.ndarray(shape=(T),dtype=int)
    if T == 0:
        return p
    for i in range(N):
        weight[0,i] = pi[i] * b[i,find(o[0])]
        path[0,i] = 0
    for t in range(1,T,1):
        cnt = 0
        argm = -1
        for i in range(N):
            for j in range(N):
                if weight[t-1 , j]*a[j,i]>cnt:
                    cnt = weight[t-1 , j]*a[j,i]
                    argm = j
            weight[t,i] = cnt * b[i,find(o[t])]
            path[t,i] = argm
    if weight[T-1,M] > weight[T-1,S] :
        p[T-1] = M
    else:
        p[T-1] = S
    i = T - 2
    while i>=0:
        p[i] = path[i+1,int(p[i+1])]
        i = i-1
        # print(i)
    return p

def readin():
    f = open("199801_seg&pos.txt", "r")
    dic_data = f.read().split('\n')
    f.close()
    dic = []
    char = {}
    cnt = 0
    for i in range(len(dic_data)):
        for j in dic_data[i].split():
            tmp = j
            tmp = tmp[tmp.find('[')+1 : len(tmp)]
            if(tmp.find(']') != -1):
                tmp = tmp[:tmp.find(']')]
            first = tmp[:tmp.find('/')]
            second = tmp[tmp.find('/')+1:len(tmp)]
            for k in first:
                if not (k in char):
                    cnt = cnt + 1
                    char[k] = cnt
            dic.append(first)
    cnt = cnt + 1
    char["unknown"] = cnt
    return dic,char

def count(dic , char):
    ml = int(len(char) - 1)
    a = np.ndarray(shape = (4, 4) , dtype = float)
    b = np.ndarray(shape = (4, ml+100) , dtype = float)
    pi = np.ndarray(shape = (4) , dtype = float)
    for i in range(4):
        pi[i] = 0
        for j in range(4):
            a[i,j] = 0
    for i in range(4):
        for j in range(ml+10):
            b[i,j] = 0
    for i in range(len(dic)):
        if len(dic[i]) == 1:
            pi[S] = pi[S] + 1
            if i>0:
                if len(dic[i-1]) == 1:
                    a[S,S] = a[S,S] + 1
                else:
                    a[M][S] = a[M][S] + 1
            b[S,char[dic[i][0]]] = b[S,char[dic[i][0]]] + 1
        else:
            pi[B] = pi[B] + 1
            if i>0:
                if len(dic[i-1]) == 1:
                    a[S,B] = a[S,B] + 1
                else:
                    a[M,B] = a[M,B] + 1
            for j in range(len(dic[i])):
                # print(b[M,char[dic[i][j]]] , j)
                if j == 0:
                    b[B,char[dic[i][0]]] = b[B,char[dic[i][0]]] + 1
                elif j == int(len(dic[i]) - 1):
                    b[M,char[dic[i][j]]] = b[M,char[dic[i][j]]] + 1
                else:
                    b[E,char[dic[i][j]]] = b[E,char[dic[i][j]]] + 1
                if 1<j and j<int(len(dic[i]) - 2):
                    a[E,E] = a[E,E] + 1
                if 0<j and j<int(len(dic[i]) - 2):
                    a[B,E] = a[B,E] + 1
                if 1<j and j<int(len(dic[i]) - 1):
                    a[E,M] = a[E,M] + 1
            if len(dic[i]) == 2:
                a[B,M] = a[B,M] + 1
                    
    suma = np.ndarray(shape = (4) , dtype = float)
    sumb = np.ndarray(shape = (ml+100) , dtype = float)
    for i in range(4):
        suma[i] = 0
        for j in range(4):
            suma[i] = suma[i] + a[i,j]
    for j in range(ml):
        sumb[j] = 0
        for i in range(4):
            sumb[j] = sumb[j] + b[i,j]
    for i in range(4):
        for j in range(4):
            if suma[i]>0:
                a[i,j] = a[i,j] / suma[i]
    pi = pi / sum(pi)
    for i in range(4):
        for j in range(ml):
            if sumb[j] > 0:
                b[i,j] = b[i,j] / sumb[j]
    for i in range(4):
        b[i,char["unknown"]] = np.mean(b[i,])
    return a,b,pi

dic,char = readin()
a,b,pi = count(dic,char)
f = open("test_sent.txt","r")
ss = f.read().split('\n')
f.close()
f=open("seg_LM.txt","w")
f.write(str(a))
f.write("\n")
f.write(str(b))
f.write("\n")
f.write(str(pi))
f.write("\n")
for i in range(100):
    p = viterbi(a,b,pi,ss[i])
    # print(p)
    for j in range(len(p)):
        f.write(ss[i][j])
        if (p[j] == M) or (p[j] == S):
            f.write('/ ')
    f.write("\n")
    if(i%100 == 0):
        print(i)
f.close()
