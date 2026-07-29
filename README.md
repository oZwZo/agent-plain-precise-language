# plain-precise

An always-on writing rule for Claude Code. It makes Claude write plain English
for a non-native English speaker whose general English is around CEFR B2, while
keeping every technical term exact.

The governing rule inside it is one sentence: **never trade precision for
readability.** If plain phrasing would make a claim vaguer, the style keeps the
precise phrasing and spends an extra sentence explaining it.

## Install

Four steps. Do all four, because the first two on their own leave the rule
half-installed.

**Step 1. Register the catalogue.**

```bash
claude plugin marketplace add oZwZo/agent-plain-precise-language
```

This prints `Successfully added marketplace`, and that message is easy to
misread. It installs nothing. It only tells Claude Code where to look.

**Step 2. Install the plugin.**

```bash
claude plugin install plain-precise@wz369-writing
```

Then run `/clear` or start a new session, because the style is part of the
system prompt and Claude Code reads that once at session start. You do not edit
`settings.json`, because the style sets `force-for-plugin: true`, which applies
it automatically whenever the plugin is enabled.

**Step 3. Add the research-integrity rules by hand.**

A plugin cannot ship a `CLAUDE.md`, so this part does not travel with the
plugin. Copy the fenced block from [`claude-md-snippet.md`](claude-md-snippet.md)
into `~/.claude/CLAUDE.md`. After the install, that file sits at
`~/.claude/plugins/marketplaces/wz369-writing/claude-md-snippet.md`.

While you are in `CLAUDE.md`, delete any line that caps output length, such as
"be concise" or "keep summaries under 5 lines". Compression is what produces the
stacked nouns and the dropped subjects that the style exists to remove, so a
length cap fights the style directly.

