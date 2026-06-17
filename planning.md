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
A user inputs a description of what they are looking for, which is usually clothing or an outfit. They may include the style, price range, and size of the clothes they are looking for. Then the tool goes through listings.json and returns 3 matching listings sorted by relevance. FitFindr picks the top result

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): may describe the style, vibe, and item of clothing the user is trying to find
- `size` (str): specifies the size that user would like the clothing to be. could be multiple dimensions. try to get exact sizes
- `max_price` (float): how much user is willing to pay. try not to choose clothing that is above this price

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
FitFindr picks the top result in listings.json according to what the user inputed

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
If search_listings returns nothing, FitFindr tells the user what to try differently and stops — it does not call suggest_outfit with empty input. After search_listings runs, check if results is empty. If yes, set an error message in the session and return early. If no, set selected_item = results[0] and proceed to suggest_outfit

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Describes an outfit and styling that would go with the listing outputed from search_listings such as - suggest_outfit(new_item=<band tee>, wardrobe=<user's wardrobe>) returns: "Pair this with your wide-leg jeans and platform Docs for a classic 90s grunge look. Roll the sleeves once and tuck the front corner slightly for shape."

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): the listing in listings.json chosen from search_listings.
- `wardrobe` (dict): a list of clothing from user's wardrobe. use items from here to pair with new_item

**What it returns:**
<!-- Describe the return value -->
A short description of an outfit and styling suggestion that would go well with the selected listing

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
The agent should tell the user that there are no clothes to pair in the wardrobe. Return early and don't go to create_fit_card.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Generate 1-2 sentence caption featuring the new item and outfit. make it unique to item and outfit

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): generated from suggest_outfit
- `new_item` (dict): the listing in listings.json chosen from search_listings.

**What it returns:**
<!-- Describe the return value -->
A string - caption featuring the new item and outfit. make it unique to item and outfit

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
say something like "no outfit generated, cannot create fit card"

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
Call search_listings using the user's description, size, and max price.
If no listings are returned, stop and show an error message with suggestions for refining the search.
If listings are found, select the top result and call suggest_outfit with the selected item and the user's wardrobe.
If no outfit can be generated, stop and inform the user that there are no suitable wardrobe items to pair with the listing.
If an outfit is generated, call create_fit_card using the outfit and selected item.
Return the fit card caption and end the workflow.

The agent knows it is done after create_fit_card successfully returns a caption or after any tool returns a stopping condition.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
The agent stores intermediate results in session state. After search_listings runs, the top result is saved as selected_item. selected_item is then passed to suggest_outfit as new_item along with the user's wardrobe. The generated outfit is saved as outfit and passed to create_fit_card together with selected_item. The agent also tracks any error messages so it can stop the workflow early if a tool returns no results.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query |Inform the user that no matching listings were found and suggest adjusting the description, size, or price range. Stop the workflow and do not call suggest_outfit.|
| suggest_outfit | Wardrobe is empty |Inform the user that there are no wardrobe items available to create an outfit. Stop the workflow and do not call create_fit_card. |
| create_fit_card | Outfit input is missing or incomplete |Return an error message such as "No outfit generated, cannot create fit card." Stop the workflow and do not generate a caption. |

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

```
flowchart TD

    U[User Query<br/>description, size, max_price, wardrobe]
    P[Planning Loop]

    U --> P

    P -->|description, size, max_price| S[search_listings]

    S -->|No matches| E1[ERROR<br/>No listings found]
    E1 --> X[Return Error Message]

    S -->|results[0]| ST1[(Session State)]
    ST1 -->|selected_item| O[suggest_outfit]

    P -->|wardrobe| O

    O -->|Wardrobe empty| E2[ERROR<br/>Cannot generate outfit]
    E2 --> X

    O -->|outfit_suggestion| ST1

    ST1 -->|selected_item + outfit_suggestion| C[create_fit_card]

    C -->|Missing outfit data| E3[ERROR<br/>Cannot create fit card]
    E3 --> X

    C -->|fit_card| ST1

    ST1 --> R[Return Result]

    R --> F[Selected Listing<br/>Outfit Suggestion<br/>Fit Card Caption]
```

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

**Milestone 3 — Individual tool implementations:**
I will use Claude to implement each tool separately. For `search_listings`, I will provide the Tool 1 specification from planning.md, including inputs, return value, and failure mode, and ask it to generate a function that searches listings.json and returns the most relevant results. For `suggest_outfit`, I will provide the Tool 2 specification and ask it to generate outfit recommendations using the selected item and wardrobe. For `create_fit_card`, I will provide the Tool 3 specification and ask it to generate a short caption based on the outfit and selected item.

I expect Claude to produce working Python functions that match the tool specifications. Before using the code, I will verify that each function accepts the correct inputs, returns the expected outputs, and handles the documented failure cases. I will test each tool independently with sample inputs and edge cases.


**Milestone 4 — Planning loop and state management:**
I will use Claude to implement the planning loop. I will provide the Architecture diagram, tool specifications, state management description, and error-handling table from planning.md. I will ask it to generate a planning loop that calls the tools in the correct order, stores intermediate results in session state, and stops when a tool returns an error condition.

I expect Claude to produce code that follows the workflow defined in the architecture diagram. Before using the code, I will verify that `selected_item`, `outfit_suggestion`, and `fit_card` are stored and passed correctly between tools. I will test both successful and failure scenarios to confirm that the workflow terminates early when required and returns the expected results.

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The planning loop extracts:
- description = "vintage graphic tee"
- max_price = 30
- wardrobe = ["baggy jeans", "chunky sneakers"]

The agent calls:

search_listings(
    description="vintage graphic tee",
    size=None,
    max_price=30
)

Tool returns:

[
  {
    "title": "Vintage Band Tee",
    "price": 25,
    "size": "M"
  },
  {
    "title": "Retro Graphic Tee",
    "price": 28,
    "size": "M"
  }
]

The agent stores:

selected_item = results[0]

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
The agent calls:

suggest_outfit(
    new_item=selected_item,
    wardrobe=["baggy jeans", "chunky sneakers"]
)

Tool returns:

"Pair the vintage band tee with your baggy jeans and chunky sneakers for a relaxed streetwear look. Tuck in the front of the shirt slightly and add a chain necklace for extra style."

The agent stores:

outfit_suggestion = returned outfit


**Step 3:**
<!-- Continue until the full interaction is complete -->
The agent calls:

create_fit_card(
    outfit=outfit_suggestion,
    new_item=selected_item
)

Tool returns:

"Throwback vibes with this vintage band tee. Paired with baggy jeans and chunky sneakers, it's an effortless everyday streetwear fit."

The agent stores:

fit_card = returned caption

**Final output to user:**
<!-- What does the user actually see at the end? -->
- Vintage Band Tee
- Price: $25
- Size: M

Outfit Suggestion - Pair the vintage band tee with your baggy jeans and chunky sneakers for a relaxed streetwear look. Tuck in the front of the shirt slightly and add a chain necklace for extra style.
Fit Card - Throwback vibes with this vintage band tee. Paired with baggy jeans and chunky sneakers, it's an effortless everyday streetwear fit.
