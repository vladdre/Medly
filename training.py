from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from datasets import Dataset
import torch
import json

# Încarcă datele din fișierul JSON
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# validare minimă structură
clean_data = []
for item in data:
    if all(k in item for k in ('input', 'boala', 'medicamente_recomandate', 'investigatii_recomandate', 'recomandari_suplimentare')):
        clean_data.append(item)
    else:
        continue
data = clean_data

# Pregătește datele pentru antrenament
inputs = []
labels = []
for item in data:
    input_text = f"Completează fișa medicală: {item['input']}"
    label_text = f"Boala: {item['boala']}. Tratament recomandat: {', '.join([med['nume'] for med in item['medicamente_recomandate']])}. Investigații suplimentare: {', '.join(item['investigatii_recomandate'])}. Recomandări suplimentare: {', '.join(item['recomandari_suplimentare'])}."
    inputs.append(input_text)
    labels.append(label_text)

# Creează un dataset Hugging Face
dataset = Dataset.from_dict({'input_texts': inputs, 'labels': labels})

# Încarcă modelul și tokenizer-ul
model_name = "t5-base"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# parametri
MAX_LEN = 256

# Funcție de tokenizare
def tokenize_function(examples):
    model_inputs = tokenizer(examples['input_texts'], max_length=MAX_LEN, truncation=True, padding='max_length')
    # tokenizare pentru target/labels
    labels_encoding = tokenizer(examples['labels'], max_length=MAX_LEN, truncation=True, padding='max_length')
    labels_ids = labels_encoding['input_ids']
    # înlocuiește pad_token_id cu -100 pentru a ignora în loss
    labels_ids = [[(tok if tok != tokenizer.pad_token_id else -100) for tok in label] for label in labels_ids]
    model_inputs['labels'] = labels_ids
    return model_inputs

# Tokenizează dataset-ul și scoate coloanele vechi
tokenized = dataset.map(tokenize_function, batched=True, remove_columns=['input_texts', 'labels'])

# split train/validation
split = tokenized.train_test_split(test_size=0.1) if len(tokenized) > 1 else {'train': tokenized, 'test': tokenized}
train_dataset = split['train']
eval_dataset = split.get('test', split['train'])

# Data collator pentru padding dinamic
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# Setează argumentele de antrenament
training_args = TrainingArguments(
    output_dir="./finetuned_t5_model",
    eval_strategy="steps",  # evaluare la fiecare pas
    save_strategy="steps",  # salvare la fiecare pas
    save_steps=500,  # salvează modelul la fiecare 500 de pași
    logging_steps=100,  # loghează progresul la fiecare 100 de pași
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=23,
    weight_decay=0.01,
    save_total_limit=2,
    load_best_model_at_end=True,  # va salva și încărca cel mai bun model
    metric_for_best_model="loss",  # folosește loss pentru alegerea celui mai bun model
)

# Creează Trainer-ul
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Antrenează modelul
trainer.train()

# Salvează modelul și tokenizer-ul finetunat
trainer.save_model("./finetuned_t5_model")
tokenizer.save_pretrained("./finetuned_t5_model")
