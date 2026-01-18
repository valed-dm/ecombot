"""Admin products messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class AdminProductsMessageManager(BaseMessageManager):
    """Message manager for admin product management messages."""

    def _load_messages(self) -> None:
        """Load admin products messages for all supported languages."""

        # English messages
        en_messages = {
            # Add product messages
            "add_product_categories_load_error": (
                "❌ Failed to load categories. Please try again."
            ),
            "add_product_no_categories": (
                "❌ No categories found. You need to create at least one category "
                "before adding products. Please use 'Add Category' first."
            ),
            "add_product_choose_category": (
                "Please choose the category for the new product:"
            ),
            "add_product_name_prompt": "Great. Now, what is the name of the product?",
            "add_product_name_empty": (
                "Please enter a valid product name (cannot be empty)."
            ),
            "add_product_name_too_long": (
                "Product name is too long (maximum 255 characters)."
            ),
            "add_product_description_prompt": (
                "Got it. Now, please provide a description for the product."
            ),
            "add_product_description_empty": (
                "Please enter a valid product description (cannot be empty)."
            ),
            "add_product_description_too_long": (
                "Product description is too long (maximum 1000 characters)."
            ),
            "add_product_price_prompt": "Excellent. What is the price? (e.g., 25.99)",
            "add_product_price_invalid": (
                "Price must be a positive number. Please try again."
            ),
            "add_product_price_format_error": (
                "Invalid price format. Please enter a number (e.g., 25.99)."
            ),
            "add_product_stock_prompt": (
                "Good. Now, how many units are in stock? (e.g., 50)"
            ),
            "add_product_stock_not_text": (
                "Please send the stock quantity as text, not a photo or sticker."
            ),
            "add_product_stock_negative": (
                "Stock cannot be negative. Please enter a whole number."
            ),
            "add_product_stock_invalid": (
                "Invalid format. Please enter a whole number."
            ),
            "add_product_image_prompt": (
                "Excellent. Now, please upload photos for the product.\n"
                "Send them one by one or as a group. Type /done when finished (or /skip)."
            ),
            "add_product_success": "✅ Product '{name}' created successfully!",
            "add_product_error": (
                "❌ An unexpected error occurred while creating the product. "
                "Please check the logs for details."
            ),
            # Edit product messages
            "edit_product_load_error": (
                "❌ Failed to load categories. Please try again."
            ),
            "edit_product_no_categories": (
                "❌ No categories found. You need to create at least one category "
                "before editing products."
            ),
            "edit_product_choose_category": ("Choose a category to see its products:"),
            "edit_product_no_products": (
                "❌ No products found in this category. "
                "Please add products first or choose another category."
            ),
            "edit_product_choose_product": "Choose a product to edit:",
            "edit_product_not_found": "❌ Product not found.",
            "edit_product_load_details_error": (
                "❌ An unexpected error occurred while loading product details."
            ),
            "edit_product_load_products_error": (
                "❌ An unexpected error occurred while loading products."
            ),
            # Delete product messages
            "delete_product_choose_category": (
                "Choose a category to delete products from:"
            ),
            "delete_product_choose_product": "Choose a product to delete:",
            "delete_product_confirmation": (
                "⚠️ Are you sure you want to delete this product?\n\n"
                "<b>{product_name}</b>\n"
                "<i>{product_description}</i>\n\n"
                "<b>Price:</b> ${product_price:.2f}\n"
                "<b>Stock:</b> {product_stock} units\n\n"
                "The product will be hidden from the catalog but preserved "
                "in order history."
            ),
            "delete_product_cancelled": "Deletion cancelled.",
            "delete_product_success": "✅ Product '{product_name}' has been deleted.",
            "delete_product_error": (
                "❌ Error: Could not delete '{product_name}'. "
                "It may have already been removed."
            ),
            "delete_product_unexpected_error": (
                "An unexpected error occurred while deleting the product."
            ),
            "delete_product_load_categories_error": (
                "❌ An unexpected error occurred while loading categories."
            ),
            "delete_product_no_categories": (
                "❌ No categories found. Please create categories and products first."
            ),
            "delete_product_load_products_error": (
                "❌ An unexpected error occurred while loading products."
            ),
            "delete_product_no_products": "❌ No products found in this category.",
            "delete_product_load_product_error": (
                "❌ An unexpected error occurred while loading product."
            ),
            "delete_product_not_found": "❌ Product not found.",
            # Restore product messages
            "restore_product_load_error": (
                "❌ An unexpected error occurred while loading deleted products."
            ),
            "restore_product_none_found": (
                "✅ No deleted products found. All products are active."
            ),
            "restore_product_choose_prompt": (
                "🔄 Choose a deleted product to restore:"
            ),
            "restore_product_success": ("✅ Product has been restored successfully!"),
            "restore_product_not_found": ("❌ Product not found or already active."),
            "restore_product_unexpected_error": (
                "❌ An unexpected error occurred while restoring the product."
            ),
            # Product edit menu messages
            "edit_menu_header": "You are editing:",
            "edit_menu_price_label": "Price:",
            "edit_menu_stock_label": "Stock:",
            "edit_menu_stock_units": "units",
            "edit_menu_choose_field": "Choose a field to edit:",
            "edit_product_fallback_prompt": "Enter the new value:",
            "edit_product_name_prompt": "Enter the new product name:",
            "edit_product_price_prompt": "Enter the new price (e.g., 25.99):",
            "edit_product_stock_prompt": "Enter the new stock quantity:",
            "edit_product_image_prompt": "Please upload a new photo for the product:",
            "edit_product_value_empty": (
                "Please enter a valid value (cannot be empty)."
            ),
            "edit_product_price_invalid": (
                "Price must be a positive number. Please try again."
            ),
            "edit_product_stock_negative": (
                "Stock cannot be negative. Please try again."
            ),
            "edit_product_field_too_long": (
                "{field} is too long (maximum {max_length} characters)."
            ),
            "edit_product_invalid_format": (
                "Invalid {field_type} format. Please try again."
            ),
            "edit_product_success": (
                "✅ Product '{name}' {field} updated successfully!"
            ),
            "edit_product_error": (
                "❌ An unexpected error occurred while updating the product."
            ),
            "edit_product_image_success": (
                "✅ Product '{name}' image updated successfully!"
            ),
            "edit_product_image_error": (
                "❌ An unexpected error occurred while updating the product image."
            ),
        }

        # Spanish messages
        es_messages = {
            # Add product messages
            "add_product_categories_load_error": (
                "❌ Error al cargar categorías. Por favor inténtalo de nuevo."
            ),
            "add_product_no_categories": (
                "❌ No se encontraron categorías. Necesitas crear al menos una "
                "categoría antes de agregar productos. "
                "Por favor usa 'Agregar Categoría' primero."
            ),
            "add_product_choose_category": (
                "Por favor elige la categoría para el nuevo producto:"
            ),
            "add_product_name_prompt": (
                "Perfecto. Ahora, ¿cuál es el nombre del producto?"
            ),
            "add_product_name_empty": (
                "Por favor ingresa un nombre de producto válido (no puede estar vacío)."
            ),
            "add_product_name_too_long": (
                "El nombre del producto es muy largo (máximo 255 caracteres)."
            ),
            "add_product_description_prompt": (
                "Entendido. Ahora, por favor proporciona una descripción "
                "para el producto."
            ),
            "add_product_description_empty": (
                "Por favor ingresa una descripción de producto válida "
                "(no puede estar vacía)."
            ),
            "add_product_description_too_long": (
                "La descripción del producto es muy larga (máximo 1000 caracteres)."
            ),
            "add_product_price_prompt": ("Excelente. ¿Cuál es el precio? (ej., 25.99)"),
            "add_product_price_invalid": (
                "El precio debe ser un número positivo. Por favor inténtalo de nuevo."
            ),
            "add_product_price_format_error": (
                "Formato de precio inválido. Por favor ingresa un número (ej., 25.99)."
            ),
            "add_product_stock_prompt": (
                "Bien. Ahora, ¿cuántas unidades hay en stock? (ej., 50)"
            ),
            "add_product_stock_not_text": (
                "Por favor envía la cantidad de stock como texto, "
                "no una foto o sticker."
            ),
            "add_product_stock_negative": (
                "El stock no puede ser negativo. Por favor ingresa un número entero."
            ),
            "add_product_stock_invalid": (
                "Formato inválido. Por favor ingresa un número entero."
            ),
            "add_product_image_prompt": (
                "Excelente. Ahora, por favor sube las fotos del producto.\n"
                "Envíalas una por una o como grupo. Escribe /done cuando termines (o /skip)."
            ),
            "add_product_success": "✅ ¡Producto '{name}' creado exitosamente!",
            "add_product_error": (
                "❌ Ocurrió un error inesperado al crear el producto. "
                "Por favor revisa los logs para más detalles."
            ),
            # Edit product messages
            "edit_product_load_error": (
                "❌ Error al cargar categorías. Por favor inténtalo de nuevo."
            ),
            "edit_product_no_categories": (
                "❌ No se encontraron categorías. Necesitas crear al menos una "
                "categoría antes de editar productos."
            ),
            "edit_product_choose_category": (
                "Elige una categoría para ver sus productos:"
            ),
            "edit_product_no_products": (
                "❌ No se encontraron productos en esta categoría. "
                "Por favor agrega productos primero o elige otra categoría."
            ),
            "edit_product_choose_product": "Elige un producto para editar:",
            "edit_product_not_found": "❌ Producto no encontrado.",
            "edit_product_load_details_error": (
                "❌ Ocurrió un error inesperado al cargar los detalles del producto."
            ),
            "edit_product_load_products_error": (
                "❌ Ocurrió un error inesperado al cargar los productos."
            ),
            # Delete product messages
            "delete_product_choose_category": (
                "Elige una categoría para eliminar productos:"
            ),
            "delete_product_choose_product": "Elige un producto para eliminar:",
            "delete_product_confirmation": (
                "⚠️ ¿Estás seguro de que quieres eliminar este producto?\n\n"
                "<b>{product_name}</b>\n"
                "<i>{product_description}</i>\n\n"
                "<b>Precio:</b> €{product_price:.2f}\n"
                "<b>Stock:</b> {product_stock} unidades\n\n"
                "El producto se ocultará del catálogo pero se conservará "
                "en el historial de pedidos."
            ),
            "delete_product_cancelled": "Eliminación cancelada.",
            "delete_product_success": (
                "✅ El producto '{product_name}' ha sido eliminado."
            ),
            "delete_product_error": (
                "❌ Error: No se pudo eliminar '{product_name}'. "
                "Puede que ya haya sido eliminado."
            ),
            "delete_product_unexpected_error": (
                "Ocurrió un error inesperado al eliminar el producto."
            ),
            "delete_product_load_categories_error": (
                "❌ Ocurrió un error inesperado al cargar las categorías."
            ),
            "delete_product_no_categories": (
                "❌ No se encontraron categorías. Por favor crea categorías y "
                "productos primero."
            ),
            "delete_product_load_products_error": (
                "❌ Ocurrió un error inesperado al cargar los productos."
            ),
            "delete_product_no_products": (
                "❌ No se encontraron productos en esta categoría."
            ),
            "delete_product_load_product_error": (
                "❌ Ocurrió un error inesperado al cargar el producto."
            ),
            "delete_product_not_found": "❌ Producto no encontrado.",
            # Restore product messages
            "restore_product_load_error": (
                "❌ Ocurrió un error inesperado al cargar los productos eliminados."
            ),
            "restore_product_none_found": (
                "✅ No se encontraron productos eliminados. "
                "Todos los productos están activos."
            ),
            "restore_product_choose_prompt": (
                "🔄 Elige un producto eliminado para restaurar:"
            ),
            "restore_product_success": (
                "✅ ¡El producto ha sido restaurado exitosamente!"
            ),
            "restore_product_not_found": (
                "❌ Producto no encontrado o ya está activo."
            ),
            "restore_product_unexpected_error": (
                "❌ Ocurrió un error inesperado al restaurar el producto."
            ),
            # Product edit menu messages
            "edit_menu_header": "Estás editando:",
            "edit_menu_price_label": "Precio:",
            "edit_menu_stock_label": "Stock:",
            "edit_menu_stock_units": "unidades",
            "edit_menu_choose_field": "Elige un campo para editar:",
            "edit_product_fallback_prompt": "Ingresa el nuevo valor:",
            "edit_product_name_prompt": "Ingresa el nuevo nombre del producto:",
            "edit_product_price_prompt": "Ingresa el nuevo precio (ej., 25.99):",
            "edit_product_stock_prompt": "Ingresa la nueva cantidad de stock:",
            "edit_product_image_prompt": (
                "Por favor sube una nueva foto para el producto:"
            ),
            "edit_product_value_empty": (
                "Por favor ingresa un valor válido (no puede estar vacío)."
            ),
            "edit_product_price_invalid": (
                "El precio debe ser un número positivo. Por favor inténtalo de nuevo."
            ),
            "edit_product_stock_negative": (
                "El stock no puede ser negativo. Por favor inténtalo de nuevo."
            ),
            "edit_product_field_too_long": (
                "{field} es muy largo (máximo {max_length} caracteres)."
            ),
            "edit_product_invalid_format": (
                "Formato de {field_type} inválido. Por favor inténtalo de nuevo."
            ),
            "edit_product_success": (
                "✅ ¡{field} del producto '{name}' actualizado exitosamente!"
            ),
            "edit_product_error": (
                "❌ Ocurrió un error inesperado al actualizar el producto."
            ),
            "edit_product_image_success": (
                "✅ ¡Imagen del producto '{name}' actualizada exitosamente!"
            ),
            "edit_product_image_error": (
                "❌ Ocurrió un error inesperado al actualizar la imagen del producto."
            ),
        }

        # Russian messages
        ru_messages = {
            # Add product messages
            "add_product_categories_load_error": (
                "❌ Не удалось загрузить категории. Пожалуйста, попробуйте снова."
            ),
            "add_product_no_categories": (
                "❌ Категории не найдены. Вам нужно создать хотя бы одну "
                "категорию перед добавлением товаров. "
                "Пожалуйста, сначала используйте 'Добавить Категорию'."
            ),
            "add_product_choose_category": (
                "Пожалуйста, выберите категорию для нового товара:"
            ),
            "add_product_name_prompt": ("Отлично. Теперь, как называется товар?"),
            "add_product_name_empty": (
                "Пожалуйста, введите корректное название товара (не может быть пустым)."
            ),
            "add_product_name_too_long": (
                "Название товара слишком длинное (максимум 255 символов)."
            ),
            "add_product_description_prompt": (
                "Понятно. Теперь, пожалуйста, предоставьте описание товара."
            ),
            "add_product_description_empty": (
                "Пожалуйста, введите корректное описание товара (не может быть пустым)."
            ),
            "add_product_description_too_long": (
                "Описание товара слишком длинное (максимум 1000 символов)."
            ),
            "add_product_price_prompt": ("Отлично. Какая цена? (например, 25.99)"),
            "add_product_price_invalid": (
                "Цена должна быть положительным числом. Пожалуйста, попробуйте снова."
            ),
            "add_product_price_format_error": (
                "Неверный формат цены. Пожалуйста, введите число (например, 25.99)."
            ),
            "add_product_stock_prompt": (
                "Хорошо. Теперь, сколько единиц на складе? (например, 50)"
            ),
            "add_product_stock_not_text": (
                "Пожалуйста, отправьте количество на складе как текст, "
                "а не фото или стикер."
            ),
            "add_product_stock_negative": (
                "Количество на складе не может быть отрицательным. "
                "Пожалуйста, введите целое число."
            ),
            "add_product_stock_invalid": (
                "Неверный формат. Пожалуйста, введите целое число."
            ),
            "add_product_image_prompt": (
                "Отлично. Теперь загрузите фото товара.\n"
                "Отправляйте их по одному или группой. Напишите /done, когда закончите (или /skip)."
            ),
            "add_product_success": "✅ Товар '{name}' успешно создан!",
            "add_product_error": (
                "❌ Произошла неожиданная ошибка при создании товара. "
                "Пожалуйста, проверьте логи для подробностей."
            ),
            # Edit product messages
            "edit_product_load_error": (
                "❌ Не удалось загрузить категории. Пожалуйста, попробуйте снова."
            ),
            "edit_product_no_categories": (
                "❌ Категории не найдены. Вам нужно создать хотя бы одну "
                "категорию перед редактированием товаров."
            ),
            "edit_product_choose_category": (
                "Выберите категорию, чтобы увидеть её товары:"
            ),
            "edit_product_no_products": (
                "❌ Товары в этой категории не найдены. "
                "Пожалуйста, сначала добавьте товары или выберите другую категорию."
            ),
            "edit_product_choose_product": "Выберите товар для редактирования:",
            "edit_product_not_found": "❌ Товар не найден.",
            "edit_product_load_details_error": (
                "❌ Произошла неожиданная ошибка при загрузке деталей товара."
            ),
            "edit_product_load_products_error": (
                "❌ Произошла неожиданная ошибка при загрузке товаров."
            ),
            # Delete product messages
            "delete_product_choose_category": (
                "Выберите категорию для удаления товаров:"
            ),
            "delete_product_choose_product": "Выберите товар для удаления:",
            "delete_product_confirmation": (
                "⚠️ Вы уверены, что хотите удалить этот товар?\n\n"
                "<b>{product_name}</b>\n"
                "<i>{product_description}</i>\n\n"
                "<b>Цена:</b> ₽{product_price:.2f}\n"
                "<b>Остаток:</b> {product_stock} шт.\n\n"
                "Товар будет скрыт из каталога, но сохранится в истории заказов."
            ),
            "delete_product_cancelled": "Удаление отменено.",
            "delete_product_success": "✅ Товар '{product_name}' был удален.",
            "delete_product_error": (
                "❌ Ошибка: Не удалось удалить '{product_name}'. "
                "Возможно, он уже был удален."
            ),
            "delete_product_unexpected_error": (
                "Произошла неожиданная ошибка при удалении товара."
            ),
            "delete_product_load_categories_error": (
                "❌ Произошла неожиданная ошибка при загрузке категорий."
            ),
            "delete_product_no_categories": (
                "❌ Категории не найдены. Сначала создайте категории и товары."
            ),
            "delete_product_load_products_error": (
                "❌ Произошла неожиданная ошибка при загрузке товаров."
            ),
            "delete_product_no_products": "❌ В этой категории товары не найдены.",
            "delete_product_load_product_error": (
                "❌ Произошла неожиданная ошибка при загрузке товара."
            ),
            "delete_product_not_found": "❌ Товар не найден.",
            # Restore product messages
            "restore_product_load_error": (
                "❌ Произошла неожиданная ошибка при загрузке удаленных товаров."
            ),
            "restore_product_none_found": (
                "✅ Удаленные товары не найдены. Все товары активны."
            ),
            "restore_product_choose_prompt": (
                "🔄 Выберите удаленный товар для восстановления:"
            ),
            "restore_product_success": ("✅ Товар успешно восстановлен!"),
            "restore_product_not_found": ("❌ Товар не найден или уже активен."),
            "restore_product_unexpected_error": (
                "❌ Произошла неожиданная ошибка при восстановлении товара."
            ),
            # Product edit menu messages
            "edit_menu_header": "Вы редактируете:",
            "edit_menu_price_label": "Цена:",
            "edit_menu_stock_label": "Остаток:",
            "edit_menu_stock_units": "шт.",
            "edit_menu_choose_field": "Выберите поле для редактирования:",
            "edit_product_fallback_prompt": "Введите новое значение:",
            "edit_product_name_prompt": "Введите новое название товара:",
            "edit_product_price_prompt": "Введите новую цену (например, 25.99):",
            "edit_product_stock_prompt": "Введите новое количество на складе:",
            "edit_product_image_prompt": "Пожалуйста, загрузите новое фото товара:",
            "edit_product_value_empty": (
                "Пожалуйста, введите корректное значение (не может быть пустым)."
            ),
            "edit_product_price_invalid": (
                "Цена должна быть положительным числом. Пожалуйста, попробуйте снова."
            ),
            "edit_product_stock_negative": (
                "Количество на складе не может быть отрицательным. "
                "Пожалуйста, попробуйте снова."
            ),
            "edit_product_field_too_long": (
                "{field} слишком длинное (максимум {max_length} символов)."
            ),
            "edit_product_invalid_format": (
                "Неверный формат {field_type}. Пожалуйста, попробуйте снова."
            ),
            "edit_product_success": ("✅ {field} товара '{name}' успешно обновлен!"),
            "edit_product_error": (
                "❌ Произошла неожиданная ошибка при обновлении товара."
            ),
            "edit_product_image_success": (
                "✅ Фото товара '{name}' успешно обновлено!"
            ),
            "edit_product_image_error": (
                "❌ Произошла неожиданная ошибка при обновлении фото товара."
            ),
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
