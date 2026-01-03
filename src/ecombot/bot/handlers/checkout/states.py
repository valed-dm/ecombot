"""Checkout FSM states and constants."""

from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class CheckoutFSM(StatesGroup):
    # States for the "slow path" / first-time user
    getting_name = State()
    getting_phone = State()
    getting_address = State()
    confirm_slow_path = State()

    # State for the "fast path" / returning user
    confirm_fast_path = State()


# Error messages
ERROR_EMPTY_CART = "Your cart is empty."
ERROR_ADDRESS_NOT_FOUND = (
    "Error: Could not find your default address. "
    "Please try again or update your profile."
)
ERROR_UNEXPECTED = "An unexpected error occurred. Please contact support."
ERROR_EMPTY_PHONE = "Please enter a valid phone number (cannot be empty)."
ERROR_EMPTY_ADDRESS = "Please enter a valid shipping address (cannot be empty)."

# Success messages
SUCCESS_ORDER_PLACED = (
    "✅ <b>Thank you! Your order #{order_number} has been placed!</b>"
)
SUCCESS_ORDER_PLACED_SLOW = (
    "✅ <b>Thank you! Your order has been placed successfully!</b>\n\n"
    "<b>Order Number:</b> <code>{order_number}</code>\n"
    "You can view its status in /orders."
)

# Progress messages
PROGRESS_PLACING_ORDER = "Placing your order, please wait..."
PROGRESS_SAVING_DETAILS = "Placing your order and saving your details..."

# Cancellation message
CHECKOUT_CANCELLED = "Checkout cancelled."

# Slow path prompts
SLOW_PATH_START = (
    "To complete your order, we need to set up your {missing_info}.\n\n"
    "Let's start with your full name (as it should appear on the package)."
)
SLOW_PATH_PHONE = "Thank you. Now, please share your phone number."
SLOW_PATH_ADDRESS = "Great. Finally, what is the full shipping address?"
