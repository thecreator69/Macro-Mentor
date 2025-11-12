#!/usr/bin/env python3
import os, csv, re, json, time, argparse, datetime, random, hashlib
import yaml, requests
from pathlib import Path
from jinja2 import Template
from slugify import slugify

ROOT = Path(__file__).resolve().parent
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
TEMPLATE = Template((ROOT / "templates" / "post.md.j2").read_text())

def load_keywords():
    rows = []
    with open(ROOT / "data" / "keywords.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("keyword"):
                rows.append(row)
    random.shuffle(rows)
    return rows

def pick_keywords(rows, n=1):
    return rows[:n]

def call_openai_chat(messages, model=None, max_tokens=1500, temperature=0.5):
    """Simple OpenAI Chat Completions client. Set OPENAI_API_KEY env var."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY env var missing")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model or CFG["llm"]["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]

def md_escape(s):
    return s.replace("|", "\|")

def generate_article(keyword, category):
    sys = (
        "You are an evidence-based fitness writer for college students. "
        "Write concise, scannable, practical content with tables, bullets, and concrete macros. "
        "Cite mainstream sources non-verbally (e.g., 'per USDA data') without links."
    )
    user = f"""Keyword: {keyword}
Audience: {CFG['niche']['audience']}
Voice: {CFG['niche']['voice']}

Produce JSON with fields:
title, hook, description, outline (array of H2s), article (markdown 900-1200 words), tags (array)."""
    out = call_openai_chat(
        [{"role":"system","content":sys},{"role":"user","content":user}],
        model=CFG["llm"]["model"],
        max_tokens=CFG["llm"]["max_tokens"],
        temperature=CFG["llm"]["temperature"],
    )
    try:
        data = json.loads(out.strip("` \n"))
    except json.JSONDecodeError:
        # Try to extract JSON via naive braces matching
        start = out.find("{")
        end = out.rfind("}")
        data = json.loads(out[start:end+1])
    return data

def write_post(data, keyword, category):
    today = datetime.date.today()
    slug = slugify(data["title"])[:80]
    fm_date = today.strftime("%Y-%m-%d %H:%M:%S %z").strip()
    canonical = (CFG["seo"].get("canonical_base") or "").rstrip("/")
    canonical_url = f"{canonical}/{'/'.join([str(today.year), f'{today.month:02d}', f'{today.day:02d}', slug])}/" if canonical else ""

    # Render template
    md = TEMPLATE.render(
        title=md_escape(data["title"]),
        date=today.isoformat(),
        category=category or "posts",
        tags=CFG["seo"]["tags"],
        author=CFG["seo"]["author"],
        description=md_escape(data.get("description","")),
        hook=md_escape(data.get("hook","")),
        body_md=data["article"],
        canonical_url=canonical_url,
        products=CFG["monetization"]["products"],
        cta_text=CFG["monetization"]["primary_cta_text"],
        cta_url=CFG["monetization"]["primary_cta_url"],
        affiliate_disclaimer=CFG["niche"]["affiliate_disclaimer"],
        amazon_tag=CFG["monetization"]["amazon_tag"],
    )

    # Jekyll expects _posts/YYYY-MM-DD-title.md
    filename = f"{today:%Y-%m-%d}-{slug}.md"
    path = ROOT / "_posts" / filename
    path.write_text(md, encoding="utf-8")
    return path

def main(once=False):
    rows = load_keywords()
    picks = pick_keywords(rows, n=CFG["posting"]["posts_per_run"])
    created = []
    for row in picks:
        data = generate_article(row["keyword"], row.get("category","posts"))
        path = write_post(data, row["keyword"], row.get("category","posts"))
        created.append(str(path))
    print("Created posts:", json.dumps(created, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="create a single post and exit")
    args = ap.parse_args()
    main(once=args.once)
