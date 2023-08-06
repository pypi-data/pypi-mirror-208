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

### Document
`Document` takes one optional argument, front matter, a dictionary, and is output as YAML.

```python
doc = Document(front_matter)
doc.write("example.md")
```

### Header
`Header` takes two arguments, a title and a level. The level relates to the header tags `<h1>` - `<h6>`:

```python
header = Header("Header Title", level)
doc >> header
```

### Paragraph
`Paragraph` takes a list of _sentences_. A _sentence_ could be a simple string or a `Sentence` (see below).

```python
p = Paragraph(["A sentence.", Sentence(["The quick", "brown fox"])])
doc >> p
```

### Sentence
`Sentence` takes three arguments, an array of strings or other markdown objects, a separator (defaults to space) and an end character (defaults to a full stop).

```python
s = Sentence(["The quick", "brown fox"], end="!")
doc >> s
```

### Horizontal Rule
`HorizontalRule` takes no arguments and produces a `---` in the output.

```python
hr = HorizontalRule()
doc >> hr
```

### Link
`Link` takes three arguments, a title, a url and an optional alternate title.

```python
l = Link("Title", "http://localhost/")
doc >> l
```

### Image
`Image` takes two arguments, a title and a url (path to image).

```python
i = Image("Picture", "/images/nice_piccie.png")
doc >> i
```

### Bold
`Bold` takes one argument, the text to be bolded.

```python
bt = Bold("Bold Text")
doc >> bt
```

### Italic
`Italic` takes one argument, the text to be italicised.

```python
it = Italic("Italic Text")
doc >> it
```

### Bold/Italic
`BoldItalic` takes one argument, the text to be bolded and italicised.

```python
bit = BoldItalic("Bold/Italic Text")
doc >> bit
```

### Strikethrough
`Strikethrough` takes one argument, the text to strikethrough.

```python
st = Strikethrough("Strikethrough Text")
doc >> st
```

### Code
`Code` takes one argument, the text to be output as code.

```python
c = Code("find / -name README.md")
doc >> c
```

### Code Block
`CodeBlock` takes one argument, the text to output as code in a block.

```python
cb = CodeBlock("ls\nfind / -name README.md")
doc >> cb
```

### Unordered List
`UnorderedList` takes one optional argument, a list of items. The resultant object can have further items added.

```python
ul = UnorderedList()
ul >> "List entry 1"
ul >> "List entry 2"
doc >> ul
```

### Ordered List
`OrderedList` takes one optional argument, a list of items. The resultant object can have further items added.

```python
ol = OrderedList()
ol >> "List entry 1"
ol >> "List entry 2"
doc >> ol
```

### Table
`Table` takes two arguments, a list of column headers and a list of column alignments. The resultant object is then used to add rows, each row being a list of columns. The number of column alignments is adjusted to match the number of columns. If the number of alignments is too small, the last alignment is repeated to fill the missing ones. If no alignment is provided, it defaults to centred (`":-:"`).

```python
t = Table(["Id", "Description"], alignment=[":--"])
t >> ["1", "One"]
t >> ["2", "Two"]
doc >> t
```

Since 1.3.0 it is now possible to easily embed tables in both lists and tables as follows:

```python
t = Table(["Id", "Description"], alignment=["--:"])
t >> ["1", "One"]
t >> ["2", UnorderedList(["Item a", "Item b"])]
ul = UnorderedList(["Item 1", t, "Item 3"])
doc >> ul
```

resulting in:

> - Item 1
> - <table><thead><tr><th style="text-align: right;"><strong>Id</strong></th><th style="text-align: right;"><strong>Description</strong></th></tr></thead><tbody><tr><td style="text-align: right;">1</td><td style="text-align: right;">One</td></tr><tr><td style="text-align: right;">2</td><td style="text-align: right;"><ul><li>Item a</li><li>Item b</li></ul></td></tr></tbody></table>
> - Item 3

_Note: Embedding requires the [Markdown](https://pypi.org/project/Markdown/) package to be installed._
