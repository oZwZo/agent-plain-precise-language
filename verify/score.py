#!/usr/bin/env python3
"""Layer 1 plain-language scorer. Deterministic, pure stdlib, no dependencies.

Measures only what a regex can measure reliably. Everything subjective (novel metaphor,
grammatical subject, noun-stack nesting, fidelity) is left to the LLM graders in layer 2,
because a bad regex produces a confidently wrong number.

Usage:
  score.py --baseline                 rebuild the baseline from the user's Claude Code logs
  score.py --text FILE [FILE ...]     score one or more plain text / markdown files
  score.py --stdin                    score text on stdin
  score.py --json                     emit JSON instead of a table
"""

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wordlists import (  # noqa: E402
    FANCY_ENGLISH, PHRASAL, INFORMAL, TERMS_OF_ART, PROTECTED_PHRASES,
)

LOGS = "/home/wz369/.claude/projects"
FREQ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freq10k.txt")

# CEFR B2 receptive vocabulary is roughly 4,000 to 5,000 word families, so the top 5,000
# most common English words is the practical band. The user reports B2 for general English.
# Their domain English is far stronger than B2, which is why they are comfortable with
# "orthogonal" and "canonical" but not with "conflate" or "provenance". The check below
# reflects that split: a rare word is only a problem when it is ORDINARY English.
B2_BAND = 5000

try:
    with open(FREQ) as _fh:
        _FREQ_WORDS = [w.strip().lower() for w in _fh if w.strip()]
    B2_COMMON = set(_FREQ_WORDS[:B2_BAND])
except OSError:
    B2_COMMON = set()

# ---------------------------------------------------------------- text preparation

FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`]*`")
MATH = re.compile(r"\$[^$]*\$")


def strip_code(text):
    """Remove fenced blocks, inline code and math. These are not prose."""
    text = FENCE.sub(" ", text)
    text = INLINE_CODE.sub(" CODE ", text)
    text = MATH.sub(" MATH ", text)
    return text


def prose_lines(text):
    """Yield only real prose lines. Skips headings, table rows, and block quotes.

    This matters. Counting a markdown table row as a sentence is what inflated the
    first-pass numbers to a 137-word 'sentence' that was never prose.
    """
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith(("#", "|", ">", "```")):
            continue
        if re.fullmatch(r"[-*_\s]{3,}", s):  # horizontal rules
            continue
        s = re.sub(r"^[-*+]\s+", "", s)          # bullet markers
        s = re.sub(r"^\d+[.)]\s+", "", s)        # numbered list markers
        if s:
            yield s


SOURCE_LABEL = re.compile(r"\s*\[(?:verified|training|inferred)\]")


def sentences(text):
    out = []
    for line in prose_lines(text):
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        # Remove the [verified] / [training] / [inferred] labels before
        # splitting. They sit after the full stop, and the splitter needs a
        # capital letter or a digit after the stop, so a label left in place
        # hides the sentence boundary. Measured effect on one real Codex reply:
        # mean sentence length read 56.75 words with the labels left in and
        # 14.13 words with them removed, on the same text.
        line = SOURCE_LABEL.sub("", line)
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line):
            if len(s.split()) >= 4:
                out.append(s.strip())
    return out


def words(text):
    return re.findall(r"[A-Za-z][A-Za-z'-]+", text)


# ---------------------------------------------------------------- detectors

NUMBERISH = re.compile(r"^[^A-Za-z]*[\d.,%×+\-/=]+\s*[A-Za-z%°]{0,12}[^A-Za-z]*$")


def bold_breakdown(text):
    """Split bold spans into heading / number / inline-emphasis. Only the last is a violation."""
    heading = number = inline = 0
    for line in text.split("\n"):
        s = line.strip()
        is_heading = s.startswith("#") or re.fullmatch(r"\*\*[^*]+\*\*:?", s) is not None
        for span in re.findall(r"\*\*([^*]+)\*\*", line):
            if is_heading:
                heading += 1
            elif NUMBERISH.match(span):
                number += 1
            else:
                inline += 1
    return heading, number, inline


