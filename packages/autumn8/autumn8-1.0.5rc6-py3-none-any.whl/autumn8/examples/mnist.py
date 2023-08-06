import torch
import torch.nn.functional as F
from torch import nn

import autumn8  # you need to `pip install autumn8` for this to work


def preprocess(input):
    print("Preprocess")
    return input


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.maxPool = nn.MaxPool2d(2)
        self.dropout1 = nn.Dropout2d(0.25)
        self.flatten = nn.Flatten(1)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.relu2 = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.conv2(x)
        x = self.maxPool(x)
        x = self.dropout1(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


dummy_input = torch.randn(1, 1, 28, 28)
model = Net()
autumn8.lib.attach_model(model, dummy_input, preprocess=preprocess)

# alternatively, to upload directly instead of using the CLI:
# autumn8.lib.service.upload_model("mnist", model, dummy_input)
