import re

SPEC_ALIASES = {
    "Brightness": [
        "brightness",
        "display brightness",
        "luminance",
        "luminosity"
    ],

    "Resolution": [
        "resolution",
        "native resolution"
    ],

    "Power Consumption": [
        "power",
        "power consumption",
        "power rating"
    ],

    "Voltage": [
        "voltage",
        "input voltage",
        "operating voltage"
    ],

    "Weight": [
        "weight",
        "net weight",
        "gross weight"
    ],

    "Viewing Angle": [
        "viewing angle",
        "horizontal viewing angle",
        "vertical viewing angle"
    ],

    "Response Time": [
        "response time"
    ],

    "Contrast Ratio": [
        "contrast ratio"
    ],

    "Refresh Rate": [
        "refresh rate"
    ]
}


def normalize_specification_name(name: str):
    if not name:
        return name

    text = name.lower().strip()

    for standard, aliases in SPEC_ALIASES.items():
        for alias in aliases:
            if alias == text:
                return standard

    return name