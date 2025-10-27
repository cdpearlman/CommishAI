"""ESPN Fantasy Football MCP Server using FastMCP."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv
from fastmcp import FastMCP

from espn_client import ESPNFantasyClient
from tavily_client import TavilyFantasyClient


# Load environment variables from .env file in the same directory as this script
# This ensures the .env file is found regardless of the working directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Extract league configuration from environment variables
LEAGUE_ID = int(os.getenv("LEAGUE_ID", "0"))
TEAM_ID = int(os.getenv("TEAM_ID", "0"))
YEAR = int(os.getenv("YEAR", "2025"))

# Initialize FastMCP server
mcp = FastMCP("ESPN Fantasy Football")

# Initialize ESPN client (will be created on-demand to handle auth)
_espn_client = None
_tavily_client = None


def get_espn_client() -> ESPNFantasyClient:
    """Get or create ESPN client instance."""
    global _espn_client
    if _espn_client is None:
        _espn_client = ESPNFantasyClient()
    return _espn_client


def get_tavily_client() -> TavilyFantasyClient:
    """Get or create Tavily client instance."""
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyFantasyClient()
    return _tavily_client


# ============================================================================
# ESPN FANTASY TOOLS
# ============================================================================

@mcp.tool()
def get_roster() -> str:
    """
    Get the full roster for your ESPN Fantasy Football team.

    Returns:
        JSON string with roster grouped by position, including player stats and injury info
    """
    try:
        if LEAGUE_ID == 0 or TEAM_ID == 0:
            return json.dumps({"error": "LEAGUE_ID and TEAM_ID must be set in .env file"})
        
        client = get_espn_client()
        roster = client.get_roster(LEAGUE_ID, TEAM_ID, YEAR)
        return json.dumps(roster, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def is_available(player_name: str) -> bool:
    """
    Check if a player is available on the ESPN Fantasy waiver wire.

    Args:
        player_name: Full name of the player to check (e.g., "Patrick Mahomes")

    Returns:
        True if player is available, False if rostered or not found
    """
    try:
        if LEAGUE_ID == 0:
            return False
        
        client = get_espn_client()
        return client.is_available(LEAGUE_ID, player_name, YEAR)
    except Exception as e:
        return False


@mcp.tool()
def get_top_available(position: str, count: int = 10) -> str:
    """
    Get the top N available players for a position in ESPN Fantasy.

    Args:
        position: Position code (QB, RB, WR, TE, K, DEF or D/ST)
        count: Number of players to return (default: 10)

    Returns:
        JSON string with list of top available players sorted by projected points
    """
    try:
        if LEAGUE_ID == 0:
            return json.dumps({"error": "LEAGUE_ID must be set in .env file"})
        
        client = get_espn_client()
        players = client.get_top_available(LEAGUE_ID, position, count, YEAR)
        return json.dumps(players, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# TAVILY SEARCH TOOLS
# ============================================================================

@mcp.tool()
def summarize_players(
    player_names: List[str], week: int, scoring_format: str = "PPR"
) -> str:
    """
    Get quick matchup summaries for multiple players.

    Args:
        player_names: List of player names to analyze
        week: Week number
        scoring_format: League scoring format (PPR, Half-PPR, Standard)

    Returns:
        JSON string with matchup summaries for each player (1-2 results per player)
    """
    try:
        client = get_tavily_client()
        all_results = {}
        
        for player_name in player_names:
            results = client.search_player_matchup(
                player_name, week, scoring_format, max_results=2
            )
            all_results[player_name] = results
        
        return json.dumps(all_results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def injury_report(player_name: str, week: int) -> str:
    """
    Get detailed injury report and start/sit advice for a player.

    Args:
        player_name: Full name of the player
        week: Week number

    Returns:
        JSON string with injury details and fantasy impact (3-4 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_injury_report(player_name, week, max_results=4)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def analyze_player(
    player_name: str, week: int, scoring_format: str = "PPR"
) -> str:
    """
    Get comprehensive in-depth analysis of a player.

    Args:
        player_name: Full name of the player
        week: Week number
        scoring_format: League scoring format (PPR, Half-PPR, Standard)

    Returns:
        JSON string with detailed analysis including matchup, volume, rankings (4-6 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_player_analysis(
            player_name, week, scoring_format, max_results=6
        )
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def find_best_adds(
    week: int, position: str = "all", scoring_format: str = "PPR"
) -> str:
    """
    Get expert waiver wire pickup recommendations for the week.

    Args:
        week: Week number
        position: Position filter (QB, RB, WR, TE, K, DEF, or 'all')
        scoring_format: League scoring format (PPR, Half-PPR, Standard)

    Returns:
        JSON string with top waiver wire recommendations (4-6 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_waiver_wire(
            week, position, scoring_format, max_results=6
        )
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_player_usage_trends(player_name: str, week: int) -> str:
    """
    Search for player usage trends and snap share data.

    Args:
        player_name: Full name of the player
        week: Week number

    Returns:
        JSON string with usage trend data (5 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_player_usage_trends(player_name, week, max_results=5)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_vegas_odds(player_or_team_name: str, week: int) -> str:
    """
    Search for Vegas odds and betting lines.

    Args:
        player_or_team_name: Player or team name
        week: Week number

    Returns:
        JSON string with odds information (2 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_vegas_odds(player_or_team_name, week, max_results=2)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def fantasy_football_search(query: str, week: int = None) -> str:
    """
    Perform a custom fantasy football search with LLM-generated query.

    Args:
        query: Custom search query string
        week: Optional week number for context

    Returns:
        JSON string with search results (4-6 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_custom(query, week, max_results=5)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

