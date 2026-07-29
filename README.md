# plain-precise

An always-on writing rule for Claude Code and Codex. It makes the model write
plain English for a non-native English speaker whose general English is around
CEFR B2, while keeping every technical term exact.

The governing rule inside it is one sentence: **never trade precision for
readability.** If plain phrasing would make a claim vaguer, the style keeps the
precise phrasing and spends an extra sentence explaining it.

## What it changes

Both examples are verbatim. Each one shows two answers to the same question,
from the same model, one written with the rule and one without. No wording was
changed and nothing was invented for this page. Where `[...]` appears, text was
left out to keep the example short.

### Example 1, the words

The question asked why a comparison method that ignores a nuisance parameter can
still give a wrong answer.

Without the rule:

> Agnosticism is bought with an assumption about how the nuisance enters, such
> as additively, or with exchangeable observations.

With the rule:

> A comparison method that does not assume a value for the nuisance parameter
> still assumes a structure for it.

Three things changed. `Agnosticism` became "does not assume", which says the
same thing in words that are taught rather than absorbed. The word `bought` was
a metaphor about buying, so it went. And `the nuisance` was written out as
`nuisance parameter`, because the clipped form hides the fact that this is a
statistical term rather than an ordinary English word.

What did not change is the claim itself. Both sentences say that the
independence holds only under an assumption about the form of the model.

### Example 2, the structure

The question asked what an effective sample size of 30 percent does to a
calculation of how many particles to simulate.

Without the rule:

> **Headline: divide any nominal-N sample size by 0.3. You need about 3.33 times
> as many particles as the naive calculation says.**
>
> [...] Any convergence check of the form "standard error below tolerance at N
> particles" fires 3.33 times too early.
>
> **Two things to pin down before you trust the 3.33**

With the rule:

> Multiply every particle count that came out of the calculation by about 3.3. A
> nominal count of 10,000 particles carries the precision of 3,000 independent
> particles, so you need about 33,000 nominal particles to reach the precision
> that the calculation asked for.
>
> [...] Reported standard errors are too small by a factor of 1.83. A reported
> value of 0.010 should be 0.018.
>
> [a heading] Two assumptions that the factor of 3.3 depends on

Four things changed.

1. **The answer arrives as an ordinary sentence.** The version without the rule
   announces that an answer is coming, in bold, before giving it.
2. **The inline bold is gone.** Two of the three fragments shown above are bold
   in the version without the rule. The style keeps bold for headings and for
   numbers with units.
3. **"Pin down" became "depends on".** One plain verb was available, so the
   figurative phrasal verb was not needed.
4. **Every number carries what it is compared against.** A count of 10,000
   nominal particles is given against 3,000 independent ones, and a reported
   standard error of 0.010 against a true 0.018.

There is also no metaphor left. In the version without the rule a convergence
check "fires 3.33 times too early", and a check does not fire.

## Install

Four steps. Do all four, because the first two on their own leave the rule
half-installed.

