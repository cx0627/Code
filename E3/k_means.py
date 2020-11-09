import numpy as cp
import matplotlib.pyplot as plt

# 迭代次数
times = 2000
# 分类器数目
k=4

# 数据读入
f = open("data.txt","r")
str_data = f.read()
ss = str_data.split('\n')
m = len(ss)
str_data = str_data.split()
n = int (len(str_data) / m - 1) 
x = cp.ndarray(shape=(m , n) , dtype=float)
y = cp.ndarray(shape=(m , 1) , dtype=float)
for i in range(m):
    for j in range(n):
        x[i , j] = float (str_data[i * (n+1) + j])
    y[i] = float (str_data[i * (n+1) + n])
# print(x)

# 欧拉距离函数
def EuclideanDistance(x , y , t = n):
    cnt = 0
    for _t in range(t):
        cnt = cnt + (x[_t] - y[_t]) ** 2
    return cp.sqrt(cnt)

# 创建c mju d lamda并初始化
mju = cp.ndarray(shape=(k , n) , dtype=float)
for i in range(k):
    mju[i] = x[i]
d = cp.ndarray(shape = (m , k) , dtype = float)
c = cp.ndarray(shape = (k , m) , dtype = float)
lamda = cp.ndarray(shape = (m) , dtype = float)
for _times in range(times):
    for j in range(m):
        for i in range(k):
            c[i , j] = 0
    for j in range(m):
        lamda[j] = -1
        _min = 10000000000000000000000000.0
        for i in range(k):
            d[j , i] = EuclideanDistance(x[j] , mju[i])
            if d[j , i] < _min:
                _min = d[j , i]
                lamda[j] = i
        # print(lamda[j] , j)
        c[int(lamda[j]) , j] = 1
    for i in range(k):
        for j in range(n):
            mju[i , j] = 0
        for j in range(m):
            if c[i , j] == 1:
                mju[i] = mju[i] + x[j]
        mju[i] = mju[i] / sum(c[i])
# for i in range(k):
#     print(str(i) + ":")
#     for j in range(m):
#         if c[i , j] == 1:
#             print(j , end=' ')
#     print()
# plt.subplot()
# for j in range(m):
#     if(c[j] == 0):
#         plt.plot(x[j,0].get(),x[j,1].get(),'ro')
#     if(c[j] == 1):
#         plt.plot(x[j,0].get(),x[j,1].get(),'bo')
#     if(c[j] == 2):
#         plt.plot(x[j,0].get(),x[j,1].get(),'go')
# plt.plot(0.5,0.5,'+')
# plt.show()
cnt = 0
for i in range(m):
    for j in range(m):
        if ((lamda[i] == lamda[j]) and (y[i] == y[j])) or ((lamda[i] != lamda[j]) and (y[i] != y[j])) :
            cnt = cnt + 1
print(cnt / m / m)