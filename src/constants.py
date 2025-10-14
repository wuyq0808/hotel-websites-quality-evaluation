#!/usr/bin/env python3
"""
⚠️ DEPRECATED: This file is deprecated and will be removed in a future version.
Please use config_loader.py and config.yaml instead.

All constants and settings have been moved to config.yaml for easier editing.
Import from config_loader instead:
    from config_loader import get_config, WebsiteKey, Feature
"""

import warnings
from enum import Enum

warnings.warn(
    "constants.py is deprecated. Use config_loader.py and config.yaml instead.",
    DeprecationWarning,
    stacklevel=2
)


class WebsiteKey(Enum):
    GOOGLE_TRAVEL = "google_travel"
    AGODA = "agoda_com"
    BOOKING_COM = "booking_com"
    SKYSCANNER = "skyscanner"


# Checkin-Checkout constants
NEXT_DAY_ONE_NIGHT = {
    "key": "next_day_one_night",
    "value": (1, 2)  # (days from today for checkin, days from today for checkout)
}

# Cities to test
CITIES = [
    # "London", 
    "Tokyo", 
    # "Dubai", "Rome", "Paris"
    ]


# Individual website constants
GOOGLE_TRAVEL = {
    "url": "https://www.google.com/travel/",
    "key": WebsiteKey.GOOGLE_TRAVEL
}

AGODA = {
    "url": "https://www.agoda.com",
    "key": WebsiteKey.AGODA
}

BOOKING_COM = {
    "url": "https://www.booking.com",
    "key": WebsiteKey.BOOKING_COM
}

SKYSCANNER_HOTELS = {
    "url": "https://www.skyscanner.com/hotels",
    "key": WebsiteKey.SKYSCANNER
}

# Common website list for all features
WEBSITES = [
    # SKYSCANNER_HOTELS,
    GOOGLE_TRAVEL,
    # BOOKING_COM,
    # AGODA,
]