# Custom Slash Commands

This directory contains custom slash commands for Claude Code.

## Available Commands

### `/hn-rewrite <filename>`

Rewrites a document in a technical, matter-of-fact style suitable for Hacker News readers.

**What it does:**
- Removes all emojis (🎉, ✅, 🚀, etc.)
- Eliminates exclamation points
- Strips bombastic/marketing language ("amazing", "incredible", "awesome")
- Converts to neutral, technical prose
- Preserves all code examples and technical content

**Usage:**
```bash
/hn-rewrite INITIAL_E2E_PLAN.md
/hn-rewrite README.md
/hn-rewrite docs/getting-started.md
```

**Example transformation:**
```
Before: "🎉 Amazing! This feature is the best and works perfectly!"
After: "This feature functions as designed and meets requirements."
```

**When to use:**
- Before sharing documentation on Hacker News
- For technical blog posts
- When you need neutral, professional tone
- To remove marketing speak from technical docs

**Note:** After creating/modifying slash commands, you may need to restart Claude Code or start a new conversation for them to be recognized.

## Creating New Commands

To create a new slash command:

1. Create a `.md` file in `.claude/commands/`
2. Name it `command-name.md` (accessible as `/command-name`)
3. Write the prompt using `{{arg1}}`, `{{arg2}}` for arguments
4. Restart Claude Code or start new conversation

Example:
```markdown
# .claude/commands/summarize.md
Summarize the file `{{arg1}}` in 3 bullet points.
```

Usage: `/summarize myfile.txt`
