# encoding: utf-8

import os
from typing import List

import torch
from torch.utils import data
from torch.nn.functional import softmax
from transformers import BertTokenizer, BertConfig, BertModel
import numpy as np


class Model(torch.nn.Module):
    def __init__(self, pretrained_model, info_labels):
        super(Model, self).__init__()
        config = BertConfig.from_pretrained(pretrained_model)
        self.bert_model = BertModel.from_pretrained(pretrained_model)
        self.dropout = torch.nn.Dropout(0.4)
        self.fc1 = torch.nn.Linear(config.hidden_size, config.hidden_size)
        self.fc2 = torch.nn.Linear(config.hidden_size, len(info_labels))
        self.relu = torch.nn.ReLU()

    def forward(self, token_ids):
        bert_out = self.bert_model(token_ids)[1]  # 句向量 [batch_size,hidden_size]
        bert_out = self.dropout(bert_out)
        bert_out = self.fc1(bert_out)
        bert_out = self.relu(bert_out)
        bert_out = self.dropout(bert_out)
        bert_out = self.fc2(bert_out)  # [batch_size,num_class]
        return bert_out


# dataloader
class DataGen(data.Dataset):
    def __init__(self, data, label):
        self.data = data
        self.label = label

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return np.array(self.data[index]), np.array(self.label[index])


def get_confidence(outputs):
    softmax_outputs = softmax(outputs, dim=-1)
    torch_max_confidence = torch.max(softmax_outputs, dim=-1).values.numpy()
    return torch_max_confidence


class TextClassificationPredictor(object):

    def __init__(self, label_file_name: str, save_dir: str = "checkpoint",
                 pretrained_model: str = "hfl/chinese-roberta-wwm-ext", device: str = "cuda:0",
                 model_file_name: str = "model_best.pt", max_length: int = 64
                 ):
        # init info labels
        self.info_labels = []
        with open(file=os.path.join(save_dir, label_file_name), mode="r", encoding="utf-8") as f:
            lines = f.readlines()
        self.info_labels = [x.strip() for x in lines if len(x.strip()) > 0]

        self.model = Model(pretrained_model=pretrained_model, info_labels=self.info_labels)
        self.model.load_state_dict(
            torch.load(os.path.join(save_dir, model_file_name), map_location=lambda storage, loc: storage)
        )
        self.device = "cpu"
        if device and device.startswith("cuda"):
            self.device = device if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        print("running model on device:", self.device)
        self.tokenizer = BertTokenizer.from_pretrained(pretrained_model)
        self.max_length = max_length

    def get_label(self, x):
        if isinstance(x, int):
            return self.info_labels[x]
        else:
            return self.info_labels.index(x)

    def get_train_test_data(self, string, max_length=64):
        data = []
        label = []
        if isinstance(string, str):
            string = ''.join(string.split())
            ids = self.tokenizer.encode(string.strip(), max_length=max_length, truncation='longest_first',
                                        padding="max_length")
            data.append(ids)
            label.append(1)
        elif isinstance(string, list):
            for one_string in string:
                one_string = ''.join(one_string.split())
                ids = self.tokenizer.encode(one_string.strip(), max_length=max_length, truncation='longest_first',
                                            padding="max_length")
                data.append(ids)
                label.append(1)
        return data, label

    def predict(self, string):
        # 预测
        x_train, y_train = self.get_train_test_data(string, max_length=self.max_length)
        train_data_set = DataGen(x_train, y_train)
        train_data_loader = data.DataLoader(train_data_set, batch_size=1)
        with torch.no_grad():
            for step, (token_ids, label) in enumerate(train_data_loader):
                token_ids = token_ids.to(self.device).long()
                outputs = self.model(token_ids)
                outputs = outputs.cpu()
                for t in outputs:
                    confidence = get_confidence(t)
                    confidence = float(confidence)
                    t = np.argmax(t)
                    label = self.get_label(int(t))

                    item = dict()
                    item['confidence'] = confidence
                    item['label'] = label
                    return item
