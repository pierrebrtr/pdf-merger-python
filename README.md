# PDF Merger with clickable ToC

Quick and dirty project in Python to merge few PDF into one. Very practical for applications files...

Schema example with TOC after introduction:

```python
{
    "Introduction": {
        "Garde": ["intro.pdf"],
        "Table des Matières": {"_toc_": True},  # TOC will be placed here
    },
    "Person 1": {
        "General Information": ["info1.pdf"],
        "ID": ["id1.pdf"],
        "Work Contract": ["contract1.pdf"],
    },
    "Person 2": {
        "General Information": ["info2.pdf"],
        "ID": ["id2.pdf"],
        "Work Contract": ["contract2.pdf"],
    },
}
```

The Table of Contents will be automatically inserted after the introduction page. You can move the `"Table des Matières"` entry anywhere in the schema to control where the TOC appears in the final document.
