# M4 - Generative AI

This module has one lesson notebook and a final project.

## Lesson notebook: retrieval-augmented generation

[`01-retrieval-augmented-generation.ipynb`](01-retrieval-augmented-generation.ipynb) explains the basics of RAG and builds the smallest complete version of it over the course's own documents: why a language model needs retrieval, the five steps (chunk, embed, retrieve, augment, generate), keyword versus neural embeddings on the same corpus, how to measure retrieval with hit rate and MRR, and the design choices and failure modes, including prompt injection through documents. It needs no API key; the generation step calls a real model only when an `ANTHROPIC_API_KEY` is present and shows the prompt otherwise. Neural embeddings are used when `sentence-transformers` is installed (Colab installs it) and the notebook falls back to TF-IDF when it is not.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maglionejm/fontys-tech-exercises/blob/main/M4%20-%20Generative%20AI/01-retrieval-augmented-generation.ipynb)

## Final project: Generative AI vs. traditional AI

**A 1,500-word paper.** Explain how generative AI differs from traditional AI, and argue which approach suits a real-world problem you choose. This is the final deliverable of the Generative AI module. It is individual work, in English, handed in by email as described in section 5.

This brief is built like an AI system: each section below is a stage in the pipeline. The one-page version is [`guidelines.pdf`](guidelines.pdf); a document template with the right headings and formatting is in [`paper-template.docx`](paper-template.docx) (also as [Markdown](paper-template.md)).

## 1. Input: the task

**Core question.** *What makes generative AI (for example ChatGPT, Claude, DALL·E) fundamentally different from traditional AI (for example machine learning models that classify or predict), and when should each be used?*

Choose **one real-world domain** (healthcare, finance, education, logistics, art, your own field) and use it as the running example throughout the paper.

You have built traditional AI yourself in this course: the Titanic survival model of Module 2 and the irony classifier of Module 3 are classifiers that learn a mapping from inputs to labels. You have also used generative tools throughout this module. Use what you built and used as concrete material; a paper that argues from its own experience reads better than one assembled from definitions.

## 2. Architecture: paper structure

Organise the paper in these five stages, in this order, and use the section titles in the second column as your headings. Word counts are targets; the total is 1,500 words, with a tolerance of 10 percent, not counting the title, the reference list and the appendix.

| Stage | Section title | What to include | Words |
|---|---|---|---|
| Training data | Background | Define traditional AI (machine learning that classifies or predicts) and generative AI (models that produce new content); cite at least four academic or otherwise credible sources | 300 |
| Model | Core comparison | Compare how each learns, what it outputs, what data it needs, how it is evaluated and how it fails (classify or predict versus create new content) | 500 |
| Inference | Case study | Apply both approaches to your domain with concrete examples: a task where a traditional model is the right tool, a task where a generative model is, and one where the choice is debatable | 350 |
| Output | Limits and ethics | Discuss bias, hallucinations, transparency, cost and environmental impact, with at least one example from your domain | 250 |
| Fine-tuning | Conclusion | Your own argued position on when to use each, and what you would recommend to a decision-maker in your domain | 100 |

## 3. AI component: human and machine

You must use a generative AI tool (ChatGPT, Claude, Gemini or similar) at least once while preparing the paper, and document it. Add a one-page **appendix** after the reference list (not counted in the word limit) with three parts:

1. **Prompt log.** Your two or three most important prompts, the tool and model you used, the date, and a summary of each response.
2. **Fact-check.** One claim the AI made, the source you used to verify it, and your verdict: confirmed, partly right, or wrong.
3. **Reflection** (about 100 words). What the AI did well, where it failed or hallucinated, and what that taught you about generative AI.

End the appendix with one sentence declaring which parts of the work AI tools assisted with. The paper text must be your own writing. AI output copied into the paper without disclosure is plagiarism under the course policy, and so is text that merely paraphrases an AI answer sentence by sentence.

## 4. Evaluation: rubric (100 points)

