# SuportAdminPanel

> Admin panel for suuport all products semiotics team


-> [Details](./bot_telegram/README.md)


### For Development
+ python3.11
+ create venv `python -m venv venv` 
  + init venv:
    + Linux | Mac: `sources venv/bin/activate`
    +  Windows:  `venv\Scripts\activate`
+ install poetry: `pip install poetry`
+ install linters: `pip install -r requirements/lint.txt`

+ install libs `poetry install`
+ install pre-commit `pre-commit install`
  + contains:
    + [isort](https://pycqa.github.io/isort/)
    + [black](https://black.readthedocs.io/en/stable/)
    + [flake8](https://flake8.pycqa.org/en/latest/index.html#quickstart)
    + [mypy](https://mypy.readthedocs.io/en/stable/index.html)
+ init git flow `git flow init`