def phrase_pattern(phrase):
    return r"\b" + re.escape(phrase).replace(r"\ ", r"\s+") + r"\b"


def mask_protected(text):
    """Blank out multi-word terms of art so their component words are not flagged.

    Without this, every "nuisance parameter" counts as a "nuisance" violation, which
    was a 100% false-positive rate on the first trial run.
    """
    for phrase in PROTECTED_PHRASES:
        text = re.sub(phrase_pattern(phrase), " PROTECTEDTERM ", text, flags=re.I)
    return text


def find_fancy(text):
    text = mask_protected(text)
    hits = {}
    for w in FANCY_ENGLISH:
        if w in TERMS_OF_ART:
            continue  # allow-list always wins
        n = len(re.findall(phrase_pattern(w), text, re.I))
        if n:
            hits[w] = n
    return hits


def find_phrasal(text):
    hits = {}
    for p in PHRASAL:
        n = len(re.findall(phrase_pattern(p), text, re.I))
        if n:
            hits[p] = n
    return hits


_INFLECT = ("s", "es", "ed", "d", "ing", "ly", "er", "est")


def _known_common(w):
    """True if w, or a plausible stem of w, is in the B2 common band."""
    if w in B2_COMMON:
        return True
    for suf in _INFLECT:
        if w.endswith(suf) and len(w) > len(suf) + 2:
            stem = w[: -len(suf)]
            if stem in B2_COMMON or (stem + "e") in B2_COMMON:
                return True
    return False


def find_above_b2(text):
    """Words outside the B2 common band that are ORDINARY English, not domain vocabulary.

    A rare word is only a problem when a B2 reader has no way to reach it. Domain terms are
    excluded because this reader's field English is well above B2: they confirmed they are
    comfortable with orthogonal, canonical, degenerate and spurious.

    Exclusions, in order:
      - allow-listed terms of art and protected multi-word phrases
      - anything with a capital, a digit, or a hyphen (proper nouns, acronyms, identifiers)
      - very short words
    What remains is lowercase ordinary English above the B2 band, which is the target.
    """
    if not B2_COMMON:
        return {}
    masked = mask_protected(text)
    hits = {}
    for m in re.finditer(r"\b[A-Za-z][A-Za-z'-]{3,}\b", masked):
        raw = m.group(0)
        if raw != raw.lower():        # any capital -> proper noun or acronym
            continue
        if "-" in raw or "'" in raw:  # compounds and contractions handled by other rules
            continue
        w = raw.lower()
        if w in TERMS_OF_ART or _known_common(w):
            continue
        hits[w] = hits.get(w, 0) + 1
    return hits


def find_informal(text):
    hits = {}
    for w in INFORMAL:
        if w in TERMS_OF_ART:
            continue
        n = len(re.findall(r"\b" + re.escape(w) + r"\b", text, re.I))
        if n:
            hits[w] = n
    return hits


_PRON_VERB = (r"(is|are|was|were|means?|kills?|makes?|gives?|shows?|leaves?|confirms?|"
              r"rules?|puts?|breaks?|has|have|had|would|will|does|do|did|changes?)\b")

# Gate. That / This / Those / These at the start of a sentence typically point at a whole
# preceding clause, which is the construction the rule bans.
UNANCHORED = re.compile(r"(?:^|(?<=[.!?])\s)(That|This|Those|These)\s+" + _PRON_VERB)

# Diagnostic only, NOT a gate. Sentence-initial "It" usually points at a noun rather than a
# clause, so flagging it produced a false positive on the first trial run: "A nuisance parameter
# is a quantity ... It changes how likely the observed data are" has exactly one candidate
# antecedent and is not ambiguous. Distinguishing noun-reference from clause-reference needs a
# grader, so this number is a hint for a human and is not scored.
SENTENCE_INITIAL_IT = re.compile(r"(?:^|(?<=[.!?])\s)It\s+" + _PRON_VERB)

