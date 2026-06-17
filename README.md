# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

Your README submission must document each tool's name, inputs, and return value. **These must exactly match your actual function signatures in `tools.py`.** Your documented interfaces will be checked against your actual function signatures in `tools.py` — if the parameter count or types contradict what's in the code, you may not receive full credit for that tool.

---

## Interaction Walkthrough

<!-- Walk through a complete interaction step by step: natural language query → each tool call (and why) → final fit card.
     Walk through this carefully — it's how graders follow your agent's reasoning without a live demo.
     Use a specific example — do not leave this as a template. -->

**User query:**

**Step 1 — Tool called:**
- Tool: search_listings
- Input: 
     - `description` (str): may describe the style, vibe, and item of clothing the user is trying to find
     - `size` (str): specifies the size that user would like the clothing to be. could be multiple dimensions. try to get exact sizes
     - `max_price` (float): how much user is willing to pay. try not to choose clothing that is above this price
- Why this tool: This picks out a new item based on what the user is looking for
- Output: Then the tool goes through listings.json and returns 3 matching listings sorted by relevance. FitFindr picks the top result

**Step 2 — Tool called:**
- Tool: suggest_outfit
- Input: 
     - `new_item` (dict): the listing in listings.json chosen from search_listings.
     - `wardrobe` (dict): a list of clothing from user's wardrobe. use items from here to pair with new_item
- Why this tool: Users want to know if an item would go well with their existing wardrobe so the output helps them with styling
- Output: Describes an outfit and styling that would go with the listing outputed from search_listings

**Step 3 — Tool called:**
- Tool: create_fit_card
- Input:
     - `outfit` (str): generated from suggest_outfit
     - `new_item` (dict): the listing in listings.json chosen from search_listings.
- Why this tool: Users want to show off their outfit on socials with a unique caption
- Output: A caption featuring the new item and outfit. make it unique to item and outfit

**Final output to user:**

---

## Error Handling and Fail Points

<!-- For each tool, describe the specific failure mode and what your agent does in response.
     This maps to the error handling section of the rubric (F5-C1). -->

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No results match the query | Inform the user that no matching listings were found and suggest adjusting the description, size, or price range. Stop the workflow and do not call suggest_outfit.|
| `suggest_outfit` | Wardrobe is empty |Inform the user that there are no wardrobe items available to create an outfit. Stop the workflow and do not call create_fit_card. |
| `create_fit_card` | Outfit input is missing or incomplete |Return an error message such as "No outfit generated, cannot create fit card." Stop the workflow and do not generate a caption. |

---

## Spec Reflection

<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:**
Writing out the specifications helped me understand what is going on and the purpose of each tool and the flow. However I don't understand why I am filling it in when the function comments kind of have the same thing. It was easy to copy and paste the context to AI.

**One divergence from your spec, and why:**
I wanted FitFindr to be more specific and unique with styling suggestions and creating fit cards. Before making this change I found the output kind of generic, since I was limiting to 1-2 sentences.

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
