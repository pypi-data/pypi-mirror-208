import os
import sys
import time
import shutil
from tqdm import tqdm
import torch
from torch.utils.data import DataLoader
from torch.nn.functional import binary_cross_entropy
from transformers import BertTokenizerFast

from lsptrain.nlp_info_extract.util import set_seed, IEDataset, SpanEvaluator, EarlyStopping
from lsptrain.nlp_info_extract.evaluate import evaluate
from lsptrain.nlp_info_extract.model import UIE
from lsptrain.nlp_info_extract.download_pretrained_model import download


def train(batch_size: int = 64, valid_steps: int = 500, model: str = "uie-base", learning_rate: float = 1e-5,
          train_path: str = "train.txt", test_path: str = "test.txt", save_dir: str = "checkpoint",
          max_seq_len: int = 64, num_epochs: int = 100, seed: int = 1000, logging_steps: int = 1000,
          max_model_num: int = 3, early_stopping: bool = False, device: str = "cuda:0"):
    """
    :param batch_size:      训练批次大小
    :param valid_steps:     验证/保存模型的步数
    :param model:           预训练模型
    :param learning_rate:   学习率
    :param train_path:      训练数据集
    :param test_path:       测试数据集
    :param save_dir:        保存目录
    :param max_seq_len:     文字长度
    :param num_epochs:      训练步数
    :param seed:            全局随机种子数
    :param logging_steps:   日志步数
    :param max_model_num:   最多保存模型参数的数量， model_best不在计算范围内
    :param early_stopping:  是否启用
    :param device:          模型训练设备，默认使用第一块显卡 cuda:0, 如果显卡不可用，默认使用cpu
    :return:
    """
    download(input_model=model)
    finetune(train_path=train_path, test_path=test_path, batch_size=batch_size, seed=seed, model=model, device=device,
             max_seq_len=max_seq_len, learning_rate=learning_rate, early_stopping=early_stopping, save_dir=save_dir,
             num_epochs=num_epochs, logging_steps=logging_steps, valid_steps=valid_steps, max_model_num=max_model_num)


def finetune(train_path: str, test_path: str, batch_size: int, seed: int, model: str, device: str, max_seq_len: int,
             learning_rate: float, early_stopping: bool, save_dir: str, num_epochs: int, logging_steps: int,
             valid_steps: int, max_model_num: int):
    set_seed(seed)

    model = model.replace('-', '_') + '_pytorch'
    tokenizer = BertTokenizerFast.from_pretrained(model)
    model = UIE.from_pretrained(model)
    if device.startswith("cuda") and torch.cuda.is_available():
        model = model.cuda()
    train_ds = IEDataset(train_path, tokenizer=tokenizer, max_seq_len=max_seq_len)
    test_ds = IEDataset(test_path, tokenizer=tokenizer, max_seq_len=max_seq_len)
    train_data_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    dev_data_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.AdamW(lr=learning_rate, params=model.parameters())
    criterion = binary_cross_entropy
    metric = SpanEvaluator()

    if early_stopping:
        early_stopping_save_dir = os.path.join(save_dir, "early_stopping")
        if not os.path.exists(early_stopping_save_dir):
            os.makedirs(early_stopping_save_dir)
        early_stopping_obj = EarlyStopping(patience=7, verbose=True, trace_func=print, save_dir=early_stopping_save_dir)

    loss_list = []
    loss_sum = 0
    loss_num = 0
    global_step = 0
    best_step = 0
    best_f1 = 0
    tic_train = time.time()

    epoch_iterator = range(1, num_epochs + 1)
    epoch_iterator = tqdm(epoch_iterator, desc='Training', unit='epoch')
    for epoch in epoch_iterator:
        train_data_iterator = train_data_loader
        train_data_iterator = tqdm(train_data_iterator, desc=f'Training Epoch {epoch}', unit='batch')
        for batch in train_data_iterator:
            epoch_iterator.refresh()
            input_ids, token_type_ids, att_mask, start_ids, end_ids = batch
            if device.startswith("cuda") and torch.cuda.is_available():
                input_ids = input_ids.cuda()
                token_type_ids = token_type_ids.cuda()
                att_mask = att_mask.cuda()
                start_ids = start_ids.cuda()
                end_ids = end_ids.cuda()
            outputs = model(input_ids=input_ids,
                            token_type_ids=token_type_ids,
                            attention_mask=att_mask)
            start_prob, end_prob = outputs[0], outputs[1]

            start_ids = start_ids.type(torch.float32)
            end_ids = end_ids.type(torch.float32)
            loss_start = criterion(start_prob, start_ids)
            loss_end = criterion(end_prob, end_ids)
            loss = (loss_start + loss_end) / 2.0
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            loss_list.append(float(loss))
            loss_sum += float(loss)
            loss_num += 1

            global_step += 1
            if global_step % logging_steps == 0:
                time_diff = time.time() - tic_train
                loss_avg = loss_sum / loss_num

                print("global step %d, epoch: %d, loss: %.5f, speed: %.2f step/s" % (
                    global_step, epoch, loss_avg, logging_steps / time_diff))
                tic_train = time.time()

            if global_step % valid_steps == 0:
                save_dir_path = os.path.join(save_dir, "model_%d" % global_step)
                if not os.path.exists(save_dir_path):
                    os.makedirs(save_dir_path)
                model_to_save = model
                model_to_save.save_pretrained(save_dir_path)
                tokenizer.save_pretrained(save_dir_path)
                if max_model_num:
                    model_to_delete = global_step - max_model_num * valid_steps
                    model_to_delete_path = os.path.join(save_dir, "model_%d" % model_to_delete)
                    if model_to_delete > 0 and os.path.exists(model_to_delete_path):
                        shutil.rmtree(model_to_delete_path)

                dev_loss_avg, precision, recall, f1 = evaluate(model, metric, data_loader=dev_data_loader,
                                                               device=device, loss_fn=criterion)
                print("Evaluation precision: %.5f, recall: %.5f, F1: %.5f, dev loss: %.5f"
                      % (precision, recall, f1, dev_loss_avg))

                # Save model which has best F1
                if f1 > best_f1:
                    print(f"best F1 performence has been updated: {best_f1:.5f} --> {f1:.5f}")
                    best_f1 = f1
                    save_dir_path = os.path.join(save_dir, "model_best")
                    model_to_save = model
                    model_to_save.save_pretrained(save_dir_path)
                    tokenizer.save_pretrained(save_dir_path)
                tic_train = time.time()

            if early_stopping:
                dev_loss_avg, precision, recall, f1 = evaluate(
                    model, metric, data_loader=dev_data_loader, device=device, loss_fn=criterion)
                print("Evaluation precision: %.5f, recall: %.5f, F1: %.5f, dev loss: %.5f"
                      % (precision, recall, f1, dev_loss_avg))
                # Early Stopping
                early_stopping_obj(dev_loss_avg, model)  # noqa
                if early_stopping_obj.early_stop:
                    tokenizer.save_pretrained(early_stopping_save_dir)  # noqa
                    sys.exit(0)
