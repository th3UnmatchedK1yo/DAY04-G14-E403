---
name: deduplicate
track: team
kind: local_transformer
team_authored: true
requires_env: []
inputs: [items, strategy]
outputs: [items, input_count, item_count, removed_count]
side_effect: false
---
# deduplicate

Removes duplicate research items while preserving the first-seen order.

Use this tool only when a list of research items has already been collected.
It does not search, fetch, summarize, or publish content.

`strategy` can be:

- `url`: compare canonical URLs and ignore common tracking parameters.
- `title`: compare normalized titles.
- `url_or_title`: treat either matching URL or matching title as a duplicate.
