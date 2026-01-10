from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint

from ecombot.db.models import Cart
from ecombot.db.models import CartItem
from ecombot.db.models import Category
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import Order
from ecombot.db.models import OrderItem
from ecombot.db.models import Product
from ecombot.db.models import User
from ecombot.schemas.enums import OrderStatus


def test_user_model_structure():
    """Test User model attributes and mixins."""
    user = User(
        telegram_id=12345,
        username="test",
        first_name="Test",
        last_name="User",
        phone="123",
        email="test@example.com",
    )
    assert user.telegram_id == 12345
    assert user.username == "test"
    # Check TimestampMixin fields exist
    assert hasattr(User, "created_at")
    assert hasattr(User, "updated_at")
    # User does not have SoftDeleteMixin
    assert not hasattr(User, "deleted_at")


def test_product_model_constraints():
    """Test Product model constraints and mixins."""
    # Check constraints defined in __table_args__
    constraints = [
        arg for arg in Product.__table_args__ if isinstance(arg, CheckConstraint)
    ]
    constraint_names = {c.name for c in constraints}
    assert "stock_non_negative" in constraint_names
    assert "price_positive" in constraint_names

    # Check Mixins (Product has both Timestamp and SoftDelete)
    assert hasattr(Product, "created_at")
    assert hasattr(Product, "updated_at")
    assert hasattr(Product, "deleted_at")


def test_cart_item_constraints():
    """Test CartItem unique constraints."""
    constraints = [
        arg for arg in CartItem.__table_args__ if isinstance(arg, UniqueConstraint)
    ]
    constraint_names = {c.name for c in constraints}
    assert "uq_cart_product" in constraint_names


def test_order_status_enum():
    """Test Order model uses the correct Enum."""
    order = Order(status=OrderStatus.PENDING)
    assert order.status == OrderStatus.PENDING
    assert order.status.value == "pending"


def test_category_structure():
    """Test Category model structure."""
    category = Category(name="Electronics")
    assert category.name == "Electronics"
    # Category has SoftDeleteMixin
    assert hasattr(Category, "deleted_at")


def test_delivery_address_structure():
    """Test DeliveryAddress instantiation."""
    address = DeliveryAddress(address_label="Home", full_address="123 St")
    assert address.address_label == "Home"
    assert address.full_address == "123 St"


def test_relationships_exist():
    """Simple check that relationship attributes are defined on the classes."""
    assert hasattr(User, "addresses")
    assert hasattr(User, "orders")
    assert hasattr(DeliveryAddress, "user")
    assert hasattr(Category, "subcategories")
    assert hasattr(Category, "products")
    assert hasattr(Product, "category")
    assert hasattr(Cart, "items")
    assert hasattr(CartItem, "cart")
    assert hasattr(CartItem, "product")
    assert hasattr(Order, "user")
    assert hasattr(Order, "items")
    assert hasattr(OrderItem, "order")
    assert hasattr(OrderItem, "product")
