"""Enforce the layout claude.ai accepts when a repository is added as a marketplace.

claude.ai clones the repository, reads .claude-plugin/marketplace.json, and
validates every plugin entry on its own. Its validator is stricter than
`claude plugin validate`:

* `"source": "."` and object sources are rejected for plugins inside the repo —
  only `./`-prefixed relative paths work;
* the plugin root must not be the marketplace root (two manifests in one
  `.claude-plugin/` folder behaves differently on the CLI and on claude.ai);
* under the default strict mode each entry needs a `.claude-plugin/plugin.json`
  whose `name` matches the entry;
* a top-level `bin/` directory makes chat and Cowork refuse the plugin;
* `SKILL.md` frontmatter must stay inside the Agent Skills specification.

These tests keep that shape intact so **Add marketplace → Add from a repository**
does not fail with the generic "check the repository URL" error.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "refero"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
MCP_URL = "https://api.refero.design/mcp"

SPEC_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMPONENT_FIELDS = {"skills", "commands", "agents", "hooks", "outputStyles", "themes"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(path: Path):
    """Read top-level frontmatter keys without a YAML dependency."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return None


class ClaudeMarketplaceTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load(MARKETPLACE)
        self.version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

    def test_required_top_level_fields(self):
        self.assertTrue(NAME_PATTERN.match(self.catalog["name"]))
        self.assertTrue(self.catalog["owner"]["name"])
        self.assertTrue(self.catalog["description"])
        self.assertEqual(self.catalog["version"], self.version)
        self.assertTrue(self.catalog["plugins"])
        # A remote $schema fetch has broken Claude Desktop marketplace sync.
        self.assertNotIn("$schema", self.catalog)

    def test_marketplace_root_has_only_the_catalog(self):
        manifests = sorted(p.name for p in MARKETPLACE.parent.iterdir() if p.is_file())
        self.assertEqual(manifests, ["marketplace.json"])
        self.assertFalse((ROOT / ".claude-plugin" / "plugin.json").exists())
        self.assertNotIn("marketplace.json", [p.name for p in PLUGIN_MANIFEST.parent.iterdir()])

    def test_entry_points_at_a_self_contained_plugin_folder(self):
        for entry in self.catalog["plugins"]:
            with self.subTest(plugin=entry["name"]):
                self.assertTrue(NAME_PATTERN.match(entry["name"]))
                self.assertTrue(entry["description"])
                source = entry["source"]
                self.assertIsInstance(source, str, "claude.ai needs a relative path source")
                self.assertTrue(source.startswith("./"), f"{source!r} must start with ./")
                self.assertNotIn("..", Path(source).parts)
                root = (ROOT / source).resolve()
                self.assertEqual(root, PLUGIN.resolve())
                self.assertTrue((root / ".claude-plugin" / "plugin.json").is_file())
                self.assertTrue((root / "README.md").is_file())
                self.assertTrue((root / "LICENSE").is_file())
                self.assertTrue((root / ".mcp.json").is_file())
                self.assertFalse((root / "bin").exists())
                # strict: false + component fields + plugin.json = conflicting manifests.
                self.assertNotIn(False, [entry.get("strict", True)])
                self.assertFalse(COMPONENT_FIELDS & entry.keys())

    def test_plugin_manifest_matches_the_entry_and_version(self):
        manifest = load(PLUGIN_MANIFEST)
        for entry in self.catalog["plugins"]:
            self.assertEqual(manifest["name"], entry["name"])
            self.assertEqual(entry["version"], self.version)
        self.assertEqual(manifest["version"], self.version)
        self.assertTrue(manifest["description"])
        self.assertTrue(manifest["license"] or (PLUGIN / "LICENSE").is_file())
        self.assertNotIn("$schema", manifest)
        self.assertEqual(manifest["icon"], "./assets/icon.png")
        self.assertTrue((PLUGIN / "assets/icon.png").is_file())

    def test_bundled_connector_is_remote_and_secret_free(self):
        plugin_mcp = load(PLUGIN / ".mcp.json")
        server = plugin_mcp["mcpServers"]["refero"]
        self.assertEqual(server["type"], "http")
        self.assertEqual(server["url"], MCP_URL)
        self.assertNotIn("Authorization", json.dumps(plugin_mcp))
        self.assertEqual(
            (ROOT / ".mcp.json").read_text(encoding="utf-8"),
            (PLUGIN / ".mcp.json").read_text(encoding="utf-8"),
        )

    def test_skills_follow_the_agent_skills_specification(self):
        skill_files = sorted(PLUGIN.glob("skills/*/SKILL.md"))
        self.assertTrue(skill_files, "the plugin must expose at least one skill")
        for path in skill_files:
            with self.subTest(skill=path.parent.name):
                fields = frontmatter(path)
                self.assertIsNotNone(fields, "SKILL.md needs YAML frontmatter")
                self.assertFalse(
                    set(fields) - SPEC_FIELDS,
                    f"{path.parent.name} uses non-spec frontmatter claude.ai can reject",
                )
                self.assertEqual(fields["name"], path.parent.name)
                self.assertTrue(NAME_PATTERN.match(fields["name"]))
                self.assertTrue(fields["description"])
                self.assertLessEqual(len(fields["description"]), 1024)
                self.assertNotIn("disable-model-invocation", fields)


class CodexCatalogTests(unittest.TestCase):
    def test_codex_catalog_points_at_the_same_plugin_folder(self):
        catalog = load(CODEX_MARKETPLACE)
        self.assertTrue(catalog["plugins"])
        for entry in catalog["plugins"]:
            source = entry["source"]
            self.assertEqual(source["source"], "local")
            self.assertEqual(source["path"], "./plugins/refero")
            root = (ROOT / source["path"]).resolve()
            self.assertTrue((root / ".codex-plugin" / "plugin.json").is_file())
            self.assertEqual(
                load(root / ".codex-plugin" / "plugin.json")["name"], entry["name"]
            )


class WebSupportTests(unittest.TestCase):
    def test_skill_documents_the_web_surface(self):
        skill = PLUGIN / "skills" / "refero-design" / "SKILL.md"
        self.assertIn("## Claude on the web", skill.read_text(encoding="utf-8"))
        guide = skill.parent / "references" / "claude-web.md"
        self.assertTrue(guide.is_file())
        text = guide.read_text(encoding="utf-8")
        for phrase in ("Connectors", "OAuth", "no shell", "state"):
            self.assertIn(phrase, text)

    def test_plugin_readme_explains_data_and_usage(self):
        text = (PLUGIN / "README.md").read_text(encoding="utf-8")
        for phrase in ("Use it", "Data", MCP_URL, "Add marketplace"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
