---
description: Run deep research then dispatch Jules with findings for informed updates
---

# Research Update Workflow

Run deep research first, then dispatch Jules with research-enriched prompts.

## Steps

1. Run deep research for all repos (or a specific one):

```bash
python scripts/deep_research.py --local
```

Or for a single repo:

```bash
python scripts/deep_research.py --repo GeminiDocs --local
```

2. Preview the research-enriched Jules prompts:

```bash
python scripts/trigger_jules.py --use-research --dry-run
```

3. Dispatch Jules with the research context:

```bash
python scripts/trigger_jules.py --use-research
```

4. For maximum efficiency, combine smart dispatch + research:

```bash
python scripts/trigger_jules.py --smart --use-research
```

This only dispatches repos that have both new changes AND research findings.

5. Full autonomous pipeline (research → Jules → auto-merge):

```bash
python scripts/trigger_jules.py --smart --use-research --auto-merge
```

## How It Works

1. `deep_research.py` generates reports in `data/research_reports/`
2. `trigger_jules.py --use-research` reads those reports
3. Research findings are injected into the Jules prompt as context
4. Jules gets focused, specific tasks instead of generic "crawl everything"

## Example Enhanced Prompt

Standard prompt: *"Follow the instructions in JULES.md..."*

Research-enhanced: *"Follow the instructions in JULES.md... Research Context: Claude Code v2.1.64 released with new --streaming flag, updated OAuth flow, and deprecation of legacy token format. Prioritize updating commands.md and changelog.md."*

## Notes

- Requires `GEMINI_API_KEY` for research and `JULES_API_KEY` for Jules
- Research reports are saved to `data/research_reports/` and committed by the weekly workflow
