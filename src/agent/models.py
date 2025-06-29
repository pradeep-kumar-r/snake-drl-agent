import torch
from torch import nn
from typing import Tuple


class ConvDQN(nn.Module):
    def __init__(self, 
                 num_classes: int, 
                 input_shape: Tuple[int, int, int] = (3, 600, 600)):
        super().__init__()
        self.num_classes = num_classes
        self.input_shape = input_shape
        in_channels, in_height, in_width = input_shape
        
        # Conv Layer 1
        self.conv1 = nn.Conv2d(in_channels, 16, kernel_size=3, stride=1, padding=1)
        self.relu1 = nn.ReLU()
        self.maxpool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        h1 = in_height // 2
        w1 = in_width // 2
        
        # Conv Layer 2
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU()
        self.maxpool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        h2 = h1 // 2
        w2 = w1 // 2
        
        # Conv Layer 3
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.relu3 = nn.ReLU()
        self.maxpool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        h3 = h2 // 2
        w3 = w2 // 2
        
        # Calculate feature size for feed forward layers
        flattened_size = 64 * h3 * w3
        
        # FC Layer 1
        self.fc1 = nn.Linear(flattened_size, 128)
        self.relu1 = nn.ReLU()
        
        # FC Layer 2
        self.fc2 = nn.Linear(128, 64)
        self.relu2 = nn.ReLU()
        
        # Output Layer
        self.output = nn.Linear(64, num_classes)
        
    def _check_input_shape(self, x: torch.Tensor) -> bool:
        return self.input_shape == (x.shape[1], x.shape[2], x.shape[3])
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        
        if not self._check_input_shape(x):
            raise ValueError(f"Input shape must be {self.input_shape}, but got {(x.shape[1], x.shape[2], x.shape[3])}")
        
        # Apply convolutional layers
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.maxpool1(x)
        
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.maxpool2(x)
        
        x = self.conv3(x)
        x = self.relu3(x)
        x = self.maxpool3(x)
        
        x = x.view(x.size(0), -1) # Flatten
        
        x = self.fc1(x)
        x = self.relu1(x)
        
        x = self.fc2(x)
        x = self.relu2(x)
        
        x = self.output(x)
        return x