These are terminal commands. If you use the desktop app, they still apply, and
[Install in the Claude desktop app](#install-in-the-claude-desktop-app) says
where to type them and what to do instead if you would rather not use a
terminal. For Codex, see [Install for Codex](#install-for-codex).

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

**Step 3. Add the research-integrity rules.**

A plugin cannot ship a `CLAUDE.md`, so this part does not travel with the plugin
and needs its own command. Step 2 already put the whole repository on your disk,
so run the script from there. No clone is needed.

```bash
bash ~/.claude/plugins/marketplaces/wz369-writing/install-claude-md.sh
```

The script adds the rules to `~/.claude/CLAUDE.md` between two marker comments,
backs the file up first, and keeps everything you wrote yourself. Running it
twice replaces the block rather than adding a second copy. It also lists any
line that caps output length, such as "be concise" or "keep summaries under 5
lines", and tells you to delete it. Compression is what produces the stacked
nouns and the dropped subjects that the style exists to remove, so a length cap
fights the style directly. The script reports those lines and does not delete
them, because they are yours.

Other things the script accepts:

```bash
bash install-claude-md.sh --dry-run    # say what would change, write nothing
bash install-claude-md.sh --print      # print the block, so you can paste it yourself
bash install-claude-md.sh --uninstall  # take the block out again
```

**Step 4. Confirm the style is actually firing.** See
[Check that it is actually running](#check-that-it-is-actually-running).

For Codex, see [Install for Codex](#install-for-codex). For claude.ai and Claude
Science, see [Other surfaces](#other-surfaces). Plugins are a Claude Code
feature and do not reach either of those.

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
├── codex/
│   ├── AGENTS.md                 the same rules, built for Codex. Generated.
│   └── build.py                  builds codex/AGENTS.md from the two sources
├── claude-ai/
│   └── preferences.md            paste-in text for claude.ai and Claude Science
├── claude-md-snippet.md          the integrity rules, the source for step 3
├── install-claude-md.sh          step 3, and its uninstall
├── install-codex.sh              the Codex install, and its uninstall
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
rebuild the Codex file, bump `version` in
`plugins/plain-precise/.claude-plugin/plugin.json`, then commit and push.

```bash
python3 codex/build.py          # rebuild codex/AGENTS.md from the two sources
python3 codex/build.py --check  # exits 1 if it is out of date
git add -A
git commit -m "what changed"
git push
```

The rebuild step matters, because `codex/AGENTS.md` is generated. If you edit
the style file and skip it, Claude Code users get the change and Codex users do
not.

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

## Install in the Claude desktop app

The desktop app and the CLI read the same configuration files, so there is
nothing separate to install. `~/.claude/settings.json` and your `CLAUDE.md` are
shared between them, and the desktop app runs the same engine underneath.

**The easy route is the built-in terminal.** Open it from the Views menu, or
press <kbd>Ctrl</kbd> and <kbd>`</kbd> on macOS and on Windows. It opens in your
session's working directory. Run the same four steps from
[Install](#install) there, then start a new session. The terminal is available
in local sessions only.

**If you would rather not use a terminal**, do the same thing by editing two
files.

1. Open `~/.claude/settings.json`, which is `%USERPROFILE%\.claude\settings.json`
   on Windows, and add these two keys. Keep whatever is already in the file, and
   merge rather than replace if either key is already present.

   ```json
   {
     "extraKnownMarketplaces": {
       "wz369-writing": {
         "source": { "source": "github", "repo": "oZwZo/agent-plain-precise-language" }
       }
     },
     "enabledPlugins": {
       "plain-precise@wz369-writing": true
     }
   }
   ```

2. Open `~/.claude/CLAUDE.md` and paste in the fenced block from
   [`claude-md-snippet.md`](claude-md-snippet.md).

3. Start a new session.

The plugin browser in the desktop app, reached from the **+** button next to the
prompt box, then **Plugins**, is worth knowing about for a different reason. It
lists what you have installed and lets you enable, disable or uninstall through
**Manage plugins**, so it is a way to turn this rule off without a terminal. The
documentation describes the browser as showing plugins from marketplaces you
have already configured, and does not say whether a new marketplace can be added
from it. I do not know whether it can. That is why step 1 above edits the
settings file directly.

**Two places the plugin does not reach.**

- The **Cowork** tab takes its skills, plugins and connectors from the Customize
  configuration, which syncs through your claude.ai account rather than from
  `~/.claude`. For that tab, and for the Chat tab, use the paste-in text in
  [Other surfaces](#other-surfaces).
- **Cloud sessions** do not get plugins that you installed on the desktop. To
  use it there, declare it under `enabledPlugins` in the repository's
  `.claude/settings.json`, and it installs when the session starts.

**One thing I could not verify.** This plugin works by shipping an output style,
and the desktop documentation never mentions output styles. Configuration is
shared and the engine is the same, so I expect it to apply. [inferred, not
tested on a desktop install] Settle it in about ten seconds by running the probe
in [Check that it is actually running](#check-that-it-is-actually-running) inside
a desktop session, as an ordinary message rather than as a shell command.

## Install for Codex

It works in Codex. I tested it on Codex CLI 0.136.0 rather than assuming it,
and the numbers are below.

```bash
curl -fsSL https://raw.githubusercontent.com/oZwZo/agent-plain-precise-language/main/install-codex.sh -o install-codex.sh
bash install-codex.sh
```

Read the script before you run it. It is one file and it does two things: it
writes the rules into `$CODEX_HOME/AGENTS.md`, where `CODEX_HOME` defaults to
`~/.codex`, and it backs that file up first. If you have a clone of this
repository, skip the download and run `bash install-codex.sh` from inside it.

Then start a new Codex session, because Codex reads the instruction file at
session start.

The same options work as for the Claude script: `--dry-run`, `--print` and
`--uninstall`.

### What is different in Codex, and why

Codex has one instruction file and no output-style mechanism, so the writing
rules and the research-integrity rules go into that one file together. In Claude
Code they are split, because there the two levels behave differently. The
combined file is built from the same two sources by `codex/build.py`, so there
is one place to edit and no second copy to keep in step.

| | Claude Code | Codex |
|---|---|---|
| where the rules live | output style, in the system prompt | `AGENTS.md`, at instruction level |
| how they arrive | `claude plugin install` | a script that writes one file |
| are the two rule sets split | yes, style and `CLAUDE.md` | no, one file holds both |
| does it reach subagents | no | yes, because `AGENTS.md` is inherited |
| turning it off | `claude plugin disable` | `bash install-codex.sh --uninstall` |

### What I measured in Codex

First, that the global file is read at all. I built an isolated `CODEX_HOME`
holding one `AGENTS.md` with a single marker instruction in it, then ran
`codex exec` from a working directory that contained no `AGENTS.md`. The marker
appeared in the reply, so the file at `$CODEX_HOME/AGENTS.md` is what produced
it.

Then the same trap-word probe used for Claude Code, one call per arm, on
`gpt-5.5` at low reasoning effort:

| metric | Codex without the rules | Codex with the rules |
|---|---|---|
| gates passed | 13 of 16 | 16 of 16 |
| fancy English per 1,000 words | 55.56 | 0.00 |
| mean sentence length in words | 18.33 | 14.13 |
| longest sentence in words | 32 | 24 |
| sentences over 25 words | 8.33% | 0.00% |

The arm without the rules kept `comparator` twice, `agnostic` twice, `nuisance`
four times and `provenance` three times. The arm with the rules wrote
"comparison method", "does not assume" and "origin", kept `nuisance parameter`
because it is a real statistical term, and glossed it inline as "an unwanted
source of variation".

This is one call per arm, so it is a single observation and not a rate.

**One honest difference from Claude Code.** The Codex reply labelled every
sentence, 15 labels in 15 sentences, almost all of them `[inferred]`. That is
more labelling than the same rules produce in Claude Code. My reading is that
the integrity rules sit at the same level as everything else in the Codex file,
whereas in Claude Code they sit in `CLAUDE.md`, one level below the style.
[inferred, from one observation, not tested] If it bothers you, delete the
`# Research integrity rules` section from your `~/.codex/AGENTS.md` after
installing, or run `bash install-codex.sh --uninstall` and paste in only the
part you want.

**What it costs.** The rules add about 4,900 input tokens to every Codex
session. Measured with `codex exec --json` on the same trivial prompt in both
arms: 28,097 input tokens without the rules against 32,960 with them. One
measurement per arm.

**A Codex plugin would not work for this.** Codex plugins bundle skills, MCP
servers and app connections. A skill loads when it is invoked, which is the same
reason a skill is the wrong shape in Claude Code, because the problem being
solved is the default rather than an occasional request. So `AGENTS.md` is the
only always-on route in Codex today. [training, checked against published
descriptions of the Codex plugin manifest rather than against the source]

## Turn it off

Every part comes out, and nothing needs a reinstall to come back.

**Claude Code, keep it installed but stop it applying.**

```bash
claude plugin disable plain-precise@wz369-writing
```

Then run `/clear` or start a new session. Turn it back on with
`claude plugin enable plain-precise@wz369-writing`. This is the one to use if
you are unsure, because it changes nothing on disk.

In the desktop app you can do the same without a terminal. Click the **+**
button next to the prompt box, choose **Plugins**, then **Manage plugins**, and
disable it there.

**Claude Code, remove it completely.**

```bash
claude plugin uninstall plain-precise@wz369-writing
claude plugin marketplace remove wz369-writing
bash ~/.claude/plugins/marketplaces/wz369-writing/install-claude-md.sh --uninstall
```

Run the third command before the first two, or keep a copy of the script,
because uninstalling the marketplace deletes the cached repository that holds
it. If it is already gone, download the script again with the `curl` line from
[Install for Codex](#install-for-codex), changing the file name to
`install-claude-md.sh`.

**Codex.**

```bash
bash install-codex.sh --uninstall
```

This takes out only the text between the markers, so anything you wrote in
`~/.codex/AGENTS.md` yourself stays. Start a new Codex session afterwards.

**If you used the no-plugin route**, run `./uninstall.sh`, which removes the
style file and the `outputStyle` key from `settings.json`.

**Every script backs the file up before it writes**, with a timestamp in the
name, such as `CLAUDE.md.bak-20260729-144045`. So a rollback is always possible
even if a script does something you did not want.

**claude.ai.** Delete the pasted text from Settings, then Profile, then
"Instructions for Claude". There is no command for that one.

## Other surfaces

**claude.ai and Claude Science.** Paste
[`claude-ai/preferences.md`](claude-ai/preferences.md) into
Settings, then Profile, then the field named "Instructions for Claude". That
field applies to all of your conversations, so it needs no per-chat action. It
is a condensed version of the style: it drops the parts that only make sense in
Claude Code, such as `file:line` citations and subagent hand-offs, and keeps
everything about words and sentences.

**Other Claude Code surfaces.** The plugin covers the CLI, the desktop app and
the IDE extensions, because those read the same `~/.claude` configuration. It
does not cover the Cowork tab or cloud sessions, which take their configuration
from your claude.ai account instead. See
[Install in the Claude desktop app](#install-in-the-claude-desktop-app) for what
to do about those two.

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
