import torch.nn as nn
from torchvision import models
from image_modalities_classifier.models.identity import Identity


class EfficientNet(nn.Module):
    """Test with efficient net b5"""

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
        if self.model_name == "efficientnet-b0":
            model = models.efficientnet_b0(pretrained=self.pretrained)
            in_features = 1280
        elif self.model_name == "efficientnet-b1":
            model = models.efficientnet_b1(pretrained=self.pretrained)
            in_features = 1280
        elif self.model_name == "efficientnet-b4":
            model = models.efficientnet_b4(pretrained=self.pretrained)
            in_features = 1792
        elif self.model_name == "efficientnet-b5":
            model = models.efficientnet_b5(pretrained=self.pretrained)
            in_features = 2048
        model.classifier[1] = nn.Linear(
            in_features=in_features, out_features=self.num_classes
        )
        self.model = model

    def _init_params(self):
        # by default set all to false
        if not self.pretrained:
            for m in self.modules():
                if isinstance(m, nn.Conv2d):
                    nn.init.kaiming_normal_(
                        m.weight, mode="fan_out", nonlinearity="silu"
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
        """Retrieva the backbone that gets features before FC"""
        # TODO: should be a deepcopy
        model = self.model
        model.classifier = Identity()
        return model
