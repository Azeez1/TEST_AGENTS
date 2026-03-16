---
globs:
  - "*_TEAM/outputs/**"
  - "outputs/**"
description: Enforce correct output routing and git hygiene
---

# Output Routing Rules

## Where Generated Content Goes
- ALL generated deliverables go to `{TEAM}/outputs/{subfolder}/` (gitignored)
- Common subfolders: `blog_posts/`, `social_media/`, `images/`, `videos/`, `emails/`, `landing_pages/`, `reports/`, `presentations/`
- Read `output_paths.json` from team memory BEFORE writing to confirm canonical paths

## What Goes Where
| Folder | Git Tracked | Use Case |
|--------|-------------|----------|
| `{TEAM}/outputs/` | NO | Real deliverables, client work, production content |
| `{TEAM}/examples/` | YES | Curated reference materials, portfolio pieces |
| `{TEAM}/templates/` | YES | Reusable starting frameworks |

## Routing Rules
- NEVER write generated content to `examples/` or `templates/` without explicit user instruction
- NEVER create output files at the repository root (e.g., `TEST_AGENTS/blog_post.md` is WRONG)
- NEVER use ambiguous relative paths like `outputs/file.md` — always include team prefix
- Correct: `MARKETING_TEAM/outputs/blog_posts/ai-trends-2026.md`
- Wrong: `outputs/blog_post.md`, `./blog_post.md`, `blog_post.md`

## Cross-Team Outputs
- Each team writes ONLY to its own `outputs/` directory
- If a workflow produces outputs for multiple teams, each team's agent saves to its own folder
- Shared deliverables that span teams go to the requesting team's outputs folder
