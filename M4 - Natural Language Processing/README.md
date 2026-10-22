# M4 - Natural Language Processing

The final project of the course: a text classification challenge. You receive tweets labelled *ironic* or *not ironic*, build a model that tells them apart, predict a hidden test set, and write up what you did and what you found. There is no lesson notebook in this module; the project is the lesson.

## What is in this folder

| Path | What it is |
|---|---|
| [`guidelines.pdf`](guidelines.pdf) | The one-page brief: the challenge, the data, what to hand in, the rules, how the 100 points are awarded, and advice. Read it first. |
| [`irony-final-project.ipynb`](irony-final-project.ipynb) | The starter notebook. Sections 1 to 6 are given and run as they are: data loading, a six-tweet guessing quiz, two exploration starters, a preprocessing function with switches, the evaluation rules with macro-F1 explained, and a baseline that works. Sections 3, 7, 8 and 10 are your work: exploration, experiments, error analysis and report. Section 9 writes your submission. |
| `data/train.csv` | 3,450 tweets with columns `id, text, label` (1 = ironic, 0 = not ironic). Explore, train and validate on this file. |
| `data/test.csv` | 1,151 tweets with columns `id, text`. Predict these; the labels are hidden and used for grading. |
| `data/sample_submission.csv` | The required format of your predictions: `id, label`, one row per test id, labels 0 or 1. |

## How to run

**Google Colab, zero setup:** open the notebook with the badge below and choose Runtime > Run all. The setup cell downloads the two data files from this repository when they are not next to the notebook.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M4%20-%20Natural%20Language%20Processing/irony-final-project.ipynb)

**Locally:** clone the repository, install the course requirements (`pip install -r requirements.txt` from the repository root), and open the notebook from this folder so that `data/` is found. Everything in the given sections runs on a laptop CPU in well under a minute; no API keys, no accounts, no GPU. The optional pretrained-model route in section 7 is the only part where a Colab GPU helps.

## What you hand in

1. The notebook, completed and run from top to bottom (Kernel > Restart & Run All).
2. `submission.csv`, written by section 9 of the notebook from the model your report names.

Name both files with your name or student number. The deadline and the hand-in channel are announced in class. The checklist at the end of the notebook is the hand-in checklist.

## The data

The tweets come from the SemEval-2018 Task 3 shared task on irony detection (Van Hee, Lefever and Hoste, 2018; [aclanthology.org/S18-1005](https://aclanthology.org/S18-1005/)). Their writers had tagged them `#irony`, `#sarcasm` or `#not`; the organisers removed those hashtags and had three linguists annotate every tweet. The corpus is republished in the TweetEval benchmark (Barbieri et al., 2020; [github.com/cardiffnlp/tweeteval](https://github.com/cardiffnlp/tweeteval)) and on Kaggle ([TweetEval, Multi-task Classification Benchmark](https://www.kaggle.com/datasets/thedevastator/tweeteval-a-multi-task-classification-benchmark)). For this course the corpus was pooled, de-duplicated and split once with a fixed seed into the two files above. User names appear as `@user` and links as `http`; hashtags, emoji, capitals and punctuation were kept.

Two rules from the guidelines bear repeating. The test labels are never used, looked up or reconstructed, and that includes the public copies of the original corpus. Pretrained language models are welcome if declared, except models that were already trained on this dataset, such as `cardiffnlp/twitter-roberta-base-irony`, because they have seen the test tweets.
