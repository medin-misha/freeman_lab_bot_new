import unittest

from app.modules.analysis_module.messages import get_messages as get_analysis_messages
from app.modules.default_diagnostic_module.messages import (
    get_messages as get_default_diagnostic_messages,
)
from app.modules.invisible_diagnostic_module.messages import (
    get_messages as get_invisible_diagnostic_messages,
)
from app.modules.menu_module.messages import get_messages as get_menu_messages
from app.modules.products_module.messages import get_messages as get_products_messages
from app.modules.system.messages import get_messages as get_system_messages
from app.core.user_support import DEVELOPER_CONTACT


class SystemSupportMessagesTests(unittest.TestCase):
    def test_system_errors_include_developer_contact(self) -> None:
        messages = get_system_messages()

        for key in (
            "auth_missing_user",
            "auth_backend_not_configured",
            "auth_backend_unavailable",
            "auth_backend_unexpected_response",
            "auth_failed",
        ):
            self.assertIn(DEVELOPER_CONTACT, messages[key])

    def test_menu_error_includes_developer_contact(self) -> None:
        messages = get_menu_messages()

        self.assertIn(DEVELOPER_CONTACT, messages["subscription_check_failed"])
        self.assertNotIn(DEVELOPER_CONTACT, messages["subscription_still_missing"])

    def test_products_errors_include_developer_contact(self) -> None:
        messages = get_products_messages()

        self.assertIn(DEVELOPER_CONTACT, messages["request_failed"])
        self.assertIn(DEVELOPER_CONTACT, messages["backend_user_not_found"])
        self.assertNotIn(DEVELOPER_CONTACT, messages["request_context_missing"])

    def test_analysis_errors_include_developer_contact(self) -> None:
        messages = get_analysis_messages()

        self.assertIn(DEVELOPER_CONTACT, messages["analysis_registration_failed"])
        self.assertIn(DEVELOPER_CONTACT, messages["analysis_auth_context_missing"])

    def test_diagnostic_error_does_not_duplicate_developer_contact(self) -> None:
        default_messages = get_default_diagnostic_messages()
        invisible_messages = get_invisible_diagnostic_messages()

        self.assertEqual(
            default_messages["diagnostic_creation_failed"].count(DEVELOPER_CONTACT),
            1,
        )
        self.assertEqual(
            invisible_messages["diagnostic_creation_failed"].count(DEVELOPER_CONTACT),
            1,
        )
