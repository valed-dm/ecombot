"""FSM states and constants for profile handlers."""

from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class EditProfile(StatesGroup):
    getting_phone = State()
    getting_email = State()


class AddAddress(StatesGroup):
    getting_label = State()
    getting_address = State()


# Profile messages
PROFILE_HEADER = "<b>Your Profile</b>\n\n"
PROFILE_TEMPLATE = (
    "<b>Name:</b> {name}\n"
    "<b>Phone:</b> {phone}\n"
    "<b>Email:</b> {email}\n\n"
    "<b>Default Address:</b>\n"
)
DEFAULT_ADDRESS_NOT_SET = "<i>Not set. You can set one in 'Manage Addresses'.</i>"

# Address management messages
ADDRESS_MANAGEMENT_HEADER = "<b>Your Delivery Addresses</b>\n\n"
NO_ADDRESSES_MESSAGE = "You have no saved addresses."

# Success messages
SUCCESS_ADDRESS_DELETED = "Address deleted successfully!"
SUCCESS_DEFAULT_ADDRESS_UPDATED = "Default address updated!"
SUCCESS_ADDRESS_SAVED = "✅ New address saved successfully!"
SUCCESS_PHONE_UPDATED = "✅ Phone number updated successfully!"
SUCCESS_EMAIL_UPDATED = "✅ Email address updated successfully!"

# Error messages
ERROR_PROFILE_LOAD_FAILED = "❌ An error occurred while loading your profile."
ERROR_ADDRESS_DELETE_FAILED = "Failed to delete address."
ERROR_DEFAULT_ADDRESS_FAILED = "Failed to update default address."
ERROR_MISSING_ADDRESS_ID = "An internal error occurred (missing address ID)."
ERROR_ADDRESS_SAVE_FAILED = "❌ An error occurred while saving the address."
ERROR_ADDRESSES_LOAD_FAILED = "❌ An error occurred while loading your addresses."
ERROR_PHONE_UPDATE_FAILED = "❌ An error occurred while updating your phone number."
ERROR_EMAIL_UPDATE_FAILED = "❌ An error occurred while updating your email address."

# FSM prompts
ADD_ADDRESS_START_PROMPT = (
    "Let's add a new address.\n\n"
    "First, give it a short label (e.g., 'Home', 'Office')."
)
ADD_ADDRESS_FULL_PROMPT = "Great. Now, please enter the full shipping address."
EDIT_PHONE_PROMPT = "Please enter your new phone number:"
EDIT_EMAIL_PROMPT = "Please enter your new email address:"

# Default values
NOT_SET_TEXT = "Not set"
