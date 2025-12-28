"""
Data Transfer Objects (DTOs) for the E-commerce Bot.

This module defines Pydantic models used to transfer data between different
layers of the application (e.g., from services to handlers).

Using DTOs ensures a clean separation of concerns, preventing the database
models from leaking into the business logic or view layers. It also provides a
clear and validated "contract" for the shape of the data.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from ecombot.schemas.enums import OrderStatus


# --- Base DTO for shared configuration ---


class BaseDTO(BaseModel):
    """Base DTO with common configuration."""

    model_config = ConfigDict(from_attributes=True)


# --- Catalog DTOs ---


class CategoryDTO(BaseDTO):
    """DTO for a product category."""

    id: int
    name: str
    description: str | None = None


class ProductDTO(BaseDTO):
    """DTO for a single product. This is what the user sees."""

    id: int
    name: str
    description: str
    price: Decimal = Field(gt=0)
    image_url: str | None = None
    category: CategoryDTO


class AdminProductDTO(ProductDTO):
    """
    A more detailed DTO for a single product, intended for the admin panel.
    It inherits all fields from the standard ProductDTO and adds internal
    data like stock levels.
    """

    stock: int = Field(ge=0)


# --- Cart DTOs ---


class CartItemDTO(BaseDTO):
    """DTO for an item within a shopping cart."""

    id: int
    quantity: int = Field(gt=0)
    product: ProductDTO


class CartDTO(BaseDTO):
    """DTO representing the user's complete shopping cart."""

    id: int
    user_id: int
    items: list[CartItemDTO]

    @property
    def total_price(self) -> Decimal:
        """Calculates the total price of all items in the cart."""
        if not self.items:
            return Decimal("0.00")
        return sum(
            (item.product.price * item.quantity for item in self.items),
            start=Decimal("0.00"),
        )


# --- Order DTOs ---


class OrderItemDTO(BaseDTO):
    """DTO for an item within a confirmed order."""

    quantity: int
    price: Decimal
    product: ProductDTO


class UserSimpleDTO(BaseDTO):
    telegram_id: int
    first_name: str


class OrderDTO(BaseDTO):
    """DTO representing a confirmed order."""

    id: int
    user: UserSimpleDTO
    order_number: str
    status: OrderStatus
    contact_name: str
    phone: str
    address: str
    delivery_method: str
    items: list[OrderItemDTO]
    created_at: datetime

    @property
    def total_price(self) -> Decimal:
        """Calculates the total price of a confirmed order."""
        if not self.items:
            return Decimal("0.00")
        return sum(
            (item.price * item.quantity for item in self.items), start=Decimal("0.00")
        )


# --- Admin DTOs (can be extended) ---


class AdminOrderSummaryDTO(BaseDTO):
    """A simplified DTO for admins to view a list of orders."""

    id: int
    user_id: int
    status: str
    contact_name: str
    total_price: Decimal


# --- User Profile DTOs ---


class DeliveryAddressDTO(BaseDTO):
    id: int
    address_label: str
    full_address: str
    is_default: bool


class UserProfileDTO(BaseDTO):
    telegram_id: int
    first_name: str
    phone: str | None
    email: str | None
    addresses: list[DeliveryAddressDTO]
