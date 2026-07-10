# modules/specification_patterns.py

SPEC_PATTERNS = {

    "make": [
        r"make\s*[:\-]\s*(.+)",
        r"manufacturer\s*[:\-]\s*(.+)",
        r"brand\s*[:\-]\s*(.+)",
        r"oem\s*[:\-]\s*(.+)"
    ],

    "model": [
        r"model\s*(?:no\.?|number)?\s*[:\-]\s*([A-Za-z0-9\-_/.]+)",
        r"product\s*code\s*[:\-]\s*([A-Za-z0-9\-_/.]+)",
        r"part\s*number\s*[:\-]\s*([A-Za-z0-9\-_/.]+)"
    ],

    "screen_size": [
        r"(\d{2,3})\s*inch",
        r"display\s*size\s*[:\-]?\s*(.+)",
        r"screen\s*size\s*[:\-]?\s*(.+)"
    ],

    "resolution": [
        r"(\d{3,4}\s*[xX×]\s*\d{3,4})",
        r"resolution\s*[:\-]?\s*(.+)"
    ],

    "brightness": [
        r"brightness\s*[:\-]?\s*(\d+\s*nit)",
        r"(\d+\s*nit)"
    ],

    "contrast_ratio": [
        r"contrast\s*ratio\s*[:\-]?\s*([\d:,]+)"
    ],

    "refresh_rate": [
        r"(\d+)\s*hz",
        r"refresh\s*rate\s*[:\-]?\s*(.+)"
    ],

    "response_time": [
        r"response\s*time\s*[:\-]?\s*(.+)"
    ],

    "processor": [
        r"processor\s*[:\-]?\s*(.+)",
        r"cpu\s*[:\-]?\s*(.+)"
    ],

    "ram": [
        r"ram\s*[:\-]?\s*(\d+\s*gb)",
        r"memory\s*[:\-]?\s*(\d+\s*gb)"
    ],

    "storage": [
        r"storage\s*[:\-]?\s*(.+)",
        r"rom\s*[:\-]?\s*(.+)",
        r"internal\s*memory\s*[:\-]?\s*(.+)"
    ],

    "operating_system": [
        r"operating\s*system\s*[:\-]?\s*(.+)",
        r"os\s*[:\-]?\s*(.+)"
    ],

    "wifi": [
        r"wifi\s*[:\-]?\s*(yes|no)",
        r"wi[- ]?fi"
    ],

    "bluetooth": [
        r"bluetooth\s*[:\-]?\s*(yes|no)",
        r"bluetooth\s*[0-9.]+"
    ],

    "hdmi": [
        r"hdmi\s*[:\-]?\s*(\d+)",
        r"hdmi\s*x\s*(\d+)"
    ],

    "usb": [
        r"usb\s*[:\-]?\s*(\d+)",
        r"usb\s*x\s*(\d+)"
    ],

    "rj45": [
        r"rj45\s*[:\-]?\s*(yes|no)",
        r"ethernet"
    ],

    "speaker": [
        r"speaker\s*[:\-]?\s*(.+)",
        r"audio\s*output\s*[:\-]?\s*(.+)"
    ],

    "power_supply": [
        r"power\s*supply\s*[:\-]?\s*(.+)",
        r"input\s*voltage\s*[:\-]?\s*(.+)"
    ],

    "power_consumption": [
        r"power\s*consumption\s*[:\-]?\s*(.+)"
    ],

    "dimensions": [
        r"dimensions\s*[:\-]?\s*(.+)"
    ],

    "weight": [
        r"weight\s*[:\-]?\s*(.+)"
    ],

    "mounting": [
        r"vesa\s*[:\-]?\s*(.+)",
        r"wall\s*mount\s*[:\-]?\s*(.+)"
    ],

    "warranty": [
        r"warranty\s*[:\-]?\s*(.+)",
        r"(\d+\s*years?)\s*warranty"
    ],

    "certification": [
        r"bis",
        r"ce",
        r"fcc",
        r"rohs",
        r"iso"
    ]
}