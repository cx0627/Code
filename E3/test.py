# import numpy as np
# from numpy.linalg import cholesky
# import matplotlib.pyplot as plt
 
# sampleNo = 1000;
# # 一维正态分布
# # 下面三种方式是等效的
# mu = 3
# sigma = 0.1
# np.random.seed(0)
# s = np.random.normal(mu, sigma, sampleNo )
# plt.subplot(141)
# plt.hist(s, 30, density=True)
 
# np.random.seed(0)
# s = sigma * np.random.randn(sampleNo ) + mu
# plt.subplot(142)
# plt.hist(s, 30, density=True)
 
# np.random.seed(0)
# s = sigma * np.random.standard_normal(sampleNo ) + mu
# plt.subplot(143)
# plt.hist(s, 30, density=True)
 
# # 二维正态分布
# mu = np.array([[1, 5]])
# Sigma = np.array([[1, 0.5], [1.5, 3]])
# R = cholesky(Sigma)
# print(R)
# s = np.dot(np.random.randn(sampleNo, 2), R) + mu
# # s = np.random.randn(1000 , 3)
# print(s)
# plt.subplot(144)
# # 注意绘制的是散点图，而不是直方图
# plt.plot(s[:,0],s[:,1],'+')
# plt.show()

import cupy as cp
x = cp.ndarray(shape=(3,2))
x[0,0]=1
x[0,1]=2
x[1,0]=4
x[1,1]=6
x[2,0]=3
x[2,1]=6
print(x)
y = cp.ndarray(shape=(1,3))
y[0,0]=1
y[0,1]=2
y[0,2]=2
# print(cp.divide(x , y.T))
# print(cp.dot(x,cp.ones(shape=(2,1) ,  dtype=float)))
x[:,1]=y.reshape(3)
print(x)