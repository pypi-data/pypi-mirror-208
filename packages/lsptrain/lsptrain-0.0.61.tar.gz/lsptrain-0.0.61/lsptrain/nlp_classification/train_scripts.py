import os
import time
import datetime
from tqdm import tqdm
import torch
from torch.utils import data
from transformers import BertConfig, BertModel, BertTokenizer
from sklearn.model_selection import train_test_split
from .model import DataGen, Model


def get_label(labels, x):
    if isinstance(x, str):
        if x not in labels:
            labels.append(x)
        return labels.index(x), labels
    else:
        return labels[x], labels


def get_train_test_data(tokenizer, datas, split_data="__", max_length=64, test_size=0.1):
    """
    :param datas: ["样本数据__标签",]
    :param max_length: 样本最大长度，超过会自动截断
    :param test_size: 测试集比率
    :return: X_train, X_test, y_train, y_test, info_labels
    """
    texts = []
    labels = []
    info_labels = []

    for one in tqdm(datas):
        if not one.strip():
            continue
        result = one.split(split_data)
        if len(result) != 2:
            continue

        text, label = result
        try:
            lebal_index, info_labels = get_label(info_labels, label.strip())
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


def get_device(device: str):
    if not device or not isinstance(device, str):
        raise Exception(f"device error: {device}")
    if device and device.startswith("cuda"):
        _device = torch.device(device) if torch.cuda.is_available() else 'cpu'
    elif device == "cpu":
        _device = torch.device("cpu")
    else:
        _device = torch.device(device)
    return _device


def load_datas(data_file: str, encoding: str = "utf-8"):
    with open(data_file, "r", encoding=encoding) as f:
        datas = f.readlines()
    datas = [x.strip() for x in datas]
    return datas


def get_optimizer(model: Model, select_optimizer: str = 'Adam', lr: float = 0.0001):
    if select_optimizer.lower() == "sgd":
        optimizer = torch.optim.SGD(model.parameters(), lr=lr, weight_decay=1e-4)
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    return optimizer


def train(train_path: str, test_size: float = 0.1,
          encoding: str = "utf-8", split_data: str = "__",
          pretrained_model: str = "hfl/chinese-roberta-wwm-ext",
          learning_rate: float = 0.0001, optimizer: str = "adam",
          batch_size: int = 64, save_dir: str = "checkpoint",
          label_file_name: str = "catalog_label.txt", save_best: bool = False,
          max_length: int = 64, num_epochs: int = 25,
          device: str = "cuda:0", job_type: str = "txt_classification"):
    """
    :param train_path: 训练集数据，应该为txt文件
    :param test_size: 测试集比例，默认0.1
    :param encoding: 打开数据字符集，默认为utf-8
    :param split_data: 切分数据与标签的分隔符， 默认'__'
    :param pretrained_model: 预训练模型名称, 默认'hfl/chinese-roberta-wwm-ext'
    :param learning_rate: 学习率，默认0.000
    :param optimizer: 模型优化函数，默认adam
    :param batch_size: 训练批次大小，默认64，如果报错提示out of memory，可以适当调小
    :param save_dir: 训练checkpoint保存路径
    :param label_file_name: 保存标签文件名
    :param save_best: 是否只保存最优模型
    :param max_length: 默认序列最大长度64，超过部分会被自动截断
    :param num_epochs: 训练步数，默认25
    :param device: 训练设备。如果可用，默认使用第一块显卡
    :param job_type: 任务名称，保存模型开头名称，默认'txt_classification'
    :return: None
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if not os.path.exists(train_path):
        raise Exception(f"file:{train_path} does not exist.")
    print("开始读取数据")

    _device = get_device(device)

    datas = load_datas(train_path, encoding=encoding)

    print("读取数据完成")
    bert_model = BertModel.from_pretrained(pretrained_model)
    config = BertConfig.from_pretrained(pretrained_model)
    tokenizer = BertTokenizer.from_pretrained(pretrained_model)

    print("开始转换数据")
    (X_train, y_train), (X_test, y_test), info_labels = get_train_test_data(tokenizer=tokenizer, datas=datas,
                                                                            split_data=split_data,
                                                                            max_length=max_length, test_size=test_size)
    print("完成转换数据")
    label_path = os.path.join(save_dir, label_file_name)
    with open(label_path, "w", encoding=encoding) as f:
        for label in info_labels:
            f.write(f"{label}\n")
    print(f"保存标签至:[{label_path}]")

    train_dataset = DataGen(X_train, y_train)
    test_dataset = DataGen(X_test, y_test)
    train_dataloader = data.DataLoader(train_dataset, batch_size=batch_size)
    test_dataloader = data.DataLoader(test_dataset, batch_size=batch_size)

    model = Model(bert_model, config, len(info_labels))
    print(f"训练使用device:[{_device}]")
    model.to(_device)

    optimizer = get_optimizer(model=model, select_optimizer=optimizer, lr=learning_rate)

    criterion = torch.nn.CrossEntropyLoss()

    print("开始训练")
    best_accu = 0
    for epoch in range(num_epochs):
        print(f"epoch = {epoch}, datetime = {datetime.datetime.now()}")
        start = time.time()
        loss_sum = 0.0
        accu = 0
        model.train()
        for token_ids, label in tqdm(train_dataloader):
            token_ids = token_ids.to(_device).long()
            label = label.to(_device).long()
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
            token_ids = token_ids.to(_device).long()
            label = label.to(_device).long()
            with torch.no_grad():
                out = model(token_ids)
                loss = criterion(out, label)
                test_loss_sum += loss.cpu().data.numpy()
                test_accu += (out.argmax(1) == label).sum().cpu().data.numpy()
        accuracy = test_accu / len(test_dataset)

        print("epoch %d, train loss:%f, train acc:%f, test loss:%f, test acc:%f, use time:" % (
            epoch, loss_sum / len(train_dataset), accu / len(train_dataset), test_loss_sum / len(test_dataset),
            test_accu / len(test_dataset)), int(time.time() - start))
        if save_best:
            # 如果只保存最优模型
            if best_accu < accuracy:
                save_path = os.path.join(save_dir, f"{job_type}_model_best.pt")
                best_accu = accuracy
                torch.save(model.state_dict(), save_path)
        else:
            save_path = os.path.join(save_dir, f"{job_type}_model_{epoch}_{test_accu / len(test_dataset)}.pt")
            torch.save(model.state_dict(), save_path)
