from os import environ

from cdislogging import get_logger

# Set log-level variable here for use in other modules
if environ.get("GEN3_DEBUG") == "True":
    LOG_LEVEL = "debug"
else:
    LOG_LEVEL = "info"

logger = get_logger("mesh-card-service", log_level=LOG_LEVEL)
