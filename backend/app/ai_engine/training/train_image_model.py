"""
Reproducible Training Script for Deepfake Detection
Dataset layout:
  datasets/
    train/
      authentic/
      manipulated/
    val/
      authentic/
      manipulated/
"""
import os
import argparse
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

from app.ai_engine.image_detector.detector import MesoInception4


class DeepfakeDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.samples = []
        self.transform = transform
        
        auth_dir = os.path.join(root_dir, "authentic")
        manip_dir = os.path.join(root_dir, "manipulated")
        
        if os.path.exists(auth_dir):
            for fname in os.listdir(auth_dir):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.samples.append((os.path.join(auth_dir, fname), 0))
                    
        if os.path.exists(manip_dir):
            for fname in os.listdir(manip_dir):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.samples.append((os.path.join(manip_dir, fname), 1))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label


def train_model(data_dir, output_model_path, epochs=10, batch_size=32, lr=0.0005):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training on device: {device}")

    train_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    val_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    train_dataset = DeepfakeDataset(os.path.join(data_dir, "train"), transform=train_transforms)
    val_dataset = DeepfakeDataset(os.path.join(data_dir, "val"), transform=val_transforms)

    if len(train_dataset) == 0:
        print("[!] Warning: Dataset directory is empty. To train with real data, place images in:")
        print(f"    {os.path.join(data_dir, 'train/authentic')} and {os.path.join(data_dir, 'train/manipulated')}")
        return

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = MesoInception4(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)

    best_val_loss = float('inf')

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / max(1, total)
        epoch_acc = correct / max(1, total)

        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f}")

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()

        val_loss = val_loss / max(1, val_total)
        val_acc = val_correct / max(1, val_total)
        scheduler.step(val_loss)

        print(f"          | Val Loss: {val_loss:.4f}   | Val Acc: {val_acc:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
            torch.save(model.state_dict(), output_model_path)
            print(f"[*] Checkpoint saved to {output_model_path}")

    print("[*] Training completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MesoInception Deepfake Detection Model")
    parser.add_argument("--data_dir", type=str, default="./datasets", help="Path to dataset root")
    parser.add_argument("--output", type=str, default="../model_artifacts/meso_weights.pth")
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    train_model(args.data_dir, args.output, epochs=args.epochs)
