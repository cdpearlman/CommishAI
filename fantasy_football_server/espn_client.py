"""ESPN Fantasy Football API client wrapper."""

import os
from typing import Dict, List, Optional, Any
from espn_api.football import League


class ESPNFantasyClient:
    """Client for interacting with ESPN Fantasy Football API."""

    def __init__(self):
        """Initialize ESPN client with credentials and config from environment."""
        self.espn_s2 = os.getenv("ESPN_S2")
        self.swid = os.getenv("ESPN_SWID")
        
        # Load league configuration from environment
        try:
            self.league_id = int(os.getenv("LEAGUE_ID", "0"))
            self.team_id = int(os.getenv("TEAM_ID", "0"))
            self.year = int(os.getenv("YEAR", "2025"))
        except (ValueError, TypeError):
            raise ValueError("LEAGUE_ID, TEAM_ID, and YEAR must be valid integers in .env file")

        if self.league_id == 0:
            raise ValueError("LEAGUE_ID must be set in .env file")

    def _get_league(self) -> League:
        """Get league object with proper authentication."""
        if self.espn_s2 and self.swid:
            return League(
                league_id=self.league_id,
                year=self.year,
                espn_s2=self.espn_s2,
                swid=self.swid
            )
        else:
            # Public league access
            return League(league_id=self.league_id, year=self.year)

    def get_roster(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the roster for the configured team.

        Returns:
            Dictionary with positions as keys and lists of player data
        """
        try:
            if self.team_id == 0:
                raise ValueError("TEAM_ID must be set in .env file")

            league = self._get_league()
            
            # Get current week for opponent lookup
            current_week = getattr(league, 'current_week', 1)
            
            # Find the team (team_id is 1-indexed in user terms, but 0-indexed in API)
            team = None
            for t in league.teams:
                if t.team_id == self.team_id:
                    team = t
                    break
            
            if not team:
                raise ValueError(f"Team ID {self.team_id} not found in league")

            # Group players by position
            roster_by_position = {}
            
            for player in team.roster:                
                player_info = {
                    "name": player.name,
                    "team": player.proTeam,
                    "position": player.position,
                    "opponenet": player.schedule.get(str(current_week), {}).get("team") if str(current_week) in player.schedule else "BYE WEEK",
                    "injury_status": player.injuryStatus,
                    "average_points": player.avg_points,
                    "percent_owned": player.percent_owned,
                    "percent_started": player.percent_started,
                    "position_rank": player.posRank,
                }
                
                if player.position not in roster_by_position:
                    roster_by_position[player.position] = []
                roster_by_position[player.position].append(player_info)

            return roster_by_position

        except Exception as e:
            raise RuntimeError(f"Failed to get roster: {str(e)}")

    def is_available(self, player_name: str) -> bool:
        """
        Check if a player is available on the waiver wire.

        Args:
            player_name: Full name of the player to check

        Returns:
            True if player is available, False otherwise
        """
        try:
            league = self._get_league()
            
            # Get all free agents (large size to ensure we capture the player)
            free_agents = league.free_agents(size=500)
            
            player_name_lower = player_name.lower()
            
            for player in free_agents:
                if player.name.lower() == player_name_lower:
                    return True
            
            return False

        except Exception as e:
            raise RuntimeError(f"Failed to check player availability: {str(e)}")

    def get_top_available(self, position: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top N available players for a given position.

        Args:
            position: Position code (QB, RB, WR, TE, K, D/ST)
            count: Number of players to return

        Returns:
            List of player data dictionaries sorted by average points
        """
        try:
            league = self._get_league()
            
            # Get current week for opponent lookup
            current_week = getattr(league, 'current_week', 1)

            
            # Map position names to ESPN position slots
            position_map = {
                "QB": "QB",
                "RB": "RB",
                "WR": "WR",
                "TE": "TE",
                "K": "K",
                "DEF": "D/ST",
                "D/ST": "D/ST",
            }
            
            espn_position = position_map.get(position.upper(), position)

            
            # Get free agents for the position
            free_agents = league.free_agents(size=count * 3, position=espn_position)

            
            players = []
            for i, player in enumerate(free_agents):
                try:
                    # Access schedule to ensure it's loaded/valid
                    _ = player.schedule
                except Exception:
                    player.schedule = None
                
                # Check if schedule is None or empty (free agents don't have schedule data)
                if player.schedule is None or not player.schedule:
                    # For free agents, try to get opponent from pro_opponent attribute
                    if hasattr(player, 'pro_opponent') and player.pro_opponent:
                        opponent = player.pro_opponent
                    else:
                        opponent = "BYE WEEK"
                else:
                    if isinstance(player.schedule, dict):
                        week_key = str(current_week)
                        if week_key in player.schedule:
                            week_data = player.schedule[week_key]
                            if isinstance(week_data, dict) and "team" in week_data:
                                opponent = week_data["team"]
                            else:
                                opponent = "BYE WEEK"
                        else:
                            opponent = "BYE WEEK"
                    else:
                        opponent = "BYE WEEK"
                
                player_info = {
                    "name": player.name,
                    "team": player.proTeam,
                    "position": player.position,
                    "opponenet": opponent,
                    "injury_status": player.injuryStatus,
                    "average_points": player.avg_points,
                    "percent_owned": player.percent_owned,
                    "percent_started": player.percent_started,
                    "position_rank": player.posRank,
                }
                players.append(player_info)
            
            # Sort by average points (descending)
            players.sort(key=lambda x: x["average_points"], reverse=True)
            
            return players[:count]

        except Exception as e:
            raise RuntimeError(f"Failed to get top available players: {str(e)}")
