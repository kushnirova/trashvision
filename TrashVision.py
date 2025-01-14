import torch
import torchvision
from torchvision import transforms, datasets, models
from torch.utils.data import Dataset, DataLoader
import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Konfiguracja
DATA_DIR = './crop_sq'
BATCH_SIZE = 32
NUM_EPOCHS = 8
LEARNING_RATE = 0.0002
DEVICE = torch.device("cuda:0")

class TrashDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.image_files = [f for f in os.listdir(data_dir) if f.endswith('.JPG')]

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = self.image_files[idx]
        img_path = os.path.join(self.data_dir, img_name)
        image = Image.open(img_path).convert('RGB')

        label_name = img_name[:-4] + '.txt'
        label_path = os.path.join(self.data_dir, label_name)
        labels = []
        try:
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    labels.append([class_id, x_center, y_center, width, height])
        except FileNotFoundError:
            print(f"Brak pliku etykiet dla {img_name}")
            return None

        if self.transform:
            image = self.transform(image)
        
        # Konwersja etykiet
        labels = torch.tensor(labels)

        return image, labels

if __name__ == '__main__':

	# Transformacje danych
	data_transforms = {
		'train': transforms.Compose([
			transforms.Resize((224, 224)),
			transforms.RandomHorizontalFlip(),
			transforms.ToTensor(),
			transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
		])
	}

	image_dataset = TrashDataset(DATA_DIR, transform=data_transforms['train'])
	dataloader = DataLoader(image_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)

	model = models.resnet18(weights="ResNet18_Weights.IMAGENET1K_V1")
     
	# Zmiana ostatniej warstwy, aby pasowała do liczby kategorii
	num_ftrs = model.fc.in_features
	model.fc = torch.nn.Linear(num_ftrs, 4)

	model = model.to(DEVICE)

	# Funkcja straty i optymalizator
	criterion = torch.nn.CrossEntropyLoss()
	optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)


	# Pętla treningu
	for epoch in range(NUM_EPOCHS):
		for images, labels in dataloader:
			if images is None:
				continue
			images = images.to(DEVICE)
			target = labels.squeeze(1).long()[:, 0].to(DEVICE)
      
			optimizer.zero_grad()
			outputs = model(images)

			loss = criterion(outputs, target)
			loss.backward()
			optimizer.step()
		print(f'Epoka [{epoch+1}/{NUM_EPOCHS}], Strata: {loss.item():.4f}')



	torch.save(model.state_dict(), 'trash_classifier.pth')