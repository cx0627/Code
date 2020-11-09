f = open("iris.data","r")
ss=f.read().split()
f.close()
f = open("data.txt","w")
for j in range(150):
    x=ss[j].split(',')
    print(x)
    for i in range(4):
        f.write(x[i])
        f.write(' ')
    if x[4] == "Iris-setosa" :
        f.write("0\n")
    elif x[4] == "Iris-versicolor" :
        f.write("1\n")
    elif x[4] == "Iris-virginica" :
        f.write("2\n")
    else :
        f.write("3\n")

f.close()