| Criterion | What is assessed | Points |
|---|---|---|
| **Conceptual accuracy** | A correct, precise distinction between generative and traditional AI: what each learns, what each outputs, how each is evaluated. Full marks for definitions a specialist would sign; half for broadly right but vague; few for confusing products with concepts or factual errors | 30 |
| **Analysis and argument** | Comparison along clear dimensions rather than a list of differences; a case study with concrete tasks on both sides; a position that weighs trade-offs. Full marks when every claim is supported and the position follows from the comparison | 25 |
| **Sources** | At least four credible sources (peer-reviewed papers, textbooks, technical reports and documentation from research labs, reputable press), cited in the text and listed consistently in APA 7 or MLA 9. Chatbot output and Wikipedia are not sources | 15 |
| **AI appendix** | An honest prompt log with tool, model and date; a real fact-check with the verification source and a verdict; a reflection that names a specific success or failure; the declaration sentence | 15 |
| **Language and structure** | Clear academic English; the five headings in the given order; within the word limit; a reader who knows nothing about your domain can follow it | 15 |

What the points do not cover is handled as follows: a paper more than 10 percent over or under length loses 5 points; a missing appendix scores 0 on that criterion and the paper is checked for undisclosed AI text; plagiarism or undisclosed AI writing is handled under the course policy, from loss of credit for the project to removal from the module. Late work follows the course policy.

## 5. Deployment: hand-in

| | |
|---|---|
| **Send to** | maglionejm@gmail.com |
| **Email subject, exactly** | `[M4_SURNAME_NAME \| PROJECT_GENAI]`, with your own surname and first name in capitals, for example `[M4_JANSEN_LUUK \| PROJECT_GENAI]` |
| **Attachment** | Your paper as a **PDF attached to the email**, named `M4_SURNAME_NAME_PROJECT_GENAI.pdf`. Links to Google Docs, Drive or other platforms are not accepted |
| **Format** | PDF, 12 pt, 1.5 line spacing, APA 7 or MLA 9 citations, English, 1,500 words (10 percent tolerance) plus the appendix |
| **Who** | Individual work. One email per student; if you must resend, keep the same subject and add `v2` to the file name |

The subject line matters more than it looks: submissions are collected automatically by subject, and in earlier modules emails with a different subject were not registered and had to be resent. Copy it from this page.

## What a strong paper looks like

It defines both kinds of AI in one paragraph a specialist would accept, then spends its words on the comparison and the case: tasks from a real domain, one where a classifier wins because the answer is a label and the data is structured, one where a generative model wins because the output is new text or images, and one where the honest answer is "it depends, and here is on what". It names costs (data, compute, money, energy) and failure modes (bias, hallucination, opacity) with an example rather than an adjective. It cites sources where claims are made, not in a block at the end. Its appendix shows an author who used the AI, caught it being wrong once, and learned something from that.

## Checklist before you send

- The five headings appear in the given order; the word count (title, references and appendix excluded) is between 1,350 and 1,650.
- At least four credible sources, cited in the text and in the reference list in one style.
- The appendix has the prompt log, the fact-check with its source and verdict, the reflection and the declaration sentence.
- The file is a PDF named `M4_SURNAME_NAME_PROJECT_GENAI.pdf`, attached to the email, 12 pt, 1.5 spacing.
- The email goes to maglionejm@gmail.com with the exact subject `[M4_SURNAME_NAME | PROJECT_GENAI]` before the deadline announced in class.

## Starting points for sources

These are starting points, not a reading list; you still need sources from your own domain.

- Jordan, M. I., & Mitchell, T. M. (2015). Machine learning: Trends, perspectives, and prospects. *Science*, 349(6245), 255–260.
- Goodfellow, I., et al. (2014). Generative adversarial nets. *Advances in Neural Information Processing Systems* 27.
- Vaswani, A., et al. (2017). Attention is all you need. *Advances in Neural Information Processing Systems* 30.
- Bommasani, R., et al. (2021). On the opportunities and risks of foundation models. arXiv:2108.07258.
- Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? *Proceedings of FAccT 2021*.
- Strubell, E., Ganesh, A., & McCallum, A. (2019). Energy and policy considerations for deep learning in NLP. *Proceedings of ACL 2019*.
