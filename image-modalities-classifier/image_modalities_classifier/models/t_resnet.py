import torch.nn as nn
from torchvision import models
from image_modalities_classifier.models.identity import Identity


class IResnet(nn.Module):
    def __init__(self, name, num_classes, pretrained=True, fine_tuned_from="whole"):
        super().__init__()
        self.model_name = name
        self.num_classes = num_classes
        self.pretrained = pretrained
        self.fine_tuned_from = fine_tuned_from
        self.model = None

        self._create_network()
        self._init_params()

    def _create_network(self):
        if self.model_name == "resnet18":
            if self.pretrained:
                model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            else:
                model = models.resnet18(weights=None)
        elif self.model_name == "resnet34":
            if self.pretrained:
                model = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
            else:
                model = models.resnet34(weights=None)
        elif self.model_name == "resnet50":
            if self.pretrained:
                model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            else:
                model = models.resnet50(weights=None)
        elif self.model_name == "resnet101":
            if self.pretrained:
                model = models.resnet101(weights=models.ResNet101_Weights.DEFAULT)
            else:
                model = models.resnet101(weights=None)
        elif self.model_name == "resnet152":
            if self.pretrained:
                model = models.resnet152(weights=models.ResNet152_Weights.DEFAULT)
            else:
                model = models.resnet152(weights=None)

        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, self.num_classes)
        self.model = model

    def _init_params(self):
        # by default set all to false
        if not self.pretrained:
            for m in self.modules():
                if isinstance(m, nn.Conv2d):
                    nn.init.kaiming_normal_(
                        m.weight, mode="fan_out", nonlinearity="relu"
                    )
                elif isinstance(m, nn.BatchNorm2d):
                    nn.init.constant_(m.weight, 1)
                    nn.init.constant_(m.bias, 0)

        for param in self.model.parameters():
            param.requires_grad = False
        # case for retraining everything
        if self.fine_tuned_from == "whole":
            for param in self.model.parameters():
                param.requires_grad = True
            return
        for param in self.model.fc.parameters():
            param.requires_grad = True

    def forward(self, x):
        return self.model(x)

    def feature_extractor(self):
        """Retrieve the backbone that gets features before FC"""
        model = self.model
        model.fc = Identity()
        return model
