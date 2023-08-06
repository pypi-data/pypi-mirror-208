# Railtown AI Python SDK

## Setup

1. `pip install railtownai`
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
