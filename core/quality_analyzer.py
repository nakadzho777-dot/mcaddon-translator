import os
import json
import re


class QualityAnalyzer:

    BAD_PATTERNS = [
        r"minecraft:",
        r"textures/",
        r"animation\.",
        r"controller\.",
        r"entity\.",
        r"item\.",
        r"block\."
    ]

    def scan(self, root_path):

        results = []

        if not root_path:
            return results

        base = (
            os.path.dirname(root_path)
            if os.path.isfile(root_path)
            else root_path
        )

        for root, _, files in os.walk(base):

            for file in files:

                if not file.endswith(".json"):
                    continue

                path = os.path.join(root, file)

                try:

                    with open(
                        path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:

                        text = f.read()

                    for pattern in self.BAD_PATTERNS:

                        matches = re.findall(pattern, text)

                        if matches:

                            results.append({
                                "file": path,
                                "issue": f"ID/パス検出: {pattern}"
                            })

                except Exception:
                    pass

        return results