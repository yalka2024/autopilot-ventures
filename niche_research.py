"""Enhanced niche research with web scraping capabilities."""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urljoin
import random

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import aiohttp

from config import config
from utils import budget_manager, generate_id, log, security_utils, RateLimiter, API_CALLS_COUNTER

# Configure logging
logger = logging.getLogger(__name__)


class NicheScraper:
    """Web scraper for global niche discovery."""

    def __init__(self):
        """Initialize niche scraper."""
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        # Rate limiting
        self.rate_limiter = RateLimiter()

        # Global search sources
        self.search_sources = {
            "google": {
                "url": "https://www.google.com/search",
                "params": {"q": "", "num": 10},
                "parser": self._parse_google_results,
            },
            "bing": {
                "url": "https://www.bing.com/search",
                "params": {"q": "", "count": 10},
                "parser": self._parse_bing_results,
            },
            "duckduckgo": {
                "url": "https://duckduckgo.com/html/",
                "params": {"q": ""},
                "parser": self._parse_duckduckgo_results,
            },
        }

        # Niche discovery sources
        self.niche_sources = {
            "exploding_topics": "https://explodingtopics.com/",
            "product_hunt": "https://www.producthunt.com/",
            "trending_on_github": "https://github.com/trending",
            "reddit_trending": "https://www.reddit.com/r/trending/",
            "twitter_trends": "https://twitter.com/explore/tabs/trending",
            "tiktok_trends": "https://www.tiktok.com/trending",
            "youtube_trending": "https://www.youtube.com/feed/trending",
        }

        # Global market sources
        self.global_sources = {
            "china_baidu": "https://www.baidu.com/s",
            "russia_yandex": "https://yandex.com/search/",
            "japan_yahoo": "https://search.yahoo.co.jp/search",
            "korea_naver": "https://search.naver.com/search.naver",
            "india_google": "https://www.google.co.in/search",
            "brazil_google": "https://www.google.com.br/search",
        }

    async def discover_global_niches(self, query: str, language: str = "en") -> List[Dict[str, Any]]:
        """Discover niches globally using multiple sources."""
        try:
            log.info(f"Starting global niche discovery for: {query}")

            # Check rate limits
            if not self.rate_limiter.check_rate_limit(f"discovery_{query}"):
                log.warning(f"Rate limit exceeded for query: {query}")
                return []

            niches = []

            # Search across multiple sources
            search_tasks = []

            # Standard search engines
            for source_name, source_config in self.search_sources.items():
                task = self._search_source(source_name, source_config, query, language)
                search_tasks.append(task)

            # Niche discovery platforms
            for source_name, source_url in self.niche_sources.items():
                task = self._scrape_niche_platform(source_name, source_url, query, language)
                search_tasks.append(task)

            # Global market sources (if language matches)
            if language in ["zh", "ru", "ja", "ko", "hi", "pt"]:
                for source_name, source_url in self.global_sources.items():
                    if self._matches_language(source_name, language):
                        task = self._search_global_market(source_name, source_url, query, language)
                        search_tasks.append(task)

            # Execute all searches concurrently
            results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, list):
                    niches.extend(result)
                elif isinstance(result, Exception):
                    log.error(f"Search failed: {result}")

            # Deduplicate and filter niches
            unique_niches = self._deduplicate_niches(niches)
            filtered_niches = self._filter_viable_niches(unique_niches)

            log.info(
                "Global niche discovery completed",
                query=query,
                total_found=len(niches),
                unique_niches=len(unique_niches),
                viable_niches=len(filtered_niches),
            )

            return filtered_niches

        except Exception as e:
            log.error(f"Global niche discovery failed: {e}")
            return []

    async def _search_source(
        self, source_name: str, source_config: Dict, query: str, language: str
    ) -> List[Dict[str, Any]]:
        """Search a specific source for niches."""
        try:
            # Rate limiting
            await asyncio.sleep(random.uniform(1, 3))

            # Prepare search parameters
            params = source_config["params"].copy()
            params["q"] = f"{query} emerging trends 2025"

            # Add language-specific parameters
            if language != "en":
                params["lr"] = f"lang_{language}"
                params["hl"] = language

            # Make request
            response = self.session.get(source_config["url"], params=params, timeout=10)

            if response.status_code == 200:
                # Parse results
                niches = source_config["parser"](response.text, query)

                # Update metrics
                API_CALLS_COUNTER.labels(api_type=source_name, status="success").inc()

                return niches
            else:
                log.warning(f"Search failed for {source_name}: {response.status_code}")
                API_CALLS_COUNTER.labels(api_type=source_name, status="error").inc()
                return []

        except Exception as e:
            log.error(f"Search failed for {source_name}: {e}")
            API_CALLS_COUNTER.labels(api_type=source_name, status="error").inc()
            return []

    async def _scrape_niche_platform(
        self, platform_name: str, platform_url: str, query: str, language: str
    ) -> List[Dict[str, Any]]:
        """Scrape niche discovery platforms."""
        try:
            # Rate limiting
            await asyncio.sleep(random.uniform(2, 5))

            # Make request
            response = self.session.get(platform_url, timeout=15)

            if response.status_code == 200:
                # Parse platform-specific content
                niches = self._parse_platform_content(platform_name, response.text, query)

                API_CALLS_COUNTER.labels(api_type=platform_name, status="success").inc()
                return niches
            else:
                log.warning(f"Platform scraping failed for {platform_name}: {response.status_code}")
                API_CALLS_COUNTER.labels(api_type=platform_name, status="error").inc()
                return []

        except Exception as e:
            log.error(f"Platform scraping failed for {platform_name}: {e}")
            API_CALLS_COUNTER.labels(api_type=platform_name, status="error").inc()
            return []

    async def _search_global_market(
        self, market_name: str, market_url: str, query: str, language: str
    ) -> List[Dict[str, Any]]:
        """Search global markets for local trends."""
        try:
            # Rate limiting
            await asyncio.sleep(random.uniform(3, 6))

            # Prepare localized query
            localized_query = self._localize_query(query, language)

            # Make request
            params = {"q": localized_query}
            response = self.session.get(market_url, params=params, timeout=15)

            if response.status_code == 200:
                # Parse global market results
                niches = self._parse_global_market_results(market_name, response.text, localized_query)

                API_CALLS_COUNTER.labels(api_type=market_name, status="success").inc()
                return niches
            else:
                log.warning(f"Global market search failed for {market_name}: {response.status_code}")
                API_CALLS_COUNTER.labels(api_type=market_name, status="error").inc()
                return []

        except Exception as e:
            log.error(f"Global market search failed for {market_name}: {e}")
            API_CALLS_COUNTER.labels(api_type=market_name, status="error").inc()
            return []

    def _parse_google_results(self, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse Google search results."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find search result containers
            results = soup.find_all("div", class_="g")

            for result in results:
                try:
                    # Extract title
                    title_elem = result.find("h3")
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    # Extract snippet
                    snippet_elem = result.find("div", class_="VwiC3b")
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                    # Extract URL
                    link_elem = result.find("a")
                    url = link_elem.get("href") if link_elem else ""

                    # Filter for niche-related content
                    if self._is_niche_related(title, snippet, query):
                        niches.append(
                            {
                                "title": title,
                                "snippet": snippet,
                                "url": url,
                                "source": "google",
                                "query": query,
                                "discovered_at": datetime.utcnow().isoformat(),
                                "relevance_score": self._calculate_relevance(title, snippet, query),
                            }
                        )

                except Exception as e:
                    log.debug(f"Failed to parse Google result: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse Google results: {e}")

        return niches

    def _parse_bing_results(self, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse Bing search results."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find search result containers
            results = soup.find_all("li", class_="b_algo")

            for result in results:
                try:
                    # Extract title
                    title_elem = result.find("h2")
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    # Extract snippet
                    snippet_elem = result.find("p")
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                    # Extract URL
                    link_elem = result.find("a")
                    url = link_elem.get("href") if link_elem else ""

                    # Filter for niche-related content
                    if self._is_niche_related(title, snippet, query):
                        niches.append(
                            {
                                "title": title,
                                "snippet": snippet,
                                "url": url,
                                "source": "bing",
                                "query": query,
                                "discovered_at": datetime.utcnow().isoformat(),
                                "relevance_score": self._calculate_relevance(title, snippet, query),
                            }
                        )

                except Exception as e:
                    log.debug(f"Failed to parse Bing result: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse Bing results: {e}")

        return niches

    def _parse_duckduckgo_results(self, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo search results."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find search result containers
            results = soup.find_all("div", class_="result")

            for result in results:
                try:
                    # Extract title
                    title_elem = result.find("a", class_="result__a")
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    # Extract snippet
                    snippet_elem = result.find("a", class_="result__snippet")
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                    # Extract URL
                    url = title_elem.get("href") if title_elem else ""

                    # Filter for niche-related content
                    if self._is_niche_related(title, snippet, query):
                        niches.append(
                            {
                                "title": title,
                                "snippet": snippet,
                                "url": url,
                                "source": "duckduckgo",
                                "query": query,
                                "discovered_at": datetime.utcnow().isoformat(),
                                "relevance_score": self._calculate_relevance(title, snippet, query),
                            }
                        )

                except Exception as e:
                    log.debug(f"Failed to parse DuckDuckGo result: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse DuckDuckGo results: {e}")

        return niches

    def _parse_platform_content(self, platform_name: str, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse content from niche discovery platforms."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            if platform_name == "exploding_topics":
                niches = self._parse_exploding_topics(soup, query)
            elif platform_name == "product_hunt":
                niches = self._parse_product_hunt(soup, query)
            elif platform_name == "trending_on_github":
                niches = self._parse_github_trending(soup, query)
            elif platform_name == "reddit_trending":
                niches = self._parse_reddit_trending(soup, query)
            # Add more platform parsers as needed

        except Exception as e:
            log.error(f"Failed to parse {platform_name} content: {e}")

        return niches

    def _parse_exploding_topics(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse Exploding Topics content."""
        niches = []
        try:
            # Find trending topics
            topic_elements = soup.find_all("div", class_="topic")

            for element in topic_elements:
                try:
                    title_elem = element.find("h3")
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    # Extract growth info
                    growth_elem = element.find("span", class_="growth")
                    growth = growth_elem.get_text().strip() if growth_elem else ""

                    niches.append(
                        {
                            "title": title,
                            "snippet": f"Trending topic with {growth} growth",
                            "url": "",
                            "source": "exploding_topics",
                            "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, growth, query),
                            "growth_metric": growth,
                        }
                    )

                except Exception as e:
                    log.debug(f"Failed to parse Exploding Topics item: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse Exploding Topics: {e}")

        return niches

    def _parse_product_hunt(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse Product Hunt content."""
        niches = []
        try:
            # Find product listings
            product_elements = soup.find_all("div", class_="item")

            for element in product_elements:
                try:
                    title_elem = element.find("h3")
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    # Extract description
                    desc_elem = element.find("p", class_="description")
                    description = desc_elem.get_text().strip() if desc_elem else ""

                    niches.append(
                        {
                            "title": title,
                            "snippet": description,
                            "url": "",
                            "source": "product_hunt",
                            "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, description, query),
                        }
                    )

                except Exception as e:
                    log.debug(f"Failed to parse Product Hunt item: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse Product Hunt: {e}")

        return niches

    def _parse_github_trending(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse GitHub trending content."""
        niches = []
        try:
            # Find trending repositories
            repo_elements = soup.find_all("article", class_="Box-row")

            for element in repo_elements:
                try:
                    title_elem = element.find("h2")
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    # Extract description
                    desc_elem = element.find("p")
                    description = desc_elem.get_text().strip() if desc_elem else ""

                    niches.append(
                        {
                            "title": title,
                            "snippet": description,
                            "url": "",
                            "source": "github_trending",
                            "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, description, query),
                        }
                    )

                except Exception as e:
                    log.debug(f"Failed to parse GitHub trending item: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse GitHub trending: {e}")

        return niches

    def _parse_reddit_trending(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse Reddit trending content."""
        niches = []
        try:
            # Find trending posts
            post_elements = soup.find_all("div", class_="Post")

            for element in post_elements:
                try:
                    title_elem = element.find("h3")
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    niches.append(
                        {
                            "title": title,
                            "snippet": "Trending on Reddit",
                            "url": "",
                            "source": "reddit_trending",
                            "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, "trending", query),
                        }
                    )

                except Exception as e:
                    log.debug(f"Failed to parse Reddit trending item: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse Reddit trending: {e}")

        return niches

    def _parse_global_market_results(self, market_name: str, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse global market search results."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Generic parsing for global markets
            # This would need to be customized for each market's specific HTML structure

            # Find common result containers
            results = soup.find_all(["div", "li"], class_=["result", "item", "listing"])

            for result in results:
                try:
                    # Extract title (try common selectors)
                    title_elem = result.find(["h3", "h2", "a"])
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()

                    # Extract snippet
                    snippet_elem = result.find(["p", "span", "div"])
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                    niches.append(
                        {
                            "title": title,
                            "snippet": snippet,
                            "url": "",
                            "source": market_name,
                            "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, snippet, query),
                        }
                    )

                except Exception as e:
                    log.debug(f"Failed to parse global market result: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to parse global market results: {e}")

        return niches

    def _is_niche_related(self, title: str, snippet: str, query: str) -> bool:
        """Check if content is related to niche discovery."""
        text = f"{title} {snippet}".lower()

        # Niche-related keywords
        niche_keywords = [
            "niche",
            "trend",
            "emerging",
            "opportunity",
            "market",
            "startup",
            "business",
            "entrepreneur",
            "passive income",
            "ecommerce",
            "saas",
            "digital product",
            "subscription",
            "monetization",
            "revenue",
            "profit",
            "growth",
        ]

        # Query-related keywords
        query_keywords = query.lower().split()

        # Check for niche keywords
        has_niche_keywords = any(keyword in text for keyword in niche_keywords)

        # Check for query keywords
        has_query_keywords = any(keyword in text for keyword in query_keywords)

        return has_niche_keywords or has_query_keywords

    def _calculate_relevance(self, title: str, snippet: str, query: str) -> float:
        """Calculate relevance score for niche."""
        text = f"{title} {snippet}".lower()
        query_lower = query.lower()

        # Simple relevance scoring
        score = 0.0

        # Title relevance (higher weight)
        title_words = title.lower().split()
        query_words = query_lower.split()

        title_matches = sum(1 for word in query_words if word in title_words)
        if title_words:
            score += (title_matches / len(title_words)) * 0.6

        # Snippet relevance
        snippet_words = snippet.lower().split()
        snippet_matches = sum(1 for word in query_words if word in snippet_words)
        if snippet_words:
            score += (snippet_matches / len(snippet_words)) * 0.4

        # Boost for trending keywords
        trending_keywords = ["2025", "trending", "emerging", "new", "hot", "viral"]
        for keyword in trending_keywords:
            if keyword in text:
                score += 0.1

        return min(score, 1.0)

    def _deduplicate_niches(self, niches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate niches based on title similarity."""
        unique_niches = []
        seen_titles = set()

        for niche in niches:
            title = niche["title"].lower()

            # Check for exact duplicates
            if title in seen_titles:
                continue

            # Check for similar titles (simple similarity check)
            is_duplicate = False
            for seen_title in seen_titles:
                if self._calculate_similarity(title, seen_title) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_niches.append(niche)
                seen_titles.add(title)

        return unique_niches

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _filter_viable_niches(self, niches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter niches for viability."""
        viable_niches = []

        for niche in niches:
            # Check relevance score
            if niche.get("relevance_score", 0) < 0.3:
                continue

            # Check for content safety
            combined_text = f"{niche['title']} {niche['snippet']}"
            safety_result = security_utils.check_content_safety(combined_text)

            if safety_result["toxicity"] > config.security.content_safety_threshold:
                continue

            # Check for business potential keywords
            business_keywords = [
                "business",
                "startup",
                "entrepreneur",
                "revenue",
                "profit",
                "market",
                "opportunity",
                "growth",
                "scaling",
                "monetization",
            ]

            has_business_potential = any(keyword in combined_text.lower() for keyword in business_keywords)

            if has_business_potential:
                viable_niches.append(niche)

        # Sort by relevance score
        viable_niches.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return viable_niches[:20]  # Return top 20

    def _localize_query(self, query: str, language: str) -> str:
        """Localize query for different languages."""
        # Simple localization - in production, use proper translation
        localizations = {
            "zh": f"{query} 2025年趋势",
            "ru": f"{query} тренды 2025",
            "ja": f"{query} 2025年トレンド",
            "ko": f"{query} 2025년 트렌드",
            "hi": f"{query} 2025 के रुझान",
            "pt": f"{query} tendências 2025",
        }

        return localizations.get(language, query)

    def _matches_language(self, source_name: str, language: str) -> bool:
        """Check if source matches language."""
        language_mapping = {
            "china_baidu": "zh",
            "russia_yandex": "ru",
            "japan_yahoo": "ja",
            "korea_naver": "ko",
            "india_google": "hi",
            "brazil_google": "pt",
        }

        return language_mapping.get(source_name) == language


# Global scraper instance
_niche_scraper = None


def get_niche_scraper() -> NicheScraper:
    """Get or create niche scraper instance."""
    global _niche_scraper
    if _niche_scraper is None:
        _niche_scraper = NicheScraper()
    return _niche_scraper


# Enhanced NicheResearchAgent integration
async def enhance_niche_research_agent(
    agent, niche: str, market_data: str = "", language: str = "en"
) -> Dict[str, Any]:
    """Enhanced niche research with web scraping."""
    try:
        # Get scraper instance
        scraper = get_niche_scraper()

        # Discover global niches
        discovered_niches = await scraper.discover_global_niches(niche, language)

        # Enhance market data with discovered niches
        enhanced_market_data = market_data + "\n\nDiscovered Niches:\n"
        for i, discovered_niche in enumerate(discovered_niches[:5], 1):
            enhanced_market_data += f"{i}. {discovered_niche['title']}\n"
            enhanced_market_data += f"   Source: {discovered_niche['source']}\n"
            enhanced_market_data += f"   Relevance: {discovered_niche.get('relevance_score', 0):.2f}\n\n"

        # Execute original agent with enhanced data
        result = await agent.execute(niche=niche, market_data=enhanced_market_data)

        # Add discovered niches to result
        if result.success:
            result.data["discovered_niches"] = discovered_niches
            result.data["scraping_sources"] = list(scraper.search_sources.keys())
            result.data["global_markets"] = list(scraper.global_sources.keys())

        return result

    except Exception as e:
        log.error(f"Enhanced niche research failed: {e}")
        # Fallback to original agent
        return await agent.execute(niche=niche, market_data=market_data)
