import cupy as cp

#超参数区
alpha = 0.005 #学习率
times = 100000 #迭代次数
lambd = 0.001 #正则系数 为0表示不带正则项

#sigmoid函数
def g (Z) :
    return 1/(1 + cp.exp(-Z))

#损失函数
def loss(W , X , Y) :
    y_hat = g (cp.dot(W.t , X))
    return - (cp.dot (Y.T , cp.log(y_hat)) + cp.dot( (1 - Y).T , cp.log(1 - y_hat)))

#梯度下降 带正则项
def gradient_descent (x , y , w , time=times , mod=100000 ) :
    # print (mod)
    # print (time)
    for i in range(time) :
        y_hat = g (cp.dot(x , w))
        w = cp.add(w , -1 * alpha / data_size * cp.add (cp.dot(x.T , cp.add(y_hat , -1 * y)) , lambd  * w) )
        if (i+1)%mod==0 :
            print ('Results of the ', end='')
            print(i+1, end='')
            print('th iteration :' , end='')
            print((-1 * cp.add(cp.dot(y.T , cp.log(y_hat)) , cp.dot((1-y.T) , cp.log(1-y_hat))) + lambd / 2 * cp.dot(w.T ,w)) / data_size)
    return w

#随机初始化
def random_initialization (p , q) :
    w = cp.ndarray(shape=(p , q) , dtype = float)
    for i in range(p) :
        for j in range (q) :
            w[i,j] = cp.random.random()*0.01
    return w

#读入数据
f = open("data.txt","r")
str = f.readline()
ss = str.split()
data_size = int(ss[0])
M = int(ss[1]) + 1
x_train = cp.ndarray (shape = (data_size , M) , dtype = float)
y_train = cp.ndarray (shape = (data_size , 1) , dtype = float)
for i in range(data_size) :
    str = f.readline()
    ss = str.split()
    for j in range(M-1) :
        x_train[i,j] = float(ss[j]);
    y_train[i,0] = float(ss[M-1])
    x_train[i,M-1]= 1
str = f.readline()
ss = str.split()
test_size = int(ss[0])
M = int(ss[1]) + 1
x_test = cp.ndarray (shape = (test_size , M) , dtype = float)
y_test = cp.ndarray (shape = (test_size , 1) , dtype = float)
for i in range(test_size) :
    str = f.readline()
    ss = str.split()
    for j in range(M-1) :
        x_test[i,j] = float(ss[j]);
    y_test[i,0] = float(ss[M-1])
    x_test[i,M-1]= 1
print(M , data_size , test_size)

#进行梯度下降 其中w初始值为随机初始化的结果
w = gradient_descent (x_train , y_train , random_initialization(M , 1) )
cnt=0
for i in range(test_size) :
    if(g(cp.dot(x_test[i] , w)) < 0.5) :
        flag=0
    else :
        flag=1
    if(flag == y_test[i,0]) :
        cnt = cnt + 1
#输出准确率
print(cnt/test_size)