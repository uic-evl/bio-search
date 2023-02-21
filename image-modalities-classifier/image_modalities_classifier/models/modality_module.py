""" Resnet wrapper """

from typing import Optional, List, Dict, Any
import torch
from torch import nn
import pytorch_lightning as pl
from torchmetrics import F1Score, Precision, Recall
import wandb

# from pl_bolts.optimizers.lr_scheduler import LinearWarmupCosineAnnealingLR

# import matplotlib.pyplot as plt
from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
    recall_score,
    precision_score,
    # confusion_matrix,
    # ConfusionMatrixDisplay,
)

from image_modalities_classifier.models.t_resnet import IResnet
from image_modalities_classifier.models.efficient import EfficientNet


model_dict = {
    "resnet18": IResnet,
    "resnet34": IResnet,
    "resnet50": IResnet,
    "resnet101": IResnet,
    "resnet152": IResnet,
    "efficientnet-b0": EfficientNet,
    "efficientnet-b1": EfficientNet,
    "efficientnet-b4": EfficientNet,
    "efficientnet-b5": EfficientNet,
}


def create_model(model_name, model_hparams):
    if model_name in model_dict:
        return model_dict[model_name](**model_hparams)
    else:
        assert (
            False
        ), f'Unknown model name "{model_name}". Available models are: {str(model_dict.keys())}'


