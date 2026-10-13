# Chunking decision

**Date:** 2026-10-13
**Decided by:** Laiba Athar
**Corpus:** documents.py + corpus.py (16 documents)
**Eval set:** eval_set.py (29 answerable, 3 unanswerable)
**Embedding model:** voyage-3-lite

## Decision

We chose `sections_contextual` with a relevance floor of `0.50`.

Including the document title and section heading helps each chunk keep its meaning, even when the body does not mention the firm or office name.

## Evidence

| Strategy | R@1 | R@3 | MRR | Context words@3 | Answer acc. | Refusal acc. |
|---|---|---|---|---|---|---|
| whole_document | 0.690 | 1.000 | 0.845 | 862 | 28/29 | 3/3 |
| sections_contextual | 0.862 | 1.000 | 0.931 | 197 | 28/29 | 3/3 |
| fixed_overlap_25 | 0.517 | 0.931 | 0.668 | 277 | 23/29 | 3/3 |

Retrieval results come from `eval_results/retrieval.json`.
The answer and refusal results in this table were measured at floor `0.35`.

We then tested `sections_contextual` at floor `0.50`. It still answered
28/29 questions correctly and refused all 3 unanswerable questions.
Average input tokens fell from 423 at `0.35` to 379 at `0.50`.

## Why this one

We chose `sections_contextual` because it retrieved the required evidence
within the top three results for all 29 answerable questions, using an
average of 197 context words compared with 862 for whole documents.

At floor `0.50`, it kept the same answer and refusal accuracy as `0.35`
while reducing average input tokens from 423 to 379. 
We gave up the wider context of whole documents, but the smaller chunks were sufficient for
most questions in our evaluation.

## Known weaknesses

The strategy still misses q24, an exact-ID question about LP-3307,
because its similarity score falls below the floor. Hybrid retrieval
with exact identifier matching may help more than changing chunk sizes.

High similarity scores do not guarantee that the answer is present,
so the model still needs to refuse unsupported questions.

## Revisit when

We will repeat the evaluation if we add longer documents or new document
types, change the embedding model, or see more incorrect answers or false
refusals. Floor `0.50` is the highest tested floor that preserved accuracy
compared with `0.35`, not a proven optimum.
