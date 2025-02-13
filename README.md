# PDF Merger with clickable ToC

Quick and dirty project in Python to merge few PDF into one. Very practical for applications files ...

Schema example :

```
{
    "Introduction": {
        "Garde": ["intro.pdf"],
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
