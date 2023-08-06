from pytorch_lightning.callbacks.callback import Callback


class ResetMetrics(Callback):
    def on_train_epoch_end(self, trainer, pl_module):
        metric_values = {}
        if pl_module.metrics:
            metric_values = reset_metrics('train', pl_module)
        trainer.train_epoch_metric_values = metric_values

    def on_validation_epoch_end(self, trainer, pl_module):
        metric_values = {}
        if pl_module.metrics:
            metric_values = reset_metrics('val', pl_module)
        trainer.val_epoch_metric_values = metric_values

    def on_test_epoch_end(self, trainer, pl_module):
        metric_values = {}
        if pl_module.metrics:
            metric_values = reset_metrics('test', pl_module)
        trainer.test_epoch_metric_values = metric_values


def reset_metrics(stage, task):    # 重置指标
    metrics = task.metrics[stage]
    metric_values = {}
    for metric in metrics:
        value = metric.compute()
        if isinstance(value, dict):
            for k, v in value.items():
                metric_values[f"{metric.name}{k}"] = v.item()
        else:
            metric_values[metric.name] = value.item()
        metric.reset()
    return metric_values
