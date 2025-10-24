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
def get_roster(league_id: int, team_id: int, year: int = 2024) -> str:
    """
    Get the full roster for an ESPN Fantasy Football team.

    Args:
        league_id: ESPN league ID (numeric)
        team_id: Team ID within the league (1-indexed, e.g., 1 for first team)
        year: Season year (default: 2024)

    Returns:
        JSON string with roster grouped by position, including player stats and injury info
    """
    try:
        client = get_espn_client()
        roster = client.get_roster(league_id, team_id, year)
        return json.dumps(roster, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def is_available(league_id: int, player_name: str, year: int = 2024) -> bool:
    """
    Check if a player is available on the ESPN Fantasy waiver wire.

    Args:
        league_id: ESPN league ID (numeric)
        player_name: Full name of the player to check (e.g., "Patrick Mahomes")
        year: Season year (default: 2024)

    Returns:
        True if player is available, False if rostered or not found
    """
    try:
        client = get_espn_client()
        return client.is_available(league_id, player_name, year)
    except Exception as e:
        return False


@mcp.tool()
def get_top_available(
    league_id: int, position: str, count: int = 10, year: int = 2024
) -> str:
    """
    Get the top N available players for a position in ESPN Fantasy.

    Args:
        league_id: ESPN league ID (numeric)
        position: Position code (QB, RB, WR, TE, K, DEF or D/ST)
        count: Number of players to return (default: 10)
        year: Season year (default: 2024)

    Returns:
        JSON string with list of top available players sorted by projected points
    """
    try:
        client = get_espn_client()
        players = client.get_top_available(league_id, position, count, year)
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
def compare_players(
    player1: str, player2: str, week: int, scoring_format: str = "PPR"
) -> str:
    """
    Compare two players for start/sit decisions.

    Args:
        player1: First player name
        player2: Second player name
        week: Week number
        scoring_format: League scoring format (PPR, Half-PPR, Standard)

    Returns:
        JSON string with head-to-head comparison and expert recommendations (4-6 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_player_comparison(
            player1, player2, week, scoring_format, max_results=5
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
def analyze_schedule(player_name: str, weeks: str = "playoffs") -> str:
    """
    Analyze a player's upcoming schedule strength.

    Args:
        player_name: Full name of the player
        weeks: Which weeks to analyze ('playoffs' for weeks 15-17, or 'ROS' for rest of season)

    Returns:
        JSON string with schedule analysis and outlook (3-5 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_schedule_strength(
            player_name, weeks, max_results=4
        )
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def check_weather(game_location: str, week: int) -> str:
    """
    Get weather forecast and fantasy impact for a game location.

    Args:
        game_location: City or stadium name (e.g., 'Buffalo', 'Green Bay')
        week: Week number

    Returns:
        JSON string with weather conditions and fantasy impact (2-3 results)
    """
    try:
        client = get_tavily_client()
        results = client.search_weather(game_location, week, max_results=3)
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

