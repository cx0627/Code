import numpy as cp
import matplotlib.pyplot as plt

# 迭代次数
times = 1
# 分类器数目
k=3

# 数据读入
f = open("data.txt","r")
str_data = f.read()
ss = str_data.split('\n')
m = len(ss)
str_data = str_data.split()
n = int (len(str_data) / m - 1) 
n = n + 1
print(n,m)
x = cp.ndarray(shape=(m , n) , dtype=float)
y = cp.ndarray(shape=(m , 1) , dtype=float)
for i in range(m):
    for j in range(n):
        x[i , j] = float (str_data[i * (n) + j])
    # y[i] = float (str_data[i * (n+1) + n])
print(x)

# 高斯分布函数
def P(x , mju , sigma):
    delta = cp.add(x , -1 * mju)
    R = -0.5 * cp.dot(cp.dot(delta.T , cp.linalg.inv(sigma)) , delta)
    S = cp.power((2 * cp.pi) , n/2) * cp.sqrt(cp.linalg.det(sigma))
    return cp.exp(R) / S

# 创建alpha mju gamma sigma并初始化
alpha = cp.ndarray(shape = (k , 1) , dtype = float)
for i in range(k):
    alpha[i , 0] = 1/k
gamma = cp.ndarray(shape=(m , k) , dtype=float)
mju = cp.ndarray(shape=(k , n) , dtype=float)
# for i in range(k):
#     mju[i] = x[i]
mju[0] = x[5]
mju[1] = x[21]
mju[2] = x[26]
sigma = cp.ndarray(shape=(k , n , n) , dtype=float)
for i in range(k):
    sigma[i] = cp.eye(n) *0.1

for _times in range(times):
    # print(_times)
    for j in range(m):
        sum = 0.0
        for i in range(k):
            # print(j,i)
            # print(mju[i].T)
            sum = sum + alpha[i , 0] * P(x[j].T , mju[i].T , sigma[i])
        for i in range(k):
            gamma[j , i] = alpha[i , 0] * P(x[j].T , mju[i].T , sigma[i]) / sum
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print (gamma)
    for i in range(k):
        sum1 = cp.zeros(shape = (1 , n) , dtype = float)
        sum2 = 0
        for j in range(m):
            sum1 = cp.add(sum1 , gamma[j , i] * x[j])
            sum2 = sum2 + gamma[j , i]
        mju[i] = (sum1 / sum2) . reshape(n)
        sum = cp.zeros(shape = (n , n) , dtype = float)
        for j in range(m):
            delta = cp.subtract(x[j] , mju[i]).reshape(1 , n)
            sum = cp.add(sum , gamma[j , i] * cp.dot(delta.T , delta))
        sigma[i] = sum / sum2
        alpha[i] = sum2 / m
    print (mju)
    print (sigma)
    print (alpha)
c = cp.ndarray(shape = (m) , dtype = int)
for j in range(m):
    cnt = 0
    ans = -1
    for i in range(k):
        if alpha[i , 0] * P(x[j].T , mju[i].T , sigma[i]) > cnt:
            cnt = alpha[i] * P(x[j].T , mju[i].T , sigma[i])
            ans = i
    c[j] = ans
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
        if ((c[i] == c[j]) and (y[i] == y[j])) or ((c[i] != c[j]) and (y[i] != y[j])) :
            cnt = cnt + 1
print(cnt / m / m)