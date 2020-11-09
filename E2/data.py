import cupy as cp

n = 50000 # 学习集组数
y_div = 0.5
d = 3 # 特征值维度
m = 10000 #测试集组数

f = open("data.txt" , "w")
print (f)

#输出学习集
f.write (str(n) + " " + str(d) + "\n")
for i in range (n) :
    x = cp.random.random (d)
    for j in range (d) :
        f.write (str(x[j]) +' ')
    if(sum (x) < d * y_div) :
        f.write ("0\n")
    else:
        f.write ("1\n")

#输出测试集
f.write (str(m) + " " + str(d) + "\n")
for i in range (m) :
    x = cp.random.random (d)
    for j in range (d) :
        f.write (str(x[j]) +' ')
    if(sum (x) < d * y_div) :
        f.write ("0\n")
    else:
        f.write ("1\n")
f.close()