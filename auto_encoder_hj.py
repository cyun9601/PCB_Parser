#%%
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import json
from pcb_parser import PCB
from pcb_parser.geometry import Polygon, Component, merge_polygon
import math
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
#%%
# 커스텀 데이터셋 클래스 정의
class PCB_dataset(Dataset):
    def __init__(self, path, resolution):
        self.path = path
        with open(path, 'r') as f:
            data = json.load(f)

        self.pcb = PCB(data, resolution)
        self.pcb_block_size = 128
        
        self.pcb_list = self.pcb.get_unfixed_components()

        self.pcb_height = math.ceil(self.pcb.board.cv_img.shape[0]/self.pcb_block_size)*self.pcb_block_size
        self.pcb_width = math.ceil(self.pcb.board.cv_img.shape[1]/self.pcb_block_size)*self.pcb_block_size

        print(self.pcb_list)
        self.dataset = []
        for i in range(len(self.pcb_list)):
            print(i)
            self.dataset.append(self.zero_padding(self.make_component(i))[np.newaxis, :])

        print(self.dataset[0])
        self.dataset = np.concatenate(self.dataset, axis=0)
        print(self.dataset.shape)
        self.dataset = torch.tensor(self.dataset, dtype=torch.float32)
        self.dataset = torch.where(self.dataset == 255, torch.tensor(1, dtype=torch.float32), self.dataset)
        
        print(self.dataset.shape, self.dataset)


    def zero_padding(self, img):
        size = (self.pcb_height, self.pcb_width)
        padd = ((0,0), (0, size[0]-img.shape[1]), (0, size[1]-img.shape[2]))
        return np.pad(img, padd, 'constant', constant_values=0)

    def make_component(self, idx):
        tmp = self.pcb.get_component(self.pcb_list[idx])
        return np.array([tmp.cv_top_img, tmp.cv_bottom_img])

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index):
        x = self.dataset[index]
        return x, _

class CNNAutoencoder(nn.Module):
    def __init__(self):
        super(CNNAutoencoder, self).__init__()

        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(2, 8, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.Conv2d(8, 16, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 16, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 8, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.ConvTranspose2d(8, 2, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(2),
            nn.Sigmoid()
        )

    def forward(self, x):
        print(x.device)
        print('x', x.shape)
        x = self.encoder(x)
        print('x_encode', x.shape)
        x = self.decoder(x)
        print('x_decode',x.shape)
        return x

    def encode(self, x):
        return self.encoder(x)

# Hyperparameters
learning_rate = 0.001
epochs = 1000

batch_size = 16
shuffle = True

# 모델 인스턴스화
model = CNNAutoencoder()
dataset = PCB_dataset('/VOLUME/PNR/data/sample_data.json', 0.05)
custom_dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=6)
test_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=2)

# Device configuration
#device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = torch.device('cuda:1')
print(device)
#%%
# Initialize the autoencoder model
model = CNNAutoencoder().to(device)

# Loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)


from sklearn.metrics import f1_score

# Training loop
for epoch in range(epochs):
    for batch_idx, (data, _) in enumerate(custom_dataloader):
        data = data.to(device)

        # Forward pass
        outputs = model(data)
        loss = criterion(outputs, data)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print('12341')
    model.eval()
    with torch.no_grad():
        y_true = []
        y_pred = []
        print('eval')
        for data, _ in test_loader:
            data = data.to(device)
            outputs = model(data).cpu()
            outputs = torch.where(outputs >= 0.5, torch.tensor(1, dtype=torch.float32), torch.tensor(0, dtype=torch.float32))
            print(data)
            print(outputs)
            #torch에서 data와 outputs의 f1 score 계산
            y_true.extend(data.cpu().numpy().reshape(-1).tolist())
            y_pred.extend(outputs.cpu().numpy().reshape(-1).tolist())
        #print(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average='micro')
        print(f'Epoch [{epoch + 1}/{epochs}], F1 score: {f1:.4f}')
        if f1 > 0.99:
            break

        # Early stopping
    model.train()

print('Training finished!')


#%%