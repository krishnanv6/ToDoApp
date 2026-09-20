#!/bin/bash
INPUT=$(cat)

echo "$INPUT" >> "$CLAUDE_PROJECT_DIR/.claude/hooks/hook-input.log"
echo "---" >> "$CLAUDE_PROJECT_DIR/.claude/hooks/hook-input.log"

# Try common field names across Bash/PowerShell tool schemas
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // .tool_input.script // .tool_input.code // empty')

# Check the command text itself
if echo "$COMMAND" | grep -iq "drop" && echo "$COMMAND" | grep -iq "table"; then
  echo "Blocked: dropping tables is not allowed" >&2
  exit 2
fi

# Inspect script files only when passed to an interpreter (not in git/other tool args)
while IFS= read -r FILE; do
  if [ -f "$FILE" ]; then
    if grep -iq "drop" "$FILE" && grep -iq "table" "$FILE"; then
      echo "Blocked: script file '$FILE' contains a destructive schema statement" >&2
      exit 2
    fi
  fi
done < <(echo "$COMMAND" | grep -oiE '(python3?|bash|sh|node|sqlite3|pwsh|powershell\.exe)\s+"?([^"'\'' ]+\.(py|sh|sql|ps1|bat|cmd))"?' | grep -oiE '[^"'\'' ]+\.(py|sh|sql|ps1|bat|cmd)' | sort -u)

exit 0
