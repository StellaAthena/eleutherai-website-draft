.DEFAULT_GOAL := build
.PHONY: data data-offline build build-offline serve serve-offline

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

serve: data
	hugo server --bind $(BIND) --port $(PORT)

serve-offline: data-offline
	hugo server --bind $(BIND) --port $(PORT)
