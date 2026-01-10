#!/bin/bash

# Create directory structure
mkdir -p tests/core
mkdir -p tests/db
mkdir -p tests/services
mkdir -p tests/bot/keyboards
mkdir -p tests/bot/handlers/admin/categories
mkdir -p tests/bot/handlers/admin/products
mkdir -p tests/bot/handlers/admin_orders
mkdir -p tests/bot/handlers/cart
mkdir -p tests/bot/handlers/catalog
mkdir -p tests/bot/handlers/checkout
mkdir -p tests/bot/handlers/orders
mkdir -p tests/bot/handlers/profile

# --- Move Files ---

# Core & Infrastructure
mv tests/test_core_*.py tests/core/ 2>/dev/null
mv tests/test_middlewares.py tests/core/ 2>/dev/null
mv tests/test_callback_data.py tests/core/ 2>/dev/null

# Database (Models & CRUD)
mv tests/test_models.py tests/db/ 2>/dev/null
mv tests/test_*_crud.py tests/db/ 2>/dev/null

# Services
# Note: This will be empty if no test_*_service.py files exist in tests/ root
mv tests/test_*_service.py tests/services/ 2>/dev/null

# Bot Keyboards
mv tests/test_keyboards_*.py tests/bot/keyboards/ 2>/dev/null

# Bot Handlers - Admin Orders (Move specific first to avoid capturing by admin glob)
mv tests/test_handlers_admin_orders_*.py tests/bot/handlers/admin_orders/ 2>/dev/null

# Bot Handlers - Admin Sub-modules (Move specific first)
mv tests/test_handlers_admin_categories_*.py tests/bot/handlers/admin/categories/ 2>/dev/null
mv tests/test_handlers_admin_products_*.py tests/bot/handlers/admin/products/ 2>/dev/null

# Bot Handlers - Admin (Remaining admin handlers like helpers, navigation)
mv tests/test_handlers_admin_*.py tests/bot/handlers/admin/ 2>/dev/null

# Bot Handlers - Cart
mv tests/test_handlers_cart_*.py tests/bot/handlers/cart/ 2>/dev/null

# Bot Handlers - Catalog
mv tests/test_handlers_catalog_*.py tests/bot/handlers/catalog/ 2>/dev/null

# Bot Handlers - Checkout
mv tests/test_handlers_checkout_*.py tests/bot/handlers/checkout/ 2>/dev/null

# Bot Handlers - Orders (User facing)
mv tests/test_handlers_orders_*.py tests/bot/handlers/orders/ 2>/dev/null

# Bot Handlers - Profile
mv tests/test_handlers_profile_*.py tests/bot/handlers/profile/ 2>/dev/null

echo "Tests reorganized successfully."