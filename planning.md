# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
search_listings(description, size, max_price) — Searches the mock listings dataset and returns matching items. Must handle the case where no matches are found.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ...
- `size` (str): ...
- `max_price` (float): ...

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
Returns matching items. and exception handling for if no match is found.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
States that no match is found.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
suggest_outfit(new_item, wardrobe) — Given a specific item and the user's current wardrobe, suggests one or more complete outfit combinations. Must handle an empty or minimal wardrobe.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...
- `wardrobe` (dict): ...

**What it returns:**
<!-- Describe the return value -->
Returns a list of one or more outfit suggestions, where each suggestion is a dict containing the new item plus complementary wardrobe pieces (e.g., {"top": ..., "bottom": ..., "shoes": ..., "notes": "casual streetwear pairing"}). If multiple valid combinations exist, returns up to 3 ranked by best style match.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the wardrobe is empty or has no compatible category items (e.g., only tops, no bottoms), the tool returns an empty list and a flag indicating insufficient wardrobe data. The agent should then suggest the new item as a standalone piece and recommend 1-2 generic items the user could pair it with, rather than failing outright.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
create_fit_card(outfit, new_item) — Takes a finalized outfit combination and the newly found item, and generates a shareable "fit card" summary (text or structured card) describing the outfit, the featured item, and price.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str):  a description or identifier of the chosen outfit combination (e.g., from suggest_outfit's output)
- `new_item` (dict):  the listing data for the item being featured (name, price, size, etc.)

**What it returns:**
<!-- Describe the return value -->
A formatted card object/string containing: item name, price, outfit description, and a short style caption (e.g., "Vintage tee + baggy jeans + chunky sneakers — effortless streetwear").

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If outfit or new_item is missing required fields, return an error flag rather than a malformed card. The agent should fall back to presenting the raw item + outfit info in plain text instead of a formatted card.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->


---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The agent inspects the user's query to determine what's missing before it can produce a final answer. It always starts by checking if a listing has been found yet — if not, it calls search_listings with extracted query params (description, size, max_price). Once a listing is found, it checks whether the user wants styling help; if so, it calls suggest_outfit with the new item and the user's wardrobe state. Once an outfit is determined, it calls create_fit_card to produce the final output. The loop terminates once a fit card (or a fallback plain-text response) has been generated, or after a fixed number of tool calls if no valid path is found — at which point it tells the user no results were available.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
The agent maintains a session-level state dict tracking: current_item (result of search_listings), wardrobe (user's existing items, loaded at session start or provided by the user), and current_outfit (result of suggest_outfit). Each tool call reads from and writes back to this shared state object so later tools (suggest_outfit, create_fit_card) don't need the user to repeat information already retrieved earlier in the session.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |


Error Handling table
ToolFailure modeAgent responsesearch_listingsNo results match the queryInform the user no matching listings were found, and suggest relaxing a constraint (e.g., "try a higher price limit or different size")suggest_outfitWardrobe is emptyPresent the new item alone with general styling notes rather than a full outfit, and prompt the user to add wardrobe items for future personalized suggestionscreate_fit_cardOutfit input is missing or incompleteFall back to a plain-text summary of the item and partial outfit info instead of a structured card

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     Use ASCII art or a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html).
     Do NOT embed an image — graders need to read your diagram directly in the file;
     an embedded image or screenshot cannot be evaluated.
     You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->


     

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

     User query
    │
    ▼
Planning Loop ───────────────────────────────────────────┐
    │                                                    │
    ├─► search_listings(description, size, max_price)    │
    │       │ results=[]                                 │
    │       ├──► [ERROR] "No listings found..." → return │
    │       │                                            │
    │       │ results=[item, ...]                        │
    │       ▼                                            │
    │   Session: selected_item = results[0]              │
    │       │                                            │
    ├─► suggest_outfit(selected_item, wardrobe)          │
    │       │                                            │
    │   Session: outfit_suggestion = "..."               │
    │       │                                            │
    └─► create_fit_card(outfit_suggestion, selected_item)│
            │                                            │
        Session: fit_card = "..."                        │
            │                                            └─ error path returns here
            ▼
        Return session



     Milestone 3 — Individual tool implementations:

Tool: Claude
Input: Tool 1-3 specs (inputs, return values, failure modes) from this planning.md
Expected output: Three standalone Python functions (search_listings, suggest_outfit, create_fit_card) matching the specified signatures and error handling
Verification: Test each function individually with both valid and edge-case inputs (no matches, empty wardrobe, incomplete outfit) before integrating

Milestone 4 — Planning loop and state management:

Tool: Claude
Input: Planning Loop, State Management, and Architecture sections + the three tool implementations from Milestone 3
Expected output: A controller/agent loop that maintains session state and calls tools in the correct order based on the Architecture diagram
Verification: Run the full example interaction (vintage tee query) and confirm the agent calls tools in the expected order and produces a complete fit card at the end



---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

A Complete Interaction — Step by Step
Example query: "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"
Step 1:

Agent parses the query and extracts description="vintage graphic tee", max_price=30, size=None (not specified). Calls search_listings(description="vintage graphic tee", size=None, max_price=30).

Step 2:

search_listings returns a matching item (e.g., a $24 vintage graphic tee). Agent stores it in state as current_item and notes the user mentioned wearing "baggy jeans and chunky sneakers" — treats this as an implicit wardrobe. Calls suggest_outfit(new_item=current_item, wardrobe={"bottom": "baggy jeans", "shoes": "chunky sneakers"}).

Step 3:

suggest_outfit returns an outfit combination pairing the tee with baggy jeans and chunky sneakers, plus a style note ("relaxed streetwear look"). Agent stores this as current_outfit and calls create_fit_card(outfit=current_outfit, new_item=current_item).

Final output to user:

A fit card showing: "Vintage Graphic Tee — $24. Style it with baggy jeans and chunky sneakers for an effortless streetwear look."


One thing worth double-checking before you lock this in: your Tool 1 spec says it should "handle the case where no matches are found," but nothing in your state management currently says what happens to the rest of the planning loop if search_listings comes back empty — does the loop just end there, or does it ask the user for a relaxed query and retry? Worth deciding explicitly since it'll affect how you code the controller.
