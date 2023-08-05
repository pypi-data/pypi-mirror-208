# pytracking-cdm
Package for internal use at the Center for Data and Methods. It contains tools for doing sequence analysis on eyetracking fixation data.

Documentation can be found [here](https://pytracking-cdm.onrender.com/).

## Contribution

### Git Branch Policies and CI
Merging with main requires a pull request that has to pass a check defined in the ci.yml github workflow. The check ensures the code is formatted, linted, docstrings exist and are styles correctly and run tests. You can't push directly to main. Create a branch, then open a PR for merging with main. Tip: [You can create branches directly from issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-a-branch-for-an-issue).  

### Dev Setup

This package is developed with poetry. Find installation instructions [here](https://python-poetry.org/docs/)
1. Clone Repo
2. Install dependencies: 
```bash
poetry install
```
3. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```
This will ensure the code is formatted, linted, docstrings exist and are styled correctly and run tests. 

### IDE requirements
Install [Black](https://github.com/psf/black) for formatting tooltips and [Ruff](https://github.com/charliermarsh/ruff) for linting tooltips in your IDE.

### Code documentation
This project uses [pydocstyle](https://github.com/PyCQA/pydocstyle) to enforce the existance and style of docstrings. [NumPys style guidelines](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard) is used. To check whether your docstrings are consistent with these guidelines, run:
```bash
poetry run pydocstyle ./pytracking_cdm
```

### Testing 
To test ensure the package functions as intended after making changes, run:
```bash
poetry run pytest -svv     
```
Tests are defined in `./tests/test_pytracking_cdm.py`


