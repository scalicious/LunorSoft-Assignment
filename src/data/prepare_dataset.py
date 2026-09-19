import json
import os
import random
from datasets import load_dataset

# Configuration
PUBLIC_DATASET_NAME = "iamtarun/python_code_instructions_18k_alpaca"
NUM_PUBLIC_EXAMPLES = 1000
CUSTOM_EXAMPLES_PATH = "data/custom_examples/education_examples.jsonl"
OUTPUT_DIR = "data/processed"
TRAIN_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "train.jsonl")
EVAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "eval.jsonl")

SYSTEM_PROMPT = "You are a helpful coding assistant for engineering students. You explain code clearly, flag common mistakes, and teach step by step."

def format_chatml(instruction, output):
    """Formats instruction and output into ChatML format."""
    return {
        "text": f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
    }

def main():
    print(f"Loading {NUM_PUBLIC_EXAMPLES} examples from {PUBLIC_DATASET_NAME}...")
    dataset = load_dataset(PUBLIC_DATASET_NAME, split="train")
    
    # Filter for examples that have python code in output and are somewhat substantial
    # To keep it simple, we'll just take the first NUM_PUBLIC_EXAMPLES after filtering out very short outputs
    filtered_public = []
    for row in dataset:
        if len(row['output']) > 20: # Simple filter
            filtered_public.append(row)
        if len(filtered_public) >= NUM_PUBLIC_EXAMPLES:
            break
            
    print(f"Loaded {len(filtered_public)} public examples.")

    print(f"Loading custom examples from {CUSTOM_EXAMPLES_PATH}...")
    custom_examples = []
    if os.path.exists(CUSTOM_EXAMPLES_PATH):
        with open(CUSTOM_EXAMPLES_PATH, 'r') as f:
            for line in f:
                if line.strip():
                    custom_examples.append(json.loads(line))
    print(f"Loaded {len(custom_examples)} custom examples.")

    # Combine and format
    all_examples_formatted = []
    
    for ex in filtered_public:
        # Public dataset uses 'instruction', 'input', 'output'
        # Sometimes 'input' is empty. Combine instruction and input if input exists.
        instruction = ex['instruction']
        if ex.get('input') and ex['input'].strip():
            instruction += "\n\n" + ex['input']
        all_examples_formatted.append(format_chatml(instruction, ex['output']))

    for ex in custom_examples:
        all_examples_formatted.append(format_chatml(ex['instruction'], ex['output']))
        
    print(f"Total formatted examples: {len(all_examples_formatted)}")

    # Shuffle
    random.seed(42)
    random.shuffle(all_examples_formatted)

    # Split (last 80 for eval, rest for train)
    eval_split_size = 80
    train_examples = all_examples_formatted[:-eval_split_size]
    eval_examples = all_examples_formatted[-eval_split_size:]

    # Write to disk
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(TRAIN_OUTPUT_PATH, 'w') as f:
        for ex in train_examples:
            f.write(json.dumps(ex) + '\n')
            
    with open(EVAL_OUTPUT_PATH, 'w') as f:
        for ex in eval_examples:
            f.write(json.dumps(ex) + '\n')
            
    print(f"Saved {len(train_examples)} training examples to {TRAIN_OUTPUT_PATH}")
    print(f"Saved {len(eval_examples)} evaluation examples to {EVAL_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
