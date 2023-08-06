import re
import numpy as np
import six
import math
import torch
import torch.nn as nn
from dataclasses import dataclass
from transformers import PretrainedConfig
from transformers.utils import ModelOutput
from typing import Optional, Tuple

from lsptrain.nlp_info_extract.ernie import ErnieModel, ErniePreTrainedModel
# from ernie_m import ErnieMModel, ErnieMPreTrainedModel
from lsptrain.nlp_info_extract.util import get_bool_ids_greater_than, get_span, get_id_and_prob, cut_chinese_sent, dbc2sbc


@dataclass
class UIEModelOutput(ModelOutput):
    """
    Output class for outputs of UIE.
    Args:
        loss (`torch.FloatTensor` of shape `(1,)`, *optional*, returned when `labels` is provided):
            Total span extraction loss is the sum of a Cross-Entropy for the start and end positions.
        start_prob (`torch.FloatTensor` of shape `(batch_size, sequence_length)`):
            Span-start scores (after Sigmoid).
        end_prob (`torch.FloatTensor` of shape `(batch_size, sequence_length)`):
            Span-end scores (after Sigmoid).
        hidden_states (`tuple(torch.FloatTensor)`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
            Tuple of `torch.FloatTensor` (one for the output of the embeddings, if the model has an embedding layer, +
            one for the output of each layer) of shape `(batch_size, sequence_length, hidden_size)`.
            Hidden-states of the model at the output of each layer plus the optional initial embedding outputs.
        attentions (`tuple(torch.FloatTensor)`, *optional*, returned when `output_attentions=True` is passed or when `config.output_attentions=True`):
            Tuple of `torch.FloatTensor` (one for each layer) of shape `(batch_size, num_heads, sequence_length,
            sequence_length)`.
            Attentions weights after the attention softmax, used to compute the weighted average in the self-attention
            heads.
    """
    loss: Optional[torch.FloatTensor] = None
    start_prob: torch.FloatTensor = None
    end_prob: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None


