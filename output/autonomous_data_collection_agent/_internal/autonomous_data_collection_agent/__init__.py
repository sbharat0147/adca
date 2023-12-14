"""Top-level package for Autonomous Data Collection Agent."""

__app_name__ = "autonomous_data_collection_agent"
__version__ = "1.0.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    APP_NOT_FOUND,
    ENDPOINT_NOT_FOUND,
    DUPLICATE_RECORD
) = range(10)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "endpoint id error",
    JSON_ERROR: "JSON error",
    APP_NOT_FOUND: "app not found.",
    ENDPOINT_NOT_FOUND: "endpoint not found",
    DUPLICATE_RECORD: "duplicate record"
}
