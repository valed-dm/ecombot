"""Catalog messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class CatalogMessageManager(BaseMessageManager):
    """Message manager for catalog-related messages."""
    
    def _load_messages(self) -> None:
        """Load catalog messages for all supported languages."""
        
        # English messages
        en_messages = {
            # Welcome and navigation
            "welcome_message": "Welcome to our store! Please choose a category to start browsing:",
            "category_products_message": "Here are the products in this category:",
            "no_products_in_category": "No products found in this category.",
            "back_to_categories": "⬅️ Back to Categories",
            
            # Product display
            "product_details_template": "<b>{name}</b>\n\n{description}\n\n<b>Price:</b> ${price:.2f}",
            "add_to_cart": "🛒 Add to Cart",
            "out_of_stock": "❌ Out of Stock",
            
            # Error messages
            "error_product_not_found": "Sorry, this product could not be found.",
            "error_category_not_found": "Sorry, this category could not be found.",
            "error_loading_catalog": "Error loading catalog. Please try again.",
        }
        
        # Spanish messages
        es_messages = {
            # Welcome and navigation
            "welcome_message": "¡Bienvenido a nuestra tienda! Elige una categoría para comenzar a navegar:",
            "category_products_message": "Aquí están los productos de esta categoría:",
            "no_products_in_category": "No se encontraron productos en esta categoría.",
            "back_to_categories": "⬅️ Volver a Categorías",
            
            # Product display
            "product_details_template": "<b>{name}</b>\n\n{description}\n\n<b>Precio:</b> ${price:.2f}",
            "add_to_cart": "🛒 Añadir al Carrito",
            "out_of_stock": "❌ Sin Stock",
            
            # Error messages
            "error_product_not_found": "Lo siento, no se pudo encontrar este producto.",
            "error_category_not_found": "Lo siento, no se pudo encontrar esta categoría.",
            "error_loading_catalog": "Error al cargar el catálogo. Por favor, inténtalo de nuevo.",
        }
        
        # Russian messages
        ru_messages = {
            # Welcome and navigation
            "welcome_message": "Добро пожаловать в наш магазин! Выберите категорию для начала просмотра:",
            "category_products_message": "Вот товары в этой категории:",
            "no_products_in_category": "В этой категории товары не найдены.",
            "back_to_categories": "⬅️ Назад к Категориям",
            
            # Product display
            "product_details_template": "<b>{name}</b>\n\n{description}\n\n<b>Цена:</b> ${price:.2f}",
            "add_to_cart": "🛒 Добавить в Корзину",
            "out_of_stock": "❌ Нет в Наличии",
            
            # Error messages
            "error_product_not_found": "Извините, этот товар не найден.",
            "error_category_not_found": "Извините, эта категория не найдена.",
            "error_loading_catalog": "Ошибка загрузки каталога. Пожалуйста, попробуйте снова.",
        }
        
        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }