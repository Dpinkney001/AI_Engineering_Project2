"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    # Replace this with your implementation

    listings = load_listings()

    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None:
            listing_size = str(listing.get("size", "")).lower()
            if size.lower() not in listing_size:
                continue
        filtered.append(listing)

    # Step 3: score by keyword overlap with description
    keywords = set(description.lower().split())

    def score(listing):
        text_fields = [
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            " ".join(listing.get("style_tags", [])),
            listing.get("brand", ""),
        ]
        listing_words = set(" ".join(text_fields).lower().split())
        return len(keywords & listing_words)

    scored = [(listing, score(listing)) for listing in filtered]

    # Step 4: drop listings with score of 0
    scored = [(listing, s) for listing, s in scored if s > 0]

    # Step 5: sort by score, highest first
    scored.sort(key=lambda pair: pair[1], reverse=True)

    return [listing for listing, _ in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    # Replace this with your implementation

    item_desc = f"{new_item.get('title', 'this item')} ({new_item.get('description', '')}), " \
                f"category: {new_item.get('category', 'unknown')}, " \
                f"style tags: {', '.join(new_item.get('style_tags', []))}, " \
                f"colors: {', '.join(new_item.get('colors', []))}"

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        # Step 2: empty wardrobe -> general styling advice
        prompt = (
            f"A user is considering buying this thrifted item: {item_desc}.\n\n"
            "They don't have any other wardrobe items on file. Give general styling "
            "advice: what kinds of pieces would pair well with this item, and what "
            "overall vibe or aesthetic does it suit? Keep it concise and practical."
        )
    else:
        # Step 3: format wardrobe items into the prompt
        wardrobe_desc = "\n".join(
            f"- {w.get('name', 'item')} ({w.get('category', 'unknown')}, "
            f"colors: {', '.join(w.get('colors', []))})"
            for w in wardrobe_items
        )
        prompt = (
            f"A user is considering buying this thrifted item: {item_desc}.\n\n"
            f"Here are the items currently in their wardrobe:\n{wardrobe_desc}\n\n"
            "Suggest 1-2 complete outfit combinations that use the new item along "
            "with specific named pieces from their wardrobe. Be specific about which "
            "wardrobe items to pair it with and why they work together."
        )

    # Step 4: call the LLM and return its response as a string
    response = call_llm(prompt)
    return response


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Replace this with your implementation

    # Step 1: guard against empty/whitespace-only outfit
    if not outfit or not outfit.strip():
        return "Can't generate a caption: no outfit suggestion was provided."

    item_name = new_item.get("title", "this piece")
    price = new_item.get("price", "an unknown price")
    platform = new_item.get("platform", "an unknown platform")

    # Step 2: build the prompt
    prompt = (
        f"Write a short Instagram/TikTok OOTD caption (2-4 sentences) for this thrifted find.\n\n"
        f"Item: {item_name}\n"
        f"Price: ${price}\n"
        f"Platform: {platform}\n"
        f"Outfit styling: {outfit}\n\n"
        "Style guidelines:\n"
        "- Sound casual and authentic, like a real person posting their outfit -- "
        "not a product description or ad copy\n"
        "- Mention the item name, price, and platform naturally, each exactly once\n"
        "- Capture the specific vibe of the outfit (not generic, e.g. avoid just saying 'cute outfit')\n"
        "- Keep it to 2-4 sentences total"
    )

    # Step 3: call the LLM at higher temperature for variation
    response = call_llm(prompt, temperature=0.9)
    return response
