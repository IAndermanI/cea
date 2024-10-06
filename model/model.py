from transformers import GPT2Tokenizer, GPT2ForSequenceClassification, Trainer, TrainingArguments
import torch
from sklearn.model_selection import train_test_split
import pandas as pd
import os

data = pd.read_csv("data.csv")
train_texts, val_texts, train_labels, val_labels = train_test_split(data["text"], data["grade"], test_size=0.2)

model_path = "local_model/rugpt3large_based_on_gpt2"

if not os.path.exists(model_path):
    print(f"Model not found in path {model_path}, downloading...")
    model = GPT2ForSequenceClassification.from_pretrained("ai-forever/rugpt3large_based_on_gpt2", num_labels=5)
    tokenizer = GPT2Tokenizer.from_pretrained("ai-forever/rugpt3large_based_on_gpt2")

    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)
else:
    print(f"Model found in path {model_path}.")
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    model = GPT2ForSequenceClassification.from_pretrained(model_path, num_labels=5)
train_encodings = tokenizer(train_texts.tolist(), truncation=True, padding=True, max_length=512)
val_encodings = tokenizer(val_texts.tolist(), truncation=True, padding=True, max_length=512)

class NewsDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = NewsDataset(train_encodings, train_labels.tolist())
val_dataset = NewsDataset(val_encodings, val_labels.tolist())


training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()

model.save_pretrained("./fine-tuned-model-1")