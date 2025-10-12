"""
Browser Helper Module
Provides browser utilities for autonomous web research using Playwright MCP
"""

import json
from typing import Optional, Dict, List, Any
from anthropic import Anthropic


class BrowserHelper:
    """Helper class for browser operations via MCP"""

    def __init__(self, client: Anthropic):
        """
        Initialize browser helper

        Args:
            client: Anthropic client with MCP enabled
        """
        self.client = client
        self.browser_available = True

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL using browser

        Args:
            url: URL to visit

        Returns:
            Result dictionary with page content
        """
        try:
            # This will be called via MCP tool use in the actual implementation
            return {
                "success": True,
                "url": url,
                "message": f"Navigated to {url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def search_web(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        Search the web for a query

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results with title, url, snippet
        """
        try:
            # This will be implemented via MCP tool use
            return []
        except Exception as e:
            return []

    async def extract_page_content(self, url: str, selector: Optional[str] = None) -> str:
        """
        Extract text content from a web page

        Args:
            url: URL to extract from
            selector: Optional CSS selector to target specific content

        Returns:
            Extracted text content
        """
        try:
            # This will be implemented via MCP tool use
            return ""
        except Exception as e:
            return f"Error extracting content: {str(e)}"

    async def take_screenshot(self, url: str) -> Optional[bytes]:
        """
        Take a screenshot of a web page

        Args:
            url: URL to screenshot

        Returns:
            Screenshot bytes or None if failed
        """
        try:
            # This will be implemented via MCP tool use
            return None
        except Exception as e:
            return None

    def format_search_results(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results as readable text

        Args:
            results: List of search result dictionaries

        Returns:
            Formatted text
        """
        if not results:
            return "No results found."

        formatted = ["Search Results:\n"]
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.get('title', 'No title')}")
            formatted.append(f"   URL: {result.get('url', '')}")
            if result.get('snippet'):
                formatted.append(f"   {result.get('snippet')}")
            formatted.append("")

        return "\n".join(formatted)


class ResearchHelper:
    """Helper for autonomous research operations"""

    def __init__(self, browser_helper: BrowserHelper):
        """
        Initialize research helper

        Args:
            browser_helper: BrowserHelper instance
        """
        self.browser = browser_helper

    async def research_topic(self, topic: str, context: str = "") -> Dict[str, Any]:
        """
        Research a topic autonomously

        Args:
            topic: Topic to research
            context: Additional context for the research

        Returns:
            Research findings dictionary
        """
        findings = {
            "topic": topic,
            "context": context,
            "sources": [],
            "summary": "",
            "key_points": []
        }

        try:
            # Search for the topic
            search_query = f"{topic} {context}".strip()
            results = await self.browser.search_web(search_query, num_results=5)

            findings["sources"] = results

            # Extract content from top results
            for result in results[:3]:
                url = result.get("url")
                if url:
                    content = await self.browser.extract_page_content(url)
                    if content:
                        findings["key_points"].append({
                            "source": result.get("title"),
                            "url": url,
                            "content_snippet": content[:500]  # First 500 chars
                        })

            return findings

        except Exception as e:
            findings["error"] = str(e)
            return findings

    async def find_examples(self, feature_type: str, domain: str = "") -> List[str]:
        """
        Find example user stories or implementations for a feature type

        Args:
            feature_type: Type of feature (e.g., "shopping cart", "login")
            domain: Domain context (e.g., "e-commerce", "healthcare")

        Returns:
            List of example descriptions
        """
        examples = []

        try:
            # Search for examples
            query = f"{feature_type} user story examples"
            if domain:
                query += f" {domain}"

            results = await self.browser.search_web(query, num_results=5)

            for result in results:
                url = result.get("url")
                if url:
                    content = await self.browser.extract_page_content(url)
                    if content and len(content) > 100:
                        examples.append({
                            "source": result.get("title"),
                            "url": url,
                            "example": content[:1000]  # First 1000 chars
                        })

            return examples

        except Exception as e:
            return []

    async def lookup_standard(self, standard_name: str) -> Dict[str, Any]:
        """
        Look up a technical or industry standard

        Args:
            standard_name: Name of standard (e.g., "WCAG 2.1", "GDPR")

        Returns:
            Standard information dictionary
        """
        standard_info = {
            "name": standard_name,
            "description": "",
            "key_requirements": [],
            "sources": []
        }

        try:
            # Search for the standard
            query = f"{standard_name} requirements specifications"
            results = await self.browser.search_web(query, num_results=3)

            standard_info["sources"] = results

            # Extract requirements from first result
            if results:
                url = results[0].get("url")
                if url:
                    content = await self.browser.extract_page_content(url)
                    if content:
                        standard_info["description"] = content[:500]

            return standard_info

        except Exception as e:
            standard_info["error"] = str(e)
            return standard_info


def create_research_prompt(notes: str, browser_instructions: str = "") -> str:
    """
    Create a prompt for the agent to perform research

    Args:
        notes: Meeting notes or requirements
        browser_instructions: Optional specific instructions for browsing

    Returns:
        Research prompt string
    """
    if browser_instructions:
        return f"""Before generating user stories, perform the following research:

{browser_instructions}

Then use the research findings along with these notes to generate comprehensive user stories:

{notes}
"""
    else:
        return f"""Analyze these notes and identify topics that would benefit from research.
Use the browser tools to search for:
1. Best practices for the features mentioned
2. Industry standards relevant to the domain
3. Example user stories for similar features

Notes to analyze:
{notes}

After gathering research context, generate comprehensive user stories.
"""
