import numpy as np

# n = 100
# m = 100
# k = 2
# y = (np.random.randn(k)+10 ) 
# y[0] = 0
# x = np.random.normal(loc = np.random.randn(k) , scale = y , size = (n , m , k))
# print(x)

def generate_data(data_size , seed = 20):
    np.random.seed(seed)
    mean = [1, 1, 1]
    cov = [[0.01, 0, 0], [0, 1, 0], [0, 0, 0.5]]
    data = np.random.multivariate_normal(mean, cov, data_size)
    return data

data = generate_data(10)
print(data)