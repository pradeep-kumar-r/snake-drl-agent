import torch
from torch import nn
from src.config import config


class ConvDQN(nn.Module):
    def __init__(self, num_classes: int=config.get_model_config().NUM_ACTIONS):
        super().__init__()
        self.num_classes = num_classes
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.relu1 = nn.ReLU()
        self.maxpool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU()
        self.maxpool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(32 * 10 * 10, 64)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(64, 16)
        self.relu4 = nn.ReLU()
        self.output = nn.Linear(16, num_classes)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.maxpool1(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.maxpool2(x)
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = self.relu3(x)
        x = self.fc2(x)
        x = self.relu4(x)
        x = self.output(x)
        return x