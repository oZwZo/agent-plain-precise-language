# Trial results

All numbers here were produced this session by the scripts in `trials/`. Nothing is estimated.

## Trial 1: does the style change how Claude writes?

12 explanation prompts, 2 arms, 3 repeats, 72 calls, **0 failures**, $13.13.
Control arm = your original `CLAUDE.md` with the 5-line cap, no output style.

| metric | control | rule | change |
|---|---|---|---|
| fancy English /1k | 1.68 | **0.00** | −100% |
| informal or invented words /1k | 0.04 | **0.00** | −100% |
| negative contractions /1k | 0.07 | **0.00** | −100% |
| figurative phrasal verbs /1k | 0.12 | 0.02 | −80% |
| inline bold /1k | 8.58 | 3.21 | −63% |
| unanchored That/This /1k | 1.69 | 0.70 | −59% |
| contrastive gapping /1k | 0.31 | 0.15 | −51% |
| sentences over 25 words | 19.37% | 11.31% | −42% |
| figures of speech /1k | 0.34 | 0.23 | −34% |
| longest sentence | 50.19 | 42.31 | −16% |
| mean sentence length | 18.19 | **15.79** | −13% |
| reduced relative /1k | 0.67 | 0.60 | −11% |
| stacked verb /1k | 0.06 | 0.05 | −9% |
| coined compound /1k | 0.60 | 0.59 | −2% |

**No metric got worse.** Total gate passes went from 388/576 to 445/576.

**Three rules barely work**: reduced relative clauses, stacked verb forms, and single-use coined
compounds all moved less than 12%. They are stated in the style but are not changing behaviour.
This is an honest negative result and those three need either stronger wording or removal.

**Sampling.** Run-to-run standard deviation on the rule arm was 1.10 words for mean sentence
length and 0.00 for every vocabulary metric. Three repeats were therefore enough. The plan
guessed at ten, which would have cost three times as much for no extra information.

## Trial 3 and 3b: the term-of-art boundary and the first-language probes

**22 of 22 pass.** $2.87.

Every word you confirmed you are comfortable with survived: `orthogonal`, `canonical`,
`degenerate`, `spurious`. Every word you confirmed is hard was replaced: `comparator`,
`provenance`, `per se`, `agnostic`, `idempotent`, `conflate`.

The two hardest cases came out right:

- `would have been determined entirely by two cluster centroids` became **"Two cluster centroids
  would set the calibration slope"**. It flattened the verb but kept `would`, so the conditional
  survives. Dropping it would have silently strengthened the claim.
- `split-half direction estimate reliability` became **"the reliability of the estimates of
  direction from split halves"**.

Both traps worked. `thin filament` used figuratively became "a narrow, elongated shape".
`blobbier ... 1.45 against 1.05` became "more isotropic than the real data, with a ratio ...".

**Caveat.** Trial 3 gives the rule to the model inside the prompt, so it tests whether the rule
*text* is clear. Trial 1 tests whether the output style fires on its own. They are different
things and 22/22 does not transfer to trial 1.

## Trial 2: fidelity. This one failed.

First run: **12 of 12 items failed**, all three graders unanimous on every item. $8.46.

Before blaming the rule I checked the grader, because a 100% unanimous failure rate is itself
suspicious and the grader prompt tells it to be adversarial.

**Grader calibration control:**
- Identity test, grading a text against itself: **0 of 6** wrongly reported loss. No false-positive bias.
- Planted test, one deliberately corrupted hedge (`may` becoming `does`): **1 of 1** caught.

The planted arm only ran once, because most originals did not contain the hedge words the
corruption function looks for, so the sensitivity evidence is thin. The identity result is solid.

**Verdict: the graders discriminate, so the failure is real.** I then read the failures myself and
confirmed at least three as true positives:

- `No redefinition of what a clone is required.` A dropped verb creating a genuine two-way
  ambiguity where the original ("without redefining what a clone is") had none.
- `No method fits D — DeepRUOT's diffusion net output is discarded` became `..., because
  DeepRUOT discards ...`. The rewrite invented a causal claim.
- `clone-second-moment 0.217` became `a clone-second-moment Spearman of 0.217`, assigning a
  statistic type the original never stated.

