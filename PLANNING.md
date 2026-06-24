# TakeMeter — Planning Document

## Community

I chose r/nba on Reddit. The subreddit is one of the highest-traffic sports communities
on the platform, producing hundreds of posts and thousands of comments daily across an
enormous range of discourse quality. A post thread on any given game might contain a
stat-backed argument about a player's playoff efficiency sitting two comments above a
one-sentence hot take about someone being overrated, with an all-caps reaction to a
specific play somewhere in between.

This range is what makes r/nba a good fit for a classification task. The distinctions
between post types are not subtle — they reflect meaningfully different kinds of
contributions that regular community members actively recognize and respond to
differently. Analysis posts tend to get more deliberate engagement; hot takes generate
argument; reactions spike and fade with the news cycle. The community itself has an
informal vocabulary around this ("actual analysis vs. ESPN take," "this is cope," etc.)
which confirms the distinctions are grounded in community norms, not imposed from
outside.

---

## Label Taxonomy

### analysis

A post that makes a structured argument supported by specific statistics, historical
comparisons, or tactical observations. The evidence is central to the claim — it would
support the argument even if all opinion framing were removed.

**Example 1:**
"I analyzed James Harden's performance in every NBA city and correlated it with those
cities' strip club ratings. Correlation coefficient of .4575 between avg strip club
rating and total sub-par games — moderate to strong. His worst performance comes in
Miami, which has the best strip clubs. His best in Toronto, which has the worst."

**Example 2:**
"The Celtics held opponents to 33.1% from three this postseason, 2nd in the league.
Their defensive scheme forces opponents into mid-range and long twos, which is why
they keep closing out games in the fourth — it's not luck, it's structural."

---

### hot_take

A bold, confident opinion stated without meaningful supporting evidence. The post
asserts rather than argues. Framing is strong (superlatives, absolutes, provocative
comparisons) but reasoning is thin or absent.

**Example 1:**
"LeBron is not and has never been better than Jordan. End of discussion."

**Example 2:**
"The Warriors dynasty is the most fraudulent championship run ever. KD ruined
basketball for an entire generation and the league let it happen."

---

### reaction

An immediate emotional response to a specific recent event, play, or game outcome.
Little to no argument — the post is expressing excitement, frustration, or disbelief
in the moment. The post is typically triggered by something that just happened and
would lose most of its meaning without that context.

**Example 1:**
"LETS GOOOOO THAT BLOCK WAS INSANE I CANNOT BELIEVE WHAT I JUST WATCHED"

**Example 2:**
"I cannot believe they just blew a 20-point lead in the 4th. This team will never
change. I'm done watching."

---

## Hard Edge Cases

### hot_take vs. analysis (primary edge case)

The hardest boundary is a post that makes a bold claim AND cites a specific statistic.

**Example from the dataset:**
"LeBron is overrated — his playoff win rate against top-seeded opponents is below .500."

This post frames a provocative claim and cites a specific stat. The question is whether
the stat is genuinely reasoning or rhetorical decoration.

**Decision rule:** If the post provides specific, verifiable evidence that would support
the claim even if you removed the opinion framing entirely, label it `analysis`. If the
stat is selected for rhetorical effect — cherry-picked, vague, or the argument would
collapse if challenged — label it `hot_take`. The win-rate example above is `hot_take`:
the framing is accusatory, the stat is cherry-picked for effect, and the post makes no
attempt to contextualize it.

### reaction vs. hot_take

Reactions are tied to a specific recent event. Hot takes are free-floating opinions
with no event anchor.

**Decision rule:** If you cannot identify what specific event or moment triggered the
post, it is not a reaction — classify it as `hot_take`.

---

## Data Collection Plan

**Source:** r/nba via the Pullpush public archive API (api.pullpush.io), which mirrors
Reddit's public post data without requiring authentication. Reddit's direct JSON API
blocked requests from development IPs, so the archive was used as a fallback.

**Collection strategy:**
- Submissions: top-scored posts across multiple time windows (month, year) and sort
  types (top, controversial) to capture diverse discourse
- Comments: top-scored comments from high-engagement threads to capture reactions and
  hot takes that appear in comment form

**Targets:** 70 examples per label (210 total).

**Handling imbalance:** After initial annotation, hot_take was severely underrepresented
(17 examples vs. 70 each for analysis and reaction). Top-scored Reddit posts skew
heavily toward long analytical content, and game thread comments dominate the reaction
count. Opinion-only posts are rarer in the high-score tier.

To reach 70 hot_takes, 53 synthetic examples were generated using Claude
(claude-sonnet-4-6) prompted to produce realistic r/nba hot take comments. These
synthetic examples are marked `notes="synthetic"` in the CSV and disclosed in the
AI usage section of the README.

---

## Evaluation Metrics

I will use the following metrics, reported per class and overall:

**Accuracy** (overall fraction correct) is reported for direct comparison with the
baseline, but it is not sufficient on its own. With three balanced classes, a model
that always predicts `analysis` achieves 33% accuracy. Accuracy does not reveal
which classes the model is failing on.

**Per-class F1** (harmonic mean of precision and recall) is the primary metric for
each class. It catches the case where the model performs well on one class but fails
completely on another — something accuracy masks with a balanced dataset.

**Precision and recall separately** matter for understanding failure mode direction.
High recall / low precision means the model over-predicts a class. Low recall / high
precision means it under-predicts. For `reaction`, I expect low recall risk: short
emotional posts might get absorbed into `hot_take` if the model fixates on sentiment
rather than event-anchoring.

**Confusion matrix** to identify which specific label pairs are being confused and in
which direction.

---

## Definition of Success

A classifier would be genuinely useful for moderation or community tooling if:

- Overall accuracy >= 0.70 on the held-out test set
- Per-class F1 >= 0.60 for all three labels (no class completely unlearned)
- Fine-tuned model beats zero-shot baseline by at least 8 percentage points
- No label pair dominates the confusion matrix (no single off-diagonal cell > 30%
  of that class's total examples)

These thresholds are set conservatively for a 210-example dataset. A model meeting
them could plausibly flag discourse quality in a real community tool, even if it
would need more data before deployment.

---

## AI Tool Plan

### Label stress-testing

Before committing to the taxonomy, I used Claude to generate 10 boundary-case posts
sitting between `hot_take` and `analysis`. Three of the generated examples could not
be cleanly classified under my original definitions, which revealed a gap: the original
definition of `analysis` did not specify that evidence must be "central" to the
argument. Adding the phrase "would support the claim even if opinion framing were
removed" resolved the ambiguity.

### Annotation assistance

Groq's `llama-3.1-8b-instant` was used to pre-label all 355 collected posts using the
locked label definitions. The Groq free tier hit a 100k daily token limit at item 352,
leaving 3 examples unannotated (logged to annotation_errors.txt). The annotated batch
was capped at 70 per label for analysis and reaction; all identified hot_takes were
kept (17 total from the real corpus).

To reach the required 70 hot_takes, 53 additional synthetic examples were generated by
Claude and disclosed with `notes="synthetic"` in the dataset. No synthetic examples
were generated for analysis or reaction.

All pre-labeled examples were accepted without manual review due to time constraints.
This is disclosed as a limitation in the README.

### Failure analysis

After collecting wrong predictions from Section 4, I will identify systematic patterns
in the error set by examining the confusion matrix and wrong prediction output.
The primary hypothesis going in is that the model will over-predict `analysis` for
long posts regardless of content, given that analysis examples tend to be longer
and the model may have learned length as a proxy signal.
