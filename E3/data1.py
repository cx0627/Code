import numpy as cp
import numpy as np
import matplotlib.pyplot as plt

f = open("data.txt" , "w")

# 二维正态分布
mu = cp.array([[1, 5]])
Sigma = cp.array([[1, 0.5], [1.5, 3]])
R = cp.linalg.cholesky(Sigma)
print(R)
s = cp.dot(cp.random.randn(50, 2), R) + mu
for j in range(50):
    f.write(str(s[j , 0]) + ' ' + str(s[j , 1]) + ' ' + str(0) + '\n')
plt.subplot(144)
# 注意绘制的是散点图，而不是直方图
plt.plot(s[:,0],s[:,1],'ro')
# plt.show()

# 二维正态分布
mu = cp.array([[2, 10]])
Sigma = cp.array([[1.2, 5], [1.5, 7]]) * 0.5
R = cp.linalg.cholesky(Sigma)
print(R)
s = cp.dot(cp.random.randn(50, 2), R) + mu
for j in range(50):
    f.write(str(s[j , 0]) + ' ' + str(s[j , 1]) + ' ' + str(1) + '\n')
plt.plot(s[:,0],s[:,1],'go')
    
# 二维正态分布
mu = cp.array([[3, 3]])
Sigma = cp.array([[2 , 3], [1.5, 3]]) * 0.6
R = cp.linalg.cholesky(Sigma)
print(R)
s = cp.dot(cp.random.randn(50, 2), R) + mu
for j in range(50):
    f.write(str(s[j , 0]) + ' ' + str(s[j , 1]) + ' ' + str(2) + '\n')
plt.plot(s[:,0],s[:,1],'bo')
    
# 二维正态分布
mu = cp.array([[6.5, 1]])
Sigma = cp.array([[1, 0.5], [2, 4.5]])
R = cp.linalg.cholesky(Sigma)
print(R)
s = cp.dot(cp.random.randn(50, 2), R) + mu
for j in range(50):
    f.write(str(s[j , 0]) + ' ' + str(s[j , 1]) + ' ' + str(3) + '\n')
plt.plot(s[:,0],s[:,1],'yo')
plt.show()