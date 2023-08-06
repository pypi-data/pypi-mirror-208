# Railtown AI Python SDK

## Setup

1. `pip install railtownai`
   1. For alpha, add `--extra-index-url https://testpypi.python.org/pypi` to the top of your requirements.txt
   1. add `railtownai==0.0.4`
1. `import railtownai`
1. `railtownai.init('YOUR_RAILTOWN_API_KEY')`
1. Log errors with the following example

```python

import railtownai

railtownai.init('YOUR_RAILTOWN_API_KEY')

try:
   some_code_that_throws_an_error()

except Exception as e:
   railtownai.log(e)
```

## Development Setup

1. Install [Python 3.10](https://www.python.org/downloads/release/python-310/)
1. Create Python virtual environment: `python -m venv .venv`
1. Use `.venv\Scripts\activate.ps1` to start python virtual environment
   1. If you on Mac OS X...
      1. `python3 -m venv .venv`
      1. `source .venv/bin/activate`
1. Install flit `pip install flit`
1. Install dependencies `flit install`

## Contributing

- Use [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/#summary) style messages
- Rebase off `main` before submitting a PR
