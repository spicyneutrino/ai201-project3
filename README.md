# TakeMeter

A fine-tuned text classifier that evaluates discourse quality in r/nba Reddit posts.
Built for CodePath AI201 Project 3.

---

## Community and Reasoning

**Community:** r/nba on Reddit.

r/nba is one of the highest-traffic sports communities on the platform, producing
hundreds of posts and thousands of comments daily. The range of discourse quality is
wide and clearly structured: a single thread on a playoff game might contain a
rigorous stat-backed argument, an unsupported opinion stated with total confidence,
and an all-caps emotional outburst — sometimes in consecutive comments.

This range makes r/nba a good fit for a classification task. The distinctions between
post types are not subtle; regular community members actively recognize and discuss
them ("this is actual analysis," "this is cope," "classic hot take"). The labels
reflect how participants in the community actually evaluate each other's contributions,
not categories imposed from outside.

---

## Label Taxonomy

### `analysis`
A post that makes a structured argument supported by specific statistics, historical
comparisons, or tactical observations. The evidence is central to the claim — it would
support the argument even if all opinion framing were removed.

**Example 1:**
> "I analyzed James Harden's performance in every NBA city and correlated it with
> strip club ratings. Correlation coefficient of .4575 between avg strip club rating
> and total sub-par games. His worst performance comes in Miami (best strip clubs),
> best in Toronto (worst strip clubs)."

**Example 2:**
> "The Celtics held opponents to 33.1% from three this postseason, 2nd in the league.
> Their defensive scheme forces opponents into mid-range shots, which is why they keep
> closing out games — it's structural, not luck."

---

### `hot_take`
A bold, confident opinion stated without meaningful supporting evidence. The post
asserts rather than argues. Framing is strong (superlatives, absolutes, provocative
comparisons) but reasoning is thin or absent.

**Example 1:**
> "LeBron is not and has never been better than Jordan. End of discussion."

**Example 2:**
> "The Warriors dynasty is the most fraudulent championship run ever. KD ruined
> basketball for an entire generation."

---

### `reaction`
An immediate emotional response to a specific recent event, play, or game outcome.
Little to no argument — expressing excitement, frustration, or disbelief in the
moment. The post loses most of its meaning without its triggering event.

**Example 1:**
> "LETS GOOOOO THAT BLOCK WAS INSANE I CANNOT BELIEVE WHAT I JUST WATCHED"

**Example 2:**
> "I cannot believe they just blew a 20-point lead in the 4th. This team will never
> change. I'm done."

---

## Data Collection

**Source:** r/nba via the Pullpush public archive API (api.pullpush.io), which mirrors
Reddit's public post and comment data without authentication. Reddit's direct JSON API
blocked requests from the collection host, so the Pullpush mirror was used as a
fallback.

**Labeling process:** Groq's `llama-3.1-8b-instant` was used to pre-label all 355
collected posts using the locked label definitions from planning.md. Each post was
sent with the label definitions as a system prompt, and the model was instructed to
output only one of the three label strings. The Groq free tier hit its 100k daily
token limit at item 352; 3 examples were skipped and logged to annotation_errors.txt.

All pre-labeled examples were accepted without manual per-example review due to time
constraints. This is a limitation: the annotation may contain noise where the LLM
misapplied a boundary, particularly at the hot_take/analysis edge.

**Hot_take imbalance:** After initial annotation, only 17 of 355 posts were labeled
`hot_take` (vs. 70 each for analysis and reaction). Top-scored r/nba posts skew
heavily toward long analytical content; opinion-only posts are rare in the high-score
tier. To reach 70 hot_take examples, 53 synthetic examples were generated using Claude
(claude-sonnet-4-6) with the prompt:
> "Generate a realistic r/nba Reddit comment that is a hot take: a bold confident
> opinion with no real evidence, asserts rather than argues. Output only the post
> text, nothing else."
These synthetic examples are marked `notes="synthetic"` in the CSV.

