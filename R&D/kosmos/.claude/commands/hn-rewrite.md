Read {{arg1}} (either a file path or GitHub issue URL) and rewrite it in a technical, matter-of-fact style suitable for a discerning Hacker News audience.

**Input Detection:**
- If {{arg1}} starts with `http://` or `https://` - fetch the URL content first using WebFetch
- Otherwise, treat {{arg1}} as a file path and read the file

Apply these transformations:

1. **Remove all emojis** (🎉, ✅, 🚀, etc.)
2. **Remove exclamation points** - replace with periods or rephrase
3. **Eliminate bombastic language**:
   - "amazing" → "effective"
   - "incredible" → "notable"
   - "awesome" → "useful"
   - "perfect" → "appropriate"
   - Remove superlatives: "best", "greatest", "most powerful"
4. **Convert to technical prose**:
   - Use precise terminology
   - Focus on facts, not enthusiasm
   - Replace marketing speak with technical descriptions
   - Use passive voice where appropriate
5. **Maintain all technical content**:
   - Keep code examples exactly as-is
   - Preserve command-line instructions
   - Maintain technical accuracy
   - Keep all links and references

Output the rewritten content with the same structure and information, but in a neutral, technical tone that respects the reader's intelligence and avoids hype.

**Usage Examples:**
```
/hn-rewrite README.md
/hn-rewrite https://github.com/jimmc414/Kosmos/issues/11
/hn-rewrite docs/announcement.md
```
