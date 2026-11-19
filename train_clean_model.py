import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import time
import json
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import sys

sys.stdout.reconfigure(line_buffering=True)

device = torch.device("cpu")
print(f"Training on device: {device}")

DATA_DIR = Path("training_data/materials_v3")
MODEL_DIR = Path("backend/ai_engine/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

batch_size = 16
image_size = (224, 224)

# Data Transforms
train_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomCrop(image_size),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.2),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_test_transform = transforms.Compose([
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

train_dataset = datasets.ImageFolder(str(DATA_DIR / "train"), transform=train_transform)
val_dataset = datasets.ImageFolder(str(DATA_DIR / "val"), transform=val_test_transform)
test_dataset = datasets.ImageFolder(str(DATA_DIR / "test"), transform=val_test_transform)

class_names = train_dataset.classes
class_to_idx = train_dataset.class_to_idx
idx_to_class = {v: k for k, v in class_to_idx.items()}
num_classes = len(class_names)

print(f"Detected {num_classes} classes: {class_names}")
print(f"Class-to-Index mapping: {class_to_idx}")
print(f"Dataset sizes: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")

# Save class mapping
with open(MODEL_DIR / "class_mapping.json", "w") as f:
    json.dump({
        "classes": class_names,
        "class_to_idx": class_to_idx,
        "idx_to_class": {str(k): v for k, v in idx_to_class.items()}
    }, f, indent=2)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

# Load Pretrained EfficientNet-B0
print("Loading Pretrained EfficientNet-B0 weights...")
weights = EfficientNet_B0_Weights.DEFAULT
model = efficientnet_b0(weights=weights)

in_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(p=0.3, inplace=True),
    nn.Linear(in_features, num_classes)
)
model = model.to(device)

criterion = nn.CrossEntropyLoss()

# Fine-tuning: differential learning rate
optimizer = optim.AdamW([
    {'params': model.features.parameters(), 'lr': 1e-4},
    {'params': model.classifier.parameters(), 'lr': 1e-3}
], weight_decay=1e-4)

num_epochs = 8
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

best_val_acc = 0.0
best_model_path = MODEL_DIR / "efficientnet_b0_material.pth"

print("\n" + "="*70)
print(f"{'Epoch':<8} | {'Train Loss':<12} | {'Train Acc':<10} | {'Val Loss':<10} | {'Val Acc':<10} | {'Status':<10}")
print("="*70)

start_time = time.time()

for epoch in range(1, num_epochs + 1):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        correct += torch.sum(preds == labels.data).item()
        total += labels.size(0)
        
    scheduler.step()
    
    epoch_train_loss = running_loss / total
    epoch_train_acc = correct / total
    
    # Validation
    model.eval()
    val_loss = 0.0
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            val_correct += torch.sum(preds == labels.data).item()
            val_total += labels.size(0)
            
    epoch_val_loss = val_loss / val_total
    epoch_val_acc = val_correct / val_total
    
    status = "Normal"
    if epoch_val_acc >= best_val_acc:
        best_val_acc = epoch_val_acc
        torch.save(model.state_dict(), best_model_path)
        status = "SAVED BEST"
        
    print(f"{epoch:<8} | {epoch_train_loss:<12.4f} | {epoch_train_acc*100:<9.1f}% | {epoch_val_loss:<10.4f} | {epoch_val_acc*100:<9.1f}% | {status}")

elapsed = time.time() - start_time
print("="*70)
print(f"Training completed in {elapsed:.1f}s. Best Val Accuracy: {best_val_acc*100:.1f}%")

# Test Set Evaluation
print("\nEvaluating on Unseen Test Set...")
model.load_state_dict(torch.load(best_model_path, map_location=device))
model.eval()

y_true = []
y_pred = []

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        _, preds = torch.max(outputs, 1)
        y_true.extend(labels.cpu().numpy())
        y_pred.extend(preds.cpu().numpy())

test_acc = accuracy_score(y_true, y_pred)
print(f"Final Test Accuracy: {test_acc*100:.2f}%\n")
print("Classification Report:")
print(classification_report(y_true, y_pred, target_names=class_names, digits=4))
print("Confusion Matrix:")
print(confusion_matrix(y_true, y_pred))
