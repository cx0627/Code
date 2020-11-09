import numpy as np

n = 100
m = 100
k = 2
y = (np.random.randn(k)+10 ) 
y[0] = 0
x = np.random.normal(loc = np.random.randn(k) , scale = y , size = (n , m , k))
print(x)