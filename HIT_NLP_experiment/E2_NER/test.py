# -*- coding:utf-8 -*-
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim

torch.manual_seed(1)


def argmax(vec):
    # return the argmax as a python int
    # 返回向量中最大值的索引位置
    _, idx = torch.max(vec, 1)
    return idx.item()


def prepare_sequence(seq, to_ix):
    # 返回序列中节点对应的索引
    idxs = [to_ix[w] for w in seq]
    return torch.tensor(idxs, dtype=torch.long)


# Compute log sum exp in a numerically stable way for the forward algorithm
# 在前向传播算法中，更鲁棒地计算log_sum_exp，防止计算上溢
def log_sum_exp(vec):
    # vec: (1, 5), type: Variable
    # max_score: (1)
    max_score = vec[0, argmax(vec)]
    # max_score_broadcast: (1, 5)
    max_score_broadcast = max_score.view(1, -1).expand(1, vec.size()[1])
    # 先减后加max_score，等价于torch.log(torch.sum(torch.exp(vec)))
    return max_score + torch.log(torch.sum(torch.exp(vec - max_score_broadcast)))


class BiLSTM_CRF(nn.Module):
    def __init__(self, vocab_size, tag_to_ix, embedding_dim, hidden_dim):
        super(BiLSTM_CRF, self).__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.vocab_size = vocab_size
        self.tag_to_ix = tag_to_ix
        self.tagset_size = len(tag_to_ix)
        self.word_embeds = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim // 2, num_layers=1, bidirectional=True)

        # Maps the output of the LSTM into tag space.
        # 将LSTM的输出hidden_dim，映射到标签空间tagset_size
        # 得到发射概率矩阵feats
        self.hidden2tag = nn.Linear(hidden_dim, self.tagset_size)

        # Matrix of transition parameters. Entry i,j is the score of transitioning to i from j
        # transitions为转移概率矩阵
        # transitions[i][j]表示从标签j转移到标签i的概率，虽然是随机生成的但是后面会迭代更新
        # transitions[i]表示从其他标签转到标签i的概率
        self.transitions = nn.Parameter(torch.randn(self.tagset_size, self.tagset_size))

        # These two statements enforce the constraint that
        # we never transfer to the start tag and we never transfer from the stop tag
        # 添加约束：不可能转移到开始标签
        self.transitions.data[tag_to_ix[START_TAG], :] = -10000
        # 添加约束：不可能从停止标签开始转移
        self.transitions.data[:, tag_to_ix[STOP_TAG]] = -10000

        # 初始化隐含层
        self.hidden = self.init_hidden()

    def init_hidden(self):
        # hidden: (num_layers * num_directions, batch_size, hidden_dim)
        # 实际上初始化的是LSTM中的h0和c0
        return (torch.randn(2, 1, self.hidden_dim // 2),
                torch.randn(2, 1, self.hidden_dim // 2))

    # 将输入句子依次经过Embedding Layer，BiLSTM Layer和Linear Layer，最终得到发射矩阵
    def _get_lstm_features(self, sentence):
        # sentence: (seq_length, vocab_size)
        self.hidden = self.init_hidden()
        # embeds: (seq_length, embedding_dim)
        embeds = self.word_embeds(sentence).view(len(sentence), 1, -1)
        # lstm_out: (seq_length, hidden_dim)
        lstm_out, self.hidden = self.lstm(embeds, self.hidden)
        # lstm_out: (seq_length, hidden_dim)
        lstm_out = lstm_out.view(len(sentence), self.hidden_dim)
        # lstm_feats: (seq_length, tagset_size)
        lstm_feats = self.hidden2tag(lstm_out)
        return lstm_feats

    # loss的前半部分log_sum_exp的结果，计算每一条可能路径的得分
    # 基于动态规划的思想，可以先计算到w_i的log_sum_exp，然后计算到w_i+1的log_sum_exp
    def _forward_alg(self, feats):
        # Do the forward algorithm to compute the partition function
        # init_alphas: (1, tagset_size)
        init_alphas = torch.full((1, self.tagset_size), -10000.)
        # START_TAG has all of the score.
        init_alphas[0][self.tag_to_ix[START_TAG]] = 0.
        # Wrap in a variable so that we will get automatic backprop
        # forward_var: (1, tagset_size)
        forward_var = init_alphas

        # Iterate through the sentence
        # feats: (seq_length, tagset_size)
        # feat: (tagset_size)
        for feat in feats:
            # The forward tensors at this timestep
            alphas_t = []
            for next_tag in range(self.tagset_size):
                # broadcast the emission score: it is the same regardless of the previous tag
                # emit_score: (1, tagset_size)
                emit_score = feat[next_tag].view(1, -1).expand(1, self.tagset_size)

                # the ith entry of trans_score is the score of transitioning to next_tag from i
                # trans_score: (1, tagset_size)
                trans_score = self.transitions[next_tag].view(1, -1)

                # The ith entry of next_tag_var is the value for the edge (i -> next_tag) before we do log-sum-exp
                # next_tag_var: (1, tagset_size)
                next_tag_var = forward_var + trans_score + emit_score

                # The forward variable for this tag is log-sum-exp of all the scores
                alphas_t.append(log_sum_exp(next_tag_var).view(1))

            # forward_var: (1, tagset_size)
            forward_var = torch.cat(alphas_t).view(1, -1)

        # terminal_var: (1, tagset_size)
        terminal_var = forward_var + self.transitions[self.tag_to_ix[STOP_TAG]]

        # alpha: (1)
        alpha = log_sum_exp(terminal_var)
        return alpha

    # loss的后半部分S(X,y)的结果，计算序列y的得分
    def _score_sentence(self, feats, tags):
        # Gives the score of a provided tag sequence
        score = torch.zeros(1)
        # tags: (seq + 1)
        tags = torch.cat([torch.tensor([self.tag_to_ix[START_TAG]], dtype=torch.long), tags])
        # feats: (seq_length, tagset_size)
        # feat: (tagset_size)
        for i, feat in enumerate(feats):
            # feat[tags[i+1]]为tags[i+1]的发射概率
            # self.transitions[tags[i + 1], tags[i]]为从tags[i]转移到tags[i + 1]的概率值
            score = score + self.transitions[tags[i + 1], tags[i]] + feat[tags[i + 1]]
        score = score + self.transitions[self.tag_to_ix[STOP_TAG], tags[-1]]
        return score

    # 使用Viterbi算法进行解码，获取最优路径
    def _viterbi_decode(self, feats):
        backpointers = []

        # Initialize the viterbi variables in log space
        # init_vvars: (1, tagset_size)
        init_vvars = torch.full((1, self.tagset_size), -10000.)
        init_vvars[0][self.tag_to_ix[START_TAG]] = 0

        # forward_var at step i holds the viterbi variables for step i - 1
        # forward_var: (1, tagset_size)
        forward_var = init_vvars
        # feats: (seq_length, tagset_size)
        # feat: (tagset_size)
        for feat in feats:
            # holds the backpointers for this step
            bptrs_t = []
            # holds the viterbi variables for this step
            viterbivars_t = []

            for next_tag in range(self.tagset_size):
                # next_tag_var[i] holds the viterbi variable for tag i at the previous step,
                # plus the score of transitioning from tag i to next_tag
                # We don't include the emission scores here
                # because the max does not depend on them (we add them in below)

                # forward_var: (1, tagset_size)
                # forward_var保存的是之前的最优路径的值
                # self.transitions[next_tag]表示从其他标签转到next_tag的概率
                next_tag_var = forward_var + self.transitions[next_tag]
                # 返回最大概率对应的tag
                best_tag_id = argmax(next_tag_var)
                # 只记录最大概率的tag
                bptrs_t.append(best_tag_id)
                # 记录最大值
                viterbivars_t.append(next_tag_var[0][best_tag_id].view(1))
            # Now add in the emission scores, and assign forward_var to the set of viterbi variables we just computed
            # 加上发射概率
            forward_var = (torch.cat(viterbivars_t) + feat).view(1, -1)
            # 记录最大概率的路径
            backpointers.append(bptrs_t)

        # Transition to STOP_TAG
        # 加上其他标签到STOP_TAG的转移概率
        terminal_var = forward_var + self.transitions[self.tag_to_ix[STOP_TAG]]
        # 返回最后一位的最大概率对应的tag
        best_tag_id = argmax(terminal_var)
        # 返回最后一位的最大概率
        path_score = terminal_var[0][best_tag_id]

        # Follow the back pointers to decode the best path
        # 从后往前开始回溯，依次得到从后往前对应的tag
        best_path = [best_tag_id]
        for bptrs_t in reversed(backpointers):
            best_tag_id = bptrs_t[best_tag_id]
            best_path.append(best_tag_id)
        # Pop off the start tag (we dont want to return that to the caller)
        start = best_path.pop()
        # 验证从START_TAG开始
        assert start == self.tag_to_ix[START_TAG]  # Sanity check
        # 得到从前往后对应的tag
        best_path.reverse()
        return path_score, best_path

    def neg_log_likelihood(self, sentence, tags):
        # 1、经过LSTM和Linear矩阵后的发射概率矩阵，作为CRF层的输入
        feats = self._get_lstm_features(sentence)

        # 2、loss的前半部分log_sum_exp的结果，计算每一条可能路径的得分
        forward_score = self._forward_alg(feats)

        # 3、loss的后半部分S(X,y)的结果，计算序列y的得分
        gold_score = self._score_sentence(feats, tags)

        # 4、两者相减，得到最终的loss
        return forward_score - gold_score

    def forward(self, sentence):
        # Don't confuse this with _forward_alg above.
        # 将forward函数和_forward_alg函数区分开

        # 1、Get the emission scores from the BiLSTM.
        # 1、得到经过LSTM和Linear矩阵后的发射概率矩阵
        lstm_feats = self._get_lstm_features(sentence)

        # 2、Find the best path, given the features.
        # 2、使用Viterbi算法进行解码，获取最优路径
        score, tag_seq = self._viterbi_decode(lstm_feats)
        return score, tag_seq


if __name__ == "__main__":
    START_TAG = "<START>"
    STOP_TAG = "<STOP>"
    EMBEDDING_DIM = 5
    HIDDEN_DIM = 4

    # Make up some training data
    training_data = [("the wall street journal reported today that apple corporation made money".split(),
                      "B I I I O O O B I O O".split()),
                     ("georgia tech is a university in georgia".split(),
                      "B I O O O O B".split())]

    word_to_ix = {}
    for sentence, tags in training_data:
        for word in sentence:
            if word not in word_to_ix:
                word_to_ix[word] = len(word_to_ix)

    tag_to_ix = {"B": 0, "I": 1, "O": 2, START_TAG: 3, STOP_TAG: 4}

    model = BiLSTM_CRF(len(word_to_ix), tag_to_ix, EMBEDDING_DIM, HIDDEN_DIM)
    optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)

    # Check predictions before training
    with torch.no_grad():
        precheck_sent = prepare_sequence(training_data[0][0], word_to_ix)
        precheck_tags = torch.tensor([tag_to_ix[t] for t in training_data[0][1]], dtype=torch.long)
        print(model(precheck_sent))

    # Make sure prepare_sequence from earlier in the LSTM section is loaded
    # again, normally you would NOT do 300 epochs, it is toy data
    for epoch in range(300):
        for sentence, tags in training_data:
            # Step 1. Remember that Pytorch accumulates gradients.
            # We need to clear them out before each instance
            model.zero_grad()

            # Step 2. Get our inputs ready for the network, that is,
            # turn them into Tensors of word indices.
            sentence_in = prepare_sequence(sentence, word_to_ix)
            targets = torch.tensor([tag_to_ix[t] for t in tags], dtype=torch.long)

            # Step 3. Run our forward pass.
            loss = model.neg_log_likelihood(sentence_in, targets)

            # Step 4. Compute the loss, gradients, and update the parameters by
            # calling optimizer.step()
            loss.backward()
            print("Epoch: ", epoch, ", Loss: ", loss.item())
            optimizer.step()

    # Check predictions after training
    with torch.no_grad():
        precheck_sent = prepare_sequence(training_data[0][0], word_to_ix)
        print(training_data[0][0])
        print(precheck_sent)
        print(model(precheck_sent))