**Step 4. Confirm the style is actually firing.** See
[Check that it is actually running](#check-that-it-is-actually-running).

For claude.ai and Claude Science, see [Other surfaces](#other-surfaces) below.
Plugins are a Claude Code feature and do not reach those.

## Why this is an output style and not a skill

This was the design question, and the answer is decided by mechanism rather than
by taste. Three ways exist to give Claude a standing instruction, and they are
not interchangeable.

| mechanism | how it works | when it fires |
|---|---|---|
| output style | modifies the system prompt, and Claude Code re-issues reminders during the conversation | every turn, automatically |
| `CLAUDE.md` | added as a user message after the system prompt | every turn, but at a weaker level |
| skill | loads task-specific instructions when it is invoked | only when called |

Source: <https://code.claude.com/docs/en/output-styles>, the "Comparisons to
related features" table.

**A skill is the wrong shape.** A skill loads when it is invoked. A writing rule
has to apply to every reply, including the reply where you forget to invoke
anything. If the rule only fires when you remember to ask for it, it does not
solve the problem, because the problem is the default.

**`CLAUDE.md` is the wrong level, for two reasons.** First, it is delivered as a
user message rather than as part of the system prompt, so a system-prompt
instruction beats it when the two disagree. Second, `CLAUDE.md` is inherited by
subagents and an output style is not. Subagent prose is intermediate machine
output, not something you read, so applying the writing rule there spends tokens
for no benefit.

**So the writing rules go in the output style, and the integrity rules stay in
`CLAUDE.md`.** The integrity rules are about honesty, and honesty should reach
subagents, so `CLAUDE.md` is the right home for those. See
[`claude-md-snippet.md`](claude-md-snippet.md).

The remaining question was distribution, and a plugin answers it. A plugin can
ship an output style in an `output-styles/` directory, and a marketplace turns
the plugin into something installable with two commands on any machine.

## What is in this repository

```
agent-plain-precise-language/
├── .claude-plugin/
│   └── marketplace.json          the catalogue, so /plugin can find the plugin
├── plugins/
│   └── plain-precise/
│       ├── .claude-plugin/
│       │   └── plugin.json       the plugin manifest
│       └── output-styles/
│           └── plain-precise.md  THE RULE. This is the only file that matters.
├── claude-ai/
│   └── preferences.md            paste-in text for claude.ai and Claude Science
├── claude-md-snippet.md          the integrity rules, copied by hand
├── install.sh                    fallback for machines with no access to the git host
├── uninstall.sh
└── verify/                       the scorer and the measured results
    ├── score.py
    ├── wordlists.py
    └── RESULTS.md
```

Everything except `plain-precise.md` is packaging. If you only want the rule,
copy that one file into `~/.claude/output-styles/` and set
`"outputStyle": "plain-precise"` in `~/.claude/settings.json`.

## Publish a change so other machines pick it up

The marketplace is this git repository. To release a change, edit the files,
bump `version` in `plugins/plain-precise/.claude-plugin/plugin.json`, then
commit and push.

```bash
git add -A
git commit -m "what changed"
git push
```

Users only receive an update when the `version` field changes, so bump it on
every release. On their side, `claude plugin marketplace update` refreshes the
local copy.

Private repositories work. Claude Code uses your existing git credential helpers
for plugin installs, so `gh auth login` or an SSH key already in `ssh-agent` is
enough. Background auto-updates are the one weak point, because the background
refresh disables credential helpers for its `git pull`. Set
`CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` if you use a private
repository, so a failed background pull keeps the existing clone instead of
re-cloning.

Then on any new machine:

```bash
claude plugin marketplace add oZwZo/agent-plain-precise-language
claude plugin install plain-precise@wz369-writing
```

## Install without the plugin system

Use this on a machine that cannot reach the git host, for example an offline
cluster node.

```bash
./install.sh          # copies the style file
./install.sh --link   # symlinks it instead, so a git pull updates it in place
```

The script backs up `settings.json` before it writes, and it changes only the
`outputStyle` key. `./uninstall.sh` reverses both steps.

`--link` is the better choice on a machine where you keep a clone of this
repository, because then `git pull` updates the live style with no second step
and there is no drifting copy.

## Other surfaces

**claude.ai and Claude Science.** Paste
[`claude-ai/preferences.md`](claude-ai/preferences.md) into
Settings, then Profile, then the field named "Instructions for Claude". That
field applies to all of your conversations, so it needs no per-chat action. It
is a condensed version of the style: it drops the parts that only make sense in
Claude Code, such as `file:line` citations and subagent hand-offs, and keeps
everything about words and sentences.

**Other Claude Code surfaces.** The plugin covers the CLI, the desktop app, the
web app and the IDE extensions, because all of them read the same
`~/.claude` configuration.

## Adapting it for a different person

The style is written in the first person for one specific reader, which is what
makes it work. Four things in it are person-specific, and a colleague who wants
to reuse it should change these four and leave the rest alone.

1. **The first-language line**, quoted here from near the top of the style file:
   "My first language is Chinese and I work in computational biology." The whole
   Compounds section and the whole
   Relative clauses section follow from Chinese specifically, because Chinese
   compounds are often coordinate where English compounds are right-headed, and
   because Chinese has no relative pronoun. For a Romance-language reader those
   two sections matter much less, and the vocabulary section matters much less
   again, because Latin roots make rare English words half-guessable.
2. **The CEFR level and the field-English gap**, in the section that begins "My
   general English is CEFR B2." Change B2 if that is wrong. Do not delete the
   gap explanation, because it is the part that stops Claude from simplifying
   `orthogonal` into something false.
3. **The word tables**: the list of terms of art to keep, and the table of fancy
   English to replace. These were calibrated by asking the reader which specific
   words were hard. Recalibrate them for a different field. A statistician and a
   structural biologist do not share a term-of-art list.
4. **The example sentences.** Every example in the style is a real construction
   from this reader's own logs. Replacing them with invented examples weakens
   the rule, so replace them with real ones from your own transcripts.

Do not change the section named "The rule that outranks every other rule", and
do not change the section named "Do not restate my dense technical text. Quote
it." Both were established by measurement rather than by preference, and the
second one is the finding this whole project turned on. See `verify/RESULTS.md`.

## Does it work

Yes for generation, with one honest limit for rewriting. Full numbers in
[`verify/RESULTS.md`](verify/RESULTS.md). The headline results, from 72 real
calls across 12 prompts and 2 arms with 0 failures:

| metric | control | with the rule | change |
|---|---|---|---|
| fancy English per 1,000 words | 1.68 | 0.00 | −100% |
| invented or informal words per 1,000 words | 0.04 | 0.00 | −100% |
| negative contractions per 1,000 words | 0.07 | 0.00 | −100% |
| inline bold per 1,000 words | 8.58 | 3.21 | −63% |
| sentences over 25 words | 19.37% | 11.31% | −42% |
| mean sentence length in words | 18.19 | 15.79 | −13% |

No metric got worse.

**Three rules barely work**, and this is recorded as a negative result rather
than hidden: reduced relative clauses fell only 11%, stacked verb forms 9%, and
single-use coined compounds 2%. They are stated in the style and they are not
changing behaviour much.

**The limit.** The fidelity gate, which tested whether rewriting existing dense
technical prose under this style preserves every claim, never passed. A bake-off
of four rewriting policies over 96 agents found the best at 50%, and the policy
that kept the original verbatim and only added a summary above it finished last
at 17%, because the summary itself reversed a claim. The conclusion is that any
act of restating dense technical prose introduces errors. The style therefore
governs prose that Claude composes itself, and it tells Claude to quote rather
than paraphrase when you hand it dense text. That is a scoping decision, not a
pass.

## Check that it is actually running

Two checks. The first says the plugin is loaded. The second says the style is
changing what Claude writes, which is the check that matters.

**Check 1, is the plugin loaded.**

```bash
claude plugin list
claude plugin details plain-precise
```

**Check 2, is the style firing.** Run this after `/clear` or in a new session:

```bash
claude -p "In two sentences, say what a comparator method that is agnostic to a nuisance parameter risks."
```

The prompt contains three trap words on purpose. Read the reply:

- The style is live if the reply writes "comparison method" instead of
  `comparator`, writes "does not assume" instead of `agnostic`, glosses
  `nuisance parameter` inline, and labels the claim `[inferred]` or
  `[training]`. It keeps `nuisance parameter` itself, because that is a real
  statistical term and the style protects terms of art.
- The style is not live if the reply keeps `comparator` and `agnostic` unchanged
  and uses em dashes.

Both arms of this probe were run during development, so the two outputs are easy
to tell apart. See [`verify/RESULTS.md`](verify/RESULTS.md).

The style is part of the system prompt, and Claude Code reads the system prompt
once at session start, so a change takes effect only after `/clear` or a new
session.

## Score your own prose against it

```bash
cd verify
python3 score.py --text some_file.md --gates
```

`score.py` needs only the Python standard library. It measures mechanical
properties such as sentence length, em dashes, inline bold and the word lists.
It deliberately does not measure anything semantic, because five wrong
measurements during development all came from trying to judge meaning with a
regular expression. Glossing, noun stacks, metaphor and pronoun anchoring need a
grader, not a pattern.

## Licence

Apache License 2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

Anyone may use, change and redistribute this, including inside a commercial
product. Two conditions apply to redistribution. They must keep the copyright
notice and the `NOTICE` file, and they must state which files they changed.
The licence also grants patent rights and withdraws them from anyone who sues
over a patent covering this work.

If you publish something built on this rule, a citation is welcome but not
required.
