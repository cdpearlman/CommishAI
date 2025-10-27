# ESPN Fantasy Football MCP Integration

A comprehensive MCP (Model Context Protocol) server for integrating ESPN Fantasy Football with Cursor AI, designed for advanced roster optimization and data-driven decision making.

## Quick Start

### 1. Install Dependencies

```bash
cd fantasy_football_server
pip install -r requirements.txt
```

### 2. Configure Your League

Create a `.env` file in the `fantasy_football_server` directory with your league configuration:

```bash
# Required: Your ESPN Fantasy League Configuration
LEAGUE_ID=your_league_id_here
TEAM_ID=your_team_id_here
YEAR=2025

# Required: Tavily Search API (for advanced research)
TAVILY_API_KEY=your_tavily_api_key

# Optional: ESPN Authentication (only for private leagues)
ESPN_S2=your_espn_s2_cookie
ESPN_SWID=your_espn_swid_cookie
```

**Getting Your League Information:**
1. Go to your ESPN Fantasy Football league page
2. League ID is in the URL: `https://fantasy.espn.com/football/league?leagueId=XXXXXX`
3. Team ID is usually 1-12 (or however many teams in your league)

**Getting Your ESPN Cookies (Private Leagues Only):**
1. Log into ESPN Fantasy Football in your browser
2. Open Developer Tools (F12 or right-click → Inspect)
3. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
4. In the left sidebar, expand **Cookies**
5. Click on `https://fantasy.espn.com`
6. Find and copy these two cookie values:
   - `espn_s2` - Copy the entire value (it's a long string)
   - `SWID` - Copy the entire value (it's a GUID format)
7. Paste these values into your `.env` file

**Getting Your Tavily API Key:**
1. Sign up at [https://tavily.com/](https://tavily.com/)
2. Copy your API key from the dashboard
3. Free tier includes 1000 searches per month

### 3. Restart Cursor

After setting up credentials, restart Cursor to load the MCP server. The server will be available as "espn-fantasy-football" in your MCP tools.

## Available Tools

### ESPN Fantasy (Current League Data)
- `get_roster` - Get full team roster with stats and injury info
- `is_available` - Check if a player is on waivers
- `get_top_available` - Get top N available players by position

### Advanced Research & Analysis
- `summarize_players` - Quick matchup summaries for multiple players
- `injury_report` - Detailed injury reports and fantasy impact
- `analyze_player` - Comprehensive player analysis with expert rankings
- `find_best_adds` - Expert waiver wire recommendations
- `search_player_usage_trends` - Player usage trends and snap share data
- `search_vegas_odds` - Vegas odds and betting lines for games
- `fantasy_football_search` - Custom fantasy football searches

## Example Usage in Cursor

Once the MCP server is running, you can use it in Cursor for advanced fantasy football analysis:

### Basic Roster Management
```
"Get my current roster"
"Is CeeDee Lamb available in my league?"
"Show me the top 5 available running backs"
```

### Advanced Player Analysis
```
"Analyze Saquon Barkley for Week 9 in PPR scoring"
"Get injury report for Justin Jefferson Week 9"
"Search usage trends for DeAndre Hopkins Week 9"
"Find Vegas odds for the Cowboys vs Eagles Week 9"
```

### Roster Optimization Workflows
```
"Find the best waiver wire pickups for Week 9"
"Compare my WR2 options: Amari Cooper vs Mike Evans"
"Analyze my RB depth and suggest streaming options"
"Check snap share trends for my flex players"
```

## Weekly Analysis Workflows

### Complete Weekly Preparation
```
1. "Get my current roster" - Review team status
2. "Find best waiver wire pickups for Week 9" - Identify targets
3. "Analyze [Player Name] Week 9" - Deep dive on key players
4. "Search Vegas odds for [Team] Week 9" - Check game environment
5. "Get injury report for [Player Name] Week 9" - Monitor health status
```

### Start/Sit Decision Process
```
1. "Summarize players: [Player A, Player B] Week 9 PPR" - Quick comparison
2. "Search usage trends for [Player Name] Week 9" - Volume analysis
3. "Search Vegas odds for [Player Team] Week 9" - Game script analysis
4. "Analyze [Player Name] Week 9 PPR" - Comprehensive evaluation
```

### Streaming Strategy (D/ST, K, TE)
```
1. "Get top available DEF Week 9" - Find streaming options
2. "Search Vegas odds for [Opponent Team] Week 9" - Check turnover potential
3. "Fantasy football search: Week 9 D/ST streaming recommendations" - Expert advice
4. "Analyze [Streaming Option] Week 9" - Final evaluation
```

### Trade Analysis
```
1. "Analyze [Trade Target] Week 9 PPR" - Evaluate acquisition
2. "Search usage trends for [Your Player] Week 9" - Assess what you're giving up
3. "Find best adds Week 9 RB" - Check waiver alternatives
4. "Search Vegas odds for [Both Teams] Week 9" - Compare situations
```

## Project Structure

```
FantasyFootball/
├── casefiles/               # Decision case files (auto-generated)
├── fantasy_football_server/
│   ├── server.py            # Main MCP server
│   ├── espn_client.py       # ESPN API wrapper
│   ├── tavily_client.py     # Tavily search client
│   ├── requirements.txt     # Python dependencies
│   └── env_template.txt     # Environment configuration template
└── README.md               # This file
```

## Features

- ✅ ESPN Fantasy Football integration (public and private leagues)
- ✅ Real-time web search with Tavily API for expert analysis
- ✅ Comprehensive player analysis with usage trends and snap share data
- ✅ Vegas odds integration for game script analysis
- ✅ Injury reports with fantasy impact assessment
- ✅ Waiver wire recommendations from expert sources
- ✅ Custom fantasy football search capabilities
- ✅ Standardized JSON format for all responses
- ✅ Environment variable configuration for security
- ✅ Full error handling and validation
- ✅ Advanced roster optimization workflows
- ✅ Data-driven decision making tools

## Requirements

- Python 3.8+
- ESPN Fantasy Football account (optional, for private leagues)
- Tavily API key (required for advanced research features - free tier available)
- Cursor IDE with MCP support

## Troubleshooting

### Server Not Starting
- Verify all dependencies are installed: `pip install -r fantasy_football_server/requirements.txt`
- Check that Python is in your PATH
- Review Cursor's MCP logs for error messages

### Configuration Issues
- Ensure `.env` file is in the `fantasy_football_server` directory
- Verify `LEAGUE_ID`, `TEAM_ID`, and `YEAR` are set correctly
- Check that `TAVILY_API_KEY` is valid and not expired

### ESPN League Access
- For public leagues: No authentication needed, just league/team IDs
- For private leagues: Re-copy ESPN cookies if they've expired
- Double-check your league ID from the ESPN URL
- Team IDs are 1-indexed (first team = 1, second team = 2, etc.)

### Tavily Search Issues
- Verify you haven't exceeded the rate limit (1000 searches/month on free tier)
- Ensure internet connection is working
- Check that search queries are specific and well-formed

## License

This project is provided as-is for personal use with fantasy football leagues.
