"""Admin categories messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class AdminCategoriesMessageManager(BaseMessageManager):
    """Message manager for admin category management messages."""

    def _load_messages(self) -> None:
        """Load admin categories messages for all supported languages."""

        # English messages
        en_messages = {
            # Add category messages
            "add_category_name_prompt": "Please enter the name for the new category:",
            "add_category_name_empty": (
                "Please enter a valid category name (cannot be empty)."
            ),
            "add_category_name_too_long": (
                "Category name is too long (maximum 255 characters)."
            ),
            "add_category_description_prompt": (
                "Great. Now enter a description for the category (or send /skip):"
            ),
            "add_category_description_too_long": (
                "Description is too long (maximum 1000 characters)."
            ),
            "add_category_success": "✅ Category '{name}' created successfully!",
            "add_category_already_exists": "⚠️ Error: {error}",
            "add_category_error": (
                "❌ An unexpected error occurred while creating the category."
            ),
            # Delete category messages
            "delete_category_load_error": (
                "❌ An unexpected error occurred while loading categories."
            ),
            "delete_category_no_categories": (
                "❌ No categories found. You need to create at least one category "
                "before deleting categories. Please use 'Add Category' first."
            ),
            "delete_category_choose_prompt": (
                "Choose the category you want to delete:"
            ),
            "delete_category_not_found": "Error: Category not found.",
            "delete_category_details_error": (
                "❌ An unexpected error occurred while loading category details."
            ),
            "delete_category_confirm_prompt": (
                "⚠️ Are you sure you want to delete the category '{name}'? "
                "It will be hidden from the catalog but preserved in order history."
            ),
            "delete_category_cancelled": "Deletion cancelled.",
            "delete_category_success": "✅ Category '{name}' has been deleted.",
            "delete_category_not_found_error": (
                "❌ Error: Could not delete '{name}'. "
                "It may have already been removed."
            ),
            "delete_category_error": (
                "❌ An unexpected error occurred while deleting '{name}'."
            ),
            # Restore category messages
            "restore_category_load_error": (
                "❌ An unexpected error occurred while loading deleted categories."
            ),
            "restore_category_none_found": (
                "✅ No deleted categories found. All categories are active."
            ),
            "restore_category_choose_prompt": (
                "🔄 Choose a deleted category to restore:"
            ),
            "restore_category_success": (
                "✅ Category and all its content have been restored successfully!"
            ),
            "restore_category_not_found": ("❌ Category not found or already active."),
            "restore_category_error": (
                "❌ An unexpected error occurred while restoring the category."
            ),
            # Common messages
            "back_to_admin_panel": "⬅️ Back to Admin Panel",
        }

        # Spanish messages
        es_messages = {
            # Add category messages
            "add_category_name_prompt": (
                "Por favor ingresa el nombre para la nueva categoría:"
            ),
            "add_category_name_empty": (
                "Por favor ingresa un nombre de categoría válido "
                "(no puede estar vacío)."
            ),
            "add_category_name_too_long": (
                "El nombre de la categoría es muy largo (máximo 255 caracteres)."
            ),
            "add_category_description_prompt": (
                "Perfecto. Ahora ingresa una descripción para la categoría "
                "(o envía /skip):"
            ),
            "add_category_description_too_long": (
                "La descripción es muy larga (máximo 1000 caracteres)."
            ),
            "add_category_success": "✅ ¡Categoría '{name}' creada exitosamente!",
            "add_category_already_exists": "⚠️ Error: {error}",
            "add_category_error": (
                "❌ Ocurrió un error inesperado al crear la categoría."
            ),
            # Delete category messages
            "delete_category_load_error": (
                "❌ Ocurrió un error inesperado al cargar las categorías."
            ),
            "delete_category_no_categories": (
                "❌ No se encontraron categorías. Necesitas crear al menos una "
                "categoría antes de eliminar categorías. "
                "Por favor usa 'Agregar Categoría' primero."
            ),
            "delete_category_choose_prompt": (
                "Elige la categoría que quieres eliminar:"
            ),
            "delete_category_not_found": "Error: Categoría no encontrada.",
            "delete_category_details_error": (
                "❌ Ocurrió un error inesperado al cargar los detalles de la categoría."
            ),
            "delete_category_confirm_prompt": (
                "⚠️ ¿Estás seguro de que quieres eliminar la categoría '{name}'? "
                "Se ocultará del catálogo pero se preservará en el historial "
                "de pedidos."
            ),
            "delete_category_cancelled": "Eliminación cancelada.",
            "delete_category_success": "✅ La categoría '{name}' ha sido eliminada.",
            "delete_category_not_found_error": (
                "❌ Error: No se pudo eliminar '{name}'. "
                "Puede que ya haya sido eliminada."
            ),
            "delete_category_error": (
                "❌ Ocurrió un error inesperado al eliminar '{name}'."
            ),
            # Restore category messages
            "restore_category_load_error": (
                "❌ Ocurrió un error inesperado al cargar las categorías eliminadas."
            ),
            "restore_category_none_found": (
                "✅ No se encontraron categorías eliminadas. "
                "Todas las categorías están activas."
            ),
            "restore_category_choose_prompt": (
                "🔄 Elige una categoría eliminada para restaurar:"
            ),
            "restore_category_success": (
                "✅ ¡La categoría y todo su contenido han sido restaurados "
                "exitosamente!"
            ),
            "restore_category_not_found": (
                "❌ Categoría no encontrada o ya está activa."
            ),
            "restore_category_error": (
                "❌ Ocurrió un error inesperado al restaurar la categoría."
            ),
            # Common messages
            "back_to_admin_panel": "⬅️ Volver al Panel Admin",
        }

        # Russian messages
        ru_messages = {
            # Add category messages
            "add_category_name_prompt": (
                "Пожалуйста, введите название для новой категории:"
            ),
            "add_category_name_empty": (
                "Пожалуйста, введите корректное название категории "
                "(не может быть пустым)."
            ),
            "add_category_name_too_long": (
                "Название категории слишком длинное (максимум 255 символов)."
            ),
            "add_category_description_prompt": (
                "Отлично. Теперь введите описание для категории (или отправьте /skip):"
            ),
            "add_category_description_too_long": (
                "Описание слишком длинное (максимум 1000 символов)."
            ),
            "add_category_success": "✅ Категория '{name}' успешно создана!",
            "add_category_already_exists": "⚠️ Ошибка: {error}",
            "add_category_error": (
                "❌ Произошла неожиданная ошибка при создании категории."
            ),
            # Delete category messages
            "delete_category_load_error": (
                "❌ Произошла неожиданная ошибка при загрузке категорий."
            ),
            "delete_category_no_categories": (
                "❌ Категории не найдены. Вам нужно создать хотя бы одну "
                "категорию перед удалением категорий. "
                "Пожалуйста, сначала используйте 'Добавить Категорию'."
            ),
            "delete_category_choose_prompt": (
                "Выберите категорию, которую хотите удалить:"
            ),
            "delete_category_not_found": "Ошибка: Категория не найдена.",
            "delete_category_details_error": (
                "❌ Произошла неожиданная ошибка при загрузке деталей категории."
            ),
            "delete_category_confirm_prompt": (
                "⚠️ Вы уверены, что хотите удалить категорию '{name}'? "
                "Она будет скрыта из каталога, но сохранена в истории заказов."
            ),
            "delete_category_cancelled": "Удаление отменено.",
            "delete_category_success": "✅ Категория '{name}' была удалена.",
            "delete_category_not_found_error": (
                "❌ Ошибка: Не удалось удалить '{name}'. "
                "Возможно, она уже была удалена."
            ),
            "delete_category_error": (
                "❌ Произошла неожиданная ошибка при удалении '{name}'."
            ),
            # Restore category messages
            "restore_category_load_error": (
                "❌ Произошла неожиданная ошибка при загрузке удаленных категорий."
            ),
            "restore_category_none_found": (
                "✅ Удаленные категории не найдены. Все категории активны."
            ),
            "restore_category_choose_prompt": (
                "🔄 Выберите удаленную категорию для восстановления:"
            ),
            "restore_category_success": (
                "✅ Категория и все её содержимое успешно восстановлены!"
            ),
            "restore_category_not_found": ("❌ Категория не найдена или уже активна."),
            "restore_category_error": (
                "❌ Произошла неожиданная ошибка при восстановлении категории."
            ),
            # Common messages
            "back_to_admin_panel": "⬅️ Назад в Админ Панель",
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
