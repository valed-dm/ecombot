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
    PICKUP_READY = "pickup_ready"
    SHIPPED = "shipped"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"

    @property
    def message_key(self) -> str:
        """Returns the message key for internationalization."""
        return f"status_{self.value}"


class DeliveryType(str, enum.Enum):
    """
    Represents the delivery service level and scope.
    Categorized by logistics tiers (Pickup -> Hyperlocal -> Local -> Regional -> National).
    """

    # 1. PICKUP
    PICKUP_STORE = "pickup_store"
    PICKUP_LOCKER = "pickup_locker"
    PICKUP_CURBSIDE = "pickup_curbside"

    # 2. HYPERLOCAL (Immediate Vicinity, e.g., < 10km)
    HYPERLOCAL_INSTANT = "hyperlocal_instant"
    HYPERLOCAL_NEIGHBORHOOD = "hyperlocal_neighborhood"

    # 3. LOCAL (City/Town limits)
    LOCAL_SAME_DAY = "local_same_day"
    LOCAL_NEXT_DAY = "local_next_day"

    # 4. REGIONAL (Intra-region / Oblast)
    REGIONAL_STANDARD = "regional_standard"
    REGIONAL_EXPRESS = "regional_express"

    # 5. NATIONAL (Federal / Inter-region)
    NATIONAL_STANDARD = "national_standard"
    NATIONAL_EXPRESS = "national_express"
    NATIONAL_PRIORITY = "national_priority"

    # 6. SPECIALIZED
    SPECIAL_SCHEDULED = "special_scheduled"
    SPECIAL_BULK = "special_bulk"

    @property
    def message_key(self) -> str:
        """Returns the message key for internationalization."""
        return f"delivery_{self.value}"
