# canomaly

<p align="center">
	<img src="imgs/logo.jpeg" alt='Searching for cumulative anomalies.' width="300"/>
</p>

<p align="center">
	<a href="https://github.com/ellerbrock/open-source-badges/" target="_blank">
		<img alt="Open Source Love" src="https://badges.frapsoft.com/os/v1/open-source.png?v=103">
	</a>
	<a href="https://canomaly.readthedocs.io/en/latest/?badge=latest" target="_blank">
		<img alt="Documentation Status" src="https://readthedocs.org/projects/canomaly/badge/?version=latest">
	</a>
	<a href="https://badge.fury.io/py/canomaly" target="_blank">
		<img alt="PyPI version" src="https://badge.fury.io/py/canomaly.svg">
	</a>
	<a href="https://img.shields.io/pypi/dm/canomaly" target="_blank">
		<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/canaomly">
	</a>
	<a href="https://github.com/galenseilis/canomaly/blob/main/LICENSE" target="_blank">
		<img alt="License" src="https://img.shields.io/badge/License-GNU--GPL-blue.svg">
	</a>
	<a href="https://github.com/psf/black" target="_blank">
		<img alt="Code style: Black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
	</a>
</p>

## Project Description
This package detects specific types of anomalies with an emphasis in looking for cumulative changes. 

## Installation
This package can be installed through [PyPi](https://pypi.org/project/canomaly/) using

```
pip install canomaly
```
or 
```
pip3 install canomaly
```

## Example Usage

```python
>>> import pandas as pd
>>> from canomaly.searchtools import cumrexpy
>>> # Get some data
>>> data = {
            'date': [
                '2018-11-20',
                '2018-11-21',
                '2018-11-22',
                '2018-11-22',
                '2018-11-23',
                '2018-11-24'],
            'email': [
                'john.doe@example.com',
                'jane.smith@example.com',
                'bob-johnson_123@example.com',
                'sarah@mydomain.co.uk',
                'frank@mydomain.com',
                'jessica_lee@mydomain.com'
                    ]
            }
>>> df = pd.DataFrame(data)
>>> df['date'] = pd.to_datetime(df['date'])
>>> # Extract regular expressions
>>> cumrexpy(df, 'email', 'date')
date
2018-11-20                           [^john\.doe@example\.com$]
2018-11-21                [^[a-z]{4}\.[a-z]{3,5}@example\.com$]
2018-11-22    [^[a-z]{4,5}[.@][a-z]+[.@][a-z]+\.[a-z]{2,3}$,...
2018-11-23    [^frank@mydomain\.com$, ^[a-z]{4,5}[.@][a-z]+[...
2018-11-24    [^frank@mydomain\.com$, ^[a-z]+[.@_][a-z]+[.@]...
Name: email_grouped, dtype: object
```

We can look at the results in markdown for clarity.

| date                | email_grouped                                                                                                    |
|:--------------------|:-----------------------------------------------------------------------------------------------------------------|
| 2018-11-20 00:00:00 | ['^john\\.doe@example\\.com$']                                                                                   |
| 2018-11-21 00:00:00 | ['^[a-z]{4}\\.[a-z]{3,5}@example\\.com$']                                                                        |
| 2018-11-22 00:00:00 | ['^[a-z]{4,5}[.@][a-z]+[.@][a-z]+\\.[a-z]{2,3}$', '^bob\\-johnson_123@example\\.com$']                           |
| 2018-11-23 00:00:00 | ['^frank@mydomain\\.com$', '^[a-z]{4,5}[.@][a-z]+[.@][a-z]+\\.[a-z]{2,3}$', '^bob\\-johnson_123@example\\.com$'] |
| 2018-11-24 00:00:00 | ['^frank@mydomain\\.com$', '^[a-z]+[.@_][a-z]+[.@][a-z]+\\.[a-z]{2,3}$', '^bob\\-johnson_123@example\\.com$']    |

## Build Documentation Locally
```bash
cd /path/to/canomaly/docs
make html
```


![Star History Chart](https://api.star-history.com/svg?repos=galenseilis/canomaly&type=Date)

