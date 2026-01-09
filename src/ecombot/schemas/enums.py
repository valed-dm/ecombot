"""
Defines enumerations used throughout the application for choices.
"""

import enum


class OrderStatus(str, enum.Enum):
    """
    Represents the lifecycle of an order.
    - PENDING: Order placed, awaiting payment/processing.
    - PROCESSING: Payment confirmed, order is being prepared.
    - PAID: Order has been paid.
    - SHIPPED: Order has been handed over to the delivery service.
    - COMPLETED: Order has been successfully delivered to the customer.
    - CANCELLED: Order has been cancelled.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @property
    def message_key(self) -> str:
        """Returns the message key for internationalization."""
        return f"status_{self.value}"
