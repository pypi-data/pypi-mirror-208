<h1 align="center"> ⭑･ﾟﾟ･*:༅｡.｡༅:*ﾟ:*:✼✿ &ensp; ITZMA Lint (It's my lint!) &ensp; ✿✼:*ﾟ:༅｡.｡༅:*･ﾟﾟ･⭑ </h1>

<p align="center"> "Your Lint, Your Rules" </p>

![GitHub](https://img.shields.io/github/license/tchitrakorn/itzma-lint)
![GitHub issues](https://img.shields.io/github/issues/tchitrakorn/itzma-lint)
[![Itzma workflow](https://github.com/tchitrakorn/itzma-lint/actions/workflows/test.yml/badge.svg)](https://github.com/tchitrakorn/itzma-lint/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/tchitrakorn/itzma-lint/branch/main/graph/badge.svg?token=46KL4N7H8P)](https://codecov.io/gh/tchitrakorn/itzma-lint)

<h2>Overview</h1>

Do you love using a linter but want even more personalized rules? Building off a traditional lint, ITZMA offers additional features such as:

*  Enforcing all functions that change the state of the programs to begin with verbs
*  Enforcing all functions that return values to be nouns
*  Enforcing array names to be plural nouns
*  ... and more!

Of course, ITZMA also contains traditional features, such as:

* Enforcing all booleans to begin with pre-allowed verbs
* Enforcing consistent case types
* ... and more!

ITZMA is a linter that lets you decide how your code will look and helps you enforce those rules!

<h2>Installation and Usage</h1>

I'm excited to share Itzma with everyone!
To use Itzma locally, please install the following dependencies:
* flake8
* ast
* inflection
* nltk

Use the following command to install the dependencies:
```
pip install <library name>
```

To use Itzma to check your Python file, simply run the following in your terminal in the appropriate directory:

```
flake8  <filename>
```

A message will be printed for each Itzma check that was not passed!
For more information about Itzma checks and error messages, check out checks.py.

<br>
<br>

<div align="center">
  
![](https://media.tenor.com/8C22RnZpGo4AAAAM/cute-llama.gif)
  
</div>

> *"I'm a llama, not an ITZMA (lint)!"*
