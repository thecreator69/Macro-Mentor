# Passive AI Blog Starter (Programmatic SEO + GitHub Pages)

This repo lets you run a **fully automated, passive AI blog** that posts N times per week from a seed keyword list.
Monetize with **affiliate links**, display ads, or digital products. Deploys on **GitHub Pages**; new posts are created on a schedule by **GitHub Actions**.

## What it does
- Reads seed keywords from `data/keywords.csv`
- Uses an LLM to generate a research-backed outline + article
- Injects your affiliate links and CTA blocks
- Saves a Jekyll-compatible post into `_posts/`
- Commits and publishes on a schedule via GitHub Actions cron

## Quick start
1. **Create a new GitHub repo** and upload these files (or push with git).
2. Enable **GitHub Pages**: Settings → Pages → Build from branch → `main` (or `master`) → `/ (root)`.
3. Add a **Repository secret**: Settings → Secrets and variables → Actions → New repository secret:
   - `OPENAI_API_KEY` = your API key (or another OpenAI-compatible provider key)
4. (Optional) Edit `_config.yml` title/description and `config.yaml` niche & monetization.
5. Commit. The scheduled workflow will run automatically (you can also trigger it manually in the Actions tab).

## Local dev
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python generate_posts.py --once
```
This creates a single new post in `_posts/` for today.

## Notes
- Keep seed keywords **niche and specific** (programmatic SEO). Aim for 200–1000 long-tail keywords.
- Start with **2–3 posts/week**. Scale once you confirm indexing and traffic.
- Respect platform policies for AI content. Add helpful tables, sources, and disclaimers.

