path = "/c/DATA/CLOUD/calendar.json"

fields = {
    "active": {
        "sat": {"type": float, "range": (0, 10)},
        "fz": {"type": float, "range": (0, 10)},  # prodromey feeling
        "text": {"type": str},
        "pain": {"type": bool, "in": "text", "match": "PAIN"},
    },
    "inactive": {
        "body": {"type": int, "range": (0, 2)},  # physical exercise
        "mind": {"type": int, "range": (0, 2)},  # mental exercise + cold showers?
        "np-p": {"type": int, "range": (0, 2)},  # 0 -> p; 1 -> m; 2 -> nothing
        "nourr": {"type": int, "range": (0, 2)},  # healthy eating
        "m-e": {"type": int, "range": (0, 2)},  # mental exercise
        "ph-e": {"type": float, "range": (0, 10)},  # physical exercise
        "exp": {"type": float, "range": (0, 10)},  # new experiences
        "sharp": {"type": float, "range": (0, 10)},  # mental clarity
        "food": {"type": str},  # list of foods, in spanish, separated by commas
    }
}