class ModalityModule(pl.LightningModule):
    """Lightning ResNet wrapper with support to ResNet18, 34, 50, 101, 152"""

    # pylint: disable=unused-argument
    def __init__(
        self,
        classes: List[str],
        num_classes: int,
        name: str = "resnet18",
        pretrained: bool = True,
        fine_tuned_from: str = "whole",
        lr: float = 1e-3,
        metric_monitor: str = "val_loss",
        mode_scheduler: str = "min",
        class_weights: Optional[List[float]] = None,
        mean_dataset: Optional[List[float]] = None,
        std_dataset: Optional[List[float]] = None,
        patience: Optional[int] = None,
    ):
        super().__init__()
        self.save_hyperparameters(
            "name",
            "classes",
            "num_classes",
            "pretrained",
            "fine_tuned_from",
            "lr",
            "class_weights",
            "metric_monitor",
            "mode_scheduler",
            "mean_dataset",
            "std_dataset",
            "patience",
        )

        model_params = {
            "name": self.hparams.name,
            "num_classes": self.hparams.num_classes,
            "fine_tuned_from": self.hparams.fine_tuned_from,
            "pretrained": self.hparams.pretrained,
        }
        self.model = create_model(name, model_params)

        loss_weight = (
            torch.Tensor(self.hparams.class_weights).to("cuda")
            if class_weights is not None
            else None
        )
        self.loss = nn.CrossEntropyLoss(weight=loss_weight)

    # pylint: disable=arguments-differ
    def forward(self, imgs):
        """Forward function that is run when visualizing the graph"""
        return self.model(imgs)

    def training_step(self, batch, batch_idx) -> float:
        # batch_idx needs to be as a parameter to match signature
        imgs, labels = batch
        preds = self.model(imgs)
        loss = self.loss(preds, labels)
        acc = (preds.argmax(dim=-1) == labels).float().mean()

        self.log("train_acc", acc, on_step=False, on_epoch=True)
        self.log("train_loss", loss, on_step=False, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        # batch_idx needs to be as a parameter to match signature
        imgs, labels = batch
        preds = self.model(imgs)
        loss = self.loss(preds, labels)
        acc = (preds.argmax(dim=-1) == labels).float().mean()
        self.log("val_acc", acc, on_step=False, on_epoch=True)
        self.log("val_loss", loss, on_step=False, on_epoch=True)

    def test_step(self, batch, batch_idx):
        # batch_idx needs to be as a parameter to match signature
        imgs, labels = batch
        out = self.model(imgs)
        loss = self.loss(out, labels)

        preds = out.argmax(dim=-1)
        return {"loss": loss, "test_preds": preds, "test_trues": labels}

    def test_epoch_end(self, outputs):
        preds = torch.stack([vec for x in outputs for vec in x["test_preds"]])
        target = torch.stack([vec for x in outputs for vec in x["test_trues"]])

        params = {"task": "multiclass", "num_classes": self.hparams.num_classes}
        # macro
        macro_params = {**params, "average": "macro"}
        f1_metric = F1Score(**macro_params).to(self.device)
        recall = Recall(**macro_params).to(self.device)
        precision = Precision(**macro_params).to(self.device)
        f1_macro = f1_metric(preds, target)  # pylint: disable=not-callable
        recall_macro = recall(preds, target)  # pylint: disable=not-callable
        prec_macro = precision(preds, target)  # pylint: disable=not-callable
        # micro
        micro_params = {**params, "average": "micro"}
        f1_metric = F1Score(**micro_params).to(self.device)
        recall = Recall(**micro_params).to(self.device)
        precision = Precision(**micro_params).to(self.device)
        f1_micro = f1_metric(preds, target)  # pylint: disable=not-callable
        recall_micro = recall(preds, target)  # pylint: disable=not-callable
        prec_micro = precision(preds, target)  # pylint: disable=not-callable
        # weighted
        weighted_params = {**params, "average": "weighted"}
        f1_metric = F1Score(**weighted_params).to(self.device)
        recall = Recall(**weighted_params).to(self.device)
        precision = Precision(**weighted_params).to(self.device)
        f1_weighted = f1_metric(preds, target)  # pylint: disable=not-callable
        recall_weighted = recall(preds, target)  # pylint: disable=not-callable
        prec_weighted = precision(preds, target)  # pylint: disable=not-callable

        self.log("test_macro_f1", f1_macro)
        self.log("test_micro_f1", f1_micro)
        self.log("test_weighted_f1", f1_weighted)

        self.log("test_macro_recall", recall_macro)
        self.log("test_micro_recall", recall_micro)
        self.log("test_weighted_recall", recall_weighted)

        self.log("test_macro_precision", prec_macro)
        self.log("test_micro_precision", prec_micro)
        self.log("test_weighted_precision", prec_weighted)

        y_true = target.cpu().numpy()
        preds = preds.cpu().numpy()
        self.logger.experiment.log(
            {
                "conf_mat": wandb.plot.confusion_matrix(
                    probs=None,
                    y_true=y_true,
                    preds=preds,
                    class_names=self.hparams.classes,
                )
            }
        )

    def configure_optimizers(self):
        if self.hparams.mode_scheduler is None:
            optimizer = torch.optim.AdamW(self.parameters(), lr=self.hparams.lr)
            return optimizer

        weight_decay = 1e-5
        if self.hparams.name in ["efficientnet-b4", "efficientnet-b5"]:
            weight_decay = 5e-6

        # if "efficient" in self.hparams.name:
        #     # https://catalog.ngc.nvidia.com/orgs/nvidia/resources/efficientnet_for_pytorch
        #     weight_decay = 1e-5
        #     if self.hparams.name in ["efficientnet-b4", "efficientnet-b5"]:
        #         weight_decay = 5e-6

        #     optimizer = torch.optim.RMSprop(
        #         self.parameters(),
        #         lr=self.hparams.lr,
        #         momentum=0.9,
        #         weight_decay=weight_decay,
        #     )
        #     scheduler = LinearWarmupCosineAnnealingLR(
        #         optimizer, warmup_epochs=10, max_epochs=100
        #     )
        #     return [optimizer], [scheduler]

        optimizer = torch.optim.AdamW(
            self.parameters(), lr=self.hparams.lr, weight_decay=weight_decay
        )

        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode=self.hparams.mode_scheduler,
            patience=5,  # Patience for the Scheduler
            verbose=True,
            eps=1e-4,
        )
        # scheduler = torch.optim.lr_scheduler.MultiStepLR(
        #     optimizer, milestones=[20, 50, 75], gamma=0.1
        # )
        return {
            "optimizer": optimizer,
            "lr_scheduler": scheduler,
            "monitor": self.hparams.metric_monitor,
        }

    def feature_extraction(self):
        features = nn.Sequential(*list(self.model.children())[:-1])
        return features
