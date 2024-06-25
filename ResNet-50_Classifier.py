import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from PIL import Image
import argparse
from PIL import Image, UnidentifiedImageError
import random


class CustomDataset(Dataset):
    def __init__(self, real_dir, fake_dir, transform=None):
        self.real_dir = real_dir
        self.fake_dir = fake_dir
        self.transform = transform
        self.real_images = [
            (os.path.join(real_dir, img), 0)
            for img in os.listdir(real_dir)
            if img.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        self.fake_images = [
            (os.path.join(fake_dir, img), 1)
            for img in os.listdir(fake_dir)
            if img.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        self.total_images = self.real_images + self.fake_images
        print("hey")

    def __len__(self):
        return len(self.total_images)

    def __getitem__(self, idx):
        img_name, label = self.total_images[idx]
        try:
            image = Image.open(img_name).convert("RGB")
            if self.transform:
                image = self.transform(image)
        except (IOError, UnidentifiedImageError):
            print(f"Warning: Skipping corrupt image {img_name}")
            return self.__getitem__((idx + 1) % len(self.total_images))
        except Exception as e:
            print(f"An error occurred: {e}")
            return self.__getitem__((idx + 1) % len(self.total_images))

        return image, label


def train_model(
    train_loader,
    val_loader,
    model,
    criterion,
    optimizer,
    scheduler,
    num_epochs,
    device,
    early_stopping_patience,
):
    best_acc = 0.0
    epochs_no_improve = 0

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        total_corrects = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            _, preds = torch.max(outputs, 1)
            total_loss += loss.item() * inputs.size(0)
            total_corrects += torch.sum(preds == labels.data)

        epoch_loss = total_loss / len(train_loader.dataset)
        epoch_acc = total_corrects.double() / len(train_loader.dataset)

        model.eval()
        val_loss = 0.0
        val_corrects = 0

        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            with torch.no_grad():
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            _, preds = torch.max(outputs, 1)
            val_loss += loss.item() * inputs.size(0)
            val_corrects += torch.sum(preds == labels.data)

        val_loss = val_loss / len(val_loader.dataset)
        val_acc = val_corrects.double() / len(val_loader.dataset)

        print(
            f"Epoch {epoch+1}/{num_epochs}, Train Loss: {epoch_loss:.4f}, Train Acc: {epoch_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
        )

        if val_acc > best_acc:
            best_acc = val_acc
            epochs_no_improve = 0
            torch.save(model.state_dict(), "new_it2i.pth")
            print(
                f"Model improved and saved at epoch {epoch+1} with validation accuracy {val_acc:.4f}"
            )
        else:
            epochs_no_improve += 1
            print(
                f"No improvement in validation accuracy for {epochs_no_improve} epochs."
            )
            if epochs_no_improve >= early_stopping_patience:
                print(f"Early stopping triggered after {epoch+1} epochs.")
                break

        scheduler.step()

    return model


def test_model(test_loader, model, device):
    print("ha")
    model.eval()
    correct = 0
    total = 0
    total_real_images = sum(
        [labels.size(0) for inputs, labels in test_loader if labels[0] == 0]
    )
    total_fake_images = sum(
        [labels.size(0) for inputs, labels in test_loader if labels[0] == 1]
    )
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            true_positive += (
                ((predicted == 1) & (labels == 1)).sum().item()
            )  ## fake is positive
            true_negative += (
                ((predicted == 0) & (labels == 0)).sum().item()
            )  ## real is negative
            false_positive += (
                ((predicted == 1) & (labels == 0)).sum().item()
            )  ## real labled as fake
            false_negative += (
                ((predicted == 0) & (labels == 1)).sum().item()
            )  ## fake labled as real

    print(f"Total images tested: {total}")
    print(f"Total real images: {total_real_images}")
    print(f"Total fake images: {total_fake_images}")
    print(f"False positives (Real images misclassified as Fake): {false_positive}")
    print(f"False negatives (Fake images misclassified as Real): {false_negative}")
    real_accuracy = (
        (true_negative / total_real_images) * 100 if total_real_images > 0 else 0
    )
    fake_accuracy = (
        (true_positive / total_fake_images) * 100 if total_fake_images > 0 else 0
    )
    print(f"Accuracy for real images: {real_accuracy:.2f}%")
    print(f"Accuracy for fake images: {fake_accuracy:.2f}%")
    overall_accuracy = (correct / total) * 100
    print(f"Overall accuracy: {overall_accuracy:.2f}%")
    true_positives = total_fake_images - false_negative
    precision = true_positives / (true_positives + false_positive)
    recall = true_positives / total_fake_images
    f1_score = 2 * (precision * recall) / (precision + recall)
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1 Score: {f1_score:.2%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and Test Image Detection Model")
    parser.add_argument(
        "--mode",
        choices=["train", "test", "both"],
        required=True,
        help="Mode to run the script in",
    )
    parser.add_argument(
        "--num_epochs", type=int, default=300, help="Number of epochs to train"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=64,
        help="Batch size for training and validation",
    )
    parser.add_argument(
        "--learning_rate", type=float, default=0.005, help="Initial learning rate"
    )
    parser.add_argument(
        "--early_stopping_patience", type=int, default=5, help="Early stopping patience"
    )
    args = parser.parse_args()

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    train_real_dir = "/home/yuying/Text2Image/resnet/training_data/real"
    train_fake_dir = "/home/yuying/Text2Image/resnet/training_data/DALLE_image"
    test_real_dir = "/home/yuying/Text2Image/resnet/testing_data/real"
    test_fake_dir = "/home/yuying/Text2Image/resnet/testing_data/dream_image"

    model = models.resnet50(weights=None)
    weights = torch.load(
        "/home/yuying/Text2Image/resnet/resnet50_a1h2_176-001a1197.pth"  ## This file is from the paper "GenImage: A Million-Scale Benchmark for Detecting AI-Generated Image"
    )
    model.load_state_dict(weights, strict=False)

    model.fc = nn.Linear(model.fc.in_features, 2)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=args.learning_rate, momentum=0.9)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.num_epochs)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    if args.mode in ["train", "both"]:
        train_dataset = CustomDataset(
            train_real_dir, train_fake_dir, transform=transform
        )
        val_dataset = CustomDataset(
            test_real_dir, test_fake_dir, transform=transform
        )  # Use a separate validation set if available
        train_loader = DataLoader(
            train_dataset, batch_size=args.batch_size, shuffle=True
        )
        val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
        model = train_model(
            train_loader,
            val_loader,
            model,
            criterion,
            optimizer,
            scheduler,
            args.num_epochs,
            device,
            args.early_stopping_patience,
        )

    if args.mode in ["test", "both"]:
        test_dataset = CustomDataset(test_real_dir, test_fake_dir, transform=transform)
        test_loader = DataLoader(
            test_dataset, batch_size=args.batch_size, shuffle=False
        )
        model.load_state_dict(torch.load("new_it2i.pth"))
        model.to(device)
        test_model(test_loader, model, device)
