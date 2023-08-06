from tqdm import tqdm
import torch


@torch.no_grad()
def evaluate(model, metric, data_loader, device='cuda:0', loss_fn=None, show_bar=True):
    """
    Given a dataset, it evals model and computes the metric.
    Args:
        model(obj:`torch.nn.Module`): A model to classify texts.
        metric(obj:`Metric`): The evaluation metric.
        data_loader(obj:`torch.utils.data.DataLoader`): The dataset loader which generates batches.
    """
    return_loss = False
    if loss_fn is not None:
        return_loss = True
    model.eval()
    metric.reset()
    loss_list = []
    loss_sum = 0
    loss_num = 0
    if show_bar:
        data_loader = tqdm(
            data_loader, desc="Evaluating", unit='batch')
    for batch in data_loader:
        input_ids, token_type_ids, att_mask, start_ids, end_ids = batch
        if device.startswith("cuda") and torch.cuda.is_available():
            input_ids = input_ids.cuda()
            token_type_ids = token_type_ids.cuda()
            att_mask = att_mask.cuda()
        outputs = model(input_ids=input_ids,
                        token_type_ids=token_type_ids,
                        attention_mask=att_mask)
        start_prob, end_prob = outputs[0], outputs[1]
        if device.startswith("cuda") and torch.cuda.is_available():
            start_prob, end_prob = start_prob.cpu(), end_prob.cpu()
        start_ids = start_ids.type(torch.float32)
        end_ids = end_ids.type(torch.float32)

        if return_loss:
            # Calculate loss
            loss_start = loss_fn(start_prob, start_ids)
            loss_end = loss_fn(end_prob, end_ids)
            loss = (loss_start + loss_end) / 2.0
            loss = float(loss)
            loss_list.append(loss)
            loss_sum += loss
            loss_num += 1
            if show_bar:
                data_loader.set_postfix(
                    {
                        'dev loss': f'{loss_sum / loss_num:.5f}'
                    }
                )

        # Calcalate metric
        num_correct, num_infer, num_label = metric.compute(start_prob, end_prob,
                                                           start_ids, end_ids)
        metric.update(num_correct, num_infer, num_label)
    precision, recall, f1 = metric.accumulate()
    model.train()
    if return_loss:
        loss_avg = sum(loss_list) / len(loss_list)
        return loss_avg, precision, recall, f1
    else:
        return precision, recall, f1
