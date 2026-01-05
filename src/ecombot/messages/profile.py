"""Profile messages for the EcomBot application."""

from ..core.messages import BaseMessageManager
from ..core.messages import Language


class ProfileMessageManager(BaseMessageManager):
    """Message manager for profile-related messages."""

    def _load_messages(self) -> None:
        """Load profile messages for all supported languages."""

        # English messages
        en_messages = {
            # Headers
            "profile_header": "<b>Your Profile</b>\n\n",
            "address_management_header": "<b>Your Delivery Addresses</b>\n\n",
            # Profile template
            "profile_template": (
                "<b>Name:</b> {name}\n"
                "<b>Phone:</b> {phone}\n"
                "<b>Email:</b> {email}\n\n"
                "<b>Default Address:</b>\n"
            ),
            # Status messages
            "not_set_text": "Not set",
            "default_address_not_set": (
                "<i>Not set. You can set one in 'Manage Addresses'.</i>"
            ),
            "no_addresses_message": "You have no saved addresses.",
            "address_not_found": "Address not found.",
            "failed_load_address_details": "Failed to load address details.",
            # Success messages
            "success_address_deleted": "Address deleted successfully!",
            "success_default_address_updated": "Default address updated!",
            "success_address_saved": "✅ New address saved successfully!",
            "success_phone_updated": "✅ Phone number updated successfully!",
            "success_email_updated": "✅ Email address updated successfully!",
            # Error messages
            "error_profile_load_failed": (
                "❌ An error occurred while loading your profile."
            ),
            "error_address_delete_failed": "Failed to delete address.",
            "error_default_address_failed": "Failed to update default address.",
            "error_missing_address_id": (
                "An internal error occurred (missing address ID)."
            ),
            "error_address_save_failed": (
                "❌ An error occurred while saving the address."
            ),
            "error_addresses_load_failed": (
                "❌ An error occurred while loading your addresses."
            ),
            "error_phone_update_failed": (
                "❌ An error occurred while updating your phone number."
            ),
            "error_email_update_failed": (
                "❌ An error occurred while updating your email address."
            ),
            # FSM prompts
            "add_address_start_prompt": (
                "Let's add a new address.\n\n"
                "First, give it a short label (e.g., 'Home', 'Office')."
            ),
            "add_address_full_prompt": (
                "Great. Now, please enter the full shipping address."
            ),
            "edit_phone_prompt": "Please enter your new phone number:",
            "edit_email_prompt": "Please enter your new email address:",
            # Address display
            "default_address_prefix": "⭐️ Default Address",
            "address_prefix": "📍 Address",
            "address_label_field": "<b>Label:</b> {label}",
            "address_full_field": "<b>Full Address:</b>\n<code>{address}</code>",
        }

        # Spanish messages
        es_messages = {
            # Headers
            "profile_header": "<b>Tu Perfil</b>\n\n",
            "address_management_header": "<b>Tus Direcciones de Entrega</b>\n\n",
            # Profile template
            "profile_template": (
                "<b>Nombre:</b> {name}\n"
                "<b>Teléfono:</b> {phone}\n"
                "<b>Email:</b> {email}\n\n"
                "<b>Dirección Predeterminada:</b>\n"
            ),
            # Status messages
            "not_set_text": "No establecido",
            "default_address_not_set": (
                "<i>No establecida. Puedes configurar una en "
                "'Gestionar Direcciones'.</i>"
            ),
            "no_addresses_message": "No tienes direcciones guardadas.",
            "address_not_found": "Dirección no encontrada.",
            "failed_load_address_details": (
                "Error al cargar los detalles de la dirección."
            ),
            # Success messages
            "success_address_deleted": "¡Dirección eliminada exitosamente!",
            "success_default_address_updated": (
                "¡Dirección predeterminada actualizada!"
            ),
            "success_address_saved": "✅ ¡Nueva dirección guardada exitosamente!",
            "success_phone_updated": (
                "✅ ¡Número de teléfono actualizado exitosamente!"
            ),
            "success_email_updated": (
                "✅ ¡Dirección de email actualizada exitosamente!"
            ),
            # Error messages
            "error_profile_load_failed": ("❌ Ocurrió un error al cargar tu perfil."),
            "error_address_delete_failed": "Error al eliminar la dirección.",
            "error_default_address_failed": (
                "Error al actualizar la dirección predeterminada."
            ),
            "error_missing_address_id": (
                "Ocurrió un error interno (ID de dirección faltante)."
            ),
            "error_address_save_failed": (
                "❌ Ocurrió un error al guardar la dirección."
            ),
            "error_addresses_load_failed": (
                "❌ Ocurrió un error al cargar tus direcciones."
            ),
            "error_phone_update_failed": (
                "❌ Ocurrió un error al actualizar tu número de teléfono."
            ),
            "error_email_update_failed": (
                "❌ Ocurrió un error al actualizar tu dirección de email."
            ),
            # FSM prompts
            "add_address_start_prompt": (
                "Vamos a agregar una nueva dirección.\n\n"
                "Primero, dale una etiqueta corta (ej., 'Casa', 'Oficina')."
            ),
            "add_address_full_prompt": (
                "Perfecto. Ahora, por favor ingresa la dirección completa " "de envío."
            ),
            "edit_phone_prompt": "Por favor ingresa tu nuevo número de teléfono:",
            "edit_email_prompt": ("Por favor ingresa tu nueva dirección de email:"),
            # Address display
            "default_address_prefix": "⭐️ Dirección Predeterminada",
            "address_prefix": "📍 Dirección",
            "address_label_field": "<b>Etiqueta:</b> {label}",
            "address_full_field": (
                "<b>Dirección Completa:</b>\n<code>{address}</code>"
            ),
        }

        # Russian messages
        ru_messages = {
            # Headers
            "profile_header": "<b>Ваш Профиль</b>\n\n",
            "address_management_header": "<b>Ваши Адреса Доставки</b>\n\n",
            # Profile template
            "profile_template": (
                "<b>Имя:</b> {name}\n"
                "<b>Телефон:</b> {phone}\n"
                "<b>Email:</b> {email}\n\n"
                "<b>Адрес по умолчанию:</b>\n"
            ),
            # Status messages
            "not_set_text": "Не установлено",
            "default_address_not_set": (
                "<i>Не установлен. Вы можете установить его в "
                "'Управление Адресами'.</i>"
            ),
            "no_addresses_message": "У вас нет сохраненных адресов.",
            "address_not_found": "Адрес не найден.",
            "failed_load_address_details": ("Не удалось загрузить детали адреса."),
            # Success messages
            "success_address_deleted": "Адрес успешно удален!",
            "success_default_address_updated": "Адрес по умолчанию обновлен!",
            "success_address_saved": "✅ Новый адрес успешно сохранен!",
            "success_phone_updated": "✅ Номер телефона успешно обновлен!",
            "success_email_updated": "✅ Email адрес успешно обновлен!",
            # Error messages
            "error_profile_load_failed": (
                "❌ Произошла ошибка при загрузке вашего профиля."
            ),
            "error_address_delete_failed": "Не удалось удалить адрес.",
            "error_default_address_failed": ("Не удалось обновить адрес по умолчанию."),
            "error_missing_address_id": (
                "Произошла внутренняя ошибка (отсутствует ID адреса)."
            ),
            "error_address_save_failed": ("❌ Произошла ошибка при сохранении адреса."),
            "error_addresses_load_failed": (
                "❌ Произошла ошибка при загрузке ваших адресов."
            ),
            "error_phone_update_failed": (
                "❌ Произошла ошибка при обновлении номера телефона."
            ),
            "error_email_update_failed": (
                "❌ Произошла ошибка при обновлении email адреса."
            ),
            # FSM prompts
            "add_address_start_prompt": (
                "Давайте добавим новый адрес.\n\n"
                "Сначала дайте ему короткую метку (например, 'Дом', 'Офис')."
            ),
            "add_address_full_prompt": (
                "Отлично. Теперь, пожалуйста, введите полный адрес доставки."
            ),
            "edit_phone_prompt": "Пожалуйста, введите ваш новый номер телефона:",
            "edit_email_prompt": "Пожалуйста, введите ваш новый email адрес:",
            # Address display
            "default_address_prefix": "⭐️ Адрес по умолчанию",
            "address_prefix": "📍 Адрес",
            "address_label_field": "<b>Метка:</b> {label}",
            "address_full_field": ("<b>Полный Адрес:</b>\n<code>{address}</code>"),
        }

        self._messages = {
            Language.EN: en_messages,
            Language.ES: es_messages,
            Language.RU: ru_messages,
        }
