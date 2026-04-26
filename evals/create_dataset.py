"""Upload existing Recce runs to LangSmith as an eval dataset."""

import os
from langsmith import Client

client = Client()

# Create the dataset
dataset_name = "Recce Eval Dataset"

# Delete if it already exists (so you can re-run this script)
for ds in client.list_datasets():
    if ds.name == dataset_name:
        client.delete_dataset(dataset_id=ds.id)
        print(f"Deleted existing dataset: {dataset_name}")

dataset = client.create_dataset(dataset_name, description="Competitive one-pagers for eval")
print(f"Created dataset: {dataset_name}")

# Find all complete runs
runs_dir = os.path.join(os.path.dirname(__file__), "..", "runs")
count = 0

for name in sorted(os.listdir(runs_dir)):
    run_path = os.path.join(runs_dir, name)
    final_path = os.path.join(run_path, "final.md")
    scout_path = os.path.join(run_path, "scout_notes.md")

    if not os.path.isdir(run_path):
        continue
    if not os.path.exists(final_path) or not os.path.exists(scout_path):
        continue

    with open(final_path) as f:
        final = f.read()
    with open(scout_path) as f:
        scout = f.read()

    client.create_example(
        inputs={
            "final_output": final,
            "scout_notes": scout,
            "run_name": name,
        },
        dataset_id=dataset.id,
    )
    count += 1
    print(f"  Added: {name}")

print(f"\nDone. {count} examples in dataset.")
