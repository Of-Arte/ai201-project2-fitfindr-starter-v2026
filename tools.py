"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "or", "that", "the", "to",
    "was", "were", "will", "with",
}

def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "") # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    wanted = _keywords(description)
    if not wanted:
        return []

    scored = []
    for listing in load_listings():
        price = listing.get("price")
        if max_price is not None and (price is None or price > max_price):
            continue
        if not _size_matches(size, listing.get("size")):
            continue

        haystack = " ".join([
            listing.get("title") or "",
            listing.get("description") or "",
            listing.get("category") or "",
            listing.get("brand") or "",
            " ".join(listing.get("style_tags") or []),
            " ".join(listing.get("colors") or []),
        ])
        score = len(wanted & _keywords(haystack))
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)  # stable: ties keep data order
    return [listing for _, listing in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    new_item = new_item or {}
    items = (wardrobe or {}).get("items") or []

    item_text = (
        f"{new_item.get('title', 'an item')} "
        f"(category: {new_item.get('category') or 'unknown'}; "
        f"colors: {', '.join(new_item.get('colors') or []) or 'unknown'}; "
        f"style: {', '.join(new_item.get('style_tags') or []) or 'unknown'}; "
        f"condition: {new_item.get('condition') or 'unknown'})"
    )

    system = (
        "You are a friendly thrift-fashion stylist. Be specific and concise. "
        "Suggest one or two outfits, each as a short sentence or two."
    )

    if not items:
        prompt = (
            f"Someone is considering buying this thrifted item: {item_text}.\n"
            "They haven't told me what's in their wardrobe, so give general "
            "styling advice: one or two outfit ideas built from common basics "
            "(say what kinds of pieces and colors work with it)."
        )
    else:
        lines = []
        for piece in items:
            details = ", ".join(
                part
                for part in (
                    piece.get("category"),
                    "/".join(piece.get("colors") or []),
                    "/".join(piece.get("style_tags") or []),
                    piece.get("notes"),
                )
                if part
            )
            lines.append(f"- {piece.get('name', 'unnamed piece')} ({details})")
        prompt = (
            f"Someone is considering buying this thrifted item: {item_text}.\n\n"
            "Their wardrobe:\n" + "\n".join(lines) + "\n\n"
            "Suggest one or two outfits that combine the new item with pieces "
            "from this wardrobe. Name the wardrobe pieces exactly as listed, "
            "and don't invent pieces they don't own."
        )

    response = (generate(prompt, system=system) or "").strip()
    if response:
        return response
    # The model answered with nothing; the contract says never return "".
    return (
        f"Couldn't generate outfit ideas for {new_item.get('title', 'this item')} "
        "just now — try again."
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    new_item = new_item or {}
    title = new_item.get("title") or "this item"

    if not (outfit or "").strip():
        return (
            f"No outfit suggestion was provided for {title}, so there's "
            "nothing to write a caption about yet."
        )

    price = new_item.get("price")
    price_text = f"${price:g}" if isinstance(price, (int, float)) else "an unlisted price"

    system = (
        "You write short, authentic social media captions for thrift finds. "
        "Sound like a real person posting, not a product listing."
    )
    prompt = (
        "Write a caption of two to four sentences for a post about this thrift find.\n"
        f"Item: {title}\n"
        f"Price: {price_text}\n"
        f"Platform: {new_item.get('platform') or 'unknown'}\n"
        f"Condition: {new_item.get('condition') or 'unknown'}\n\n"
        f"Outfit idea:\n{outfit.strip()}\n\n"
        "Mention the item, its price and its platform once each, and be "
        "specific about the vibe. No hashtag spam (at most two) and no "
        "bullet points. Return only the caption."
    )

    response = (generate(prompt, system=system) or "").strip()
    return response or f"Couldn't write a caption for {title} just now — try again."
