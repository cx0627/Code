数据集D的经验熵$H(D)=-\sum_{k=1}^{K}\frac{|C_k|}{|D|}\log_2\frac{|C_k|}{|D|}$

计算条件A对D的条件经验熵$H(D|A)=-\sum_{i=1}^{n}\frac{|D_i|}{|D|}\sum_{k=1}^{K}\frac{|D_{ki}|}{|D_i|}\log_2\frac{|D_{ki}|}{|D_i|}$

信息增益$g(D,A)=H(D)-H(D|A)$

剪枝 损失函数$C_a(T)=C(T)+\alpha|T|=\sum_{t=1}^{|T|}N_tH_t(T)+\alpha|T|=-\sum_{t=1}^{|T|}\sum_{k=1}^{K}N_{tk}\log\frac{N_{tk}}{N_{t}}+\alpha|T|$

朴素贝叶斯估计/极大似然估计
先验概率$P(Y=c_k)$

$y=arg\max_{c_k}P(Y=c_k)\Pi_{j=1}^nP(X^{(j)}=x^{(j)}|Y=c_k)$