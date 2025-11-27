"""ESPN Fantasy Football MCP Server using FastMCP."""

import sys
import os

# Redirect stdout to stderr to prevent any imports from corrupting the JSON-RPC stream
# This fixes "invalid trailing data" errors caused by libraries printing to stdout
_original_stdout = sys.stdout
sys.stdout = sys.stderr

try:
    import json
    from pathlib import Path
    from typing import Any, Dict, List
    from dotenv import load_dotenv
    from fastmcp import FastMCP

    from espn_client import ESPNFantasyClient
    from tavily_client import TavilyFantasyClient
finally:
    # Restore stdout
    sys.stdout = _original_stdout

# Ensure stdout is in binary mode or UTF-8 to avoid encoding issues on Windows
if sys.platform == "win32":
    import io
    try:
        # Set newline='' to prevent automatic \n -> \r\n translation
        sys.stdout.reconfigure(encoding='utf-8', newline='')
        sys.stdin.reconfigure(encoding='utf-8', newline='')
    except AttributeError:
        pass

    # Monkeypatch stdout to strip carriage returns (\r) which can cause "invalid trailing data"
    class StripCRBuffer:
        def __init__(self, buffer):
            self.buffer = buffer
            
        def write(self, b):
            if isinstance(b, bytes):
                return self.buffer.write(b.replace(b'\r', b''))
            return self.buffer.write(b)
            
        def flush(self):
            self.buffer.flush()
            
        def __getattr__(self, name):
            return getattr(self.buffer, name)

    class StripCRStdout:
        def __init__(self, wrapped):
            self.wrapped = wrapped
            if hasattr(wrapped, 'buffer'):
                self.buffer = StripCRBuffer(wrapped.buffer)
            else:
                self.buffer = None
                
        def write(self, s):
            if isinstance(s, str):
                return self.wrapped.write(s.replace('\r', ''))
            return self.wrapped.write(s)
            
        def flush(self):
            self.wrapped.flush()
            
        def __getattr__(self, name):
            return getattr(self.wrapped, name)

    sys.stdout = StripCRStdout(sys.stdout)


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
def get_roster() -> str:
    """
    Get the full roster for your ESPN Fantasy Football team.

    Returns:
        JSON string with roster grouped by position, including player stats and injury info
    """
    try:
        client = get_espn_client()
        roster = client.get_roster()
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
        client = get_espn_client()
        return client.is_available(player_name)
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
        client = get_espn_client()
        players = client.get_top_available(position, count)
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
            results = client.summarize_players(
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
        results = client.injury_report(player_name, week, max_results=4)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def analyze_player(
    player_name: str, week: int, position: str, scoring_format: str = "PPR"
) -> str:
    """
    Get comprehensive in-depth analysis of a player with position-specific metrics.

    Args:
        player_name: Full name of the player
        week: Week number
        position: Player position (QB, RB, WR, TE, K, DEF, other)
        scoring_format: League scoring format (PPR, Half-PPR, Standard)

    Returns:
        JSON string with detailed analysis including position-specific metrics and ROS rankings
    """
    try:
        client = get_tavily_client()
        results = client.analyze_player(
            player_name, week, position, scoring_format
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
        results = client.find_best_adds(
            week, position, scoring_format, max_results=6
        )
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_player_usage_trends(player_name: str, week: int, position: str = "other") -> str:
    """
    Search for player usage trends with position-specific metrics.

    Args:
        player_name: Full name of the player
        week: Week number
        position: Player position (RB, WR, TE, or other)

    Returns:
        JSON string with usage trend data grouped by metric type
    """
    try:
        client = get_tavily_client()
        results = client.get_player_usage_trends(player_name, week, position)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_matchup_context(week: int, opponent: str) -> str:
    """
    Get matchup context for an opponent's defense.

    Args:
        week: Week number
        opponent: Opponent team name or abbreviation

    Returns:
        JSON string with defensive matchup context including DVOA (3 results)
    """
    try:
        client = get_tavily_client()
        results = client.get_matchup_context(week, opponent)
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
        results = client.fantasy_football_search(query, week, max_results=5)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport='stdio', show_banner=False, log_level="ERROR")

