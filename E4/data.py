import numpy as np

n = 10
m = 10
k = 3
y = (np.random.randn(k)+10 ) 
y[0] = 0
x = np.random.normal(loc = np.random.randn(k) , scale = y , size = (n , m , k))
# print(x)
f = open("data.txt","w")
# def generate_data(data_size , seed = 20):
#     np.random.seed(seed)
#     mean = [1, 1, 1]
#     cov = [[1, 0, 0], [0, 1, 0], [0, 0, 0]]
#     data = np.random.multivariate_normal(mean, cov, data_size)
#     return data

# data = generate_data(10)
f.write(str(str(n)+' '+str(m)+' '+str(k)+'\n'))
for i in range(n):
    for j in range(m):
        for l in range(k):
            f.write(str(x[i, j, l]) + ' ')
        f.write('\n')
f.close()