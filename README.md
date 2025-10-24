# ESPN Fantasy Football MCP Integration

A comprehensive MCP (Model Context Protocol) server for integrating ESPN Fantasy Football with Cursor AI.

## Quick Start

### 1. Install Dependencies

```bash
cd fantasy_football_server
pip install -r requirements.txt
```

### 2. Set Up Credentials

Create a `.env` file in the `fantasy_football_server` directory with your API credentials:

```bash
# ESPN Fantasy (Optional - only for private leagues)
ESPN_S2=your_espn_s2_cookie
ESPN_SWID=your_swid_cookie

# Tavily Search (Required for web search features)
TAVILY_API_KEY=your_tavily_api_key
```

**Getting Your Tavily API Key:**
1. Sign up at [https://tavily.com/](https://tavily.com/)
2. Copy your API key from the dashboard
3. Free tier includes 1000 searches per month

### 3. Get Your Credentials

**ESPN (Public Leagues):**
- No credentials needed! Just use your league ID.

**ESPN (Private Leagues):**
- Log into ESPN Fantasy
- Extract `espn_s2` and `SWID` cookies from your browser

For detailed instructions, see [fantasy_football_server/README.md](fantasy_football_server/README.md)

### 4. Restart Cursor

After setting up credentials, restart Cursor to load the MCP server. The server will be available as "espn-fantasy-football" in your MCP tools.

## Available Tools

### ESPN Fantasy (Current League Data)
- `get_roster` - Get full team roster with stats
- `is_available` - Check if a player is on waivers
- `get_top_available` - Get top N available players by position

### Tavily Search (Real-time Research)
- `summarize_players` - Quick matchup summaries for multiple players
- `injury_report` - Detailed injury reports and fantasy impact
- `analyze_player` - Comprehensive player analysis with expert rankings
- `compare_players` - Head-to-head player comparisons
- `find_best_adds` - Expert waiver wire recommendations
- `analyze_schedule` - Schedule strength analysis for playoffs
- `check_weather` - Weather impact on outdoor games
- `fantasy_football_search` - Custom fantasy football searches

## Example Usage in Cursor

Once the MCP server is running, you can use it in Cursor:

**Basic Queries:**
```
"Get my ESPN roster for league 12345, team 1"
"Is Patrick Mahomes available in ESPN league 67890?"
"Show me the top 5 available running backs in my league"
```

**Advanced Research:**
```
"Analyze Saquon Barkley for Week 9 in my PPR league"
"Compare Travis Kelce vs George Kittle for this week"
"Get injury report for Justin Jefferson"
"Find the best waiver wire pickups for Week 9"
"Check the playoff schedule for my running backs"
```

**Roster Optimization:**
```
"Help me optimize my roster for Week 9"
"Who should I pick up to replace my injured RB?"
"Should I start Player A or Player B this week?"
```

## Project Structure

```
.cursor/
├── mcp_config.json          # MCP server configuration
fantasy_football_server/
├── server.py                # Main MCP server
├── espn_client.py           # ESPN API wrapper
├── requirements.txt         # Python dependencies
└── README.md               # Detailed documentation
```

## Documentation

For complete setup instructions, troubleshooting, and API details, see:
- [fantasy_football_server/README.md](fantasy_football_server/README.md)

## Features

- ✅ ESPN Fantasy Football integration (public and private leagues)
- ✅ Real-time web search with Tavily API
- ✅ Get team rosters with player stats and injury info
- ✅ Check player availability on waivers
- ✅ Get top available players by position
- ✅ Quick matchup summaries for multiple players
- ✅ Detailed injury reports and fantasy impact analysis
- ✅ Comprehensive player analysis with expert rankings
- ✅ Head-to-head player comparisons for start/sit decisions
- ✅ Expert waiver wire recommendations
- ✅ Schedule strength analysis for playoff planning
- ✅ Weather impact assessment for outdoor games
- ✅ Standardized JSON format
- ✅ Environment variable configuration for security
- ✅ Full error handling and validation

## Requirements

- Python 3.8+
- ESPN account (optional, for private ESPN leagues)
- Tavily API key (required for web search features - free tier available)

## Troubleshooting

### Server Not Starting
- Verify all dependencies are installed: `pip install -r fantasy_football_server/requirements.txt`
- Check that Python is in your PATH
- Review Cursor's MCP logs for error messages

### Authentication Errors
- For ESPN: Re-copy cookies if they've expired
- For Tavily: Verify API key is correct in .env file

### Tavily Search Errors
- Check that TAVILY_API_KEY is set in your .env file
- Verify you haven't exceeded the rate limit (1000 searches/month on free tier)
- Ensure internet connection is working

### Can't Find League or Team
- Double-check your league ID from the URL
- Team IDs are 1-indexed (first team = 1, second team = 2, etc.)
- Ensure the league year is correct for ESPN

For more help, see the detailed [troubleshooting guide](fantasy_football_server/README.md#troubleshooting).

## License

This project is provided as-is for personal use with fantasy football leagues.