REDUCED_RELATIVE = re.compile(
    r"\b(the|a|an|this|that|these|those)\s+"
    r"([a-z]+(?:\s+[a-z]+)?)\s+"
    r"(I|we|you|they|he|she|it|R\d[\w.]*|[A-Z][\w.]*)\s+"
    r"(could|can|did|do|does|have|has|had|gave|give|made|make|found|find|used|use|"
    r"wrote|write|ran|run|built|build|set|sent|saw|see)\b"
)

STACKED_VERB = re.compile(
    r"\b(would|could|should|might|may|must|will|shall)\s+(?:not\s+)?have\s+been\s+\w+", re.I
)

NEG_CONTRACTION = re.compile(
    r"\b\w*n't\b|\bcan't\b|\bwon't\b|\bshan't\b", re.I
)

GAPPING = re.compile(r",\s*not\s+[a-z]\w*\s*[.;,]")

COINED_COMPOUND = re.compile(r"\b[a-z]+(?:-[a-z]+){2,}\b")

# Noun stacks need a part-of-speech tagger to detect honestly. The first attempt here
# matched "two-sample t-test is the" and "within-group variance is unknown", because it
# accepted any four words after a hyphen rather than four nouns. Both were false
# positives. Rather than ship a number that cannot be trusted, this is reported as
# diagnostic only and is NOT a gate. Noun stacks are judged by the layer 2 graders.
#
# The stop-word filter below removes the worst of the false positives but does not make
# the measure reliable, so treat the output as a hint for a human, not as a score.
_STOP = r"(?:is|are|was|were|be|been|the|a|an|and|or|but|of|in|on|to|for|with|that|this|it|not)"
NOUN_STACK_HYPHEN = re.compile(
    r"\b[a-z]+-[a-z]+\s+(?!%s\b)[a-z]+\s+(?!%s\b)[a-z]+\b" % (_STOP, _STOP)
)

FIGURATIVE = re.compile(
    r"\b(kills?|killed|in disguise|money (?:panel|shot)|the kicker|"
    r"smoking gun|dead in the water|buys? (?:you|us)|not free|"
    r"reshapes?|survives?|blow(?:s)? up|falls? apart)\b", re.I
)


# ---------------------------------------------------------------- scoring

