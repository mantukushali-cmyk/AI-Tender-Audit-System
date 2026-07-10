import re
from modules.specification_normalizer import normalize_specification_name

from modules.specification_patterns import SPECIFICATION_PATTERNS


def extract_specifications(page_text):
    """
    Extract technical specifications from one page.

    Returns:
    [
        {
            "parameter": "...",
            "value": "...",
            "unit": "..."
        }
    ]
    """

    results = []

    if not page_text:
        return results

    for parameter, patterns in SPECIFICATION_PATTERNS.items():
    
        for pattern in patterns:

            matches = re.finditer(
                pattern,
                page_text,
                flags=re.IGNORECASE
            )

            for match in matches:

                value = match.group(1).strip()

                if len(value) < 2:
                    continue

                unit = ""

                if len(match.groups()) >= 2:
                    unit = match.group(2).strip()

                normalized_parameter = normalize_specification_name(parameter)

                results.append(
                    {
                        "parameter": normalized_parameter,
                        "value": value,
                        "unit": unit
                    }
                )
    # -----------------------------
    # Remove duplicates
    # -----------------------------
    unique = {}

    for item in results:
        key = (
            item["parameter"],
            item["value"],
            item["unit"]
        )
        unique[key] = item

    return list(unique.values())
    