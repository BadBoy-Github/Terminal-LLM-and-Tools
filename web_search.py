"""Web Search tool module for Day 2 agent.

Allows the AI chatbot to perform live web searches for current information,
news, recent events, and real-time facts using DuckDuckGo.
"""

from typing import Any, Dict, List

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def search_web(query: str = "", max_results: int = 3, **kwargs: Any) -> str:
    """Search the web for up-to-date information on a given topic.

    Args:
        query: The search query terms to find on the web.
        max_results: The maximum number of search results to return (default: 3).
        **kwargs: Additional arguments, handles aliases like 'q' or 'search_query'.

    Returns:
        A formatted string containing titles, snippets, and source URLs.
    """
    target_query = query or kwargs.get("q") or kwargs.get("search_query") or kwargs.get("keywords") or ""
    clean_query = str(target_query).strip()
    if not clean_query:
        return "Error: Empty search query provided."

    try:
        ddgs = DDGS()
        raw_results = list(ddgs.text(clean_query, max_results=max_results))

        if not raw_results:
            return f"No search results found for query: '{clean_query}'."

        formatted_snippets: List[str] = []
        for index, item in enumerate(raw_results, start=1):
            title = item.get("title", "Untitled").strip()
            body = item.get("body", "").strip()
            link = item.get("href", "").strip()
            snippet = f"[{index}] {title}\nSummary: {body}\nSource: {link}"
            formatted_snippets.append(snippet)

        return "\n\n".join(formatted_snippets)

    except Exception as exc:
        return f"Error executing web search for '{clean_query}': {exc}"


# Tool definition compatible with OpenAI / Hugging Face Chat Completions API
WEB_SEARCH_TOOL: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the live web for up-to-date information, current news, "
            "recent events, real-time facts, weather, and current data. "
            "Use this tool whenever the user asks about current info or facts "
            "that require real-time or external verification."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query keywords to look up on the web.",
                },
            },
            "required": ["query"],
        },
    },
}


if __name__ == "__main__":
    print("=== Web Search Tool Self-Test ===")
    test_query = "latest Python release"
    print(f"Searching for: '{test_query}'...\n")
    output = search_web(test_query, max_results=2)
    print(output)
