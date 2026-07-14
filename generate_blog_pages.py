from __future__ import annotations

import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import markdown
import yaml


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "content-blog"
OUTPUT_DIR = ROOT / "blog"
INDEX_PATH = ROOT / "blog.html"
MIN_DATE = datetime.min.replace(tzinfo=timezone.utc)


NAV = """<nav class="nav-menu" aria-label="Primary navigation">
        <div class="nav-item has-menu">
          <a href="about.html">About</a>
          <div class="dropdown about-dropdown" role="menu">
            <div class="dropdown-group">
              <span>EleutherAI</span>
              <a href="about.html">About</a>
              <a href="staff.html">Staff</a>
            </div>
          </div>
        </div>
        <div class="nav-item has-menu">
          <a href="research.html">Research</a>
          <div class="dropdown research-dropdown" role="menu">
            <div class="dropdown-group">
              <span>NLP</span>
              <a href="research.html#nlp">Model Training</a>
              <a href="research.html#nlp">Evaluation</a>
              <a href="research.html#nlp">Multilingual</a>
              <a href="research.html#nlp">Datasets</a>
            </div>
            <div class="dropdown-group">
              <span>Interpretability</span>
              <a href="research.html#interpretability">Circuits</a>
              <a href="research-training-dynamics.html">Training Dynamics</a>
              <a href="research.html#interpretability">Data Attribution</a>
            </div>
            <div class="dropdown-group">
              <span>Alignment</span>
              <a href="research.html#alignment">Open Weight Safety</a>
              <a href="research.html#alignment">Behavioral Safety</a>
            </div>
            <div class="dropdown-group">
              <span>Other Research</span>
              <a href="research.html#other-research">Other Modalities</a>
              <a href="research.html#other-research">Privacy and Security</a>
            </div>
          </div>
        </div>
        <a href="community.html">Community</a>
        <a href="blog.html">Blog</a>
        <a class="support" href="support.html">Support Us</a>
      </nav>"""

SOCIAL_LINKS = """<div class="social-links" aria-label="Social links">
        <a class="social-link" href="mailto:contact@eleuther.ai" aria-label="Email EleutherAI">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4z"></path><path d="m4 7 8 6 8-6"></path></svg>
        </a>
        <a class="social-link" href="https://discord.gg/zBGx3azzUn" aria-label="EleutherAI Discord">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 8.5c3.4-1.8 6.6-1.8 10 0l1.3 6.9c-1.2 1-2.5 1.6-4 1.9l-.8-1.3c-1 .2-2 .2-3 0l-.8 1.3c-1.5-.3-2.8-.9-4-1.9L7 8.5z"></path><path d="M9.5 13h.1"></path><path d="M14.4 13h.1"></path></svg>
        </a>
        <a class="social-link" href="https://github.com/EleutherAI" aria-label="EleutherAI GitHub">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 18c-3-1-4-3.4-4-6.1a8 8 0 0 1 16 0c0 2.7-1 5.1-4 6.1"></path><path d="M9 19v-3.2c0-.9.7-1.6 1.6-1.6h2.8c.9 0 1.6.7 1.6 1.6V19"></path><path d="M9 8.2 7.8 5.8"></path><path d="m15 8.2 1.2-2.4"></path></svg>
        </a>
        <a class="social-link" href="https://twitter.com/AiEleuther" aria-label="EleutherAI on X">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 5 12 14"></path><path d="M18 5 6 19"></path></svg>
        </a>
      </div>"""

FOOTER = f"""<footer>
    <div class="wrap">
      <span>EleutherAI</span>
      {SOCIAL_LINKS}
    </div>
  </footer>"""


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, parts[2].strip()


def parse_date(value) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif not value:
        return MIN_DATE
    else:
        raw = str(value).replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError:
            return MIN_DATE
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_people(value) -> str:
    if not value:
        return "EleutherAI"
    if isinstance(value, str):
        return value
    return ", ".join(str(item) for item in value)


def shortcode_attrs(raw: str) -> dict:
    attrs = {}
    for key, value in re.findall(r"([A-Za-z0-9_-]+)\s*=\s*\"([^\"]*)\"", raw):
        attrs[key] = value
    return attrs


