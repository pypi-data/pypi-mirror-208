#!make

DIR := ${CURDIR}

.PHONY: build
build:
	docker buildx build --tag=sigexport .

.PHONY: test
test: build
	docker run --rm --entrypoint='' -v $(DIR):/fresh sigexport:latest bash -c 'cd /fresh && pip install . pytest pytest-cov && pytest --cov=sigexport'
