"""Word lists for the plain-language scorer.

Three groups:
  FANCY_ENGLISH  - rare general-English words with an exact plain equivalent. Must reach zero.
  PHRASAL        - figurative phrasal verbs with a one-word plain equivalent. Must reach zero.
  INFORMAL       - invented / informal / visual words. Must reach zero.
  TERMS_OF_ART   - allow-list. These must NEVER be flagged and must never be replaced.

The user confirmed the split personally, so these are calibrated, not guessed:
  hard  -> nuisance, comparator, provenance, per se, sans, agnostic, idempotent
  fine  -> orthogonal, canonical, degenerate, spurious
"""

# Confirmed hard by the user, plus others of the same kind.
FANCY_ENGLISH = {
    "comparator": "comparison method",
    "comparators": "comparison methods",
    "nuisance": "unwanted, or name the thing it interferes with",
    "provenance": "origin",
    "per se": "in itself",
    "sans": "without",
    "agnostic": "does not assume",
    "idempotent": "safe to run more than once",
    "conflate": "treat two separate things as one",
    "conflates": "treats two separate things as one",
    "conflated": "treated two separate things as one",
    "salient": "important",
    "obviate": "remove the need for",
    "obviates": "removes the need for",
    "requisite": "required",
    "extant": "existing",
    "attenuate": "weaken",
    "attenuates": "weakens",
    "delineate": "describe",
    "instantiate": "create",
    "instantiates": "creates",
    "tractable": "workable",
    "intractable": "not workable",
    "elide": "leave out",
    "elides": "leaves out",
    "subsume": "include",
    "subsumes": "includes",
    "ostensibly": "apparently",
    "a priori": "in advance",
    "de facto": "in practice",
    "ipso facto": "by that fact",
    "modulo": "apart from",
    "viz": "namely",
    "commensurate": "matching",
    "parsimonious": "simple",
    "germane": "relevant",
    "nascent": "early",
    "opaque": "hard to inspect",
    "brittle": "easily broken",
}

# Figurative phrasal verbs. Key is a regex-safe phrase; whitespace matches any run of spaces.
PHRASAL = {
    "pin down": "determine",
    "pins down": "determines",
    "pinning down": "determining",
    "pinned down": "determined",
    "paper over": "hide",
    "papers over": "hides",
    "papering over": "hiding",
    "papered over": "hid",
    "bolt on": "add afterwards",
    "bolted on": "added afterwards",
    "bolting on": "adding afterwards",
    "boils down to": "reduces to",
    "boil down to": "reduce to",
    "bake in": "build in",
    "baked in": "built in",
    "baking in": "building in",
    "shakes out": "turns out",
    "shake out": "turn out",
    "teases apart": "separates",
    "tease apart": "separate",
    "walk back": "withdraw",
    "walks back": "withdraws",
    "back out": "remove",
    "sanity-check": "check",
    "sanity check": "check",
    "loose end": "unresolved question",
    "loose ends": "unresolved questions",
    "hand-wave": "argue loosely",
    "hand-waving": "arguing loosely",
    "hand-wavy": "loosely argued",
}

# Invented / informal / visual. Cannot be exhaustive by design, graders catch the rest.
INFORMAL = {
    "blobbier", "blobby", "blobbiness",
    "spikier", "spiky",
    "janky", "jank",
    "gnarly", "hairy",
    "fiddly", "clunky",
    "sane", "sanity",
    "sloppy", "messy", "ugly", "nasty",
    "wonky", "dodgy", "squishy",
}

# Allow-list. Never flag, never replace. The four the user confirmed, plus domain vocabulary.
TERMS_OF_ART = {
    # user-confirmed as comfortable
    "orthogonal", "orthogonality", "canonical", "degenerate", "degeneracy",
    "spurious",
    # statistics and maths
    "kurtosis", "skewness", "marginal", "marginals", "residual", "residuals",
    "separatrix", "saddle", "eigenvalue", "eigenvector", "isotropic", "anisotropic",
    "heteroscedasticity", "homoscedastic", "stochastic", "deterministic",
    "posterior", "prior", "likelihood", "variance", "covariance", "quantile",
    "pearson", "spearman", "wasserstein", "kolmogorov", "smirnov", "icc",
    "monotonic", "convex", "concave", "gradient", "jacobian", "hessian",
    "significant", "significance", "power", "bias", "normal", "robust",
    "mixing", "stiff", "sharp", "tight", "regularisation", "regularization",
    # dynamics and modelling
    "fokker", "planck", "langevin", "euler", "maruyama", "ode", "sde", "pde",
    "diffusion", "drift", "advection", "flux", "manifold", "trajectory",
    "optimal", "transport", "barycentre", "barycenter", "coupling",
    # biology and single-cell
    "atac", "clone", "clones", "clonal", "lineage", "barcode", "barcodes",
    "transcriptome", "embedding", "pseudotime", "fate", "progenitor",
    "unipotent", "multipotent", "actin", "filament", "metaclone",
    # tooling
    "slurm", "numpy", "scipy", "pytorch", "anndata", "scanpy",
}


# Multi-word terms of art. A flagged word inside one of these is NOT a violation.
#
# This list exists because of a real false positive found in testing: every single
# occurrence of "nuisance" in the trial outputs was "nuisance parameter", which is a
# genuine statistical term. Renaming it would break the link to the literature, so the
# correct handling is to gloss the phrase, not to replace the word.
PROTECTED_PHRASES = [
    "nuisance parameter",
    "nuisance parameters",
    "nuisance variable",
    "nuisance variables",
    "spurious correlation",
    "spurious correlations",
    "canonical correlation",
    "canonical form",
    "degenerate case",
    "degenerate distribution",
    "orthogonal projection",
    "orthogonal basis",
    "provenance graph",     # a real term in workflow / data-lineage tooling
    "agnostic prior",
]


def _norm(w):
    return w.lower().strip()


def is_term_of_art(word):
    """True if the word is on the allow-list and must never be flagged."""
    return _norm(word) in TERMS_OF_ART
