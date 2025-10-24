"""ESPN Fantasy Football API client wrapper."""

import os
from typing import Dict, List, Optional, Any
from espn_api.football import League


class ESPNFantasyClient:
    """Client for interacting with ESPN Fantasy Football API."""

    def __init__(self):
        """Initialize ESPN client with optional credentials from environment."""
        self.espn_s2 = os.getenv("ESPN_S2")
        self.swid = os.getenv("ESPN_SWID")

    def _get_league(self, league_id: int, year: int) -> League:
        """Get league object with proper authentication."""
        if self.espn_s2 and self.swid:
            return League(
                league_id=league_id,
                year=year,
                espn_s2=self.espn_s2,
                swid=self.swid
            )
        else:
            # Public league access
            return League(league_id=league_id, year=year)

    def get_roster(
        self, league_id: int, team_id: int, year: int = 2024
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the roster for a specific team.

        Args:
            league_id: ESPN league ID
            team_id: Team ID within the league (1-indexed)
            year: Season year (defaults to 2024)

        Returns:
            Dictionary with positions as keys and lists of player data
        """
        try:
            league = self._get_league(league_id, year)
            
            # Find the team (team_id is 1-indexed in user terms, but 0-indexed in API)
            team = None
            for t in league.teams:
                if t.team_id == team_id:
                    team = t
                    break
            
            if not team:
                raise ValueError(f"Team ID {team_id} not found in league")

            # Group players by position
            roster_by_position = {}
            
            for player in team.roster:
                position = player.lineupSlot
                
                player_info = {
                    "name": player.name,
                    "team": player.proTeam if hasattr(player, "proTeam") else "",
                    "status": "ACTIVE",
                    "injury_status": self._get_injury_status(player),
                    "injury_details": getattr(player, "injuryStatus", ""),
                    "projected_points": getattr(player, "projected_points", 0.0),
                    "slot_position": position,
                    "eligible_positions": self._get_eligible_positions(player),
                }
                
                if position not in roster_by_position:
                    roster_by_position[position] = []
                roster_by_position[position].append(player_info)

            return roster_by_position

        except Exception as e:
            raise RuntimeError(f"Failed to get roster: {str(e)}")

    def is_available(
        self, league_id: int, player_name: str, year: int = 2024
    ) -> bool:
        """
        Check if a player is available on the waiver wire.

        Args:
            league_id: ESPN league ID
            player_name: Full name of the player to check
            year: Season year (defaults to 2024)

        Returns:
            True if player is available, False otherwise
        """
        try:
            league = self._get_league(league_id, year)
            
            # Get all free agents (large size to ensure we capture the player)
            free_agents = league.free_agents(size=500)
            
            player_name_lower = player_name.lower()
            
            for player in free_agents:
                if player.name.lower() == player_name_lower:
                    return True
            
            return False

        except Exception as e:
            raise RuntimeError(f"Failed to check player availability: {str(e)}")

    def get_top_available(
        self, league_id: int, position: str, count: int = 10, year: int = 2024
    ) -> List[Dict[str, Any]]:
        """
        Get the top N available players for a given position.

        Args:
            league_id: ESPN league ID
            position: Position code (QB, RB, WR, TE, K, D/ST)
            count: Number of players to return
            year: Season year (defaults to 2024)

        Returns:
            List of player data dictionaries sorted by projected points
        """
        try:
            league = self._get_league(league_id, year)
            
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
            for player in free_agents:
                player_info = {
                    "name": player.name,
                    "team": player.proTeam if hasattr(player, "proTeam") else "",
                    "position": espn_position,
                    "status": "ACTIVE",
                    "injury_status": self._get_injury_status(player),
                    "injury_details": getattr(player, "injuryStatus", ""),
                    "projected_points": getattr(player, "projected_points", 0.0),
                    "percent_owned": getattr(player, "percent_owned", 0.0),
                    "stats": self._get_player_stats(player),
                }
                players.append(player_info)
            
            # Sort by projected points (descending)
            players.sort(key=lambda x: x["projected_points"], reverse=True)
            
            return players[:count]

        except Exception as e:
            raise RuntimeError(f"Failed to get top available players: {str(e)}")

    @staticmethod
    def _get_injury_status(player) -> str:
        """Extract injury status from player data."""
        if hasattr(player, "injuryStatus"):
            status = player.injuryStatus
            if status and status != "ACTIVE":
                injury_map = {
                    "INJURY_RESERVE": "Injured Reserve",
                    "OUT": "Out",
                    "DOUBTFUL": "Doubtful",
                    "QUESTIONABLE": "Questionable",
                    "PROBABLE": "Probable",
                    "SUSPENSION": "Suspended",
                    "DAY_TO_DAY": "Day-to-Day",
                }
                return injury_map.get(status, status)
        
        return "Healthy"

    @staticmethod
    def _get_eligible_positions(player) -> List[str]:
        """Extract eligible positions from player data."""
        if hasattr(player, "eligibleSlots"):
            return [str(slot) for slot in player.eligibleSlots]
        return []

    @staticmethod
    def _get_player_stats(player) -> Dict[str, float]:
        """Extract player statistics."""
        stats = {}
        if hasattr(player, "stats"):
            try:
                # Get the most recent stats
                for stat in player.stats:
                    if hasattr(stat, "breakdown") and stat.breakdown is not None:
                        stats = stat.breakdown
                        break
            except Exception:
                pass
        return stats

