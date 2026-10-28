# Refero

A Claude plugin that bundles the **Refero Design** skill and a read-only Refero
MCP connector. Before any UI, product-design, landing-page, dashboard, or visual
polish work, the skill makes research mandatory: it searches curated visual
styles, real product screens, and user flows, locks concrete references, and
turns them into a decision ledger and design direction. The bundled craft
references cover typography, color, spacing, motion, icons, copywriting, and
anti-AI-slop checks.

## Use it

In Claude on the web, open **Customize → Plugins → Add → Add marketplace → Add
from a repository**, enter `osa822630-droid/refero_skill`, then add the
**Refero** plugin. Start a chat and ask for a design (for example, "research
references and design a pricing page"). Open **Customize → Plugins → Refero →
Connectors** and connect the Refero connector to enable live style, screen, and
flow searches. Without the connector the skill still works with its bundled
craft references and any references you provide. In Claude Code and Cowork the
connector connects automatically when you sign in through OAuth.

From Claude Code, add the marketplace and install in one step:

```text
/plugin install refero --marketplace osa822630-droid/refero_skill
```

## Data

The skill sends search queries and requested reference IDs to Refero's read-only
MCP server at `https://api.refero.design/mcp`. The connector authenticates with
your Refero account through the browser (OAuth); no API keys, tokens, or
credentials are stored in this plugin. Research queries and results are handled
under Refero's privacy policy. The plugin does not write to your files or upload
your project.

## Layout

This folder is the plugin root: it holds `.claude-plugin/plugin.json`, the
`skills/` directory, `.mcp.json`, the icon/banner assets, this README, and a
copy of the license. The marketplace catalogs live two levels up at
`.claude-plugin/marketplace.json` (Claude) and
`.agents/plugins/marketplace.json` (Codex). Keeping the plugin inside its own
folder is required for claude.ai's **Add marketplace** sync; a plugin that is
also the marketplace root exposes two manifests in one directory and fails
remote validation.
