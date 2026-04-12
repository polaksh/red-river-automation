"""Common navigation and wait helpers. All page objects inherit from BasePage."""

from support.config import CONFIG
from support.traced import TracedPage
from pages.locators import BaseLocators, NavLocators


class BasePage:

    _base = BaseLocators()
    _nav = NavLocators()

    def __init__(self, traced_page: TracedPage) -> None:
        self._page = traced_page

    def navigate_home(self) -> None:
        self._page.goto(CONFIG.ui_base_url)
        self._page.wait_for_selector(self._base.product_card)

    def navigate_to_cart(self) -> None:
        self._page.click(self._nav.cart_btn)
        self._page.wait_for_selector(self._base.page_wrapper)

    def accept_alert(self) -> str:
        dialog_message = ""

        def handle_dialog(dialog):
            nonlocal dialog_message
            dialog_message = dialog.message
            dialog.accept()

        self._page.on("dialog", handle_dialog)
        self._page.wait_for_timeout(1000)
        self._page.remove_listener("dialog", handle_dialog)
        return dialog_message
