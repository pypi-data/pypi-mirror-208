from ..metrics import MetricBase
from torchmetrics import Metric


def set_metric_attr(metric, name=None, stages=None, dl_idx:int=None, on_step:bool=None, on_epoch:bool=None, on_bar:bool=None):
    """
    Args:
        metric: 指标
        name: 指标名
        stages: 在哪些阶段运行，取值为 'train', 'val', 'test' 或者它们组成的列表，默认值 ['train', 'val', 'test']
        dl_idx: 验证或测试阶段使用多个dataloader时，指标运行在哪个dataloader之上，默认值 -1 表示所有的dataloader
        on_step: 是否将每个batch的指标值记入日志，默认值 True
        on_epoch: 是否将每个epoch的指标值记入日志，默认值 False
        on_bar: 指标是否在pytorch_lightning内置的进度条上显示，默认值 True
    """
    # 默认属性取值
    attr = {'name': None, 'stages': ['train', 'val', 'test'], 'dl_idx': -1,
            'on_step': True, 'on_epoch': False, 'on_bar': True}

    if isinstance(metric, (tuple, list)):
        assert len(metric) == 2, "'`metric` should be a tuple of (metric_name, metric_callable) or (metric_callable, metric_name)"
        if callable(metric[0]):      # (metric_callable, dataloader_idx)
            metric, name_ = metric
        elif callable(metric[1]):    # (metric_name, metric_callable)
            name_, metric = metric
        attr['name'] = name_
    else:
        for k, v in attr.items():
            attr[k] = getattr(metric, k, v)

    # 如果没有提供name
    if attr['name'] is None:
        attr['name'] = metric.__name__ if hasattr(metric, '__name__') else type(metric).__name__

    if not isinstance(metric, (Metric, MetricBase)):  # 如果指标是一个函数（或其他可调用对象）
        metric = MetricBase(metric)

    if name is not None:
        attr['name'] = name
    if stages is not None:
        if isinstance(stages, (list, tuple)):
            for stage in stages:
                assert stage in ['train', 'val', 'test']
        else:
            assert stages in ['train', 'val', 'test']
            stages = [stages]
        attr['stages'] = stages
    if dl_idx is not None:
        attr['dl_idx'] = dl_idx
        attr['name'] = f"{attr['name']}/{dl_idx}"
    if on_step is not None:
        attr['on_step'] = on_step
    if on_epoch is not None:
        attr['on_epoch'] = on_epoch
    if on_bar is not None:
        attr['on_bar'] = on_bar

    # 设置指标属性
    for k, v in attr.items():
        setattr(metric, k, v)

    return metric
