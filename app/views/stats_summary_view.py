import tkinter as tk
from tkinter import ttk

from core.translation_stats import TranslationStats

class StatsSummaryView:

```
def __init__(self, processor):
    self.processor = processor
    self.stats = TranslationStats()

def get_summary(self):

    path = getattr(
        self.processor,
        "source_path",
        None
    )

    if not path:
        return {
            "rate": 0,
            "untranslated": 0
        }

    result = self.stats.analyze(path)

    return {
        "rate": result["rate"],
        "untranslated": result["untranslated"]
    }
```