### The design fault this exposed

**Rewriting is more dangerous than writing.** When Claude writes its own thoughts, naming the
logical relation behind an em dash is free, because it knows what it meant. When Claude rewrites
someone else's dense prose, the same rule forces it to *infer and commit to* a relation the author
left implicit. That adds information, which is the exact failure this gate exists to catch.

The plan treated generation and rewriting as the same task. They are not.

### The fix

A "rewriting existing text" section was added to the top of the style, overriding the rest in that
mode. Four rules: do not name a relation the original left unstated, do not resolve an ambiguity
by picking one reading, do not add a type or gloss the original did not state, and check the
grammar of any sentence you restructure. If a style rule would break one of these, keep the
original wording.

### A methodology bug caught during the re-run

The first re-run reported 144 candidate originals, up from 65 in the first run. That jump was
this session's own output landing in the logs. Of 159 eligible messages, **114 were written
during this session and only 45 predated it**, so the re-run was largely grading prose written
while the rule was being built. Some of it had already been written under the style, which would
have made the rewrite task trivially easy and the pass rate meaningless.

`fidelity.py` now excludes anything timestamped on or after `2026-07-27T14:00:00`. The clean run
excludes 664 messages and works from 42 genuine pre-intervention candidates.

The **first** run's conclusion is unaffected. Both failures I hand-verified came from real
historical prose about ClonalFlow and DeepRUOT, not from today.

## Trial 6: your blind read

`trials/runs/blind_pairs.md` holds 10 before/after pairs, shuffled, labelled only A and B.
The key is in `blind_pairs_KEY.json`. Do not open it until you have judged all ten.

For each pair, record which version is easier, and whether you think the meaning changed.
The second question matters more.

## Trial 4: gloss decay. Works, except the hand-off reset.

A six-turn conversation where Claude introduces `Wasserstein-2` itself. Read by hand, because the
detector was wrong in both directions:

| turn | what Claude wrote | stage |
|---|---|---|
| 1 | "the smallest average squared distance over all ways of matching every particle..." | full gloss |
| 2 | "(the optimal transport distance from the previous answer)" | short tag |
| 3 to 6 | the bare term | no gloss |

**That is exactly the three-stage decay you specified.** Full gloss, then short tag, then bare term.

**The hand-off reset FAILS.** Turn 6 relayed a subagent's finding and did not return to a full
gloss, which the rule requires.

The first version of this trial was invalid. My questions contained the term, so Claude reasonably
treated it as known and never introduced it. The corrected probe describes the idea and lets
Claude name it.

## Trial 5: the habits that already work survive

Across the six turns: **0 em dashes**, source labels in 4 of 6 turns, numbers with units in 3 of 6.
Nothing regressed.

## The recurring mistake in this session, worth recording

I produced **five** wrong measurements from regular expressions today, and every one of them would
have been reported as fact if I had not checked the underlying text:

1. `nuisance` flagged as fancy English, when all 13 hits were `nuisance parameter`, a real term.
2. A noun-stack detector matching `two-sample t-test is the`.
3. Sentence-initial `It` gated as unanchored, when `It` points at a noun rather than a clause.
4. Gloss detection missing a gloss written as a predicate rather than a parenthetical.
5. Gloss detection then matching `Wasserstein-2 is out of reach at 100,000 particles` as a
   definition. Errors 4 and 5 cancelled out into a "PASS" for entirely the wrong reasons.

The plan's two-layer design was right: regular expressions for mechanical properties, graders for
anything semantic. I kept violating it by trying to regex semantic judgments. **Glossing, noun
stacks, metaphor and pronoun anchoring are all semantic and belong to the grader layer.** The
scorer now says so in comments at each of those points.

## The rewrite-policy bake-off: four methods, none clean

96 agents, 89 completed, 7 failed on a session limit. 4 policies x 6 real pre-session originals x
3 adversarial graders, each grader given a different lens (claims, numbers, hedges and agency).

| policy | passed | rate |
|---|---|---|
| B, vocabulary and punctuation only, restructuring forbidden | 3/6 | **50%** |
| D, full style with every guess marked `[?]` | 3/6 | 50%, grading incomplete |
| A, current style unchanged | 2/6 | 33% |
| C, keep the original verbatim and add a summary above it | 1/6 | **17%** |

