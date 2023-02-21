""" Resnet wrapper """

from typing import Optional, List, Dict, Any
import torch
from torch import nn
from torchvision import models
import pytorch_lightning as pl
from pl_bolts.optimizers.lr_scheduler import LinearWarmupCosineAnnealingLR

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


class Resnet(pl.LightningModule):
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
        preds = self.model(imgs)
        # loss = self.loss(y_hat, y_true)
        # _, preds = torch.max(y_hat, dim=1)
        acc = (preds.argmax(dim=-1) == labels).float().mean()
        self.log("test_acc", acc, on_step=False, on_epoch=True)
        # return {"loss": loss, "test_preds": preds, "test_trues": y_true}

    # def test_epoch_end(self, outputs):
    #     avg_loss = torch.stack([x["loss"] for x in outputs]).mean()
    #     y_preds = torch.stack([vec.float() for x in outputs for vec in x["test_preds"]])
    #     y_trues = torch.stack([vec.float() for x in outputs for vec in x["test_trues"]])
    #     accuracy = 100 * torch.sum(y_preds == y_trues.data) / (y_trues.shape[0] * 1.0)

    #     # fig, axis = plt.subplots(figsize=(4, 4))
    #     # cm = confusion_matrix(y_trues.cpu(), y_preds.cpu())
    #     # disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    #     # if self.logger:
    #     #     self.logger.experiment.log({"confusion_matrix": fig})

    #     test_f1 = f1_score(y_trues.cpu(), y_preds.cpu(), average="macro")
    #     balanced_acc = balanced_accuracy_score(y_trues.cpu(), y_preds.cpu())
    #     recall = recall_score(y_trues.cpu(), y_preds.cpu(), average="macro")
    #     precision = precision_score(y_trues.cpu(), y_preds.cpu(), average="macro")

    #     self.log("test_acc", accuracy)
    #     self.log("test_loss", avg_loss)
    #     self.log("macro_f1", test_f1)
    #     self.log("balanced_acc", balanced_acc)
    #     self.log("recall", recall)
    #     self.log("precision", precision)

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
