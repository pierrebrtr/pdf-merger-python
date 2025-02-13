# Example configuration - Copy this file to config.py and update with your structure
SCHEMA = {
    "Introduction": {
        "Garde": ["intro.pdf"],
        "Table des Matières": {"_toc_": True},  # Special marker for TOC placement
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