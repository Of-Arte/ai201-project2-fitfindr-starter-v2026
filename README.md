# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps a user find clothing items and get outfit ideas for them. The user types a request such as `vintage graphic tee under $30` or `denim jacket, size M`. The agent extracts the description, size and price limits from the request, and searches the listings in `data/listings.json` for the top match. Then, the model provides outfit ideas that use pieces from the user's wardrobe or general styling advice if the wardrobe is empty. Finally, it writes a fit card caption that names the item, its price and its platform. If nothing matches, the user gets a message saying what was searched and what to change instead.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches listings.json for items matching a description, and optionally a size and a price ceiling. Does not call the model.
- **Inputs:**
  - `description` (str): keywords matched against each listing's title, description, category, brand, style tags and colors.
  - `size` (str or None): a size such as "M" or "US 9". Matches whole size tokens so "M" matches "S/M" but "S" does not match "US 9". "One Size" listings match any size. None skips size filtering.
  - `max_price` (float or None): maximum price in dollars. None skips price filtering.
- **Returns:** A list of listing dicts (id, title, description, category, style_tags, size, condition, price, colors, brand, platform), best keyword match first. Listings with no matching keywords are dropped.
- **When it has nothing:** An empty list `[]` (never None).

### `suggest_outfit`

- **What it does:** Asks the model for outfit ideas that combines a new item with pieces from the user's wardrobe.
- **Inputs:**
  - `new_item` (dict): a listing dict for the item the user is considering
  - `wardrobe` (dict): a dict with an `items` key holding a list of owned pieces (may be empty)
- **Returns:** A string of outfit suggestions that name specific wardrobe pieces the user already owns.
- **When it has nothing:** If `wardrobe['items']` is empty, it returns general styling advice for the item instead. It never returns an empty string.

### `create_fit_card`

- **What it does:** Asks the model to write a short caption about the find, based on the item and the outfit suggestion.
- **Inputs:**
  - `outfit` (str): the outfit suggestion string from `suggest_outfit`
  - `new_item` (dict): the listing dict for the item (title, price, platform)
- **Returns:** A 2-4 sentence caption that mentions the item, its price, and its platform once each.
- **When it has nothing:** If `outfit` is empty, it returns a message saying there's no outfit to write a caption for.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**

- If `search_listings` returns an empty list, set `session["error"]` to a message naming what was searched and what the user could change (built by `_nothing_found_message`), and return the session without calling `suggest_outfit`. Otherwise store the first result in `session["selected_item"]` and call `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`. A price pattern (`under`/`below`/`less than`/`max`/`up to` plus `$N`) sets `max_price`. A size pattern (`size M`, `size US 9`, or `, M`) sets `size`. The remaining text becomes `description`. Anything not found becomes `None`.

**What moves through the session:** `query`, then `parsed` (description, size, max_price), then `search_results`, then `selected_item` (the first result), then `outfit_suggestion`, then `fit_card`. `wardrobe` is set at the start. `error` stays `None` unless the run stops early.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30, size M'
[1] parse_query
      in:  vintage graphic tee under $30, size M
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Pair the Y2K Baby Tee with the baggy straight-leg jeans and chunky white sneakers for a classic, effortless st…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Live laugh love a butterfly moment. Snagged this Y2K baby tee on Depop for just $18 and the print is giving ab…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair the Y2K Baby Tee with the baggy straight-leg jeans and chunky white sneakers for a classic, effortless street-style look.

Alternatively, wear it with the wide-leg khaki trousers layered under the vintage black denim jacket, finished off with black combat boots for an edgy, contrasting vibe.

  Fit card: Live laugh love a butterfly moment. Snagged this Y2K baby tee on Depop for just $18 and the print is giving absolute early 2000s pop star off-duty vibes. Pair it with baggy denim for everyday grunge or dress it down with combat boots. #depop #y2kstyle

2 model calls this session, 523 prompt + 130 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Pair these vintage jeans with your white ribbed tank top and black cropped zip hoodie for a classic streetwear look, finished off with chunky white sneakers.

