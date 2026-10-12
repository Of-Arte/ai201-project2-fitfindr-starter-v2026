"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes all three tools",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops before second tool",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # State stability: selected_item id is identical across 5 runs. Criterion 3.
        "name": "same query produces same selected item",
        "query": "oversized flannel shirt",
        "wardrobe": "example",
        "criterion": 3,
    },
    # ── Criterion 4: Fit card across 5 different items (>=2 unbranded) ────────
    {
        # Item 1 (unbranded): Y2K Baby Tee — Butterfly Print ($18, depop)
        "name": "fit card item 1 unbranded baby tee",
        "query": "butterfly baby tee",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Item 2 (unbranded): Corduroy Wide-Leg Pants — Rust ($32, depop)
        "name": "fit card item 2 unbranded corduroy pants",
        "query": "corduroy wide leg pants rust",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Item 3 (branded): Vintage Levi's 501 Jeans — Medium Wash ($38, depop)
        "name": "fit card item 3 levis 501 jeans",
        "query": "vintage levis 501 jeans",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Item 4 (branded): 90s Track Jacket — Navy/White Stripe ($45, poshmark)
        "name": "fit card item 4 track jacket",
        "query": "90s track jacket navy",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Item 5 (branded): Oversized Flannel Shirt — Plaid Red/Black ($22, thredUp)
        "name": "fit card item 5 flannel shirt",
        "query": "oversized flannel shirt plaid",
        "wardrobe": "example",
        "criterion": 4,
    },
    # ── Criterion 5: Price ceiling across 5 distinct queries ──────────────────
    {
        # Query 1: Boots with $50 ceiling
        "name": "price ceiling query 1 boots under 50",
        "query": "suede boots under $50",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Query 2: Graphic tee with $25 ceiling
        "name": "price ceiling query 2 tee under 25",
        "query": "graphic tee under $25",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Query 3: Flannel with $25 ceiling
        "name": "price ceiling query 3 flannel under 25",
        "query": "flannel shirt under $25",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Query 4: Jacket with $45 ceiling
        "name": "price ceiling query 4 jacket under 45",
        "query": "denim jacket under $45",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Query 5: Pants with $35 ceiling
        "name": "price ceiling query 5 pants under 35",
        "query": "corduroy pants under $35",
        "wardrobe": "example",
        "criterion": 5,
    },
    # ── Failure Mode Diagnostic ───────────────────────────────────────────────
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe fallback",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
