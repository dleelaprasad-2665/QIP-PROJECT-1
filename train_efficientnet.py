import os
import json
import time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import efficientnet_b0
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# Set seeds
torch.manual_seed(42)
np.random.seed(42)

DATA_DIR = Path("training_data/materials")
MODEL_DIR = Path("backend/ai_engine/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Device
device = torch.device("cpu")
print(f"Training on device: {device}")

# Preprocessing transforms (consistent between training and inference)
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.3),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Datasets
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

# Compute class weights for cross entropy to handle imbalance
class_counts = [0] * num_classes
for _, label in train_dataset.samples:
    class_counts[label] += 1

total_samples = len(train_dataset)
class_weights = [total_samples / (num_classes * max(1, count)) for count in class_counts]
class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32).to(device)

print(f"Class sample counts in Train: {dict(zip(class_names, class_counts))}")
print(f"Class weights: {[round(w, 2) for w in class_weights]}")

# DataLoaders
batch_size = 16
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

# Build EfficientNet-B0
model = efficientnet_b0(weights=None)
in_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(p=0.3, inplace=True),
    nn.Linear(in_features, num_classes)
)
model = model.to(device)

criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=15)

# Training Loop
num_epochs = 15
best_val_acc = 0.0
best_model_path = MODEL_DIR / "efficientnet_b0_material.pth"

history = {
    "epoch": [],
    "train_loss": [],
    "train_acc": [],
    "val_loss": [],
    "val_acc": []
}

print("\n" + "="*70)
print(f"{'Epoch':<8} | {'Train Loss':<12} | {'Train Acc':<10} | {'Val Loss':<10} | {'Val Acc':<10} | {'Status':<10}")
print("="*70)

start_time = time.time()

for epoch in range(1, num_epochs + 1):
    # Train
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
    
    train_loss = running_loss / total
    train_acc = (correct / total) * 100.0
    
    # Validate
    model.eval()
    val_loss_running = 0.0
    val_correct = 0
    val_total = 0
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            val_loss_running += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            val_correct += torch.sum(preds == labels.data).item()
            val_total += labels.size(0)
            
    val_loss = val_loss_running / val_total
    val_acc = (val_correct / val_total) * 100.0
    
    status = ""
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save({
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "class_to_idx": class_to_idx,
            "class_names": class_names,
            "best_val_acc": best_val_acc
        }, best_model_path)
        status = "SAVED BEST"
        
    history["epoch"].append(epoch)
    history["train_loss"].append(round(train_loss, 4))
    history["train_acc"].append(round(train_acc, 2))
    history["val_loss"].append(round(val_loss, 4))
    history["val_acc"].append(round(val_acc, 2))
    
    print(f"{epoch:<8} | {train_loss:<12.4f} | {train_acc:<9.1f}% | {val_loss:<10.4f} | {val_acc:<9.1f}% | {status:<10}")

total_duration = time.time() - start_time
print("="*70)
print(f"Training completed in {total_duration:.1f}s. Best Val Accuracy: {best_val_acc:.1f}%")

# Load best checkpoint for final evaluation on unseen held-out TEST set
print("\n" + "="*70)
print("EVALUATING BEST CHECKPOINT ON HELD-OUT TEST SET (60 UNSEEN IMAGES)")
print("="*70)

checkpoint = torch.load(best_model_path, map_location=device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

y_true = []
y_pred = []
y_probs = []

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs = inputs.to(device)
        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1)
        _, preds = torch.max(outputs, 1)
        
        y_true.extend(labels.cpu().numpy())
        y_pred.extend(preds.cpu().numpy())
        y_probs.extend(probs.cpu().numpy())

y_true = np.array(y_true)
y_pred = np.array(y_pred)

acc = accuracy_score(y_true, y_pred)
prec_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
rec_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)

print(f"\nOverall Test Accuracy : {acc * 100:.2f}%")
print(f"Macro Precision        : {prec_macro * 100:.2f}%")
print(f"Macro Recall           : {rec_macro * 100:.2f}%")
print(f"Macro F1-Score         : {f1_macro * 100:.2f}%")

print("\nDetailed Per-Class Performance:")
clf_report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

conf_matrix = confusion_matrix(y_true, y_pred).tolist()
print("\nConfusion Matrix (Rows: Ground Truth, Columns: Predicted):")
print(f"{'':<16} " + " ".join([f"{c[:6]:>7}" for c in class_names]))
for i, row in enumerate(conf_matrix):
    row_str = " ".join([f"{val:>7}" for val in row])
    print(f"{class_names[i]:<16} {row_str}")

# Save full results
results_payload = {
    "model_architecture": "EfficientNet-B0",
    "training_epochs": num_epochs,
    "total_training_time_seconds": round(total_duration, 1),
    "classes": class_names,
    "class_to_idx": class_to_idx,
    "history": history,
    "test_metrics": {
        "accuracy": round(acc * 100, 2),
        "macro_precision": round(prec_macro * 100, 2),
        "macro_recall": round(rec_macro * 100, 2),
        "macro_f1": round(f1_macro * 100, 2)
    },
    "per_class_metrics": clf_report,
    "confusion_matrix": conf_matrix
}

with open(MODEL_DIR / "training_evaluation.json", "w") as f:
    json.dump(results_payload, f, indent=2)

print(f"\nTrained weights and evaluation report saved successfully to {MODEL_DIR}!")
