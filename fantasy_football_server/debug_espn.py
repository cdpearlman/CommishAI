#!/usr/bin/env python3
"""Debug script to test ESPN API connection and identify the issue."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from espn_api.football import League

def debug_league_connection():
    """Debug the ESPN league connection step by step."""
    print("=== ESPN API Debug ===")
    
    # Test credentials
    espn_s2 = os.getenv("ESPN_S2")
    swid = os.getenv("ESPN_SWID")
    
    print(f"ESPN_S2 present: {bool(espn_s2)}")
    print(f"SWID present: {bool(swid)}")
    
    if not espn_s2 or not swid:
        print("ERROR: Missing ESPN credentials")
        return
    
    try:
        print("\n1. Creating league object...")
        league = League(
            league_id=524166927,
            year=2025,
            espn_s2=espn_s2,
            swid=swid
        )
        print("SUCCESS: League object created successfully")
        
        print("\n2. Testing league.teams...")
        print(f"Number of teams: {len(league.teams)}")
        
        print("\n3. Finding team 7...")
        target_team = None
        for i, team in enumerate(league.teams):
            print(f"Team {i+1}: ID={team.team_id}, Name={team.team_name}")
            if team.team_id == 7:
                target_team = team
                break
        
        if not target_team:
            print("ERROR: Team ID 7 not found")
            return
        
        print(f"SUCCESS: Found team: {target_team.team_name}")
        
        print("\n4. Testing roster access...")
        print(f"Roster size: {len(target_team.roster)}")
        
        print("\n5. Testing first few players...")
        for i, player in enumerate(target_team.roster[:3]):
            print(f"\nPlayer {i+1}:")
            print(f"  Name: {player.name}")
            print(f"  Type: {type(player)}")
            print(f"  Attributes: {dir(player)}")
            
            # Test the problematic attributes
            try:
                lineup_slot = player.lineupSlot
                print(f"  LineupSlot: {lineup_slot} (type: {type(lineup_slot)})")
            except Exception as e:
                print(f"  LineupSlot ERROR: {e}")
            
            try:
                pro_team = getattr(player, 'proTeam', None)
                print(f"  ProTeam: {pro_team} (type: {type(pro_team)})")
            except Exception as e:
                print(f"  ProTeam ERROR: {e}")
            
            try:
                injury_status = getattr(player, 'injuryStatus', None)
                print(f"  InjuryStatus: {injury_status} (type: {type(injury_status)})")
            except Exception as e:
                print(f"  InjuryStatus ERROR: {e}")
        
        print("\nSUCCESS: Debug completed successfully")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_league_connection()
