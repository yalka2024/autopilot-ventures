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
from functools import lru_cache

from config import config
from utils import budget_manager, generate_id, log, security_utils, RateLimiter, API_CALLS_COUNTER

# Configure logging
logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter implementation."""
    def __init__(self, max_calls: int = 100, period: timedelta = timedelta(hours=1)):
        self.max_calls = max_calls
        self.period = period.total_seconds()
        self.call_times = []

    def check_rate_limit(self, key: str) -> bool:
        """Check if rate limit is exceeded for a given key."""
        now = time.time()
        self.call_times = [t for t in self.call_times if now - t < self.period]
        return len(self.call_times) < self.max_calls

    def record_call(self, key: str):
        """Record a new API call."""
        self.call_times.append(time.time())
        self.call_times = [t for t in self.call_times if time.time() - t < self.period]

class NicheScraper:
    """Web scraper for global niche discovery."""

    def __init__(self):
        """Initialize niche scraper with global rate limiting."""
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
        self.global_limiter = RateLimiter(max_calls=100, period=timedelta(hours=1))  # Global limit
        self.rate_limiter = RateLimiter(max_calls=10, period=timedelta(minutes=1))  # Per-source limit

        # Search sources
        self.search_sources = {
            "google": {"url": "https://www.google.com/search", "params": {"q": "", "num": 10}, "parser": self._parse_google_results},
            "bing": {"url": "https://www.bing.com/search", "params": {"q": "", "count": 10}, "parser": self._parse_bing_results},
            "duckduckgo": {"url": "https://duckduckgo.com/html/", "params": {"q": ""}, "parser": self._parse_duckduckgo_results},
        }

        # Niche discovery platforms
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
        """Discover niches globally using multiple sources with caching and retries."""
        try:
            log.info(f"Starting global niche discovery for: {query}")

            # Global rate limit check
            if not self.global_limiter.check_rate_limit(f"global_{query}"):
                log.warning(f"Global rate limit exceeded for query: {query}")
                return []

            niches = []

            # Concurrent searches
            search_tasks = []

            # Standard search engines
            for source_name, source_config in self.search_sources.items():
                task = self._search_source(source_name, source_config, query, language)
                search_tasks.append(task)

            # Niche discovery platforms
            for source_name, source_url in self.niche_sources.items():
                task = self._scrape_niche_platform(source_name, source_url, query, language)
                search_tasks.append(task)

            # Global market sources
            if language in ["zh", "ru", "ja", "ko", "hi", "pt"]:
                for source_name, source_url in self.global_sources.items():
                    if self._matches_language(source_name, language):
                        task = self._search_global_market(source_name, source_url, query, language)
                        search_tasks.append(task)

            # Execute with retries
            results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, list):
                    niches.extend(result)
                elif isinstance(result, Exception):
                    log.error(f"Search failed: {result}")

            # Deduplicate and filter
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

    @lru_cache(maxsize=100)
    async def _cached_search(self, source_name: str, query: str, language: str) -> List[Dict[str, Any]]:
        """Cached search for a specific source."""
        source_config = self.search_sources.get(source_name)
        if not source_config:
            return []
        return await self._search_source(source_name, source_config, query, language)

    async def _search_source(self, source_name: str, source_config: Dict, query: str, language: str) -> List[Dict[str, Any]]:
        """Search a specific source with retries."""
        for attempt in range(3):
            try:
                if not self.rate_limiter.check_rate_limit(f"{source_name}_{query}"):
                    log.warning(f"Rate limit exceeded for {source_name}")
                    return []

                await asyncio.sleep(random.uniform(1, 3))

                params = source_config["params"].copy()
                params["q"] = f"{query} emerging trends 2025"

                if language != "en":
                    params["lr"] = f"lang_{language}"
                    params["hl"] = language

                response = self.session.get(source_config["url"], params=params, timeout=10)
                if response.status_code == 200:
                    API_CALLS_COUNTER.labels(api_type=source_name, status="success").inc()
                    return source_config["parser"](response.text, query)
                log.warning(f"Attempt {attempt+1} failed for {source_name}: {response.status_code}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                log.error(f"Attempt {attempt+1} failed for {source_name}: {e}")
                await asyncio.sleep(2 ** attempt)
        API_CALLS_COUNTER.labels(api_type=source_name, status="error").inc()
        return []

    async def _scrape_niche_platform(self, platform_name: str, platform_url: str, query: str, language: str) -> List[Dict[str, Any]]:
        """Scrape niche discovery platforms with retries."""
        for attempt in range(3):
            try:
                if not self.rate_limiter.check_rate_limit(f"{platform_name}_{query}"):
                    log.warning(f"Rate limit exceeded for {platform_name}")
                    return []

                await asyncio.sleep(random.uniform(2, 5))

                response = self.session.get(platform_url, timeout=15)
                if response.status_code == 200:
                    API_CALLS_COUNTER.labels(api_type=platform_name, status="success").inc()
                    return self._parse_platform_content(platform_name, response.text, query)
                log.warning(f"Attempt {attempt+1} failed for {platform_name}: {response.status_code}")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                log.error(f"Attempt {attempt+1} failed for {platform_name}: {e}")
                await asyncio.sleep(2 ** attempt)
        API_CALLS_COUNTER.labels(api_type=platform_name, status="error").inc()
        return []

    async def _search_global_market(self, market_name: str, market_url: str, query: str, language: str) -> List[Dict[str, Any]]:
        """Search global markets with retries."""
        for attempt in range(3):
            try:
                if not self.rate_limiter.check_rate_limit(f"{market_name}_{query}"):
                    log.warning(f"Rate limit exceeded for {market_name}")
                    return []

                await asyncio.sleep(random.uniform(3, 6))

                localized_query = self._localize_query(query, language)
                params = {"q": localized_query}
                response = self.session.get(market_url, params=params, timeout=15)
                if response.status_code == 200:
                    API_CALLS_COUNTER.labels(api_type=market_name, status="success").inc()
                    return self._parse_global_market_results(market_name, response.text, localized_query)
                log.warning(f"Attempt {attempt+1} failed for {market_name}: {response.status_code}")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                log.error(f"Attempt {attempt+1} failed for {market_name}: {e}")
                await asyncio.sleep(2 ** attempt)
        API_CALLS_COUNTER.labels(api_type=market_name, status="error").inc()
        return []

    def _parse_google_results(self, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse Google search results with robust error handling."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            results = soup.find_all("div", class_="g")
            for result in results:
                try:
                    title_elem = result.find("h3")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    snippet_elem = result.find("div", class_="VwiC3b")
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    link_elem = result.find("a")
                    url = link_elem.get("href") if link_elem else ""
                    if self._is_niche_related(title, snippet, query):
                        niches.append({
                            "title": title, "snippet": snippet, "url": url, "source": "google",
                            "query": query, "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, snippet, query)
                        })
                except Exception as e:
                    log.debug(f"Failed to parse Google result: {e}")
        except Exception as e:
            log.error(f"Failed to parse Google results: {e}")
        return niches

    def _parse_bing_results(self, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse Bing search results with robust error handling."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            results = soup.find_all("li", class_="b_algo")
            for result in results:
                try:
                    title_elem = result.find("h2")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    snippet_elem = result.find("p")
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    link_elem = result.find("a")
                    url = link_elem.get("href") if link_elem else ""
                    if self._is_niche_related(title, snippet, query):
                        niches.append({
                            "title": title, "snippet": snippet, "url": url, "source": "bing",
                            "query": query, "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, snippet, query)
                        })
                except Exception as e:
                    log.debug(f"Failed to parse Bing result: {e}")
        except Exception as e:
            log.error(f"Failed to parse Bing results: {e}")
        return niches

    def _parse_duckduckgo_results(self, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo search results with robust error handling."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            results = soup.find_all("div", class_="result")
            for result in results:
                try:
                    title_elem = result.find("a", class_="result__a")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    snippet_elem = result.find("a", class_="result__snippet")
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    url = title_elem.get("href") if title_elem else ""
                    if self._is_niche_related(title, snippet, query):
                        niches.append({
                            "title": title, "snippet": snippet, "url": url, "source": "duckduckgo",
                            "query": query, "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, snippet, query)
                        })
                except Exception as e:
                    log.debug(f"Failed to parse DuckDuckGo result: {e}")
        except Exception as e:
            log.error(f"Failed to parse DuckDuckGo results: {e}")
        return niches

    def _parse_platform_content(self, platform_name: str, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse content from niche discovery platforms with specific handlers."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            if platform_name == "exploding_topics":
                return self._parse_exploding_topics(soup, query)
            elif platform_name == "product_hunt":
                return self._parse_product_hunt(soup, query)
            elif platform_name == "trending_on_github":
                return self._parse_github_trending(soup, query)
            elif platform_name == "reddit_trending":
                return self._parse_reddit_trending(soup, query)
            return []
        except Exception as e:
            log.error(f"Failed to parse {platform_name} content: {e}")
            return []

    def _parse_exploding_topics(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse Exploding Topics content with robust extraction."""
        niches = []
        try:
            topic_elements = soup.find_all("div", class_="topic")
            for element in topic_elements:
                try:
                    title_elem = element.find("h3")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    growth_elem = element.find("span", class_="growth")
                    growth = growth_elem.get_text().strip() if growth_elem else ""
                    if self._is_niche_related(title, growth, query):
                        niches.append({
                            "title": title, "snippet": f"Trending with {growth} growth",
                            "url": "", "source": "exploding_topics", "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, growth, query),
                            "growth_metric": growth
                        })
                except Exception as e:
                    log.debug(f"Failed to parse Exploding Topics item: {e}")
        except Exception as e:
            log.error(f"Failed to parse Exploding Topics: {e}")
        return niches

    def _parse_product_hunt(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse Product Hunt content with robust extraction."""
        niches = []
        try:
            product_elements = soup.find_all("div", class_="item")
            for element in product_elements:
                try:
                    title_elem = element.find("h3")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    desc_elem = element.find("p", class_="description")
                    description = desc_elem.get_text().strip() if desc_elem else ""
                    if self._is_niche_related(title, description, query):
                        niches.append({
                            "title": title, "snippet": description, "url": "",
                            "source": "product_hunt", "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, description, query)
                        })
                except Exception as e:
                    log.debug(f"Failed to parse Product Hunt item: {e}")
        except Exception as e:
            log.error(f"Failed to parse Product Hunt: {e}")
        return niches

    def _parse_github_trending(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse GitHub trending content with robust extraction."""
        niches = []
        try:
            repo_elements = soup.find_all("article", class_="Box-row")
            for element in repo_elements:
                try:
                    title_elem = element.find("h2")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    desc_elem = element.find("p")
                    description = desc_elem.get_text().strip() if desc_elem else ""
                    if self._is_niche_related(title, description, query):
                        niches.append({
                            "title": title, "snippet": description, "url": "",
                            "source": "trending_on_github", "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, description, query)
                        })
                except Exception as e:
                    log.debug(f"Failed to parse GitHub trending item: {e}")
        except Exception as e:
            log.error(f"Failed to parse GitHub trending: {e}")
        return niches

    def _parse_reddit_trending(self, soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
        """Parse Reddit trending content with robust extraction."""
        niches = []
        try:
            post_elements = soup.find_all("div", class_="Post")
            for element in post_elements:
                try:
                    title_elem = element.find("h3")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    if self._is_niche_related(title, "trending", query):
                        niches.append({
                            "title": title, "snippet": "Trending on Reddit", "url": "",
                            "source": "reddit_trending", "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, "trending", query)
                        })
                except Exception as e:
                    log.debug(f"Failed to parse Reddit trending item: {e}")
        except Exception as e:
            log.error(f"Failed to parse Reddit trending: {e}")
        return niches

    def _parse_global_market_results(self, market_name: str, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse global market search results with market-specific logic."""
        niches = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            if market_name == "china_baidu":
                results = soup.find_all("div", class_="c-container")
            elif market_name == "russia_yandex":
                results = soup.find_all("li", class_="serp-item")
            elif market_name == "japan_yahoo":
                results = soup.find_all("div", class_="sw-Contents")
            elif market_name == "korea_naver":
                results = soup.find_all("li", class_="section_item")
            elif market_name in ["india_google", "brazil_google"]:
                results = soup.find_all("div", class_="g")
            else:
                results = soup.find_all(["div", "li"], class_=["result", "item"])
            for result in results:
                try:
                    title_elem = result.find(["h3", "a"])
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    snippet_elem = result.find(["p", "span"])
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    if self._is_niche_related(title, snippet, query):
                        niches.append({
                            "title": title, "snippet": snippet, "url": "",
                            "source": market_name, "query": query,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "relevance_score": self._calculate_relevance(title, snippet, query)
                        })
                except Exception as e:
                    log.debug(f"Failed to parse {market_name} result: {e}")
        except Exception as e:
            log.error(f"Failed to parse {market_name} results: {e}")
        return niches

    def _is_niche_related(self, title: str, snippet: str, query: str) -> bool:
        """Check if content is related to niche discovery."""
        text = f"{title} {snippet}".lower()
        niche_keywords = [
            "niche", "trend", "emerging", "opportunity", "market", "startup",
            "business", "entrepreneur", "passive income", "ecommerce", "saas",
            "digital product", "subscription", "monetization", "revenue", "profit",
            "growth",
        ]
        query_keywords = query.lower().split()
        return any(keyword in text for keyword in niche_keywords + query_keywords)

    def _calculate_relevance(self, title: str, snippet: str, query: str) -> float:
        """Calculate relevance score for niche."""
        text = f"{title} {snippet}".lower()
        query_lower = query.lower()
        score = 0.0
        title_words = title.lower().split()
        query_words = query_lower.split()
        title_matches = sum(1 for word in query_words if word in title_words)
        if title_words:
            score += (title_matches / len(title_words)) * 0.6
        snippet_words = snippet.lower().split()
        snippet_matches = sum(1 for word in query_words if word in snippet_words)
        if snippet_words:
            score += (snippet_matches / len(snippet_words)) * 0.4
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
        """Filter niches for viability with market size proxy."""
        viable_niches = []
        for niche in niches:
            if niche.get("relevance_score", 0) < 0.3:
                continue
            combined_text = f"{niche['title']} {niche['snippet']}"
            safety_result = security_utils.check_content_safety(combined_text)
            if safety_result["toxicity"] > config.security.content_safety_threshold:
                continue
            business_keywords = [
                "business", "startup", "entrepreneur", "revenue", "profit",
                "market", "opportunity", "growth", "scaling", "monetization",
            ]
            has_business_potential = any(keyword in combined_text.lower() for keyword in business_keywords)
            if has_business_potential:
                # Proxy for market size: Boost if "global" or high-growth term
                market_size_boost = 0.1 if any(k in combined_text.lower() for k in ["global", "growth", "trending"]) else 0
                niche["relevance_score"] += market_size_boost
                viable_niches.append(niche)
        viable_niches.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return viable_niches[:20]

    def _localize_query(self, query: str, language: str) -> str:
        """Localize query for different languages."""
        localizations = {
            "zh": f"{query} 2025年趋势",
            "ru": f"{quote_plus(query)} тренды 2025",
            "ja": f"{query} 2025年トレンド",
            "ko": f"{query} 2025년 트렌드",
            "hi": f"{query} 2025 के रुझान",
            "pt": f"{quote_plus(query)} tendências 2025",
        }
        return localizations.get(language, quote_plus(query))

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

    # Optional SerpApi Integration (Uncomment and configure if using)
    # import os
    # from dotenv import load_dotenv
    # load_dotenv()
    # api_key = os.getenv('SERPAPI_KEY')
    #
    # async def scrape_niches(self, query: str, language: str = "en") -> List[Dict[str, Any]]:
    #     url = f"https://serpapi.com/search?q={quote_plus(query)}&api_key={api_key}&hl={language}"
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url) as response:
    #             if response.status == 200:
    #                 data = await response.json()
    #                 return [{"title": r["title"], "snippet": r.get("snippet", ""), "url": r.get("link", ""),
    #                          "source": "serpapi", "query": query, "discovered_at": datetime.utcnow().isoformat(),
    #                          "relevance_score": 0.5} for r in data.get("organic_results", [])]
    #             return []

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
        scraper = get_niche_scraper()
        discovered_niches = await scraper.discover_global_niches(niche, language)
        enhanced_market_data = market_data + "\n\nDiscovered Niches:\n"
        for i, discovered_niche in enumerate(discovered_niches[:5], 1):
            enhanced_market_data += f"{i}. {discovered_niche['title']}\n"
            enhanced_market_data += f"   Source: {discovered_niche['source']}\n"
            enhanced_market_data += f"   Relevance: {discovered_niche.get('relevance_score', 0):.2f}\n\n"
        result = await agent.execute(niche=niche, market_data=enhanced_market_data)
        if result.success:
            result.data["discovered_niches"] = discovered_niches
            result.data["scraping_sources"] = list(scraper.search_sources.keys())
            result.data["global_markets"] = list(scraper.global_sources.keys())
        return result
    except Exception as e:
        log.error(f"Enhanced niche research failed: {e}")
        return await agent.execute(niche=niche, market_data=market_data)
