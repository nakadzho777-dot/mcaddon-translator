import os

REQUIRED_FOLDERS = [
    "behavior_packs",
    "resource_packs"
]


def validate_structure(folder):
    """mcaddon構造チェック"""

    found = []

    for root, dirs, _ in os.walk(folder):
        for d in dirs:
            if d in REQUIRED_FOLDERS:
                found.append(d)

    missing = [f for f in REQUIRED_FOLDERS if f not in found]

    return {
        "valid": len(missing) == 0,
        "missing": missing
    }