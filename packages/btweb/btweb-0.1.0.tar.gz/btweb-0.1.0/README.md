<a name="top"></a>
<a name="overview"></a>

# Overview

This module wraps around the get method for the python requests library.

I'm only using it to download files for now.

The reason for this package is for me to reuse it across all my projects.

I'll likely build upon it in the future.

# Prerequisites:

- Python 2.7+

# Installation

* From pypi: `pip3 install btweb`
* From this git repo: `pip3 install git+https://github.com/berttejeda/bert.webadapter.git`<br />
  Note: To install a specific version of the library from this git repo, <br />
  suffix the git URL in the above command with @{ tag name }, e.g.: <br />
  git+https://github.com/berttejeda/bert.webadapter.git@0.0.1

# Usage Examples

## Download a file from a URL using Basic HTTP Authentication

```python

from btweb import WebAdapter

webadapter = WebAdapter()
res = webadapter.get(url, 
  username=username,
  password=password)
```

## Download a file from a URL using Basic HTTP Authentication, caching the result for 30 minutes

```python

from btweb import WebAdapter

webadapter = WebAdapter()
res = webadapter.get(url, 
  username=username,
  password=password,        
  cache=True,
  cache_path='.',
  cache_time=30)
```

# Keyword Args

```
Keyword                                      | Type                    | Possible Values        | Effect                           | Example
-------------------------------------------- | ----------------------- | --------------------------------------------------------------
fail_on_errors                               | bool                    | [True, False]          | Raise an error instead           | webadapter = WebAdapter(fail_on_errors=True)
                                                                       |                        | of ignoring and                  |
                                                                       |                        | returning 'None' or empty string |
```