D's number is unreliable, because all 7 grader failures fell on D, so some D items had fewer than
two usable graders.

**The decisive result is C finishing last.** C cannot lose information by construction, since the
original sits underneath untouched. It failed because the summary itself reversed a claim: it wrote
"lowering one setting would fix one problem" where the original said "Cutting g0 doesn't fix
concern (ii)".

So the problem was never which rewriting method to use. **Any act of restating dense technical
prose introduces errors.** The style now says so directly, and tells Claude to quote rather than
paraphrase.

### Two real bugs in the rule, both found here and both fixed

1. **The contraction rule corrupted an imperative.** "My read: don't put an invented statistic in
   the paper" became "does not put an invented statistic in the paper". That turns an instruction
   into a description. The rule now says to check whether the contraction is an order or a
   statement, and to write "do not" for an order.
2. **`provenance` to `origin` lost meaning.** In data lineage, provenance names a record of where
   each result came from and how it was produced, which "origin" does not carry. You listed
   `provenance` as hard, and that is still true in loose use, so the rule now splits by sense the
   same way `nuisance parameter` does.

### One thing a grader spotted that I would have missed

Policy B's output opened with a sentence that was not in the original: "This matches exactly the
intended edits, everything else untouched." A grader flagged it as a fabricated claim about the
transformation's own fidelity, and noted it reads like an attempt to get a reviewer to accept the
output without checking. Worth knowing that a rewriting step can insert self-certifying text.

## Trial 7: does it work in Codex?

Yes. Tested on Codex CLI 0.136.0, model `gpt-5.5`, reasoning effort low.

**First, that a global instruction file is read at all.** I built an isolated `CODEX_HOME`
containing one `AGENTS.md` whose only instruction was to begin every reply with the token
`ZQ7-MARKER`, then ran `codex exec` from a working directory that held no `AGENTS.md`. The reply
opened with `ZQ7-MARKER`, so `$CODEX_HOME/AGENTS.md` is what produced it and the working directory
is not a confound.

**Then the trap-word probe.** One call per arm, same prompt, using three words the style is meant
to replace and one it is meant to keep.

| metric | without the rules | with the rules |
|---|---|---|
| gates passed | 13 of 16 | 16 of 16 |
| fancy English per 1,000 words | 55.56 | 0.00 |
| mean sentence length in words | 18.33 | 14.13 |
| longest sentence in words | 32 | 24 |
| sentences over 25 words | 8.33% | 0.00% |

The arm without the rules used `comparator` twice, `agnostic` twice, `nuisance` four times and
`provenance` three times. The arm with the rules wrote "comparison method", "does not assume" and
"origin", kept `nuisance parameter`, and glossed it inline.

One call per arm, so this is a single observation and not a rate.

**Context cost, measured rather than estimated.** Same trivial prompt in both arms, token counts
read from `codex exec --json`: 28,097 input tokens without the rules and 32,960 with them. So the
file costs about 4,900 input tokens per session. One measurement per arm.

**One difference from Claude Code, recorded because it is not an improvement.** The Codex reply
carried 15 source labels across 15 sentences, almost all `[inferred]`. That is heavier labelling
than the same rules produce in Claude Code. My reading is that the integrity rules sit at the same
level as everything else in the single Codex file, whereas in Claude Code they sit in `CLAUDE.md`,
one level below the output style. [inferred, from one observation, not tested]

### A scorer bug this trial exposed

The sentence splitter needs a capital letter or a digit after the full stop. A trailing
`[inferred]` starts with a bracket, so the splitter could not see the boundary and merged whole
paragraphs into one sentence. On the same Codex reply it reported a mean sentence length of 56.75
words with the labels left in and 14.13 words with them removed. The fix strips
`[verified]`, `[training]` and `[inferred]` before splitting. This is the sixth measurement error
in this project that came from my own scorer rather than from the model.

After the fix the baseline still reproduces: mean sentence length 16.17 words, against 16.2 in the
original measurement.

## The reader preferred the control arm on one passage, and was right

This is the first judgment from the reader the style was built for, and it went against the style.
Shown two versions of the same answer, they said the one written without the rule read better.