Alternatively, wear the jeans tucked into your black combat boots along with the oversized grey crewneck sweatshirt and the brown leather belt for a cozy, vintage-inspired vibe.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats the effortless 90s off-duty model vibe of a good medium wash. These vintage Levi's 501 jeans are up on my depop for $38 and ready to be lived in. Just toss them on with some beat-up white sneakers and a plain tee for the ultimate effortless look. #vintagelevis #depopseller
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- _What I asked for:_ I asked Claude how a query like "vintage graphic tee under $30" could be parsed into `description`, `size` and `max_price`, while I was weighing a wardrobe-based branch rule.
- _What came back:_ Claude explained that the wardrobe isn't parsed from the query at all, and laid out three options: regex, string splitting, or asking the model for JSON, with the trade-offs of each.
- _What I changed:_ I dropped the wardrobe branch idea and committed to regex parsing in search_listings(). I filled in "How the query is parsed" with the real patterns.

**Moment 2**

- _What I asked for:_ I asked Claude to review my Tool Inventory for `search_listings` against the code for that tool, and to check that the flow followed the spec.
- _What came back:_ Claude noticed the branch rule matched, but the `search_listings` entry didn't match the implementation. `description` referenced "the user's query" but the tool matched keywords against the title, description, category, brand, style tags and colors. It listed `size` and `max_price` as plain `str` and `float` when both can be `None`.
- _What I changed:_ I rewrote the entry. `description` is now keywords, `size` and `max_price` are `str or None` and `float or None`, and a size matches only on whole tokens.

**Moment 3**

- _What I asked for:_ I asked Claude to write throwaway Python scripts to check criteria 4 and 5 for the 19:20 run. For each try it pulled the selected item's price and platform, then checked that the fit card contained `$price` and the platform name, and did not contain "None".
- _What came back:_ Every fit card passed. Every listing was at or under its ceiling, including the $45 jacket at exactly $45. Both criteria came back MET at 5/5.
- _What I changed:_ After examining the results and confirming the correctness of the scripts, I updated the README to record those results under "The Improvement".

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops before second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. same query produces same selected item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card has price and platform without None | 4 of 5 across 5 items | — | — | — | — | — | NOT EVALUATED (only 1 item in `scenarios.py`) |
| 5. price ceiling strictly respected | 5 of 5 across 5 queries | — | — | — | — | — | NOT EVALUATED (only 1 query in `scenarios.py`) |

*`scenarios.py` held only one scenario each for criteria 4 and 5, so neither could be scored against its multi-item / multi-query target.*

**Real output from one try**, pasted as text, naming the file and function
that produced it:

### Criterion 1: matching query completes all three tools (Try 1)
- **File & function:** `agent.py::run_agent`
- **Query:** `vintage graphic tee under $30`

```text
stopped early: no
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
search_results: 10

Outfit suggestion:
Pair the Y2K Baby Tee with the baggy straight-leg jeans, black combat boots, and the vintage black denim jacket for an edgy, nostalgic street style. Alternatively, style it with the wide-leg khaki trousers, brown leather belt, and chunky white sneakers for a cute, retro-casual look.

Fit card:
Living for this Y2K butterfly baby tee to channel that ultimate early 2000s brat-pack energy. It’s in mint condition and listed on Depop right now for $18. Pair it with baggy cargos and stomper boots for a gritty, nostalgic street style look. #y2kstyle #thriftootd
```

### Criterion 2: impossible query stops before second tool (Try 1)
- **File & function:** `agent.py::_nothing_found_message` (invoked via `agent.py::run_agent`)
- **Query:** `designer ballgown size XXS under $5`

```text
stopped early: yes — Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
selected_item: (none)
search_results: 0

Trace:
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit
```

### Criterion 3: same query produces same selected item (Try 1)
- **File & function:** `tools.py::search_listings` and `agent.py::run_agent`
- **Query:** `oversized flannel shirt`

```text
stopped early: no
selected_item: Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp)
search_results: 7

Trace:
[1] parse_query
      in:  oversized flannel shirt
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 7 items: Oversized Flannel Shirt — Plaid Red/Black, Knit Cardigan — Chunky Brown, Oversized Crewneck Sweatshirt — Vintage Navy … +4 more
      →    7 match(es)
[3] select_item
      out: Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp)
```

*(Note: `selected_item` resolved to `lst_003` Oversized Flannel Shirt — Plaid Red/Black in all 5 tries).*

### Criterion 4: fit card has price and platform without None (Try 1)
- **File & function:** `tools.py::create_fit_card`
- **Query:** `y2k baby tee butterfly print`
- **Item evaluated:** `Y2K Baby Tee — Butterfly Print` (listing `lst_002`, `brand: null`, price `$18.0`, platform `depop`)

