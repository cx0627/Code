import cupy as cp

doc = ["no-recurrence-events","recurrence-events","?","10-19","20-29",
"30-39","40-49","50-59","60-69","70-79",
"80-89","90-99","?","lt40","ge40",
"premeno","?","0-4","5-9","10-14",
"15-19","20-24","25-29","30-34","35-39",
"40-44","45-49","50-54","55-59","?",
"0-2","3-5","6-8","9-11","12-14",
"15-17","18-20","21-23","24-26","27-29",
"30-32","33-35","36-39","?","yes",
"no","?","1","2","3",
"?","left","right","?","left-up",
"left-low","right-up","right-low","central","?"]
index = [0,0,0,1,1,
1,1,1,1,1,
1,1,1,2,2,
2,2,3,3,3,
3,3,3,3,3,
3,3,3,3,3,
4,4,4,4,4,
4,4,4,4,4,
4,4,4,4,4,
4,4,4,4,5,
5,5,6,6,6,
6,7,7,7,8,
8,8,8,8,8]

f = open("breast-cancer.data","r")
M = 60
test_size = 86
fstr = f.read()
fstr = fstr.split('\n')
data_size = len(fstr)
data = cp.ndarray(shape = (data_size , M) , dtype = float )
y = cp.ndarray(shape = (data_size , 1) , dtype = float )
for i in range(data_size) :
    for j in range(M):
        data[i,j] = 0
for i in range(data_size) :
    ss = fstr[i].split(',')
    for j in range(M):
        if(ss[index[j]] == doc [j]) :
            data[i,j]=1
    if ss[9] == "yes" :
        y[i] = 1
    else :
        y[0] = 0
f.close()
cnt = 0
vis = cp.ndarray(shape =(data_size) , dtype = int)
while(cnt < test_size) :
    random_x = cp.random.randint(0 , data_size)
    if(vis[random_x] == 0) :
        vis[random_x] = 1
        cnt = cnt + 1
f = open("data.txt","w")
f.write(str(data_size - test_size)+" "+str(M)+"\n")
# f.write(str(data_size)+" "+str(M)+"\n")
for i in range(data_size) :
    if vis[i] == 1 :
        continue
    for j in range(M):
        f.write(str(data[i,j])+' ')
    f.write(str(y[i,0])+"\n")
f.write(str(test_size)+" "+str(M)+"\n")
for i in range(data_size) :
    if vis[i] == 0 :
        continue
    for j in range(M):
        f.write(str(data[i,j])+' ')
    f.write(str(y[i,0])+"\n")