def clean_markdown(text: str) -> str:
    def figure(match: re.Match) -> str:
        attrs = shortcode_attrs(match.group(1))
        src = attrs.get("src")
        if not src:
            return ""
        alt = escape(attrs.get("alt") or attrs.get("caption") or "")
        caption = escape(attrs.get("caption") or "")
        caption_html = f"<figcaption>{caption}</figcaption>" if caption else ""
        return f'<figure><img src="{src}" alt="{alt}">{caption_html}</figure>'

    def collapse(match: re.Match) -> str:
        attrs = shortcode_attrs(match.group(1))
        summary = escape(attrs.get("summary") or "Details")
        return f"<details><summary>{summary}</summary>"

    text = text.replace("](huggingface.co/)", "](https://huggingface.co/)")
    text = text.replace("](PPO Sentiments Example)", "](https://github.com/CarperAI/trlx/blob/main/examples/ppo_sentiments.py)")
    text = text.replace("](./year-one/)", "](year-one.html)")
    text = re.sub(r"\]\(\[(https?://[^\]]+)\]\(https?://[^\)]+\)\)", r"](\1)", text)
    text = re.sub(r"\{\{<\s*figure\b([^}]*)>\}\}", figure, text)
    text = re.sub(r"\{\{<\s*/\s*figure\s*>\}\}", "", text)
    text = re.sub(r"\{\{<\s*collapse\b([^}]*)>\}\}", collapse, text)
    text = re.sub(r"\{\{<\s*/\s*collapse\s*>\}\}", "</details>", text)
    text = re.sub(r"\{\{<\s*discord/channel\s+\"([^\"]+)\"\s*>\}\}", r"\1", text)
    text = re.sub(r"\{\{<\s*discord/handle[^>]*name=\"([^\"]+)\"[^>]*>\}\}", r"\1", text)
    text = re.sub(r"\{\{<\s*discord/mention\s+\"([^\"]+)\"\s*>\}\}", r"\1", text)
    text = re.sub(r"\{\{<[^>]+>\}\}", "", text)
    text = text.replace("<date datetime=", "<time datetime=")
    text = text.replace("</date>", "</time>")
    return text


def absolutize_assets(html: str, article: bool) -> str:
    prefix = "../" if article else ""
    html = html.replace('href="/https://cadentj.github.io/demo//', 'href="https://cadentj.github.io/demo/')
    html = html.replace('href="/mechanistic-anomaly-detection-research-update/"', 'href="mad_research_update.html"')
    html = html.replace('href="/mad_research_update/"', 'href="mad_research_update.html"')
    html = html.replace('href="/mad_research_update_2/"', 'href="mad_research_update_2.html"')
    html = html.replace('href="/why-release-a-large-language-model/"', 'href="why-release-a-large-language-model.html"')
    html = html.replace('src="/images/blog/', f'src="{prefix}assets/blog/')
    html = html.replace('href="/images/blog/', f'href="{prefix}assets/blog/')
    html = html.replace('src="/images/research-log/', f'src="{prefix}assets/current-site/research-log/')
    html = html.replace('href="/images/research-log/', f'href="{prefix}assets/current-site/research-log/')
    html = html.replace('src="/images/', f'src="{prefix}assets/current-site/')
    html = html.replace('href="/images/', f'href="{prefix}assets/current-site/')
    html = html.replace('src="images/blog/', f'src="{prefix}assets/blog/')
    html = html.replace('href="images/blog/', f'href="{prefix}assets/blog/')
    html = html.replace('src="../images/blog/', f'src="{prefix}assets/blog/')
    html = html.replace('href="../images/blog/', f'href="{prefix}assets/blog/')
    html = html.replace('href="x"', 'href="#"')
    return html


def render_markdown(text: str, article: bool) -> str:
    html = markdown.markdown(
        clean_markdown(text),
        extensions=["fenced_code", "tables", "toc", "sane_lists"],
        output_format="html5",
    )
    return absolutize_assets(html, article=article)


def excerpt(body: str, description: str | None) -> str:
    if description:
        return str(description)
    plain = re.sub(r"\s+", " ", re.sub(r"[\*_#>`\[\]\(\)]", " ", body)).strip()
    return plain[:220] + ("..." if len(plain) > 220 else "")


def rel_nav(nav: str, depth: int) -> str:
    if depth == 0:
        return nav
    prefix = "../"
    return re.sub(r'href="(?!https?:|mailto:|#)([^"]+)"', lambda m: f'href="{prefix}{m.group(1)}"', nav)


