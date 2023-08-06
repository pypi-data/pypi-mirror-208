format:
	black .
	ruff --fix .

test:
	black --check .
	ruff .
	mypy
	$(MAKE) test-pytest

test-pytest:
	python -m pytest --cov=sporestack --cov-fail-under=39 --cov-report=term --durations=3 --cache-clear

build-dist:
	rm dist/* || true
	# This should result in a reproducible wheel.
	SOURCE_DATE_EPOCH=$$(git log -1 --format=%ct) flit build

# This shouldn't be needed often, but is nice for validation.
twine-check:
	twine check --strict dist/*

servedocs:
	pdoc sporestack

publish: build-dist
	# The sdist isn't reproducible, but the wheel is.
	python -m twine upload dist/*
