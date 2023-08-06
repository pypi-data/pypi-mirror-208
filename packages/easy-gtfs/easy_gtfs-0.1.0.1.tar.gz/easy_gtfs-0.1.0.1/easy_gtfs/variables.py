

ERRORMANAGER = None


REQUIRED_OPTIONS: dict = {
    "always": "This file always has to be part of the dataset.",
    "conditional": "This file has to be part of the dataset only in certain cases.",
    "optional": "This file does not need to be part of the dataset."
}


FILES: dict = {
    "agency.txt": {
        "required": "always"
    },
    "stops.txt": {
        "required": "always"
    },
    "routes.txt": {
        "required": "always"
    },
    "trips.txt": {
        "required": "always"
    },
    "stop_times.txt": {
        "required": "always"
    },
    "calendar.txt": {
        "required": "conditional"
    },
    "calendar_dates.txt": {
        "required": "conditional"
    },
    "fare_attributes.txt": {
        "required": "optional"
    },
    "fare_rules.txt": {
        "required": "optional"
    },
    "shapes.txt": {
        "required": "optional"
    },
    "frequencies.txt": {
        "required": "optional"
    },
    "transfers.txt": {
        "required": "optional"
    },
    "pathways.txt": {
        "required": "optional"
    },
    "levels.txt": {
        "required": "optional"
    },
    "feed_info.txt": {
        "required": "conditional"
    },
    "translations.txt": {
        "required": "optional"
    },
    "attributions.txt": {
        "required": "optional"
    }
}