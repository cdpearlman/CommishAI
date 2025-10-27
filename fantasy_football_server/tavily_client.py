"""Tavily Search API client for fantasy football research."""

import os
from typing import Dict, List, Optional, Any
from tavily import TavilyClient


class TavilyFantasyClient:
    """Client for conducting fantasy football research via Tavily search API."""

    # Reputable fantasy football sources to prioritize
    TIER_1_SOURCES = [
        "espn.com",
        "fantasypros.com",
        "nfl.com",
        "nbcsports.com",
        "sports.yahoo.com",
        "ftnfantasy.com",
        "playerprofiler.com"
    ]
    
    TIER_2_SOURCES = [
        "cbssports.com",
        "rotoballer.com",
        "footballguys.com",
        "sleeper.com"
    ]
    
    # Sources to exclude (social media, forums)
    EXCLUDED_DOMAINS = [
        "reddit.com",
        "twitter.com",
        "x.com",
        "facebook.com",
        "instagram.com",
    ]

    def __init__(self):
        """Initialize Tavily client with API key from environment."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key or api_key == "your_tavily_api_key_here":
            raise ValueError(
                "TAVILY_API_KEY not found or not set in environment. "
                "Please set your Tavily API key in the .env file."
            )
        
        self.client = TavilyClient(api_key=api_key)

    def _search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Tavily search with common parameters.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            include_domains: Optional list of specific domains to include
            
        Returns:
            List of search result dictionaries with title, url, content
        """
        try:
            # Build search parameters
            search_params = {
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
                "include_answer": False,
                "exclude_domains": self.EXCLUDED_DOMAINS,
            }
            
            # Add domain filtering if specified
            if include_domains:
                search_params["include_domains"] = include_domains
            
            # Execute search
            response = self.client.search(**search_params)
            
            # Extract and format results
            results = []
            if "results" in response:
                for result in response["results"]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0),
                    })
            
            # Sort by score (relevance) and filter reputable sources to top
            results = self._prioritize_sources(results)
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Tavily search failed: {str(e)}")

    def _prioritize_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize results from reputable fantasy football sources.
        
        Args:
            results: List of search results
            
        Returns:
            Reordered list with reputable sources first
        """
        tier_1 = []
        tier_2 = []
        other = []
        
        for result in results:
            url = result.get("url", "").lower()
            
            # Check if from tier 1 source
            if any(domain in url for domain in self.TIER_1_SOURCES):
                tier_1.append(result)
            # Check if from tier 2 source
            elif any(domain in url for domain in self.TIER_2_SOURCES):
                tier_2.append(result)
            else:
                other.append(result)
        
        # Return prioritized list
        return tier_1 + tier_2 + other

    def search_player_matchup(
        self,
        player_name: str,
        week: int,
        scoring_format: str = "PPR",
        max_results: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Search for weekly matchup summary for a player.
        
        Args:
            player_name: Full player name
            week: Week number
            scoring_format: League scoring format (PPR, Half-PPR, Standard)
            max_results: Maximum results to return (default 2)
            
        Returns:
            List of search results with matchup analysis
        """
        query = (
            f"Week {week} 2025 {scoring_format} fantasy football "
            f"{player_name} matchup ranking start sit"
        )
        return self._search(query, max_results=max_results)

    def search_injury_report(
        self,
        player_name: str,
        week: int,
        max_results: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Search for injury report and fantasy impact.
        
        Args:
            player_name: Full player name
            week: Week number
            max_results: Maximum results to return (default 4)
            
        Returns:
            List of search results with injury information
        """
        query = (
            f"({player_name} 'injury' OR 'practice' OR 'DNP' OR 'questionable' OR 'out') "
            f"week {week} site:rotowire.com OR site:espn.com"
        )
        return self._search(query, max_results=max_results)

    def search_player_analysis(
        self,
        player_name: str,
        week: int,
        scoring_format: str = "PPR",
        max_results: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Search for comprehensive player analysis.
        
        Args:
            player_name: Full player name
            week: Week number
            scoring_format: League scoring format
            max_results: Maximum results to return (default 6)
            
        Returns:
            List of search results with detailed analysis
        """
        query = (
            f"Week {week} 2025 {player_name} {scoring_format} fantasy analysis "
            f"matchup volume projection expert rankings"
        )
        return self._search(query, max_results=max_results)

    def search_waiver_wire(
        self,
        week: int,
        position: str = "all",
        scoring_format: str = "PPR",
        max_results: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Search for waiver wire pickup recommendations.
        
        Args:
            week: Week number
            position: Position filter (QB, RB, WR, TE, all)
            scoring_format: League scoring format
            max_results: Maximum results to return (default 6)
            
        Returns:
            List of search results with waiver recommendations
        """
        position_text = f"{position} " if position != "all" else ""
        query = (
            f"Week {week} 2025 {position_text}fantasy football waiver wire "
            f"pickups {scoring_format} best adds"
        )
        return self._search(query, max_results=max_results)

    def search_player_usage_trends(
        self,
        player_name: str,
        week: int,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for player usage trends and snap share data.
        
        Args:
            player_name: Full player name
            week: Week number
            max_results: Maximum results to return (default 5)
            
        Returns:
            List of search results with usage trend data
        """
        query = (
            f"{player_name} snap share last 4 weeks "
            f"site:pro-football-reference.com OR site:playerprofiler.com OR "
            f"\"snap\" \"routes\" \"target share\" \"{player_name}\""
        )
        return self._search(query, max_results=max_results)

    def search_vegas_odds(
        self,
        player_or_team_name: str,
        week: int,
        max_results: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Search for Vegas odds and betting lines.
        
        Args:
            player_or_team_name: Player or team name
            week: Week number
            max_results: Maximum results to return (default 2)
            
        Returns:
            List of search results with odds information
        """
        query = (
            f"game odds {player_or_team_name} week {week} over/under spread "
            f"implied total 'odds' 'over/under' 'implied points'"
        )
        return self._search(query, max_results=max_results)

    def search_custom(
        self,
        query: str,
        week: Optional[int] = None,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Execute a custom search query.
        
        Args:
            query: Custom search string
            week: Optional week number to add context
            max_results: Maximum results to return (default 5)
            
        Returns:
            List of search results
        """
        # Add week context if provided
        if week:
            query = f"Week {week} 2025 {query}"
        
        return self._search(query, max_results=max_results)

