# encoding: utf-8
# @author: k

import numpy as np
import torch

from torch.utils import data


# dataloader
class DataGen(data.Dataset):
    def __init__(self, data, label):
        self.data = data
        self.label = label

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return np.array(self.data[index]), np.array(self.label[index])


class Model(torch.nn.Module):
    def __init__(self, bert_model, bert_config, num_class):
        super(Model, self).__init__()
        self.bert_model = bert_model
        self.dropout = torch.nn.Dropout(0.4)
        self.fc1 = torch.nn.Linear(bert_config.hidden_size, bert_config.hidden_size)
        self.fc2 = torch.nn.Linear(bert_config.hidden_size, num_class)
        self.relu = torch.nn.ReLU()

    def forward(self, token_ids):
        bert_out = self.bert_model(token_ids)[1]  # 句向量 [batch_size,hidden_size]
        bert_out = self.dropout(bert_out)
        bert_out = self.fc1(bert_out)
        bert_out = self.relu(bert_out)
        bert_out = self.dropout(bert_out)
        bert_out = self.fc2(bert_out)
        return bert_out