```text
Totally obsessed with this butterfly print Y2K baby tee I just dropped on Depop for $18. The print gives off major 2000s pop star vibes, especially styled with baggy denim and chunky boots. Grab it before I change my mind and keep it for myself! 🦋 #y2kstyle #depopseller
```

*(Output shows 1 item tested; did not evaluate 5 distinct items as required by the original Unit 3 target).*

### Criterion 5: price ceiling strictly respected (Try 1)
- **File & function:** `tools.py::search_listings` (via `mcp_server.py`)
- **Query:** `denim jacket under $40` (parsed: `max_price: 40.0`)

```text
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 5 items: Vintage Levi's 501 Jeans — Medium Wash, High-Waisted Denim Shorts — Cutoff, Shacket — Olive Canvas … +2 more
      →    5 match(es)

search_results (5 items):
1. Vintage Levi's 501 Jeans — Medium Wash ($38.00)
2. High-Waisted Denim Shorts — Cutoff ($24.00)
3. Shacket — Olive Canvas ($33.00)
4. Denim Mini Skirt — Distressed ($30.00)
5. Denim Vest — 90s Vintage ($27.00)
```

*(Output shows 1 query tested; did not evaluate 5 distinct queries as required by the original Unit 3 target).*

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| #   | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1   | Matching query completes all three tools | In at least 4 of 5 tries | MET (5/5) | In all 5 tries with `'vintage graphic tee under $30'`, all three tools executed and returned a complete fit card. |
| 2   | Impossible query stops before second tool | 5 of 5 tries | MET (5/5) | In all 5 tries with `'designer ballgown size XXS under $5'`, search returned `[]`, loop halted before `suggest_outfit`, and an actionable message was set in `session["error"]`. |
| 3   | Something about state | 5 of 5 tries | MET (5/5) | Across all 5 tries with `'oversized flannel shirt'`, `session["selected_item"]["id"]` resolved to `lst_003`. |
| 4   | Something about the fit card | In 4 of 5 tries across 5 different items (≥2 unbranded) | NOT EVALUATED | Only 1 unbranded item (`lst_002`) was tested across 5 attempts; `scenarios.py` lacked entries for the remaining 4 items required by the target. |
| 5   | Your choice (price ceiling) | For 5 queries with price limit, all results ≤ limit in 5/5 tries | NOT EVALUATED | Only 1 price-limited query (`'denim jacket under $40'`) was tested across 5 attempts; `scenarios.py` lacked entries for the other 4 queries required by the target. |

**Diagnoses**

- **Criteria 1, 2, and 3:** Fully tested and met without defect. The loop, MCP search tool, branch stop condition, and session state persistence were stable across all 5 runs.
- **Criteria 4 and 5 (Configuration Oversight):**
  - **Where it happened:** `scenarios.py`
  - **Mechanism:** Both criteria were written in unit 3 as multi-item and multi-query tests. During setup I authored a single scenario for each, assuming the runner's 5 repeated tries would satisfy "out of 5". Repeating one item 5 times did not test variation across items, so multi-entity criteria were never exercised.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
python app.py ask 'boots' --trace

[1] parse_query
      in:  boots
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 1 items: Suede Chelsea Boots — Tan
      →    1 match(es)
[3] select_item
      out: Suede Chelsea Boots — Tan ($44.0, poshmark)
[4] suggest_outfit
      in:  Suede Chelsea Boots — Tan ($44.0, poshmark)
      out: Pair the Suede Chelsea Boots with the baggy straight-leg jeans, white ribbed tank top, and vintage black denim…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Suede Chelsea Boots — Tan ($44.0, poshmark)
      out: Scored these gorgeous tan suede Chelsea boots in fair condition on Poshmark for just $44, and they have that p…

  Found:    Suede Chelsea Boots — Tan — $44.0 on poshmark

  Outfit:   Pair the Suede Chelsea Boots with the baggy straight-leg jeans, white ribbed tank top, and vintage black denim jacket for an effortless, classic look. Alternatively, style them with the wide-leg khaki trousers, white ribbed tank top, and brown leather belt for a warm, monochromatic earth-tone outfit.

  Fit card: Scored these gorgeous tan suede Chelsea boots in fair condition on Poshmark for just $44, and they have that perfectly worn-in 70s rockstar vibe. I’m picturing them with baggy straight-leg denim and a black vintage jacket for days when I want to look effortlessly cool without trying. #thriftedstyle #poshmarkfinds

