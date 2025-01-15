import torch
from torchvision import models, transforms
from PIL import Image

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
NUM_CLASSES = 4

model = models.resnet18(weights=None)
 # Nie ładujemy pre-trained weights
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, NUM_CLASSES)
model.load_state_dict(torch.load('trash_classifier_v9.pth', weights_only=True))
model.to(DEVICE)
model.eval()
#ResNet18
#trash_classifierv1 = 8/16
#trash_classifierv2 = 12/16
#trash_classifierv3 = 12/16
#trash_classifierv4 = 10/16 - myli papier z plastikiem
#trash_classifierv5 = 12/16 - myli papier z plastikiem
#trash_classifierv6 = 13/16 - myli papier z plastikiem
#trash_classifierv7 = 11/16
#trash_classifierv8 = 8/16
#trash_classifierv9 = 14/16
#trash_classifierv10 = 13/16
#trash_classifierv10 = 12/16


categories = ["Plastik", "Metal", "Szkło", "Papier"]

data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def classify_image(image_path):
    image = Image.open(image_path).convert('RGB')
    image = data_transforms(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad(): # Wyłączamy obliczanie gradientów podczas inferencji
        outputs = model(image)
        _, predicted = torch.max(outputs, 1) # Pobieramy indeks z największą wartością (predykcja)

    return predicted.item()

# 0 = Plastik
# 1 = Metal
# 2 = Szkło
# 3 = Papier
correct_ans = [3, 0, 1, 2, 3, 0, 1, 3, 0, 0, 0, 1, 0, 0, 0]
correct_count = 0

for i in range(len(correct_ans)):
    image_path = './test_images/test_' + str(i+1) + ".jpg" # Zastąp ścieżką do obrazu
    predicted_class = classify_image(image_path)
    print("-"*50)
    if predicted_class == correct_ans[i]:
        print("Dobra odpowiedź!")
        print(f'Przewidywana klasa: {categories[predicted_class]} dla test {i+1}')
        correct_count+=1
    else:
        print("Niepoprawna odpowiedź!")
        print(f'Przewidywana klasa: {categories[predicted_class]} dla test {i+1}. Poprawna klasa to {categories[correct_ans[i]]} ')

print("Tyle dobrze:", correct_count, "/", len(correct_ans))
