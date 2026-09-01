import torch
import torch.nn as nn
import os

class CROMADownstreamClassifier(nn.Module):
    """
    Lightweight downstream classification head for CROMA joint embeddings.
    Designed for patch-level (tile) classification (e.g., Water, Built-up).
    """
    def __init__(self, embedding_dim: int = 768, num_classes: int = 2):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_classes = num_classes
        
        # Lightweight Linear Probe
        # If linear is insufficient, this can be upgraded to an MLP.
        self.classifier = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(embedding_dim, num_classes)
        )
        
    def forward(self, joint_embedding: torch.Tensor) -> torch.Tensor:
        """
        Args:
            joint_embedding: [Batch, embedding_dim] tensor from CROMA
        Returns:
            logits: [Batch, num_classes] 
        """
        return self.classifier(joint_embedding)

    def save_checkpoint(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.state_dict(), path)
        
    def load_checkpoint(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Checkpoint not found at {path}")
        self.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
