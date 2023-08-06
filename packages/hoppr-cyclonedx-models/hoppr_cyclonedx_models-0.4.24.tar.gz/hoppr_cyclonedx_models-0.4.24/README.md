# hoppr_cyclonedx_models

[![pypi](https://img.shields.io/pypi/v/hoppr-cyclonedx-models)](https://pypi.org/project/hoppr-cyclonedx-models)
[![downloads](https://pepy.tech/badge/hoppr-cyclonedx-models/month)](https://pepy.tech/project/hoppr-cyclonedx-models)
[![versions](https://img.shields.io/badge/python-3.7.2-blue.svg)](https://gitlab.com/hoppr/hoppr-cyclonedx-models)
[![license](https://img.shields.io/gitlab/license/hoppr/hoppr-cyclonedx-models)](https://gitlab.com/hoppr/hoppr-cyclonedx-models/-/blob/main/LICENSE)

Serializable CycloneDX Models.   Quickly get up and running with models generated directly off the specification.

Current generated models can be found here: [Generated Models](https://gitlab.com/hoppr/hoppr-cyclonedx-models/-/tree/main/hoppr_cyclonedx_models)

## Installation

Install using `pip install -U hoppr-cyclonedx-models` or `poetry add hoppr-cyclonedx-models`.  

## A Simple Example:

```py
from hoppr_cyclonedx_models.cyclonedx_1_4 import Component

data = {'type': 'library', 'purl': 'pkg:pypi/django@1.11.1', 'name': 'django', 'version': '1.11.1'}

component = Component(**data)
print(component.purl)
```

## Contributing

For guidance setting up a development environment and how to make a contribution to _hoppr-cyclonedx-models_, see [Contributing to Hoppr](https://hoppr.dev/docs/development/contributing).
