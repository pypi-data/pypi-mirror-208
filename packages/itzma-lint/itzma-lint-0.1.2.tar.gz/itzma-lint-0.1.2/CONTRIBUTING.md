<h1 align="center"> ⭑･ﾟﾟ･*:༅｡.｡༅:*ﾟ:*:✼✿ &ensp; ITZMA Lint (It's my lint!) &ensp; ✿✼:*ﾟ:༅｡.｡༅:*･ﾟﾟ･⭑ </h1>

<p align="center"> "Your Lint, Your Rules" </p>

![GitHub](https://img.shields.io/github/license/tchitrakorn/itzma-lint)
![GitHub issues](https://img.shields.io/github/issues/tchitrakorn/itzma-lint)
[![Itzma workflow](https://github.com/tchitrakorn/itzma-lint/actions/workflows/test.yml/badge.svg)](https://github.com/tchitrakorn/itzma-lint/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/tchitrakorn/itzma-lint/branch/main/graph/badge.svg?token=46KL4N7H8P)](https://codecov.io/gh/tchitrakorn/itzma-lint)

<h2>Overview</h1>

Itzma Lint is an open source project and welcomes any contribution! Please follow the steps below to help you get started.

<h2>Pre-requisites</h2>
Please make sure you have ```python >= 3.9```

<h2>Dependencies</h2>

For development purposes, please install the following dependencies:

* pylint
* coverage
* black
* check-manifest
* mypy

Use the following command for the installation:
```
make develop
```

<h2>Steps</h2>
1. Make sure the pre-requisites are satisfied.
2. Fork the repository and ```git clone``` to a development branch.
3. Install all necessary dependencies.
4. Make some changes! To add or edit Itzma checks, check out ```checks.py```. To add helper functions, check out ```helpers.py```. The main program is ```flake8_itzma.py```.
5. Add some tests for your new features! All tests and sample tests are located in ```tests/```.
6. Run ```make tests``` and ```make coverage``` and achieve at least 80% coverage.
7. Run ```make lint``` to make sure everything looks good and properly formatted.
8. Make a PR! If everything looks good and all tests are passed, we will merge it to main.

<h2>Future Improvements</h2>
If you're wondering, "What should I contribute?", here are some suggestions:
* More unique customized checks!
* A way to incorporate user's input(s) to personalize their very own linter!
* A way to further utilize nltk and other NLP tools!


<h3>That's it! Thank you for contributing to Itzma!</h3>