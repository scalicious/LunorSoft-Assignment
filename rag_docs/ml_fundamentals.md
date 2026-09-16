# Machine Learning Fundamentals for Engineering Students

## What is Machine Learning?

Machine Learning (ML) is a subset of AI where models **learn from data** instead of following explicit rules. Instead of `if-else` logic, we give the model examples and let it find patterns.

**Three Main Types:**
- **Supervised Learning** - Labelled data (input → output pairs). Example: predicting house prices.
- **Unsupervised Learning** - No labels, find hidden structure. Example: customer segmentation.
- **Reinforcement Learning** - Agent learns by reward/punishment. Example: game-playing AI.

---

## Core Concepts

### Training vs Inference
- **Training**: Feeding data to the model and adjusting its parameters (weights) to minimize error. Expensive (GPU, hours/days).
- **Inference**: Running the trained model on new data to get predictions. Fast (CPU is often fine).

### Loss Function
Measures how wrong the model's predictions are. The goal is to minimize loss.
- **MSE (Mean Squared Error)** - Used for regression: `loss = mean((y_pred - y_true)²)`
- **Cross-Entropy Loss** - Used for classification: penalizes wrong confident predictions heavily.

### Gradient Descent & Backpropagation
- **Gradient Descent** - The optimizer adjusts weights by moving in the direction that decreases loss.
- **Backpropagation** - Computes the gradient of loss with respect to every weight using the chain rule.
- **Learning Rate** - Controls the step size. Too high = overshoots. Too low = takes forever.

### Overfitting & Underfitting
- **Overfitting** - Model memorizes training data but fails on new data. Fix: more data, dropout, regularization.
- **Underfitting** - Model is too simple to capture patterns. Fix: larger model, more epochs.
- **Validation Set** - Held-out data used to check for overfitting during training.

---

## Key Algorithms

### Linear Regression
Predicts a continuous value by fitting a line: `y = mx + b`
```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### Logistic Regression (Classification)
Despite the name, it's a classification algorithm. Uses sigmoid to output probabilities.
```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X_train, y_train)
```

### Decision Trees & Random Forests
- **Decision Tree** - Splits data on feature thresholds. Prone to overfitting.
- **Random Forest** - Ensemble of decision trees. Reduces overfitting by averaging.
```python
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100)
```

### K-Nearest Neighbors (KNN)
Classifies based on the `k` closest training examples. Simple but slow for large data.
```python
from sklearn.neighbors import KNeighborsClassifier
model = KNeighborsClassifier(n_neighbors=5)
```

---

## Neural Networks

### Architecture
```
Input Layer → Hidden Layer(s) → Output Layer
```
Each layer applies: `output = activation(W * input + b)`

### Common Activation Functions
| Function | Formula                   | Use Case            |
|----------|---------------------------|---------------------|
| ReLU     | `max(0, x)`               | Hidden layers (CNN) |
| Sigmoid  | `1 / (1 + e^(-x))`        | Binary output       |
| Softmax  | `e^x / sum(e^x)`          | Multi-class output  |
| Tanh     | `(e^x - e^(-x))/(e^x + e^(-x))` | RNNs         |

### PyTorch Neural Net Example
```python
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(784, 256),  # Input layer
            nn.ReLU(),
            nn.Dropout(0.2),      # Regularization
            nn.Linear(256, 10),   # Output layer
        )
    
    def forward(self, x):
        return self.layers(x)

model = SimpleNet()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()
```

### Training Loop
```python
for epoch in range(num_epochs):
    for X_batch, y_batch in dataloader:
        optimizer.zero_grad()        # Clear gradients
        predictions = model(X_batch) # Forward pass
        loss = criterion(predictions, y_batch)
        loss.backward()              # Backpropagation
        optimizer.step()             # Update weights
    print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
```

---

## Large Language Models (LLMs) & Fine-Tuning

### What is a Transformer?
The architecture powering modern LLMs (GPT, Qwen, LLaMA). Key components:
- **Self-Attention** - Each token "looks at" all other tokens to understand context.
- **Positional Encoding** - Tells the model the order of tokens (transformers have no notion of order by default).
- **Feed-Forward Layers** - Standard dense layers applied after attention.

### What is Fine-Tuning?
Taking a pre-trained model (already knows language) and training it further on your specific domain data. Much cheaper than training from scratch.

### What is LoRA (Low-Rank Adaptation)?
A parameter-efficient fine-tuning technique. Instead of updating all billions of weights, LoRA injects small trainable matrices into specific layers.
- **r** (rank) - Controls the size of adapters. Higher = more capacity but more parameters.
- **lora_alpha** - Scaling factor. Usually set to `2 * r`.
- **target_modules** - Which layers to apply LoRA to (typically `q_proj`, `v_proj`).

**Result:** Only ~1-5% of parameters are trained, but performance approaches full fine-tuning!

### What is RAG (Retrieval-Augmented Generation)?
Instead of training the model to memorize facts, we retrieve relevant documents at inference time and feed them into the prompt. This avoids hallucination and allows up-to-date knowledge.
```
User Query → Embed query → Search vector DB → Get top-k docs → Augment prompt → LLM generates answer
```

---

## Evaluation Metrics

| Task           | Metric                 | Description                                         |
|----------------|------------------------|-----------------------------------------------------|
| Regression     | MSE, MAE, R²           | How close predictions are to true values            |
| Classification | Accuracy, F1, AUC-ROC  | How correctly classes are predicted                 |
| Language Gen.  | BLEU, ROUGE, Perplexity| How similar generated text is to reference text     |
| Retrieval      | MRR, NDCG, Recall@k    | How well relevant docs are ranked                   |

### BLEU Score
Measures overlap between generated and reference text using n-gram precision. Used in translation and code generation.
- Score ranges from 0 (no match) to 1 (perfect match).

### Perplexity
Measures how "surprised" the model is by a text. Lower = better. Used to evaluate language models.
`Perplexity = exp(cross-entropy loss)`