class UIE(ErniePreTrainedModel):
    """
    UIE model based on Bert model.
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`PretrainedConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
    """

    def __init__(self, config: PretrainedConfig):
        super(UIE, self).__init__(config)
        self.encoder = ErnieModel(config)
        self.config = config
        hidden_size = self.config.hidden_size

        self.linear_start = nn.Linear(hidden_size, 1)
        self.linear_end = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

        # if hasattr(config, 'use_task_id') and config.use_task_id:
        #     # Add task type embedding to BERT
        #     task_type_embeddings = nn.Embedding(
        #         config.task_type_vocab_size, config.hidden_size)
        #     self.encoder.embeddings.task_type_embeddings = task_type_embeddings

        #     def hook(module, input, output):
        #         input = input[0]
        #         return output+task_type_embeddings(torch.zeros(input.size(), dtype=torch.int64, device=input.device))
        #     self.encoder.embeddings.word_embeddings.register_forward_hook(hook)

        self.post_init()

    def forward(self, input_ids: Optional[torch.Tensor] = None,
                token_type_ids: Optional[torch.Tensor] = None,
                position_ids: Optional[torch.Tensor] = None,
                attention_mask: Optional[torch.Tensor] = None,
                head_mask: Optional[torch.Tensor] = None,
                inputs_embeds: Optional[torch.Tensor] = None,
                start_positions: Optional[torch.Tensor] = None,
                end_positions: Optional[torch.Tensor] = None,
                output_attentions: Optional[bool] = None,
                output_hidden_states: Optional[bool] = None,
                return_dict: Optional[bool] = None
                ):
        """
        Args:
        input_ids (`torch.LongTensor` of shape `({0})`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`BertTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.FloatTensor` of shape `({0})`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are **not masked**,
            - 0 for tokens that are **masked**.
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`torch.LongTensor` of shape `({0})`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`:
            - 0 corresponds to a *sentence A* token,
            - 1 corresponds to a *sentence B* token.
            [What are token type IDs?](../glossary#token-type-ids)
        position_ids (`torch.LongTensor` of shape `({0})`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is **not masked**,
            - 0 indicates the head is **masked**.
        inputs_embeds (`torch.FloatTensor` of shape `({0}, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        start_positions (`torch.LongTensor` of shape `(batch_size,)`, *optional*):
            Labels for position (index) of the start of the labelled span for computing the token classification loss.
            Positions are clamped to the length of the sequence (`sequence_length`). Position outside of the sequence
            are not taken into account for computing the loss.
        end_positions (`torch.LongTensor` of shape `(batch_size,)`, *optional*):
            Labels for position (index) of the end of the labelled span for computing the token classification loss.
            Positions are clamped to the length of the sequence (`sequence_length`). Position outside of the sequence
            are not taken into account for computing the loss.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.encoder(
            input_ids=input_ids,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            attention_mask=attention_mask,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict
        )
        sequence_output = outputs[0]

        start_logits = self.linear_start(sequence_output)
        start_logits = torch.squeeze(start_logits, -1)
        start_prob = self.sigmoid(start_logits)
        end_logits = self.linear_end(sequence_output)
        end_logits = torch.squeeze(end_logits, -1)
        end_prob = self.sigmoid(end_logits)

        total_loss = None
        if start_positions is not None and end_positions is not None:
            loss_fct = nn.BCELoss()
            start_loss = loss_fct(start_prob, start_positions)
            end_loss = loss_fct(end_prob, end_positions)
            total_loss = (start_loss + end_loss) / 2.0

        if not return_dict:
            output = (start_prob, end_prob) + outputs[2:]
            return ((total_loss,) + output) if total_loss is not None else output

        return UIEModelOutput(
            loss=total_loss,
            start_prob=start_prob,
            end_prob=end_prob,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )


class PyTorchInferBackend:
    def __init__(self,
                 model_path_prefix,
                 device='cuda:0',
                 use_fp16=False):

        print(">>> [PyTorchInferBackend] Creating Engine ...")

        self.model = UIE.from_pretrained(model_path_prefix)
        self.model.eval()
        self.device = device
        if self.device.startswith("cuda") and torch.cuda.is_available():
            print(">>> [PyTorchInferBackend] Use GPU to inference ...")
            if use_fp16:
                print(">>> [PyTorchInferBackend] Use FP16 to inference ...")
                self.model = self.model.half()
            self.model = self.model.cuda()
        else:
            print(">>> [PyTorchInferBackend] Use CPU to inference ...")
        print(">>> [PyTorchInferBackend] Engine Created ...")

    def infer(self, input_dict):
        import torch
        for input_name, input_value in input_dict.items():
            input_value = torch.LongTensor(input_value)
            if self.device.startswith("cuda") and torch.cuda.is_available():
                input_value = input_value.cuda()
            input_dict[input_name] = input_value

        outputs = self.model(**input_dict)
        start_prob, end_prob = outputs[0], outputs[1]
        if self.device.startswith("cuda") and torch.cuda.is_available():
            start_prob, end_prob = start_prob.cpu(), end_prob.cpu()
        start_prob = start_prob.detach().numpy()
        end_prob = end_prob.detach().numpy()
        return start_prob, end_prob


class UIEPredictor(object):

    def __init__(self, model, schema, task_path=None, schema_lang="zh", device='cuda:0'
                 , position_prob=0.5, max_seq_len=64, batch_size=1, split_sentence=False, use_fp16=False):

        assert isinstance(device, six.string_types), "The type of device must be string."
        assert device == "cpu" or device.startswith("cuda"), "The device must be cpu or gpu."

        self._model = model
        self._task_path = task_path
        self._device = device
        self._position_prob = position_prob
        self._max_seq_len = max_seq_len
        self._batch_size = batch_size
        self._split_sentence = split_sentence
        self._use_fp16 = use_fp16

        self._schema_tree = None
        self._is_en = True if model in ['uie-base-en'] or schema_lang == 'en' else False
        self.set_schema(schema)
        self._prepare_predictor()

    def _prepare_predictor(self):

        if self._task_path is None:
            self._task_path = self._model.replace('-', '_') + '_pytorch'

        from transformers import BertTokenizerFast
        self._tokenizer = BertTokenizerFast.from_pretrained(self._task_path)

        self.inference_backend = PyTorchInferBackend(self._task_path, device=self._device, use_fp16=self._use_fp16)

    def set_schema(self, schema):
        if isinstance(schema, dict) or isinstance(schema, str):
            schema = [schema]
        self._schema_tree = self._build_tree(schema)

    def __call__(self, inputs):
        texts = inputs
        if isinstance(texts, str):
            texts = [texts]
        results = self._multi_stage_predict(texts)
        return results

    def _multi_stage_predict(self, datas):
        """
        Traversal the schema tree and do multi-stage prediction.
        Args:
            datas (list): a list of strings
        Returns:
            list: a list of predictions, where the list's length
                equals to the length of `datas`
        """
        results = [{} for _ in range(len(datas))]
        # input check to early return
        if len(datas) < 1 or self._schema_tree is None:
            return results

        # copy to stay `self._schema_tree` unchanged
        schema_list = self._schema_tree.children[:]
        while len(schema_list) > 0:
            node = schema_list.pop(0)
            examples = []
            input_map = {}
            cnt = 0
            idx = 0
            if not node.prefix:
                for data in datas:
                    examples.append({
                        "text": data,
                        "prompt": dbc2sbc(node.name)
                    })
                    input_map[cnt] = [idx]
                    idx += 1
                    cnt += 1
            else:
                for pre, data in zip(node.prefix, datas):
                    if len(pre) == 0:
                        input_map[cnt] = []
                    else:
                        for p in pre:
                            if self._is_en:
                                if re.search(r'\[.*?\]$', node.name):
                                    prompt_prefix = node.name[:node.name.find(
                                        "[", 1)].strip()
                                    cls_options = re.search(
                                        r'\[.*?\]$', node.name).group()
                                    # Sentiment classification of xxx [positive, negative]
                                    prompt = prompt_prefix + p + " " + cls_options
                                else:
                                    prompt = node.name + p
                            else:
                                prompt = p + node.name
                            examples.append({
                                "text": data,
                                "prompt": dbc2sbc(prompt)
                            })
                        input_map[cnt] = [i + idx for i in range(len(pre))]
                        idx += len(pre)
                    cnt += 1
            if len(examples) == 0:
                result_list = []
            else:
                result_list = self._single_stage_predict(examples)

            if not node.parent_relations:
                relations = [[] for i in range(len(datas))]
                for k, v in input_map.items():
                    for idx in v:
                        if len(result_list[idx]) == 0:
                            continue
                        if node.name not in results[k].keys():
                            results[k][node.name] = result_list[idx]
                        else:
                            results[k][node.name].extend(result_list[idx])
                    if node.name in results[k].keys():
                        relations[k].extend(results[k][node.name])
            else:
                relations = node.parent_relations
                for k, v in input_map.items():
                    for i in range(len(v)):
                        if len(result_list[v[i]]) == 0:
                            continue
                        if "relations" not in relations[k][i].keys():
                            relations[k][i]["relations"] = {
                                node.name: result_list[v[i]]
                            }
                        elif node.name not in relations[k][i]["relations"].keys(
                        ):
                            relations[k][i]["relations"][
                                node.name] = result_list[v[i]]
                        else:
                            relations[k][i]["relations"][node.name].extend(
                                result_list[v[i]])

                new_relations = [[] for i in range(len(datas))]
                for i in range(len(relations)):
                    for j in range(len(relations[i])):
                        if "relations" in relations[i][j].keys(
                        ) and node.name in relations[i][j]["relations"].keys():
                            for k in range(
                                len(relations[i][j]["relations"][
                                        node.name])):
                                new_relations[i].append(relations[i][j][
                                                            "relations"][node.name][k])
                relations = new_relations

            prefix = [[] for _ in range(len(datas))]
            for k, v in input_map.items():
                for idx in v:
                    for i in range(len(result_list[idx])):
                        if self._is_en:
                            prefix[k].append(" of " +
                                             result_list[idx][i]["text"])
                        else:
                            prefix[k].append(result_list[idx][i]["text"] + "的")

            for child in node.children:
                child.prefix = prefix
                child.parent_relations = relations
                schema_list.append(child)
        return results

    def _convert_ids_to_results(self, examples, sentence_ids, probs):
        """
        Convert ids to raw text in a single stage.
        """
        results = []
        for example, sentence_id, prob in zip(examples, sentence_ids, probs):
            if len(sentence_id) == 0:
                results.append([])
                continue
            result_list = []
            text = example["text"]
            prompt = example["prompt"]
            for i in range(len(sentence_id)):
                start, end = sentence_id[i]
                if start < 0 and end >= 0:
                    continue
                if end < 0:
                    start += (len(prompt) + 1)
                    end += (len(prompt) + 1)
                    result = {"text": prompt[start:end],
                              "probability": prob[i]}
                    result_list.append(result)
                else:
                    result = {
                        "text": text[start:end],
                        "start": start,
                        "end": end,
                        "probability": prob[i]
                    }
                    result_list.append(result)
            results.append(result_list)
        return results

    def _auto_splitter(self, input_texts, max_text_len, split_sentence=False):
        '''
        Split the raw texts automatically for model inference.
        Args:
            input_texts (List[str]): input raw texts.
            max_text_len (int): cutting length.
            split_sentence (bool): If True, sentence-level split will be performed.
        return:
            short_input_texts (List[str]): the short input texts for model inference.
            input_mapping (dict): mapping between raw text and short input texts.
        '''
        input_mapping = {}
        short_input_texts = []
        cnt_org = 0
        cnt_short = 0
        for text in input_texts:
            if not split_sentence:
                sens = [text]
            else:
                sens = cut_chinese_sent(text)
            for sen in sens:
                lens = len(sen)
                if lens <= max_text_len:
                    short_input_texts.append(sen)
                    if cnt_org not in input_mapping.keys():
                        input_mapping[cnt_org] = [cnt_short]
                    else:
                        input_mapping[cnt_org].append(cnt_short)
                    cnt_short += 1
                else:
                    temp_text_list = [
                        sen[i:i + max_text_len]
                        for i in range(0, lens, max_text_len)
                    ]
                    short_input_texts.extend(temp_text_list)
                    short_idx = cnt_short
                    cnt_short += math.ceil(lens / max_text_len)
                    temp_text_id = [
                        short_idx + i for i in range(cnt_short - short_idx)
                    ]
                    if cnt_org not in input_mapping.keys():
                        input_mapping[cnt_org] = temp_text_id
                    else:
                        input_mapping[cnt_org].extend(temp_text_id)
            cnt_org += 1
        return short_input_texts, input_mapping

    def _single_stage_predict(self, inputs):
        input_texts = []
        prompts = []
        for i in range(len(inputs)):
            input_texts.append(inputs[i]["text"])
            prompts.append(inputs[i]["prompt"])
        # max predict length should exclude the length of prompt and summary tokens
        max_predict_len = self._max_seq_len - len(max(prompts)) - 3

        short_input_texts, self.input_mapping = self._auto_splitter(
            input_texts, max_predict_len, split_sentence=self._split_sentence)

        short_texts_prompts = []
        for k, v in self.input_mapping.items():
            short_texts_prompts.extend([prompts[k] for i in range(len(v))])
        short_inputs = [{
            "text": short_input_texts[i],
            "prompt": short_texts_prompts[i]
        } for i in range(len(short_input_texts))]

        sentence_ids = []
        probs = []

        input_ids = []
        token_type_ids = []
        attention_mask = []
        offset_maps = []

        padding_type = "longest"
        encoded_inputs = self._tokenizer(
            text=short_texts_prompts,
            text_pair=short_input_texts,
            stride=2,
            truncation=True,
            max_length=self._max_seq_len,
            padding=padding_type,
            add_special_tokens=True,
            return_offsets_mapping=True,
            return_tensors="np")

        start_prob_concat, end_prob_concat = [], []
        for batch_start in range(0, len(short_input_texts), self._batch_size):
            input_ids = encoded_inputs["input_ids"][batch_start:batch_start + self._batch_size]
            token_type_ids = encoded_inputs["token_type_ids"][batch_start:batch_start + self._batch_size]
            attention_mask = encoded_inputs["attention_mask"][batch_start:batch_start + self._batch_size]
            offset_maps = encoded_inputs["offset_mapping"][batch_start:batch_start + self._batch_size]

            input_dict = {
                "input_ids": np.array(
                    input_ids, dtype="int64"),
                "token_type_ids": np.array(
                    token_type_ids, dtype="int64"),
                "attention_mask": np.array(
                    attention_mask, dtype="int64")
            }

            outputs = self.inference_backend.infer(input_dict)
            start_prob, end_prob = outputs[0], outputs[1]
            start_prob_concat.append(start_prob)
            end_prob_concat.append(end_prob)
        start_prob_concat = np.concatenate(start_prob_concat)
        end_prob_concat = np.concatenate(end_prob_concat)

        start_ids_list = get_bool_ids_greater_than(
            start_prob_concat, limit=self._position_prob, return_prob=True)
        end_ids_list = get_bool_ids_greater_than(
            end_prob_concat, limit=self._position_prob, return_prob=True)

        input_ids = input_dict['input_ids']
        sentence_ids = []
        probs = []
        for start_ids, end_ids, ids, offset_map in zip(start_ids_list,
                                                       end_ids_list,
                                                       input_ids.tolist(),
                                                       offset_maps):
            for i in reversed(range(len(ids))):
                if ids[i] != 0:
                    ids = ids[:i]
                    break
            span_list = get_span(start_ids, end_ids, with_prob=True)
            sentence_id, prob = get_id_and_prob(span_list, offset_map.tolist())
            sentence_ids.append(sentence_id)
            probs.append(prob)

        results = self._convert_ids_to_results(short_inputs, sentence_ids,
                                               probs)
        results = self._auto_joiner(results, short_input_texts,
                                    self.input_mapping)
        return results

    def _auto_joiner(self, short_results, short_inputs, input_mapping):
        concat_results = []
        is_cls_task = False
        for short_result in short_results:
            if short_result == []:
                continue
            elif 'start' not in short_result[0].keys(
            ) and 'end' not in short_result[0].keys():
                is_cls_task = True
                break
            else:
                break
        for k, vs in input_mapping.items():
            if is_cls_task:
                cls_options = {}
                single_results = []
                for v in vs:
                    if len(short_results[v]) == 0:
                        continue
                    if short_results[v][0]['text'] not in cls_options.keys():
                        cls_options[short_results[v][0][
                            'text']] = [1, short_results[v][0]['probability']]
                    else:
                        cls_options[short_results[v][0]['text']][0] += 1
                        cls_options[short_results[v][0]['text']][
                            1] += short_results[v][0]['probability']
                if len(cls_options) != 0:
                    cls_res, cls_info = max(cls_options.items(),
                                            key=lambda x: x[1])
                    concat_results.append([{
                        'text': cls_res,
                        'probability': cls_info[1] / cls_info[0]
                    }])
                else:
                    concat_results.append([])
            else:
                offset = 0
                single_results = []
                for v in vs:
                    if v == 0:
                        single_results = short_results[v]
                        offset += len(short_inputs[v])
                    else:
                        for i in range(len(short_results[v])):
                            if 'start' not in short_results[v][
                                i] or 'end' not in short_results[v][i]:
                                continue
                            short_results[v][i]['start'] += offset
                            short_results[v][i]['end'] += offset
                        offset += len(short_inputs[v])
                        single_results.extend(short_results[v])
                concat_results.append(single_results)
        return concat_results

    def predict(self, input_data):
        results = self._multi_stage_predict(input_data)
        return results

    @classmethod
    def _build_tree(cls, schema, name='root'):
        """
        Build the schema tree.
        """
        schema_tree = SchemaTree(name)
        for s in schema:
            if isinstance(s, str):
                schema_tree.add_child(SchemaTree(s))
            elif isinstance(s, dict):
                for k, v in s.items():
                    if isinstance(v, str):
                        child = [v]
                    elif isinstance(v, list):
                        child = v
                    else:
                        raise TypeError(
                            "Invalid schema, value for each key:value pairs should be list or string"
                            "but {} received".format(type(v)))
                    schema_tree.add_child(cls._build_tree(child, name=k))
            else:
                raise TypeError(
                    "Invalid schema, element should be string or dict, "
                    "but {} received".format(type(s)))
        return schema_tree


class SchemaTree(object):
    """
    Implementataion of SchemaTree
    """

    def __init__(self, name='root', children=None):
        self.name = name
        self.children = []
        self.prefix = None
        self.parent_relations = None
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.name

    def add_child(self, node):
        assert isinstance(
            node, SchemaTree
        ), "The children of a node should be an instacne of SchemaTree."
        self.children.append(node)