2 model calls this session, 514 prompt + 138 output tokens
```

**Empty search**

```
python app.py ask '...' --trace

[1] parse_query
      in:  ...
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit

  Nothing in the listings matched description '...'.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'.

0 model calls this session
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** I edited `scenarios.py` to add the missing scenarios: 5 distinct items for criterion 4 (including 2 unbranded: baby tee and corduroy pants) and 5 distinct price-limited queries for criterion 5. Then I re-ran `python run_eval.py`. 

**Which failure it was meant to fix:** The NOT EVALUATED verdicts on criteria 4 and 5, which the diagnosis traced to a test configuration gap in `scenarios.py`.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops before second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. same query produces same selected item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card has price and platform without None | 4 of 5 across 5 items | PASS | PASS | PASS | PASS | PASS | MET (5/5 on each of 5 items) |
| 5. price ceiling strictly respected | 5 of 5 across 5 queries | PASS | PASS | PASS | PASS | PASS | MET (5/5 on each of 5 queries) |

For criteria 4 and 5, each Try cell means that try passed on all 5 items / all 5 queries.

### Criterion 4: fit card has price and platform without None (all 5 items, 5 tries each)
- **File & function:** `tools.py::create_fit_card`

| Item | Query | Brand | Price / platform | Tries with price + platform, no "None" |
| ---- | ----- | ----- | ---------------- | -------------------------------------- |
| Y2K Baby Tee — Butterfly Print | `butterfly baby tee` | none | $18 / depop | 5/5 |
| Corduroy Wide-Leg Pants — Rust | `corduroy wide leg pants rust` | none | $32 / depop | 5/5 |
| Vintage Levi's 501 Jeans — Medium Wash | `vintage levis 501 jeans` | Levi's | $38 / depop | 5/5 |
| 90s Track Jacket — Navy/White Stripe | `90s track jacket navy` | Champion | $45 / poshmark | 5/5 |
| Oversized Flannel Shirt — Plaid Red/Black | `oversized flannel shirt plaid` | Woolrich | $22 / thredUp | 5/5 |

I checked all 25 fit cards by script: each contains the selected item's price and platform name, and none contains "None". Sample (baby tee, Try 1):

```text
Found this absolute gem of a Y2K baby tee with the cutest butterfly print and I am obsessed. It’s in gorgeous condition and up on Depop right now for $18. Pair it with baggy jeans and combat boots for that effortless edgy streetwear look. #depop #y2kstyle
```

### Criterion 5: price ceiling strictly respected (all 5 queries, 5 tries each)
- **File & function:** `tools.py::search_listings` (via `mcp_server.py`)

| Query | Ceiling | Matches | Highest price in results | All ≤ ceiling |
| ----- | ------- | ------- | ------------------------ | ------------- |
| `suede boots under $50` | $50 | 1 | $44 | yes, 5/5 |
| `graphic tee under $25` | $25 | 4 | $24 | yes, 5/5 |
| `flannel shirt under $25` | $25 | 2 | $22 | yes, 5/5 |
| `denim jacket under $45` | $45 | 7 | $45 | yes, 5/5 |
| `corduroy pants under $35` | $35 | 2 | $32 | yes, 5/5 |

The run log records only the match count and the selected item per try, so I confirmed the full result lists by calling `search_listings` directly with the same parsed arguments. Counts match the log (1, 4, 2, 7, 2) and every price is at or under the ceiling. The search is deterministic, so all 5 tries return the same list. The $45 jacket hits the ceiling exactly, which shows the check is inclusive.

**Did it help, and how do I know:** Yes. I know because I checked all 25 fit cards for "price and platform without None", and the full result list of each price-limited query against its ceiling. The unbranded items showed the null-brand handling in `create_fit_card` works

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

No criterion is currently missed, but the coverage is limited. This shows the tools meet my targets on these 5 items and queries, but there are other edge cases to test. Criterion 4 and 5 pass because the queries are too easy, Criterion 5 has only one result at its ceiling, and nothing tests a price filter combined with a size filter. With more time I would rewrite these criteria to be more challenging by targeting those edge cases..  

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