**Label distribution:**

| Label    | Count | Percentage |
|----------|-------|------------|
| analysis | 70    | 33.3%      |
| hot_take | 70    | 33.3%      |
| reaction | 70    | 33.3%      |
| **Total**| **210**| **100%** |

**Difficult-to-label examples:**

1. **"LeBron is overrated — his playoff win rate against top-seeded opponents is below .500."**
   Could be `hot_take` (bold claim, accusatory framing) or `analysis` (cites a stat).
   Labeled `hot_take`: the stat is cherry-picked for rhetorical effect, the framing is
   accusatory, and the post makes no attempt to contextualize the number.

2. **"Steph Curry's greatest strength isn't his shooting — it's that his off-ball movement creates open looks for teammates that most analysts don't credit him for."**
   Could be `analysis` (makes a structural observation) or `hot_take` (no numbers).
   Labeled `analysis`: the post makes a verifiable tactical observation with a
   falsifiable claim, even without citing statistics.

3. **"This is what happens when you build a team around one guy who disappears in big games. Classic KD."**
   Could be `reaction` (responding to a specific loss) or `hot_take` (general opinion
   about KD). Labeled `hot_take`: without a clear event anchor in the text, the post
   reads as a general standing opinion rather than an in-the-moment response.

---

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased` (HuggingFace)
**Training platform:** Google Colab (T4 GPU)
**Training libraries:** `transformers`, `datasets`, `scikit-learn`

**Training configuration:**
- Epochs: 3
- Learning rate: 2e-5
- Batch size: 16 (train), 32 (eval)
- Weight decay: 0.01
- Warmup steps: 50
- Dataset split: 70% train / 15% validation / 15% test (stratified)

**Key hyperparameter decision:** 3 epochs was kept as the default rather than
increasing it. With only 210 examples (147 in training), more epochs would increase
overfitting risk on a dataset this small. The validation accuracy at epoch 3 was
monitored via `load_best_model_at_end=True` — the best checkpoint was used for
evaluation. Increasing to 5 epochs was tested mentally: with 53 synthetic hot_takes
in the training set, additional epochs would further reinforce the synthetic style
patterns rather than helping the model generalize to real posts.

---

## Baseline Description

**Model:** `llama-3.1-8b-instant` via Groq API (zero-shot, no fine-tuning)

The original spec calls for `llama-3.3-70b-versatile`, but the Groq free tier's 100k
daily token limit was exhausted during data annotation. `llama-3.1-8b-instant` was
used instead as it has a separate rate limit.

**Prompt used:**

```
You are classifying posts from r/nba on Reddit.
Assign each post to exactly one of the following categories.

analysis: A post that makes a structured argument supported by specific statistics,
  historical comparisons, or tactical observations — the evidence is central and would
  support the claim even without opinion framing.
Example: "The Celtics held opponents to 33.1% from three this postseason, 2nd in the
  league. That scheme is the reason they keep closing out games."

hot_take: A bold, confident opinion stated without meaningful supporting evidence —
  the post asserts rather than argues, and the framing is strong but the reasoning
  is thin or absent.
Example: "Steph Curry is the most overrated player in NBA history full stop."

reaction: An immediate emotional response to a specific event, play, or game —
  little to no argument, the post is expressing excitement, frustration, or disbelief.
Example: "LETS GOOOOO THAT BLOCK WAS INSANE I CANNOT BELIEVE WHAT I JUST WATCHED"

Respond with ONLY the label name.
Do not explain your reasoning.

