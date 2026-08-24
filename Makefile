.DEFAULT_GOAL := build
.PHONY: data data-offline data-live-strict test check-tools check-links check-generated freshness build build-offline build-blog build-blog-offline build-all build-all-offline build-all-strict-offline build-production build-blog-production verify verify-live serve serve-offline serve-blog serve-blog-offline serve-all serve-all-offline

PORT ?= 8060
MAIN_PORT ?= 8067
BLOG_PORT ?= 8068
BIND ?= 127.0.0.1
PYTHON ?= python3
HUGO ?= hugo

data:
	$(PYTHON) generate_hugo_data.py
	$(PYTHON) scripts/refresh_youtube_reading_groups.py

data-offline:
	$(PYTHON) generate_hugo_data.py --offline
	$(PYTHON) scripts/refresh_youtube_reading_groups.py --offline

data-live-strict:
	$(PYTHON) generate_hugo_data.py --strict
	$(PYTHON) scripts/refresh_youtube_reading_groups.py --strict

test:
	$(PYTHON) -m pytest -q

check-tools:
	$(PYTHON) scripts/check_tools.py

check-links:
	$(PYTHON) scripts/check_site_links.py public public-blog

check-generated:
	git diff HEAD --exit-code -- eleutherai_papers.csv data/generated

freshness:
	$(PYTHON) scripts/report_data_freshness.py

build: data
	$(HUGO) --cleanDestinationDir

build-offline: data-offline
	$(HUGO) --cleanDestinationDir

build-blog:
	$(HUGO) --config hugo-blog.toml --destination public-blog --cleanDestinationDir

build-blog-offline: build-blog

build-all: build build-blog

build-all-offline: build-offline build-blog-offline

build-all-strict-offline: data-offline
	$(HUGO) --cleanDestinationDir --panicOnWarning
	$(HUGO) --config hugo-blog.toml --destination public-blog --cleanDestinationDir --panicOnWarning

build-production: test data
	$(HUGO) --cleanDestinationDir --panicOnWarning

build-blog-production: test
	$(HUGO) --config hugo-blog.toml --destination public-blog --cleanDestinationDir --panicOnWarning

verify: check-tools test build-all-strict-offline check-links check-generated
	git diff --check

verify-live: check-tools test data-live-strict
	$(HUGO) --cleanDestinationDir --panicOnWarning
	$(HUGO) --config hugo-blog.toml --destination public-blog --cleanDestinationDir --panicOnWarning
	$(PYTHON) scripts/check_site_links.py public public-blog
	$(PYTHON) scripts/report_data_freshness.py --require-live
	git diff HEAD --exit-code -- eleutherai_papers.csv data/generated
	git diff --check

serve: data
	hugo server --bind $(BIND) --port $(PORT)

serve-offline: data-offline
	hugo server --bind $(BIND) --port $(PORT)

serve-blog:
	hugo server --config hugo-blog.toml --destination public-blog --disableFastRender --bind $(BIND) --port $(PORT)

serve-blog-offline: serve-blog

serve-all: data
	@$(MAKE) _serve-all

serve-all-offline: data-offline
	@$(MAKE) _serve-all

.PHONY: _serve-all
_serve-all:
	@set -e; \
	main_url="http://$(BIND):$(MAIN_PORT)/"; \
	blog_url="http://$(BIND):$(BLOG_PORT)/"; \
	MAIN_BASE_URL="$$main_url" BLOG_BASE_URL="$$blog_url" $(HUGO) server --disableFastRender --bind $(BIND) --port $(MAIN_PORT) & main_pid=$$!; \
	MAIN_BASE_URL="$$main_url" BLOG_BASE_URL="$$blog_url" $(HUGO) server --config hugo-blog.toml --destination public-blog --disableFastRender --bind $(BIND) --port $(BLOG_PORT) & blog_pid=$$!; \
	trap 'kill $$main_pid $$blog_pid 2>/dev/null || true' INT TERM EXIT; \
	wait $$main_pid $$blog_pid
