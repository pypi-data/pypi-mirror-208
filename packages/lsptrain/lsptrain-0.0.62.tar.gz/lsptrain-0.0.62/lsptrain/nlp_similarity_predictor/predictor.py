# encoding: utf-8

import numpy as np
from transformers import BertTokenizer


class TextSimilarityPredictor(object):

    def __init__(self, pretrained_tokenizer: str = "hfl/chinese-roberta-wwm-ext"):
        """
        :param pretrained_model: 预训练模型，默认使用 'hfl/chinese-roberta-wwm-ext'
        """
        if not pretrained_tokenizer:
            raise ValueError("pretrained_tokenizer input error")
        self.tokenizer = BertTokenizer.from_pretrained(pretrained_tokenizer)

    def compute(self, list1, list2):
        """
        计算余弦相似度，基础方法
        输入值为转换后的 tokenizer
        """
        result = np.dot(list1, list2) / (np.linalg.norm(list1) * np.linalg.norm(list2))
        return result

    def get_tokenizer(self, string: str, max_length: int = 64):
        """文本转词向量"""
        ids = self.tokenizer.encode(string.strip(),
                                    max_length=max_length,
                                    truncation='longest_first',
                                    padding="max_length")
        return ids

    def predict(self, string1: str, string2: str):
        """
        输入两个字符串，不用进行长度限定，输出相似度的浮点数，0-1之间
        开发只测试了中文，没有对英文进行测试，不保证效果，如需推理英文，可以考虑更换默认的 pretrained_tokenizer
        :param string1: str
        :param string2: str
        :return: float
        """
        if not string1 or not string2:
            raise ValueError("string1 and string2 cannot be empty")
        if not isinstance(string1, str) or not isinstance(string2, str):
            raise TypeError(f"string1 and string2 must be str, got type(string1): {type(string1)}, type(string2): {type(string2)}")
        max_length = max(len(string1), len(string2))
        tokenizer1 = self.get_tokenizer(string=string1, max_length=max_length)
        tokenizer2 = self.get_tokenizer(string=string2, max_length=max_length)
        result = self.compute(tokenizer1, tokenizer2)
        return result
