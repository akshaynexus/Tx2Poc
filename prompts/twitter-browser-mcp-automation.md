# Twitter Browser MCP Hourly Automation Prompt

Use `$twitter-browser-mcp` to monitor these X/Twitter accounts for new crypto attack-event alerts:

- `@DefimonAlerts`
- `@PeckShieldAlert`

Use this runtime directory for state and outputs:

`twitter-events/`

Use this state file:

`twitter-events/state.json`

Run the skill's state `window` command first. If the state file is missing or has no `last_check_time`, use the returned default of `now - 10 minutes`. Check only tweets posted after `last_check_time` and no later than `check_started_at`.

For each account, use browser MCP to inspect new posts. For any post that may describe an exploit, hack, drain, attack transaction, suspicious transaction, flash-loan attack, oracle manipulation, reentrancy, bridge incident, or other on-chain security event, open the tweet detail page and inspect the first 10 visible replies/comments because transaction hashes or chain details may be in replies.

Extract protocol name, chain, transaction hash or transaction URL, attack type, loss/assets if stated, tweet URL, tweet id, posting account, timestamp, whether evidence came from the tweet or a reply, and a short evidence paraphrase. Preserve exact transaction hashes and use `unknown` for missing fields.

Write any run artifacts, screenshots, raw snippets, or structured alert output under the runtime directory. Do not write runtime output into the skill folder.

After all configured accounts are checked successfully, advance the state by running the skill's `complete` command with the original `check_started_at` timestamp, checked account list, and number of alerts found. Do not advance the state if browser access or account checks failed before completion.

Report only new matching attack alerts. If none are found, report the checked window, checked accounts, and that no new matching alerts were found.
