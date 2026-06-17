"""
tests/test_tools.py

Pytest tests for all three FitFindr tools.
LLM-backed tools (suggest_outfit, create_fit_card) are tested with mocks
so they run offline without a GROQ_API_KEY.
"""

from unittest.mock import MagicMock, patch

import pytest

from tools import create_fit_card, search_listings, suggest_outfit
from utils.data_loader import get_example_wardrobe, load_listings


# ── Helpers ────────────────────────────────────────────────────────────────────

def _mock_groq(text: str):
    """Return a patched Groq client whose .chat.completions.create() returns text."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices[0].message.content = text
    return mock_client


SAMPLE_ITEM = load_listings()[0]
SAMPLE_WARDROBE = get_example_wardrobe()
EMPTY_WARDROBE = {"items": []}


# ── Tool 1: search_listings ────────────────────────────────────────────────────

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    # Nonsense query + extreme constraints → empty list, no exception
    results = search_listings("xyznotaword", size="XXS", max_price=1)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    # All prices in dataset are >= 12, so this should return nothing
    assert results == []


def test_search_price_inclusive():
    # Price of 38.0 exists (lst_001); max_price=38 should include it
    results = search_listings("vintage jeans", max_price=38)
    assert all(item["price"] <= 38 for item in results)


def test_search_size_filter_case_insensitive():
    # "m" lowercase should match listings sized "M" or "S/M"
    results = search_listings("top", size="m", max_price=None)
    for item in results:
        assert "m" in item["size"].lower()


def test_search_size_no_match():
    # No listings are size "XXXL"
    results = search_listings("shirt", size="XXXL", max_price=None)
    assert results == []


def test_search_sorted_by_relevance():
    # First result should score at least as high as the last
    results = search_listings("vintage denim streetwear")
    assert len(results) >= 2
    # All results should have at least one keyword hit (score > 0)
    keywords = {"vintage", "denim", "streetwear"}
    for item in results:
        text = " ".join([
            item["title"], item["description"], item["category"],
            " ".join(item["style_tags"]), " ".join(item["colors"]),
            item.get("brand") or "",
        ]).lower()
        assert any(kw in text for kw in keywords)


def test_search_no_filters():
    # With no filters, any keyword match returns results
    results = search_listings("blue")
    assert len(results) > 0


# ── Tool 2: suggest_outfit ─────────────────────────────────────────────────────

@patch("tools._get_groq_client")
def test_suggest_outfit_with_wardrobe(mock_get_client):
    mock_get_client.return_value = _mock_groq("Pair with your dark jeans and white sneakers.")
    result = suggest_outfit(SAMPLE_ITEM, SAMPLE_WARDROBE)
    assert isinstance(result, str)
    assert len(result) > 0


def test_suggest_outfit_empty_wardrobe_returns_empty_string():
    # Empty wardrobe → empty string (signals failure to caller), no LLM call
    result = suggest_outfit(SAMPLE_ITEM, EMPTY_WARDROBE)
    assert result == ""


@patch("tools._get_groq_client")
def test_suggest_outfit_calls_llm(mock_get_client):
    mock_client = _mock_groq("Some outfit suggestion.")
    mock_get_client.return_value = mock_client
    suggest_outfit(SAMPLE_ITEM, SAMPLE_WARDROBE)
    assert mock_client.chat.completions.create.called


@patch("tools._get_groq_client")
def test_suggest_outfit_empty_wardrobe_does_not_call_llm(mock_get_client):
    # LLM should never be reached when wardrobe is empty
    mock_client = _mock_groq("Should not be called.")
    mock_get_client.return_value = mock_client
    suggest_outfit(SAMPLE_ITEM, EMPTY_WARDROBE)
    mock_client.chat.completions.create.assert_not_called()


# ── Tool 3: create_fit_card ────────────────────────────────────────────────────

@patch("tools._get_groq_client")
def test_create_fit_card_returns_caption(mock_get_client):
    mock_get_client.return_value = _mock_groq("Thrifted this gem on Depop for $38 and I'm obsessed.")
    result = create_fit_card("Pair with dark jeans and white sneakers.", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert len(result) > 0


def test_create_fit_card_empty_outfit_string():
    # Empty outfit → error message string, no exception
    result = create_fit_card("", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "no outfit" in result.lower() or "cannot" in result.lower()


def test_create_fit_card_whitespace_outfit():
    # Whitespace-only outfit treated as empty
    result = create_fit_card("   ", SAMPLE_ITEM)
    assert "no outfit" in result.lower() or "cannot" in result.lower()


@patch("tools._get_groq_client")
def test_create_fit_card_calls_llm(mock_get_client):
    mock_client = _mock_groq("Caption text here.")
    mock_get_client.return_value = mock_client
    create_fit_card("Some outfit description.", SAMPLE_ITEM)
    assert mock_client.chat.completions.create.called


@patch("tools._get_groq_client")
def test_create_fit_card_prompt_includes_item_details(mock_get_client):
    mock_client = _mock_groq("Caption.")
    mock_get_client.return_value = mock_client

    create_fit_card("Some outfit.", SAMPLE_ITEM)

    call_args = mock_client.chat.completions.create.call_args
    prompt = call_args.kwargs["messages"][0]["content"]
    assert str(SAMPLE_ITEM["price"]) in prompt
    assert SAMPLE_ITEM["platform"] in prompt
