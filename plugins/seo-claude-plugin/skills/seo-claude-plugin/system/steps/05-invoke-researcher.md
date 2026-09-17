# Step 05: Invoke Researcher Plugin

ACTION: Ask the user how many resources they require (typically 8–12 for a full article). Retain as `resources-requested`.

## Locate the researcher plugin

ACTION: Run the following to find the researcher plugin's research skill. The plugin cache root is derived from `${CLAUDE_PLUGIN_ROOT}` (resolved by the framework to this plugin's installation path) so no home directory is hardcoded:

```bash
find "$(dirname "$(dirname "${CLAUDE_PLUGIN_ROOT}")")" \
  -path "*/researcher/*/skills/research/SKILL.md" \
  | sort -V | tail -1
```

IF no path is returned:
  STOP and inform the user: "The researcher plugin is not installed. Please install it from the plugin marketplace and then continue."
ELSE:
  Retain the found path as `researcher-skill-md`.
  Derive `researcher-plugin-root` by stripping `/skills/research/SKILL.md` from the end of the path.

## Execute the researcher inline

NOTE: The researcher plugin determines its project directory from context. Because `project-dir` is already established in this session, the researcher will use it without any remapping. Resources will be written to `{project-dir}/resources/` and the candidate links index to `{project-dir}/candidate-links.md`.

When following the researcher's instructions, interpret any reference to `${CLAUDE_PLUGIN_ROOT}` as `researcher-plugin-root` (so the researcher can read its own bundled files — anti-thrashing rules, resource selection rules, PDF retrieval runbook). All project-level output paths flow through `project-dir` as already established.

ACTION: Read `researcher-skill-md` and follow all instructions it contains as a direct continuation of this workflow, with:
- `project-dir` = already-established `project-dir`
- Research mode = **directed**
- Topic, direction, goal = contents of `{project-dir}/topic-direction-goal.md` (the researcher's Phase 0 will detect this file and skip interactive setup)
- Resources requested = `resources-requested`

ACTION: When the researcher's synthesis phase is complete, continue immediately to step 06 — do not STOP.
