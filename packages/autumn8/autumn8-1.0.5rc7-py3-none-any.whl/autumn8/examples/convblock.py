import torch
from torch import nn


class ConvBlock(nn.Module):
    def __init__(self):
        super(ConvBlock, self).__init__()
        self.conv = nn.Conv2d(32, 32, 3, 1, padding=1)
        self.conv2 = nn.Conv2d(32, 32, 3, 1, padding=1)
        self.conv3 = nn.Conv2d(32, 32, 3, 1, padding=1)

    def forward(self, x):
        return self.conv3(self.conv2(self.conv(x))) + x
