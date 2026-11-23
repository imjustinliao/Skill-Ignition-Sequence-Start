# Track: models (training, fine-tuning, evaluation)

For projects whose core is a model: a classifier, a fine-tuned LLM, a vision or audio model, a recommender. Guide like a careful ML engineer: evaluation first, the simplest approach that clears the bar, no surprise GPU bills.

## Questions

Ask only those you cannot infer, alongside the drafted direction (`intake.md` › 3).

1. **Input, output, and what "good" means**: the metric and the bar it must clear.
2. **What data do you have, and may you use it** (license, consent, personal data)?
3. **Compute budget and where it runs**: free notebook GPU · a rented GPU for a few hours · a paid model API; a demo, an API or a device. Default: an API or a pretrained model, shipped as a demo.

## The draft

`docs/architecture.md` gets: the approach ladder and where to start, the evaluation set and metric, the baseline, compute and cost estimate (GPU hours × hourly rate, or API calls × price), data handling, and how it ships (Shape: data → training → evaluation → serving). The message summarizes it, with the cost on its own line.

**The ladder**, climbing only when evaluation shows the current step falls short: prompt an existing model → add retrieval → fine-tune (LoRA or QLoRA) → train from scratch.

## Principles (after Karpathy's training recipe)

- **Become one with the data** before writing model code: look at many examples, check labels, duplicates and imbalance.
- **Build the full train-and-evaluate skeleton first** with a trivial model and a fixed seed. Establish baselines (input-independent, simple heuristic, human) and check the initial loss is sane.
- **Overfit one batch** to prove the pipeline can learn, then scale up with a proven architecture and default optimizer settings; regularize; tune with random search.
- **Evaluation before training**: a held-out test set the model never trains on, the metric fixed in advance, results across more than one seed.
- **Read outputs by hand**: twenty real predictions tell you more than a number.

## Defaults

Hugging Face for models and datasets (`transformers`, `datasets`, PEFT, TRL); PyTorch; Weights & Biases or TensorBoard for tracking; pinned package versions and fixed seeds for reproducibility; a tiny smoke run before any paid run.

## Build and verify

- End to end on about 100 samples first: data loads, the model trains, evaluation runs, the loss falls.
- Compare against the baseline every time; check for train/test leakage.
- Log every run's config, data version, metric and cost in the tracker; summarize the best runs in `docs/progress.md` › Decisions.
- **Every paid run needs the owner's approval** with its estimated cost; set spend limits on API keys and stop idle GPUs.

## Ship

A demo people can try: a Hugging Face Space with Gradio (or a small web page calling the model's API), plus a model card covering intended use, data, evaluation results, limits and license. Sample inputs in the README.

## Pitfalls

Leakage between train and test · no baseline · one seed reported as a result · unreproducible runs · data you have no right to use or that holds personal data · training from scratch when a prompt or fine-tune would do · surprise GPU bills.
