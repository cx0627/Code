import cupy as cp
import matplotlib as plt
import matplotlib.pyplot as plt
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0" #指定使用0号cpu

#超参数
left_boundary = 0 #左边界
right_boundary = 1 #右边界
data_size = 10 #训练集个数
data_scale = 0.15 #训练集噪声
test_size = 100 #测试集个数
test_scale = 0 #测试集噪声
data_seed = 42 #随机种子
M = 5 #高阶函数维度
lambd = 0.001 #正则系数
alpha = 0.0005 #学习率
times = 50000 #迭代次数

#等距离生成数据
def uniform(left,right,size):
    x = cp.linspace(left,right,size)
    return x.reshape(size,1)

#生成随机数据
def create_data(dscale,size):
    x = uniform(left_boundary,right_boundary,size)
    cp.random.seed(data_seed)
    y = sin_fun(x)+cp.random.normal(scale=dscale, size=x.shape)
    return x,y

#返回sin(2*pi*x)
def sin_fun(x):
    return cp.sin(2*cp.pi*x)

#返回解析解 不带正则项
def least_square(X , Y) :
    return  cp.dot(cp.dot(cp.linalg.inv(cp.dot(X.T , X)) , X.T) , Y)

#返回解析解 带正则项
def least_square_regular(X , Y) :
    return  cp.dot(cp.dot(cp.linalg.inv( cp.add(cp.dot(X.T , X) , lambd*cp.eye(M, k = 0) ) ) , X.T) , Y)

#生成范德蒙行列式
def vandermonde(X , M) :
    xx = cp.ndarray(shape=( cp.size(X), M) , dtype=float)
    for i in range(cp.size(X)) :
        cnt = 1.0
        for j in range(M) :
            xx [i,j] = float(cnt)
            cnt = cnt * X[i]
    return xx

#随机初始化
def random_initialization (p , q) :
    w = cp.ndarray(shape=(p , q) , dtype = float)
    for i in range(p) :
        for j in range (q) :
            w[i,j] = cp.random.random()*0.01
    return w

#梯度下降 带正则项
def gradient_descent (x , y , w , time=times , mod=100000 ) :
    # print (mod)
    # print (time)
    for i in range(time) :
        w=cp.add(w , -1 * alpha * cp.add(cp.dot(x.T , cp.add (cp.dot(x,w) , -1*y) ) , lambd*w) )
        if i%mod==0 :
            print ('Results of the '+str(i)+'th iteration :'+
            str(cp.add( cp.dot(cp.add(cp.dot(x ,  w) , -1*y).T , cp.add(cp.dot(x ,  w) , -1*y)) / 2 , lambd / 2 * cp.dot(w.T , w))[0,0]))
            print ()
    return w

#生成损失函数
def loss( x, y, w):
    diff = cp.add(cp.dot(x , w) , -1 * y) 
    loss = 1.0/(2*data_size)*cp.dot(diff.T , diff)
    return loss[0,0]

#梯度函数
def gradient_function(x, y, w):
    return (1.0/M) *( cp.add(cp.add(cp.dot(cp.dot(x.T , x) , w) ,-1* cp.dot(x.T , y)) , 0.001 * w))

# 共轭梯度法
def conjugate_gradient(x, y):
    Q = (1 / M) * cp.add(cp.dot(x.T , x) , lambd * cp.eye(M))
    w = cp.zeros(M).T
    r = -gradient_function(x, y, w)
    p = r
    count = 0
    for i in range(M):
        count += 1
        a = (cp.dot(r.T , r)[0,0] / cp.dot(cp.dot(p.T , Q) , p)[0,0])
        r_prev = r
        w = cp.add(w , cp.dot(a , p))
        r = cp.add(r , -1 * cp.dot(cp.dot(a , Q) , p))
        p = cp.add(r , (cp.dot(r.T , r)[0,0] / cp.dot(r_prev.T , r_prev)[0,0]) * p)
    return w

#根据w绘图
def draw( w ) :
    plt.scatter(x_train.get(),y_train.get(),facecolor="none", edgecolor="b", s=50, label="training data")
    plt.plot(x_test.get(),cp.dot(vandermonde (x_test , M) , w).get(),c="r",label="fitting")
    plt.plot(x_test.get(),y_test.get(),c="g",label="$\sin(2\pi x)$")
    plt.legend()
    plt.show()

#生成训练接
x_train,y_train = create_data(data_scale,data_size)
#生成测试集
x_test,y_test = create_data(test_scale,test_size)

#解析解的w
# w = least_square (vandermonde (x_train , M), y_train)
#解析解带正则项的w
w = least_square_regular (vandermonde (x_train , M), y_train)
#梯度下降的w
# w = gradient_descent (vandermonde (x_train , M) , y_train , random_initialization(M , 1))
#共轭梯度的w
# w = conjugate_gradient(vandermonde (x_train , M) , y_train)
print(w)
draw(w)