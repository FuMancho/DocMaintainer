---
description: Use Jules to fix GitHub issues labeled with jules-fix across any repo
---

# Jules Auto-Fix Workflow

Leverage Jules's autonomous coding to fix issues directly via GitHub labels.

## How It Works

1. Create an issue in any of your repos
2. Add the `jules-fix` label
3. Jules picks it up and opens a PR with the fix

## Setup (per repo)

Add this GitHub Action to any repo where you want auto-fix:

```yaml
# .github/workflows/jules-fix.yml
name: Jules Auto-Fix
on:
  issues:
    types: [labeled]

jobs:
  jules-fix:
    if: github.event.label.name == 'jules-fix'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Clone DocMaintainer tools
        run: git clone --depth 1 https://github.com/FuMancho/DocMaintainer.git /tmp/DocMaintainer

      - name: Trigger Jules
        env:
          JULES_API_KEY: ${{ secrets.JULES_API_KEY }}
        run: |
          python /tmp/DocMaintainer/scripts/trigger_jules.py \
            --repo ${{ github.event.repository.name }} \
            --auto-merge \
            --timeout 3600
```

## Or manually from DocMaintainer

```bash
# Fix a specific issue  
python scripts/trigger_jules.py --repo Guardian

# With auto-merge
python scripts/trigger_jules.py --repo Guardian --auto-merge
```

## Best Practices

- Write clear issue titles — Jules uses them as task descriptions
- Include reproduction steps for bugs
- Tag issues with complexity labels if available
- Jules works best with AGENTS.md in the repo for context
