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
        self, league_id: int, team_id: int, year: int = 2025
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
            
            # Get current week for opponent lookup
            current_week = getattr(league, 'current_week', 1)
            
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
            List of player data dictionaries sorted by average points
        """
        try:
            league = self._get_league(league_id, year)
            
            # Get current week for opponent lookup
            current_week = getattr(league, 'current_week', 1)
            print(f"DEBUG: Current week = {current_week}")
            
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
            print(f"DEBUG: Position '{position}' mapped to ESPN position '{espn_position}'")
            
            # Get free agents for the position
            free_agents = league.free_agents(size=count * 3, position=espn_position)
            print(f"DEBUG: Found {len(free_agents)} free agents for position {espn_position}")
            
            players = []
            for i, player in enumerate(free_agents):
                print(f"\nDEBUG: Processing player {i+1}: {player.name}")
                try:
                    print(f"DEBUG: Player schedule type: {type(player.schedule)}")
                    print(f"DEBUG: Player schedule value: {player.schedule}")
                except Exception as e:
                    print(f"DEBUG: Error accessing schedule: {e}")
                    player.schedule = None
                
                # Check if schedule is None or empty (free agents don't have schedule data)
                if player.schedule is None or not player.schedule:
                    print(f"DEBUG: Schedule is None or empty for {player.name}")
                    # For free agents, try to get opponent from pro_opponent attribute
                    if hasattr(player, 'pro_opponent') and player.pro_opponent:
                        opponent = player.pro_opponent
                        print(f"DEBUG: Using pro_opponent: {opponent}")
                    else:
                        opponent = "BYE WEEK"
                        print(f"DEBUG: No pro_opponent available, using BYE WEEK")
                else:
                    # Debug the schedule structure
                    if hasattr(player.schedule, '__dict__'):
                        print(f"DEBUG: Schedule has __dict__: {player.schedule.__dict__}")
                    elif isinstance(player.schedule, dict):
                        print(f"DEBUG: Schedule is dict with keys: {list(player.schedule.keys())}")
                        print(f"DEBUG: Schedule dict contents: {player.schedule}")
                    elif isinstance(player.schedule, (list, tuple)):
                        print(f"DEBUG: Schedule is {type(player.schedule)} with {len(player.schedule)} items")
                        if player.schedule:
                            print(f"DEBUG: First schedule item: {player.schedule[0]}")
                            print(f"DEBUG: First schedule item type: {type(player.schedule[0])}")
                    else:
                        print(f"DEBUG: Schedule is unexpected type: {type(player.schedule)}")
                    
                    # Debug the opponent retrieval step by step
                    print(f"DEBUG: Looking for week '{current_week}' in schedule")
                    if isinstance(player.schedule, dict):
                        week_key = str(current_week)
                        print(f"DEBUG: Checking if '{week_key}' exists in schedule dict")
                        if week_key in player.schedule:
                            week_data = player.schedule[week_key]
                            print(f"DEBUG: Week data found: {week_data}")
                            print(f"DEBUG: Week data type: {type(week_data)}")
                            if isinstance(week_data, dict) and "team" in week_data:
                                opponent = week_data["team"]
                                print(f"DEBUG: Opponent found: {opponent}")
                            else:
                                print(f"DEBUG: Week data doesn't contain 'team' key or isn't a dict")
                                opponent = "BYE WEEK"
                        else:
                            print(f"DEBUG: Week '{week_key}' not found in schedule")
                            opponent = "BYE WEEK"
                    else:
                        print(f"DEBUG: Schedule is not a dict, cannot use .get() method")
                        opponent = "BYE WEEK"
                
                print(f"DEBUG: Final opponent value: {opponent}")
                
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
