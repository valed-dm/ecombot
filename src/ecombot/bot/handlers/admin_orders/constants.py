"""Constants and templates for admin order management."""

# Error messages
ERROR_QUERY_DATA_NONE = "Query data cannot be None"
ERROR_ORDER_NOT_FOUND = "Could not find this order."
ERROR_INVALID_ORDER_ID = "Invalid order ID format."
ERROR_STATUS_UPDATE_FAILED = "An error occurred while updating the status."

# Success messages
SUCCESS_STATUS_UPDATED = "Order status updated to {status}"

# Progress messages
PROGRESS_FETCHING_ORDERS = "Fetching {status} orders, please wait..."

# UI text
SELECT_STATUS_PROMPT = "Please select a status to view orders:"
ORDERS_LIST_HEADER = "<b>Orders - {status} ({count})</b>\n\n"
NO_ORDERS_FOUND = "No orders found with this status."
TEXT_TRUNCATED_SUFFIX = "\n\n[Truncated due to length]"

# Telegram limits
MAX_MESSAGE_LENGTH = 4096
TRUNCATE_THRESHOLD = 4090
