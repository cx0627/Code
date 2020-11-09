import cupy as cp
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

# 中心化
def zeroMean(dataMat):      
    meanVal=np.mean(dataMat,axis=0)     #按列求均值，即求各个特征的均值
    newData=dataMat-meanVal
    return newData,meanVal

# Pca
def pca(dataMat,n):
    newData,meanVal=zeroMean(dataMat)
    covMat=np.cov(newData,rowvar=0)    #求协方差矩阵,return ndarray；若rowvar非0，一列代表一个样本，为0，一行代表一个样本
    eigVals,eigVects=np.linalg.eig(np.mat(covMat))#求特征值和特征向量,特征向量是按列放的，即一列代表一个特征向量
    eigValIndice=np.argsort(eigVals)            #对特征值从小到大排序
    n_eigValIndice=eigValIndice[-1:-(n+1):-1]   #最大的n个特征值的下标
    n_eigVect=eigVects[:,n_eigValIndice]        #最大的n个特征值对应的特征向量
    lowDDataMat=newData*n_eigVect               #低维特征空间的数据
    reconMat=(lowDDataMat*n_eigVect.T)+meanVal  #重构数据
    return lowDDataMat,reconMat

I = mpimg.imread('./wed.jpg')#读取图片
image_shape = I.shape
# n , m 表示数据的像素点的长宽
m = image_shape[0]
n = image_shape[1]
# k 表示 像素点的颜色 黑白是1 彩色（RGB）一般是3 
if len(image_shape) == 3:
    k = image_shape[2]
else:
    k=1
print(image_shape)
print(m, n, k)
print(np.array(I).shape)
print(type(I[0,0,0]))
x = np.ndarray(shape=(m, n, k) , dtype = float , buffer = I*1.0)
print(n , m , k)

# 压缩后的维度
d = 20
rM = np.ndarray(shape=(m , n , k) , dtype = float)
for i in range(k):
    lowDDataMat,reconMat = pca (I[ :, :, i] , d)
    rM[:, :, i] = np.real(reconMat)/255
plt.imshow(rM)
plt.show()
# 计算信噪比
sum = 0
for i in range(m):
    for j in range(n):
        sum = sum + (np.abs(reconMat[i,j]-x[i,j])**2)
sum = sum / n / m
print(0)
print(20*np.log10(n/np.sqrt(sum)))