def page_shell(title: str, body: str, depth: int = 0) -> str:
    css = "../site-page.css" if depth else "site-page.css"
    logo = "../assets/eleutherai-logo.svg" if depth else "assets/eleutherai-logo.svg"
    home = "../index.html" if depth else "index.html"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | EleutherAI</title>
  <link rel="stylesheet" href="{css}">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="{home}" aria-label="EleutherAI home">
        <img class="brand-logo" src="{logo}" alt="EleutherAI">
      </a>
      {rel_nav(NAV, depth)}
    </div>
  </header>
{body}
</body>
</html>
"""


def load_posts() -> list[dict]:
    posts = []
    source_files = sorted(SOURCE_DIR.glob("*.md")) + sorted(SOURCE_DIR.glob("*/index.md"))
    for fp in source_files:
        if fp.name == "_index.md":
            continue
        meta, body = parse_front_matter(fp.read_text(errors="ignore"))
        if str(meta.get("draft", "")).lower() == "true":
            continue
        date = parse_date(meta.get("date"))
        title = str(meta.get("title") or fp.stem.replace("-", " ").title())
        posts.append(
            {
                "slug": fp.parent.name if fp.name == "index.md" else fp.stem,
                "title": title,
                "date": date,
                "date_label": date.strftime("%b %-d, %Y") if date != MIN_DATE else "",
                "authors": normalize_people(meta.get("author") or meta.get("contributors")),
                "categories": meta.get("categories") or [],
                "description": excerpt(body, meta.get("description")),
                "body_html": render_markdown(body, article=True),
            }
        )
    posts.sort(key=lambda item: item["date"], reverse=True)
    return posts


def write_article(post: dict) -> None:
    body = f"""  <main>
    <article class="blog-article">
      <div class="wrap article-wrap">
        <a class="back-link" href="../blog.html">Back to blog</a>
        <header class="article-header">
          <h1>{escape(post["title"])}</h1>
          <p class="article-dek">{escape(post["description"])}</p>
          <div class="article-meta">
            <span>{escape(post["date_label"])}</span>
            <span>{escape(post["authors"])}</span>
          </div>
        </header>
        <div class="article-body">
          {post["body_html"]}
        </div>
      </div>
    </article>
  </main>
  {FOOTER}"""
    (OUTPUT_DIR / f"{post['slug']}.html").write_text(page_shell(post["title"], body, depth=1))


def write_index(posts: list[dict]) -> None:
    featured = posts[:3]
    recent = posts[3:18]
    featured_html = "\n".join(
        f"""          <article class="card blog-card">
            <h3>{escape(post["title"])}</h3>
            <p class="item-meta">{escape(post["date_label"])}</p>
            <p>{escape(post["description"])}</p>
            <a class="link" href="blog/{post["slug"]}.html">Read post -></a>
          </article>"""
        for post in featured
    )
    recent_html = "\n".join(
        f"""          <article class="artifact-row">
            <div>
              <h3><a href="blog/{post["slug"]}.html">{escape(post["title"])}</a></h3>
              <p class="item-meta">{escape(post["date_label"])} · {escape(post["authors"].split(",")[0])}</p>
              <p>{escape(post["description"])}</p>
            </div>
          </article>"""
        for post in recent
    )
    body = f"""  <main>
    <section class="hero">
      <div class="wrap">
        <h1>Research notes, announcements, and technical essays.</h1>
        <p class="lede">Long-form technical notes, release announcements, and essays from EleutherAI researchers and collaborators.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <div>
            <h2>Latest posts</h2>
          </div>
          <p class="section-intro">Research notes, release writeups, policy commentary, and community updates from EleutherAI researchers and collaborators.</p>
        </div>
        <div class="grid">
{featured_html}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <div>
            <h2>Recent archive</h2>
          </div>
          <p class="section-intro">Browse recent posts from the EleutherAI archive, including research notes, release writeups, policy commentary, and community updates.</p>
        </div>
        <div class="artifact-table blog-list">
{recent_html}
        </div>
      </div>
    </section>
  </main>
  {FOOTER}"""
    INDEX_PATH.write_text(page_shell("Blog", body, depth=0))


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    posts = load_posts()
    for post in posts:
        write_article(post)
    write_index(posts)
    print(f"Generated {len(posts)} blog posts")


if __name__ == "__main__":
    main()
