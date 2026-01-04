"""Constants for catalog handlers."""

# Welcome and navigation messages
WELCOME_MESSAGE = "Welcome to our store! Please choose a category to start browsing:"
CATEGORY_PRODUCTS_MESSAGE = "Here are the products in this category:"

# Error messages
ERROR_PRODUCT_NOT_FOUND = "Sorry, this product could not be found."

# Product display template
PRODUCT_DETAILS_TEMPLATE = (
    "<b>{name}</b>\n\n" "{description}\n\n" "<b>Price:</b> ${price:.2f}"
)
