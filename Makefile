.DEFAULT_GOAL := build
.PHONY: data data-offline build build-offline build-blog build-blog-offline build-all build-all-offline serve serve-offline serve-blog serve-blog-offline

PORT ?= 8060
BIND ?= 127.0.0.1

data:
	python3 generate_hugo_data.py

data-offline:
	python3 generate_hugo_data.py --offline

build: data
	hugo --cleanDestinationDir

build-offline: data-offline
	hugo --cleanDestinationDir

build-blog:
	hugo --config hugo-blog.toml --destination public-blog --cleanDestinationDir

build-blog-offline: build-blog

build-all: build build-blog

build-all-offline: build-offline build-blog-offline

serve: data
	hugo server --bind $(BIND) --port $(PORT)

serve-offline: data-offline
	hugo server --bind $(BIND) --port $(PORT)

serve-blog:
	hugo server --config hugo-blog.toml --destination public-blog --disableFastRender --bind $(BIND) --port $(PORT)

serve-blog-offline: serve-blog
