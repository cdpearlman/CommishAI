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

    def summarize_players(
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

    def injury_report(
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

    def analyze_player(
        self,
        player_name: str,
        week: int,
        position: str,
        scoring_format: str = "PPR",
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for comprehensive player analysis with position-specific metrics.
        
        Args:
            player_name: Full player name
            week: Week number
            position: Player position (QB, RB, WR, TE, K, DEF, other)
            scoring_format: League scoring format
            
        Returns:
            Dictionary with results grouped by metric type
        """
        results = {}
        
        # Position-specific searches
        if position == "QB":
            # QB: CPOE + ROS rankings
            cpoe_query = f"Week {week} 2025 {player_name} CPOE Completion Percentage Over Expected"
            results["cpoe"] = self._search(cpoe_query, max_results=2)
            
        elif position == "RB":
            # RB: RYOE + MTF + ROS rankings
            ryoe_query = f"Week {week} 2025 {player_name} RYOE Rushing Yards Over Expected"
            results["ryoe"] = self._search(ryoe_query, max_results=2)
            
            mtf_query = f"Week {week} 2025 {player_name} MTF Missed Tackles Forced per touch"
            results["mtf"] = self._search(mtf_query, max_results=2)
            
        elif position in ["WR", "TE"]:
            # WR/TE: YPRR + WOPR + ROS rankings
            yprr_query = f"Week {week} 2025 {player_name} YPRR Yards Per Route Run"
            results["yprr"] = self._search(yprr_query, max_results=2)
            
            wopr_query = f"Week {week} 2025 {player_name} WOPR Weighted Opportunity Rating"
            results["wopr"] = self._search(wopr_query, max_results=2)
            
        elif position in ["K", "DEF"]:
            # K and DEF: ROS rankings only
            pass
            
        else:
            # Other positions: General analysis
            general_query = (
                f"Week {week} 2025 {player_name} {scoring_format} fantasy analysis "
                f"matchup volume projection expert rankings"
            )
            results["general_analysis"] = self._search(general_query, max_results=4)
        
        # Add ROS rankings for all positions
        ros_query = f"Week {week} 2025 {player_name} fantasy football rest of season ROS rankings"
        results["ros_rankings"] = self._search(ros_query, max_results=2)
        
        return results

    def find_best_adds(
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

    def get_player_usage_trends(
        self,
        player_name: str,
        week: int,
        position: str = "other",
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for player usage trends with position-specific metrics.
        
        Args:
            player_name: Full player name
            week: Week number
            position: Player position (RB, WR, TE, or other)
            
        Returns:
            Dictionary with results grouped by metric type
        """
        results = {}
        
        # Position-specific searches
        if position == "RB":
            # RB: Rushing attempts percentage
            rush_att_query = f"Week {week} 2025 {player_name} rushing attempts percentage share"
            results["rushing_attempts_pct"] = self._search(rush_att_query, max_results=2)
            
        elif position in ["WR", "TE"]:
            # WR/TE: Route Participation % + Air Yards Share
            route_part_query = f"Week {week} 2025 {player_name} route participation percent"
            results["route_participation"] = self._search(route_part_query, max_results=2)
            
            air_yards_query = f"Week {week} 2025 {player_name} air yards share AY%"
            results["air_yards_share"] = self._search(air_yards_query, max_results=2)
            
        else:
            # Other positions: General snap share and usage
            general_query = (
                f"{player_name} 2025 week {week} snap share last 4 weeks "
                f"site:pro-football-reference.com OR site:playerprofiler.com OR "
                f"\"snap\" \"routes\" \"target share\" \"{player_name}\""
            )
            results["general_usage"] = self._search(general_query, max_results=5)
        
        return results

    def get_matchup_context(
        self,
        week: int,
        opponent: str,
    ) -> List[Dict[str, Any]]:
        """
        Search for matchup context including defensive DVOA.
        
        Args:
            week: Week number
            opponent: Opponent team name or abbreviation
            
        Returns:
            List of search results with defensive matchup information
        """
        query = f"{opponent} 2025 week {week} Defense DVOA"
        return self._search(query, max_results=3)

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
            f"game odds {player_or_team_name} 2025 week {week} over/under spread "
            f"implied total 'odds' 'over/under' 'implied points'"
        )
        return self._search(query, max_results=max_results)

    def fantasy_football_search(
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

