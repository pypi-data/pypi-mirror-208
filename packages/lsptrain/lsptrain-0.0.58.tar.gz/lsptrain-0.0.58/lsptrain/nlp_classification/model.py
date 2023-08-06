# encoding: utf-8
# @author: k

import argparse
import datetime
from tqdm import tqdm
import os
import time

import numpy as np
import torch
from transformers import BertTokenizer, BertConfig, BertModel
from torch.utils import data
from sklearn.model_selection import train_test_split


def setup_classification_args():
    parser = argparse.ArgumentParser("预训练分类任务")
    parser.add_argument("--train_path", default="", type=str,
                        help="训练集数据，应该为txt文件")
    parser.add_argument("--test_size", default=0.1, type=float,
                        help="测试集比例，默认0.1")
    parser.add_argument("--encoding", default="utf-8", type=str,
                        help="打开数据字符集，默认为utf-8")
    parser.add_argument("--split_data", default="__", type=str,
                        help="切分数据与标签的分隔符， 默认'__'")
    parser.add_argument("-pm", "--pretrained_model", default="hfl/chinese-roberta-wwm-ext", type=str,
                        help="预训练模型名称, 默认'hfl/chinese-roberta-wwm-ext'")
    parser.add_argument("-lr", "--learning_rate", default=0.0001,
                        type=float, help="学习率，默认0.0001")
    parser.add_argument("-o", "--optimizer", choices=["adam", "sgd"], default="adam", type=str,
                        help="模型优化函数，默认adam")
    parser.add_argument("-b", "--batch_size", default=64, type=int,
                        help="训练批次大小，如果报错提示out of memory，可以适当调小")
    parser.add_argument("-s", "--save_dir", default="checkpoint", type=str,
                        help="训练checkpoint保存路径")
    parser.add_argument("--label_file_name", default="catalog_label.txt", type=str,
                        help="保存标签文件名")
    parser.add_argument("--save_best", default=False, type=bool,
                        help="是否只保存最优模型")
    parser.add_argument("--max_length", default=64, type=int,
                        help="默认序列最大长度64，超过部分会被自动截断")
    parser.add_argument("-e", "--num_epochs", default=25, type=int,
                        help="训练步数，默认25")
    parser.add_argument("-d", "--device", default="cuda:0",
                        help="训练设备。如果可用，默认使用第一块显卡")
    parser.add_argument("-j", "--job_type", default="txt_classification", type=str,
                        help="任务名称，保存模型开头名称，默认'txt_classification'")
    args = parser.parse_args()

    return args


args = setup_classification_args()

if not os.path.exists(args.save_dir):
    os.mkdir(args.save_dir)

if not os.path.exists(args.train_path):
    raise Exception(f"file:{args.train_path} does not exist.")


def load_datas(data_file: str):
    with open(data_file, "r", encoding=args.encoding) as f:
        datas = f.readlines()
    datas = [x.strip() for x in datas]
    return datas


print("开始读取数据")

datas = load_datas(args.train_path)

print("读取数据完成")

info_labels = []

# 加载预训练模型
pretrained = args.pretrained_model
tokenizer = BertTokenizer.from_pretrained(pretrained)
bert_model = BertModel.from_pretrained(pretrained)
config = BertConfig.from_pretrained(pretrained)


def get_label(x):
    if isinstance(x, str):
        if x not in info_labels:
            info_labels.append(x)
        return info_labels.index(x)
    else:
        return info_labels[x]


def get_train_test_data(datas, split_data="__", max_length=args.max_length, test_size=args.test_size):
    """
    :param datas: ["样本数据__标签",]
    :param max_length: 样本最大长度，超过会自动截断
    :param test_size: 测试集比率
    :return: X_train, X_test, y_train, y_test, info_labels
    """
    texts = []
    labels = []

    for one in tqdm(datas):
        result = one.split(split_data)
        if len(result) != 2:
            continue

        text, label = result
        try:
            lebal_index = get_label(label.strip())
            text = tokenizer.encode(text.strip(), max_length=max_length, padding="max_length",
                                    truncation="longest_first")
            texts.append(text)
            labels.append(lebal_index)
        except Exception as e:
            print(e)
            continue
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=test_size, random_state=0,
                                                        shuffle=True)
    return (X_train, y_train), (X_test, y_test), info_labels