def score(text, label="text"):
    text = strip_code(text)
    w = words(text)
    n = len(w) or 1
    per1k = lambda c: round(1000.0 * c / n, 2)  # noqa: E731

    sents = sentences(text)
    lens = sorted(len(s.split()) for s in sents)
    ns = len(lens) or 1

    heading, number, inline = bold_breakdown(text)
    fancy = find_fancy(text)
    phrasal = find_phrasal(text)
    informal = find_informal(text)
    above_b2 = find_above_b2(text)

    em = text.count("—")
    unanchored = len(UNANCHORED.findall(text))
    initial_it = len(SENTENCE_INITIAL_IT.findall(text))
    reduced = len(REDUCED_RELATIVE.findall(text))
    stacked = len(STACKED_VERB.findall(text))
    negcon = len(NEG_CONTRACTION.findall(text))
    gapping = len(GAPPING.findall(text))
    coined = len(COINED_COMPOUND.findall(text))
    stack3 = len(NOUN_STACK_HYPHEN.findall(text))
    figs = len(FIGURATIVE.findall(text))

    return {
        "label": label,
        "words": n,
        "sentences": len(sents),
        "mean_sentence_len": round(sum(lens) / ns, 2) if lens else 0,
        "median_sentence_len": lens[ns // 2] if lens else 0,
        "pct_over_25w": round(100.0 * sum(1 for x in lens if x > 25) / ns, 2),
        "pct_over_40w": round(100.0 * sum(1 for x in lens if x > 40) / ns, 2),
        "longest_sentence": lens[-1] if lens else 0,
        "em_dash_per1k": per1k(em),
        "inline_bold_per1k": per1k(inline),
        "bold_heading": heading,
        "bold_number": number,
        "fancy_english_per1k": per1k(sum(fancy.values())),
        "fancy_english_hits": fancy,
        "phrasal_per1k": per1k(sum(phrasal.values())),
        "phrasal_hits": phrasal,
        "informal_per1k": per1k(sum(informal.values())),
        "informal_hits": informal,
        "above_b2_per1k": per1k(sum(above_b2.values())),
        "above_b2_types": len(above_b2),
        "above_b2_hits": above_b2,
        "figurative_per1k": per1k(figs),
        "unanchored_pronoun_per1k": per1k(unanchored),
        "sentence_initial_it_per1k": per1k(initial_it),  # diagnostic only, not a gate
        "reduced_relative_per1k": per1k(reduced),
        "stacked_verb_per1k": per1k(stacked),
        "neg_contraction_per1k": per1k(negcon),
        "gapping_per1k": per1k(gapping),
        "coined_compound_per1k": per1k(coined),
        "noun_stack_per1k": per1k(stack3),
    }


GATES = [
    # key, comparison, threshold, human label
    ("em_dash_per1k", "<=", 0.0, "em dashes"),
    ("inline_bold_per1k", "<=", 0.0, "inline bold for emphasis"),
    ("fancy_english_per1k", "<=", 0.0, "fancy English words"),
    ("phrasal_per1k", "<=", 0.0, "figurative phrasal verbs"),
    ("informal_per1k", "<=", 0.0, "invented / informal words"),
    ("figurative_per1k", "<=", 0.0, "figures of speech"),
    ("unanchored_pronoun_per1k", "<=", 0.0, "unanchored sentence-initial pronoun"),
    ("reduced_relative_per1k", "<=", 0.0, "relative clause with pronoun dropped"),
    ("stacked_verb_per1k", "<=", 0.0, "stacked verb form"),
    ("neg_contraction_per1k", "<=", 0.0, "negative contraction"),
    ("gapping_per1k", "<=", 0.0, "contrastive gapping"),
    ("coined_compound_per1k", "<=", 2.0, "single-use coined compound"),
    # noun_stack_per1k is deliberately NOT a gate. See the comment on NOUN_STACK_HYPHEN.
    ("longest_sentence", "<=", 40, "longest sentence (words)"),
    # The mean stays a hard gate, because the reader still prefers short
    # sentences overall. What they rejected was the per-sentence cap, not the
    # preference. The lower bound stops a run from passing by chopping
    # everything into fragments.
    ("mean_sentence_len", "<=", 16.0, "mean sentence length"),
    ("mean_sentence_len", ">=", 8.0, "mean sentence length (lower bound)"),
]

# Advisory. Measured and printed, but it does not decide pass or fail.
#
# The reader rejected the 25-word figure as a cap on individual sentences: a
# sentence may run past 25 words when the longer sentence is clear at first
# glance. They did not reject short sentences, so the mean above stays a gate
# and only this per-sentence count moves here.
#
# Results recorded before this change counted 16 gates. They now count 15, so
# the two sets of pass counts are not directly comparable. Every underlying
# number is unchanged.
ADVISORY = [
    ("pct_over_25w", "<=", 5.0, "sentences over 25 words (%)"),
]


def check_gates(s):
    out = []
    for rules, advisory in ((GATES, False), (ADVISORY, True)):
        for key, op, thr, label in rules:
            v = s.get(key, 0)
            ok = (v <= thr) if op == "<=" else (v >= thr)
            out.append({"metric": label, "value": v, "op": op, "threshold": thr,
                        "pass": ok, "advisory": advisory})
    return out


# ---------------------------------------------------------------- log corpus

def load_corpus(model=None):
    texts = []
    for fp in glob.glob(os.path.join(LOGS, "**", "*.jsonl"), recursive=True):
        try:
            fh = open(fp, errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("type") != "assistant" or d.get("isSidechain"):
                    continue
                m = d.get("message") or {}
                if model and m.get("model") != model:
                    continue
                for blk in (m.get("content") or []):
                    if isinstance(blk, dict) and blk.get("type") == "text":
                        t = blk.get("text") or ""
                        if t.strip():
                            texts.append(t)
    return "\n".join(texts)


def print_table(s, gates=None):
    print("\n=== %s ===" % s["label"])
    print("  words %d, prose sentences %d" % (s["words"], s["sentences"]))
    rows = [
        ("mean sentence length", s["mean_sentence_len"]),
        ("median sentence length", s["median_sentence_len"]),
        ("sentences over 25 words (%)", s["pct_over_25w"]),
        ("sentences over 40 words (%)", s["pct_over_40w"]),
        ("longest sentence (words)", s["longest_sentence"]),
        ("em dashes /1k", s["em_dash_per1k"]),
        ("inline bold /1k", s["inline_bold_per1k"]),
        ("fancy English /1k", s["fancy_english_per1k"]),
        ("phrasal verbs /1k", s["phrasal_per1k"]),
        ("informal words /1k", s["informal_per1k"]),
        ("figures of speech /1k", s["figurative_per1k"]),
        ("unanchored pronoun /1k", s["unanchored_pronoun_per1k"]),
        ("reduced relative /1k", s["reduced_relative_per1k"]),
        ("stacked verb /1k", s["stacked_verb_per1k"]),
        ("neg contraction /1k", s["neg_contraction_per1k"]),
        ("gapping /1k", s["gapping_per1k"]),
        ("coined compound /1k", s["coined_compound_per1k"]),
        ("noun stack /1k", s["noun_stack_per1k"]),
    ]
    for k, v in rows:
        print("    %-32s %8s" % (k, v))
    if s["fancy_english_hits"]:
        print("    fancy English hits: %s" % dict(sorted(
            s["fancy_english_hits"].items(), key=lambda x: -x[1])[:12]))
    if s["phrasal_hits"]:
        print("    phrasal hits:       %s" % s["phrasal_hits"])
    if s["informal_hits"]:
        print("    informal hits:      %s" % s["informal_hits"])
    if gates:
        hard = [g for g in gates if not g.get("advisory")]
        soft = [g for g in gates if g.get("advisory")]
        failed = [g for g in hard if not g["pass"]]
        print("\n  GATES: %d/%d pass" % (len(hard) - len(failed), len(hard)))
        for g in failed:
            print("    FAIL  %-42s %s (need %s %s)"
                  % (g["metric"], g["value"], g["op"], g["threshold"]))
        missed = [g for g in soft if not g["pass"]]
        if missed:
            print("  advisory, not counted:")
            for g in missed:
                print("    over  %-42s %s (guide %s %s)"
                      % (g["metric"], g["value"], g["op"], g["threshold"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--text", nargs="*")
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gates", action="store_true", help="also evaluate pass/fail gates")
    a = ap.parse_args()

    results = []
    if a.baseline:
        for model in ("claude-opus-5", "claude-opus-4-8"):
            results.append(score(load_corpus(model), "baseline " + model))
    if a.text:
        for fp in a.text:
            with open(fp, errors="replace") as fh:
                results.append(score(fh.read(), os.path.basename(fp)))
    if a.stdin:
        results.append(score(sys.stdin.read(), "stdin"))
    if not results:
        ap.error("give --baseline, --text or --stdin")

    if a.json:
        payload = []
        for s in results:
            item = dict(s)
            if a.gates:
                item["gates"] = check_gates(s)
            payload.append(item)
        print(json.dumps(payload, indent=2))
    else:
        for s in results:
            print_table(s, check_gates(s) if a.gates else None)


if __name__ == "__main__":
    main()
