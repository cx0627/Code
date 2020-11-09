import numpy as np
import matplotlib.pyplot as plt

label_or_not = True

times = 20
n_of_x = 0
m_of_X = 0
K = 0
filename = "data.txt"

#读数据
f = open(filename, "r")
string = f.readline()
temp = string.split()
m_of_X = int(temp[0])
n_of_x = int(temp[1])
K = int(temp[2])
D = np.empty(shape = (m_of_X, n_of_x), dtype = float)
Y = np.empty(shape = (m_of_X), dtype = str)
temp_cnt = 0
for i in range(m_of_X):
    string = f.readline()
    temp = string.split()
    for j in range(n_of_x):
        D[i, j] = float(temp[j])
    if(label_or_not):
        Y[i] = temp[n_of_x]



def prob_Gauss(x, mju, sigma):           #高斯分布函数在x点处的概率，参数为mju和sigma
    return np.exp(-1.0 / 2 * np.dot(np.dot((x - mju), np.linalg.inv(sigma)), (x - mju).T)) / (np.power((2 * np.pi), n_of_x / 2) * np.sqrt(np.linalg.det(sigma)))

def EM():       #EM算法，D为样本集，K为高斯混合分成的个数
    alpha = np.ones(shape = (K, 1), dtype = float) / K
    mju = np.empty(shape = (K, n_of_x), dtype = float)
    sigma = np.empty(shape = (K, n_of_x, n_of_x), dtype = float)
    gamma = np.empty(shape = (m_of_X, K), dtype = float)

    for i in range(K):
        sigma[i] = np.eye(n_of_x) * 0.1

    # mju = np.matrix([[0.403, 0.237], [0.714, 0.346], [0.532, 0.472]])
    
    for i in range(K):
        mju[i] = D[i]

    cnt = 0   #迭代次数
    while True:
        print(cnt)
        #E步
        for j in range(m_of_X):
            for i in range(K):
                temp_fz = alpha[i, 0] * prob_Gauss(np.matrix(D[j,:]), np.matrix(mju[i,:]), sigma[i])
                temp_fm = 0;
                for a in range(K):
                    temp_fm += alpha[a, 0] * prob_Gauss(np.matrix(D[j,:]), np.matrix(mju[a,:]), sigma[a])
                gamma[j, i] = temp_fz / temp_fm
        # print(gamma)
        #M步
        for i in range(K):
            
            #更新mju
            temp_fz = np.zeros(shape = (1, n_of_x), dtype = float)
            for j in range(m_of_X):
                temp_fz += gamma[j, i] * np.matrix(D[j,:])
            temp_fm = 0
            for j in range(m_of_X):
                temp_fm += gamma[j, i]
            mju[i] = temp_fz / temp_fm

            #更新sigma
            temp_fz = np.zeros(shape = (n_of_x, n_of_x), dtype = float)
            for j in range(m_of_X):
                temp_fz += gamma[j, i] * np.dot((np.matrix(D[j,:]) - np.matrix(mju[i,:])).T, (np.matrix(D[j,:]) - np.matrix(mju[i,:])))
            sigma[i:] = temp_fz / temp_fm

            #更新alpha
            alpha[i, 0] = temp_fm / m_of_X
        # print(mju)
        # print(sigma)
        # print(alpha)
        cnt += 1
        if(cnt >= times):
            break
    label = np.zeros(shape = (m_of_X), dtype = int)
    for i in range(m_of_X):
        temp_label = 0
        temp_prob = 0
        for j in range(K):
            if(gamma[i, j] > temp_prob):
                temp_prob = gamma[i, j]
                temp_label = j
        label[i] = temp_label

    plt.subplot()
    for j in range(m_of_X):
        if label[j] == 0:
            plt.plot(D[j, 0], D[j, 1], 'ro')
        if label[j] == 1:
            plt.plot(D[j, 0], D[j, 1], 'go')
        if label[j] == 2:
            plt.plot(D[j, 0], D[j, 1], 'bo')
    # plt.plot(0.5,0.5,'+')
    plt.show()

    cnt = 0
    for i in range(m_of_X):
        for j in range(m_of_X):
            if((label[i] == label[j]) & (Y[i] is Y[j] )) | ((label[i] != label[j]) & (not(Y[i] is Y[j] ))):
                cnt += 1

    print("EM算法的Rand指数为：" + str(cnt / m_of_X / m_of_X))


def get_dis(x, mju):
    num = x.shape[1]
    temp = 0.0
    for i in range(num):
        temp += (x[0, i] - mju[0, i])**2
    return np.sqrt(temp)


def K_Means():           #K-Means算法
    label = np.empty(shape = (m_of_X, 1), dtype = int)
    mju = np.empty(shape = (K, n_of_x), dtype = float)
    for i in range(K):
        mju[i] = D[i]

    # mju = np.matrix([[0.403, 0.237], [0.714, 0.346], [0.532, 0.472]])

    cnt = 0;
    while True:
        print(cnt)
        C = np.zeros(shape = (K), dtype = int)
        label = np.empty(shape = (m_of_X), dtype = int)
        for j in range(m_of_X):
            d = 1.0e10
            temp_label = 0
            for i in range(K):
                if(get_dis(np.matrix(D[j,:]), np.matrix(mju[i,:])) < d):
                    d = get_dis(np.matrix(D[j,:]), np.matrix(mju[i,:]))
                    temp_label = i
            label[j] = temp_label
            C[temp_label] += 1

        #更新mju
        for i in range(K):
            temp = np.zeros(shape = (n_of_x), dtype = float)
            for a in range(m_of_X):
                if(label[a] == i):
                    temp += D[a,:]
            mju[i] = temp / C[i]
        cnt += 1
        if(cnt >= times):
            break
    plt.subplot()
    for j in range(m_of_X):
        if label[j] == 0:
            plt.plot(D[j, 0], D[j, 1], 'ro')
        if label[j] == 1:
            plt.plot(D[j, 0], D[j, 1], 'go')
        if label[j] == 2:
            plt.plot(D[j, 0], D[j, 1], 'bo')
    # plt.plot(0.5,0.5,'+')
    plt.show()

    cnt = 0
    for i in range(m_of_X):
        for j in range(m_of_X):
            if((label[i] == label[j]) & (Y[i] is Y[j] )) | ((label[i] != label[j]) & (not(Y[i] is Y[j] ))):
                cnt += 1

    print("K_Means算法的Rand指数为：" + str(cnt / m_of_X / m_of_X))     


EM()
K_Means()