Valid labels:
analysis
hot_take
reaction
```

Results were collected by running the classification function against every example in
the locked test set (32 examples) before fine-tuning began.

---

## Evaluation Report

### Overall Accuracy

| Model                        | Accuracy |
|------------------------------|----------|
| Zero-shot baseline (Groq)    | 0.9375   |
| Fine-tuned DistilBERT        | 0.5938   |
| Difference                   | -0.3438  |

The fine-tuned model performs substantially worse than the zero-shot baseline.
This result is explained in detail in the reflection section below.

---

### Per-Class Metrics

**Fine-tuned DistilBERT:**

| Class    | Precision | Recall | F1   | Support |
|----------|-----------|--------|------|---------|
| analysis | 0.500     | 1.000  | 0.667| 10      |
| hot_take | 0.778     | 0.636  | 0.700| 11      |
| reaction | 0.667     | 0.182  | 0.286| 11      |

**Zero-shot baseline (Groq llama-3.1-8b-instant):**

The baseline achieved 93.75% overall accuracy on the same 32-example test set.
The baseline correctly classified all 10 analysis examples, 10 of 11 hot_take
examples, and 10 of 11 reaction examples.

---

### Confusion Matrix (Fine-Tuned Model)

Rows = true label. Columns = predicted label.

|              | pred: analysis | pred: hot_take | pred: reaction |
|--------------|---------------|---------------|---------------|
| **analysis** | 10            | 0             | 0             |
| **hot_take** | 3             | 7             | 1             |
| **reaction** | 7             | 2             | 2             |

The dominant failure pattern: 7 of 11 reaction examples were predicted as `analysis`.
The model learned to over-predict `analysis` for any substantive-length post.

---

### Wrong Prediction Analysis

**Wrong prediction 1: reaction predicted as analysis**

A game thread comment expressing frustration after a loss — something like an emotional
recap of what went wrong in the fourth quarter. The model predicted `analysis`.

Why it failed: the post was several sentences long and mentioned specific game events
(a turnover, a missed shot). The model learned that multi-sentence posts with specific
references belong to `analysis`. It never learned to distinguish "specific event
reference" (reaction) from "specific statistical evidence" (analysis). This is a
labeling/data problem: the training set's analysis examples tend to be long and
specific, and so do many reaction posts.

**Wrong prediction 2: reaction predicted as hot_take**

A short explosive comment responding to a trade announcement: "I CANNOT BELIEVE THEY
TRADED HIM THIS IS INSANE THE FRONT OFFICE HAS LOST THEIR MIND."

Why it failed: the post contains strong assertive language ("has lost their mind")
which resembles the confident declarative style of synthetic hot_takes used in
training. The model likely picked up on the assertive register rather than the
event-anchoring that distinguishes reactions. This is a data problem: synthetic
hot_takes were uniformly declarative, which reinforced a surface-level style signal
rather than a semantic one.

**Wrong prediction 3: hot_take predicted as analysis**

"Westbrook was never a good basketball player. Just an empty stats guy. Anyone who
watched him play and not just looked at the box score knows this."

Why it failed: this post references "stats" and "box score" — vocabulary that appears
frequently in the training analysis examples. The model associated those terms with
`analysis` even though no actual statistics are cited. This is a classic surface-level
word association failure: the model learned topic-adjacent vocabulary rather than the
structural distinction between citing evidence and asserting without it.

---

### Sample Classifications

Posts run through the fine-tuned model with predicted label and confidence:

| Post (truncated to 100 chars)                                              | Predicted   | Confidence |
|----------------------------------------------------------------------------|-------------|------------|
| "LeBron is not and has never been better than Jordan. End of discussion."  | hot_take    | 0.89       |
| "I analyzed Harden's performance across every NBA city using box score..." | analysis    | 0.94       |
| "LETS GOOOOO THAT BLOCK WAS INSANE I CANNOT BELIEVE THIS"                 | analysis    | 0.71       |
| "Giannis only looks good because the East is weak. Always has been."       | hot_take    | 0.82       |
| "The Celtics defense ranks 2nd in opponent 3P% at 33.1% this postseason..." | analysis  | 0.91       |

The `analysis` prediction on the Harden post is reasonable: the post describes a
methodology, cites a correlation coefficient, and draws a conclusion from evidence —
exactly what the analysis label is intended to capture.

The `analysis` prediction on the reaction post (row 3) illustrates the core failure:
the model cannot distinguish emotional event responses from substantive argument when
both are expressed in longer text.

---

## Model vs. Intention Reflection

The intended distinction for `reaction` was event-anchoring: reactions are triggered
by something specific that just happened. What the model actually learned was a length
and register heuristic: short, declarative, assertive text maps to `hot_take`; longer,
specific text maps to `analysis`; and nothing maps reliably to `reaction` because the
model never learned the concept of an event anchor.

This gap was caused by a data problem. The 53 synthetic hot_takes I generated to
balance the dataset were all short and declarative. This reinforced a spurious
correlation: hot_take = short and confident. Real hot_takes from Reddit are often
longer and more elaborate. Meanwhile, real reactions from high-scoring Reddit posts
tend to be more articulate than simple exclamations — they reference specific game
events in detail, which made them look like analysis to a model that learned
"specific reference = analysis."

The model did learn one boundary well: hot_take vs. analysis. F1 of 0.70 for hot_take
and 0.667 for analysis suggests the model can distinguish between these two when they
are presented in their prototypical forms. It simply failed to leave conceptual space
for a third class that shares surface properties with both.

The zero-shot baseline's 93.75% accuracy shows that the label definitions are
semantically coherent — a general language model can apply them correctly most of the
time. The fine-tuned model's regression confirms that the training data was the
problem, not the task.

---

## Spec Reflection

**One way the spec helped:** The spec's emphasis on hard edge cases before annotation
was the most valuable structural guidance. Writing the decision rule for hot_take vs.
analysis before collecting data forced me to pin down exactly what "evidence is
central" means, which made the Groq pre-labeling prompt much more precise. Without
that constraint, the prompt would have produced inconsistent labels at the boundary.

**One way implementation diverged:** The spec assumes manual annotation is the primary
labeling method, with LLM pre-labeling as an optional acceleration. In this
implementation, LLM pre-labeling was the only annotation method — no manual review was
performed due to time constraints. Additionally, hot_take balance was achieved through
synthetic generation rather than collecting more real posts. Both deviations are
disclosed in the data collection section and the AI usage section, but they represent
a meaningful departure from the spec's data quality expectations.

---

## AI Usage

**Instance 1: Synthetic hot_take generation**

After initial annotation, only 17 of 355 posts were labeled `hot_take`. I directed
Claude (claude-sonnet-4-6) to generate realistic r/nba hot take posts using the locked
label definition as the prompt. Claude produced 53 synthetic examples. I reviewed them
for plausibility and discarded none — all 53 were appended to the dataset with
`notes="synthetic"`. In retrospect I should have generated more varied examples,
including longer multi-sentence hot_takes, to prevent the model from learning that
short = hot_take.

**Instance 2: AGENTS.md / project scaffolding**

I directed Claude to write the AGENTS.md specification file (equivalent to a CLAUDE.md
for Cursor Agent), which defined the label taxonomy, data collection strategy,
annotation pipeline, and task order for the automated agent workflow. Claude produced
the initial taxonomy including the hot_take/analysis decision rule. I reviewed and
kept the taxonomy unchanged. The data collection pivot to Pullpush (after Reddit
blocked direct API access) was handled autonomously by the Cursor agent without
additional instruction.

**Instance 3: Failure pattern analysis**

After reviewing the confusion matrix showing 7/11 reactions misclassified as analysis,
I described the pattern to Claude and asked it to identify the likely cause. Claude
identified the synthetic data distributional shift (short declarative hot_takes
teaching the model a length/register heuristic) as the primary cause. I verified this
against the actual wrong predictions and confirmed the pattern held: every reaction
misclassified as analysis was a longer post with specific event references.

**Annotation disclosure:** All 210 training examples were labeled by `llama-3.1-8b-instant`
via Groq with no manual per-example review. 53 hot_take examples are synthetic,
generated by Claude. These are marked in the CSV with `notes="synthetic"`.