Without the rule, 19 words:

> **Headline: divide any nominal-N sample size by 0.3. You need about 3.33 times as many particles
> as the naive calculation says.**

With the rule, 37 words, under a heading reading "The answer":

> Multiply every particle count that came out of the calculation by about 3.3. A nominal count of
> 10,000 particles carries the precision of 3,000 independent particles, so you need about 33,000
> nominal particles to reach the precision that the calculation asked for.

| metric | without the rule | with the rule | the style's target |
|---|---|---|---|
| words | 19 | 37 | none |
| mean sentence length | 10.5 | 21.0 | about 15 |
| longest sentence | 13 | 29 | under 25 |
| sentences over 25 words | 0% | 50% | at most 5% |

**The rule arm fails the rule's own sentence-length gate on this passage.** Trial 1 measured mean
sentence length across whole answers and found 15.79 words, which passes. So this is a local
failure that an average over a whole answer hides.

**The mechanism is two rules pulling against each other.** "Length follows from clarity, so do not
compress" and "keep almost every sentence under 25 words" both apply, and the first one won. The
style states no priority between them. It states a priority only between precision and
readability.

**One correction to my own first reading of this.** I initially wrote that the ban on inline bold
had removed the only visual mark showing where the answer was. That was wrong, and it came from an
excerpt I built badly. The rule arm did mark the answer, with a heading reading "The answer", which
the style permits.

### The reader's decision, and what changed because of it

I proposed making the 25-word target win over "do not compress". The reader rejected that:

> I don't think the 25 word target is the compulsory. If the longer sentence is easier to
> understand, I don't mind.

**My first attempt at this change overshot, and the reader corrected it again:**

> I prefer short sentences overall. What i don't agree is the 25 word target. So no need to force
> every sentence to be restricted in 25 word. If sometimes you need more than 25 words to make the
> sentence clear in the first glance, that is allowed.

So the preference for short sentences never changed. Only the cap on each individual sentence did.
I had rewritten the rule as "sentence length is a check, not a limit", which reads as neutral about
length, and I had also advised dropping "prefer short sentences" from an older instruction file.
Both were wrong. The rule now states the preference first and the exception second.

The fault in that passage is
repetition, not length. It says "calculation" three times in 37 words and states the precision
twice. Cutting only the repetition gives a version that says the same thing in 26 words, on the
same count that gives 37 for the original and 19 for the version without the rule. Splitting the
long sentence into short ones would not have helped.

Three things changed as a result.

1. **The style.** The Sentences section now opens with "Prefer short sentences. Treat 25 words as
   a guide rather than as a cap." The exception is stated next: a sentence that needs more than 25
   words to be clear at first glance should be written long. It also says to cut repetition before
   touching length. The 40-word figure stays, because that is where the comprehension evidence is
   strongest.
2. **The pre-send checklist.** Item 1 was "Split every one over 25 words". It now says to cut a
   repeated noun phrase first, then to split only when the sentence is not clear at first glance,
   and it closes by repeating that sentences should still be short on average. The list of the
   three most common failures now opens with repetition inside a sentence rather than with long
   sentences.
3. **The scorer.** `pct_over_25w` moved from `GATES` to a new `ADVISORY` list, printed under a
   heading reading "advisory, not counted", because that metric measures the rejected per-sentence
   cap. Both `mean_sentence_len` bounds stay hard gates, because the preference for short
   sentences did not change. `longest_sentence <= 40` stays a hard gate. The gate count therefore
   falls from 16 to 15, so pass counts recorded above this line are not directly comparable with
   ones recorded below it. No underlying measurement changed.

On the disputed passage the corrected instrument gives the right verdict. It fails on mean
sentence length, at 21.0 words against a gate of 16.0, and its 50 percent of sentences over 25
words is reported as advisory rather than as a failure.

This is the first time the reader has overruled a rule, and it went against the rule I would have
defended. Recording it here because the alternative is a style that scores well against its own
instrument and reads worse to the person it was built for.

## Not done

- 30 of the 42 eligible pre-session answers were not used in the fidelity trial. That is a cost
  cap, not full coverage.
- The hand-off reset needs a fix and a re-test.
- Your blind read of the ten pairs, which is the final gate and only you can do it.
