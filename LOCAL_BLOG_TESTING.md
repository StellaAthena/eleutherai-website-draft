# Local Blog Testing Setup

When developing locally and testing the blog integration, you can point the main site's Blog link to your local blog build.

## Quick Start

Terminal 1 - Main site:
```bash
cd /Users/stellabiderman/Documents/research/codex/eleutherai_homepage_draft
BLOG_BASE_URL="http://127.0.0.1:1313/" make serve-offline
```

Terminal 2 - Blog:
```bash
cd /Users/stellabiderman/Documents/research/codex/eleutherai_homepage_draft
PORT=1313 hugo server --config hugo-blog.toml --bind 127.0.0.1
```

Then open http://127.0.0.1:8060/ in your browser. The "Blog" link in the navigation will point to http://127.0.0.1:1313/ locally.

## How It Works

The `BLOG_BASE_URL` environment variable overrides the default `blogBaseURL` parameter in `hugo.toml`:
- **Default (production)**: `https://blog.eleuther.ai/`
- **Override (local testing)**: Set via `BLOG_BASE_URL` environment variable

This is configured in `layouts/partials/header.html`:
```go
{{- $blogBaseURL := site.Params.blogBaseURL | default "https://blog.eleuther.ai/" -}}
{{- $blogURL := os.Getenv "BLOG_BASE_URL" | default $blogBaseURL -}}
```

## Production Deployment

For production, the environment variable is not set, so the default `https://blog.eleuther.ai/` is used automatically.
