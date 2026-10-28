# Refero Design in Claude on the web

This guide covers **Claude on the web** (claude.ai chat in the browser, the
desktop app's Chat tab, and mobile). There is no shell, no file tools, and no
`/mcp` command; the same guidance applies to any similar chat-only environment.
Cowork and Claude Code should keep following the main
[SKILL.md](../SKILL.md) as written.

The research-first methodology does not change. Only the way you reach tools and
deliver work changes.

## What loads in chat

| Plugin component | In chat |
| --- | --- |
| `skills/refero-design/SKILL.md` and its references | Loads; Claude can consult the bundled craft guides |
| Remote MCP server declared in `.mcp.json` | Listed on the plugin's **Connectors** tab after the user adds/connects it |
| Commands | Load as skills |
| Hooks, agents, local MCP servers | Ignored |

## Connecting Refero

Installing the plugin does **not** sign you in. In chat:

1. Open **Customize → Plugins → Refero → Connectors**.
2. If the Refero connector says **Not added**, add it; if it says
   **Not connected**, connect it.
3. Complete the Refero OAuth sign-in in the browser window that opens.
4. Start a **new chat** after the connector shows **Connected**.

Live research requires a Refero account with access to the MCP tools (a paid
Refero plan). If tools are unavailable, do not invent styles, screens, or flows.
Say which research layer is unavailable and use bundled craft references plus
user-provided screenshots, URLs, or design systems as the evidence base. The
same reference-lock and decision-ledger rules still apply.

## Research without a shell

- Call the `refero_*` tools through the connected connector. Tool names may be
  prefixed by the connector name; use the names your client shows.
- Do not run `claude mcp add`, `/mcp`, Bash, Glob, Read, or any file-editing
  command. Those steps in the main skill are for Claude Code and Cowork only.
- Full style records are large. Retrieve 3-4 at a time and summarize the traits
  you will actually use instead of dumping every result into the conversation.
- When a bundled reference guide cannot be opened, follow the short version of
  its rules inside `SKILL.md` and say which guide you could not load.

## Delivering the work

Chat cannot edit a repository, run a dev server, or take a screenshot. For
implementation requests:

- Provide complete, copy-pasteable code (single-file HTML/CSS, a component, or a
  full file list with paths) in the message or an artifact.
- Include the reference lock and decision ledger as a short fenced block so the
  decisions survive into a new chat or a Project's knowledge:

```text
Refero design state
Brief: [what/who/platform/goal/tone]
Evidence: [connected connector + styles/screens/flows used, or craft references]
Primary reference: [name + 3-5 traits to preserve]
Borrow only: [1-2 narrow details]
Token commitments: [canvas, type, accent, radius, border/shadow, media]
Decision ledger: [choice -> source -> reason]
Open checks: [what the user must run locally]
```

- State plainly which visual-QA, rendering, or test checks you could not run.
  Ask the user to run them and paste back a screenshot or the failing output,
  then compare it against the locked direction and fix drift.
- Keep imagery roles honest: if a needed photo or illustration cannot be
  produced here, specify the aspect ratio, subject, and art direction for a
  placeholder or an asset the user adds later.

## Quality gate on the web

Before replying, confirm the usual gate in `SKILL.md`, plus:

- Did I avoid claiming live Refero research when the connector was not
  connected?
- Did I keep every major choice traceable to a reference, the user's brief, or a
  craft rule?
- Did I hand over runnable code and name the checks I could not run?
- Did I leave a compact state block the user can carry into another chat?
