import os
import sys
import time
import json
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    has_torch = True
except ImportError:
    has_torch = False

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if has_torch:
    from engine.models.croma_classifier import CROMADownstreamClassifier
    BaseDataset = Dataset
else:
    BaseDataset = object

class CachedEmbeddingDataset(BaseDataset):
    def __init__(self, embeddings, labels):
        self.embeddings = embeddings
        self.labels = labels

    def __len__(self):
        return len(self.embeddings)

    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]

def generate_synthetic_cache(num_samples=100, embedding_dim=768):
    """
    Generates synthetic embeddings for testing the training script locally
    without downloading 60GB of BigEarthNet-MM data.
    """
    print(f"Generating {num_samples} synthetic embeddings for local script validation...")
    if not has_torch: return None, None
    X = torch.randn(num_samples, embedding_dim)
    # Binary classification: 0 (Water), 1 (Built-up)
    y = torch.randint(0, 2, (num_samples,))
    return X, y

def train_croma_head(is_synthetic=True, epochs=5, batch_size=32, lr=1e-3):
    print("--- CROMA Downstream Head Training ---")
    
    if not has_torch:
        print("[PENDING HARDWARE] PyTorch or Scikit-Learn is not installed.")
        print("Cannot train the downstream head locally on this hardware.")
        return
        
    from engine.models.croma_classifier import CROMADownstreamClassifier
    
    embedding_dim = 768
    num_classes = 2
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    
    if is_synthetic:
        print("\n[WARNING] Using synthetic data to validate training pipeline.")
        print("This does NOT produce a scientifically valid trained model.")
        X_train, y_train = generate_synthetic_cache(800, embedding_dim)
        X_val, y_val = generate_synthetic_cache(200, embedding_dim)
    else:
        # Placeholder for real data loading (e.g. BigEarthNet-MM)
        # 1. Load manifest
        # 2. Iterate through files, run CROMA to get `joint_GAP`
        # 3. Cache embeddings to disk (e.g., experiments/croma_embeddings/)
        # 4. Load from cache
        print("\n[PENDING DATA/HARDWARE] Real dataset (e.g. BigEarthNet-MM) not found.")
        print("Stopping honest execution rather than fabricating real evaluation metrics.")
        return
        
    train_dataset = CachedEmbeddingDataset(X_train, y_train)
    val_dataset = CachedEmbeddingDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    model = CROMADownstreamClassifier(embedding_dim=embedding_dim, num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    print("\nStarting Training (Frozen CROMA + Trainable Linear Probe)...")
    start_time = time.time()
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(train_loader):.4f}")
        
    # Validation
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch = X_batch.to(device)
            logits = model(X_batch)
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(y_batch.numpy())
            
    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='macro')
    
    print("\n--- Validation Metrics (SYNTHETIC ONLY) ---")
    print(f"Accuracy: {acc:.4f}")
    print(f"Macro F1: {f1:.4f}")
    print("\nPer-class results:")
    print(classification_report(all_labels, all_preds, target_names=["Water", "Built-up"]))
    
    if is_synthetic:
        print("\n[NOTE] Not saving synthetic checkpoint to avoid polluting the model registry.")
    else:
        save_path = "models/croma_head_water_builtup.pt"
        model.save_checkpoint(save_path)
        print(f"Model saved to {save_path}")
        
        # Save experiment metadata
        os.makedirs("experiments/croma_classifier", exist_ok=True)
        meta = {
            "model": "CROMA-base + LinearProbe",
            "dataset": "BigEarthNet-MM (mocked/synthetic)",
            "train_samples": len(train_dataset),
            "val_samples": len(val_dataset),
            "embedding_dim": embedding_dim,
            "epochs": epochs,
            "accuracy": acc,
            "macro_f1": f1
        }
        with open("experiments/croma_classifier/metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
            
if __name__ == "__main__":
    # By default, we run in synthetic mode to prove the script works locally
    # To run real training, we would set is_synthetic=False and provide data.
    train_croma_head(is_synthetic=True)
