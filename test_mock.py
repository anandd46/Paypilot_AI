




import re

_CATEGORY_KEYWORDS = [
    ("headphone", "Headphones", 10),
    ("smartphone", "Smartphones", 10),
    ("phone", "Smartphones", 9),
    ("gaming", "Gaming", 5),
]

def get_category(msg):
    best_category = None
    best_priority = -1
    for kw, cat, priority in _CATEGORY_KEYWORDS:
        if kw in msg and priority > best_priority:
            best_category = cat
            best_priority = priority
    return best_category

print(get_category("find gaming headphones under 5000"))
