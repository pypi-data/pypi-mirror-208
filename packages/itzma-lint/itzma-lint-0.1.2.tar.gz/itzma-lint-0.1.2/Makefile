.ONESHELL:
#########
# BUILD #
#########
develop:
	python -m pip install pylint
	python -m pip install coverage
	python -m pip install check-manifest
	python -m pip install black
	python -m pip install mypy
	python -m pip install inflection

build:
	python setup.py build build_ext --inplace

install:
	python -m pip install .

#########
# LINTS #
#########
lint:
	python -m black src .
	pylint --rcfile=.pylintrc $$(git ls-files '*.py')

# alias
lints: lint

format:
	python -m black src .

# alias
fix: format

check:
	check-manifest -v

# alias
checks: check

annotate:
	python -m mypy src

#########
# TESTS #
#########
test: ## clean and run unit tests
	python -m unittest src/tests/test_itzma.py

coverage:  ## clean and run unit tests with coverage
	python -m coverage run -m unittest src/tests/test_itzma.py
	python -m coverage report
	python -m coverage json

# Alias
tests: test

###########
# VERSION #
###########
show-version:
	bump2version --dry-run --allow-dirty setup.py --list | grep current | awk -F= '{print $2}'

patch:
	bump2version patch

minor:
	bump2version minor

major:
	bump2version major

########
# DIST #
########
dist-build:  # Build python dist
	python setup.py sdist bdist_wheel

dist-check:
	python -m twine check dist/*

dist: clean build dist-build dist-check  ## Build dists

publish:  # Upload python assets
	echo "would usually run python -m twine upload dist/* --skip-existing"

#########
# CLEAN #
#########
deep-clean: ## clean everything from the repository
	git clean -fdx

clean: ## clean the repository
	rm -rf .coverage coverage cover htmlcov logs build dist *.egg-info .pytest_cache

############################################################################################

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'

.PHONY: develop build install lint lints format fix check checks annotate test coverage show-coverage tests show-version patch minor major dist-build dist-check dist publish deep-clean clean help