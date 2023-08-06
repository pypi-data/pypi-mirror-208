# t-python-markdown

A simple to use markdown generator for Python.


## Installation
```
pip install t-python-markdown
```


## Example

```python
from t_python_markdown import Document, Header, Paragraph, Sentence, Bold, Table, UnorderedList
import time
import requests

j = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json").json()
bpi = j["bpi"]

front_matter = {
    "title": j["chartName"],
    "authors": ["A.U.Thor"],
    "date": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
}

doc = Document(front_matter)
doc >> Header(j["chartName"], 1)
doc >> Paragraph([j["disclaimer"]])
al = [("--:" if isinstance(_, (int, float)) else ":-:" if _.startswith("&") else ":--") for _ in bpi[list(bpi.keys())[0]].values()]
t = Table([_.replace("_", " ").title() for _ in bpi[list(bpi.keys())[0]].keys()], alignment=al)
doc >> t
ul = UnorderedList()
doc >> Paragraph("Bitcoin Price Index")
doc >> ul

for k, v in bpi.items():
  t >> [_ for _ in bpi[k].values()]
  ul >> Sentence([Bold(k), bpi[k]["description"]])

# Write markdown to file
doc.write("example.md")
```

Saved as `example.py` then running `python example.py` results in:

```markdown
---
title: Bitcoin
authors:
- A.U.Thor
date: '2023-02-25T14:17:02Z'
...

# Bitcoin

This data was produced from the CoinDesk Bitcoin Price Index (USD). Non-USD currency data converted using hourly conversion rate from openexchangerates.org

| **Code** | **Symbol** | **Rate** | **Description** | **Rate Float** |
| :-- | :-: | :-- | :-- | --: |
| USD | &#36; | 23,007.6135 | United States Dollar | 23007.6135 |
| GBP | &pound; | 19,224.9778 | British Pound Sterling | 19224.9778 |
| EUR | &euro; | 22,412.7746 | Euro | 22412.7746 |

Bitcoin Price Index

- **USD** United States Dollar.
- **GBP** British Pound Sterling.
- **EUR** Euro.
```


## Usage
For usage, see https://www.cix.co.uk/~toyne/t-python-markdown/usage/


## Recent Changelog
**1.4.0**  
- Improve support for embedded lists and tables. Now able to wrap child items in other markdown elements

**1.3.2**  
- Add support for attribute lists when processing embedded lists

**1.3.1**  
- Add support for attribute lists when processing embedded tables

**1.3.0**  
- Add support for tables and lists embedded in other tables and lists

**1.2.1**  
- Bring into line with docs site

**1.2.0**  
- Add support for Strikethrough