print("开始转换数据")
(X_train, y_train), (X_test, y_test), info_labels = get_train_test_data(datas=datas, test_size=0.1)
print("完成转换数据")

label_path = os.path.join(args.save_dir, args.label_file_name)

with open(label_path, "w", encoding=args.encoding) as f:
    for label in info_labels:
        f.write(f"{label}\n")
print(f"保存标签至:[{label_path}]")


# dataloader
class DataGen(data.Dataset):
    def __init__(self, data, label):
        self.data = data
        self.label = label

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return np.array(self.data[index]), np.array(self.label[index])


batch_size = args.batch_size
train_dataset = DataGen(X_train, y_train)
test_dataset = DataGen(X_test, y_test)
train_dataloader = data.DataLoader(train_dataset, batch_size=batch_size)
test_dataloader = data.DataLoader(test_dataset, batch_size=batch_size)


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


def get_device(device: str):
    if not device or not isinstance(device, str):
        raise Exception(f"device error: {device}")
    if device and device.startswith("cuda"):
        _device = torch.device(args.device) if torch.cuda.is_available() else 'cpu'
    elif device == "cpu":
        _device = torch.device("cpu")
    else:
        _device = torch.device(args.device)
    return _device


model = Model(bert_model, config, len(info_labels))
if args.device and args.device.startswith("cuda"):
    device = torch.device(args.device) if torch.cuda.is_available() else 'cpu'
elif args.device == "cpu":
    device = torch.device("cpu")
else:
    device = torch.device(args.device)
print(f"训练使用device:[{device}]")
model.to(device)


def get_optimizer(select_optimizer: str = 'Adam', lr: float = 0.0001):
    if select_optimizer.lower() == "sgd":
        optimizer = torch.optim.SGD(model.parameters(), lr=lr, weight_decay=1e-4)
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    return optimizer


criterion = torch.nn.CrossEntropyLoss()
optimizer = get_optimizer(args.optimizer, args.learning_rate)


def cmd_train():
    print("开始训练数据")
    best_accu = 0
    for epoch in range(args.num_epochs):
        print(f"epoch = {epoch}, datetime = {datetime.datetime.now()}")
        start = time.time()
        loss_sum = 0.0
        accu = 0
        model.train()
        for token_ids, label in tqdm(train_dataloader):
            token_ids = token_ids.to(device).long()
            label = label.to(device).long()
            out = model(token_ids)
            loss = criterion(out, label)
            optimizer.zero_grad()
            loss.backward()  # 反向传播
            optimizer.step()  # 梯度更新
            loss_sum += loss.cpu().data.numpy()
            accu += (out.argmax(1) == label).sum().cpu().data.numpy()

        test_loss_sum = 0.0
        test_accu = 0
        model.eval()
        for token_ids, label in tqdm(test_dataloader):
            token_ids = token_ids.to(device).long()
            label = label.to(device).long()
            with torch.no_grad():
                out = model(token_ids)
                loss = criterion(out, label)
                test_loss_sum += loss.cpu().data.numpy()
                test_accu += (out.argmax(1) == label).sum().cpu().data.numpy()
        accuracy = test_accu / len(test_dataset)
        print("epoch %d, train loss:%f, train acc:%f, test loss:%f, test acc:%f, use time:" % (
            epoch, loss_sum / len(train_dataset), accu / len(train_dataset), test_loss_sum / len(test_dataset),
            test_accu / len(test_dataset)), int(time.time() - start))
        if args.save_best:
            # 如果只保存最优模型
            if best_accu < accuracy:
                save_path = os.path.join(args.save_dir, f"{args.job_type}_model_best.pt")
                best_accu = accuracy
                torch.save(model.state_dict(), save_path)
        else:
            save_path = os.path.join(args.save_dir, f"{args.job_type}_model_{epoch}_{test_accu / len(test_dataset)}.pt")
            torch.save(model.state_dict(), save_path)
