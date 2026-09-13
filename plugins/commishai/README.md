# CommishAI plugin

CommishAI is a skills-only Agent Plugin for ChatGPT and Codex. It reads live ESPN
fantasy football data through a bundled Python CLI and provides two workflows:

- `fantasy-weekly`: lineup, waiver-wire, add/drop, injury, and streaming advice.
- `fantasy-trades`: offer evaluation, trade-market matching, and pitch drafting.

## Local requirements

Install the Python dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Keep `league.yaml` and `.env` in the project where you use CommishAI. The CLI
searches the working directory and its parents for `league.yaml`; ESPN credentials
remain local and are never included in the plugin package.

Validate connectivity from the repository root:

```bash
python plugins/commishai/scripts/ff.py doctor
```

The ESPN client is read-only. CommishAI recommends lineup and transaction changes,
but the manager executes them in ESPN.
