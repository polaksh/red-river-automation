"""Product detail page."""

from support.traced import TracedPage
from pages.base_page import BasePage
from pages.locators import ProductLocators


class ProductPage(BasePage):

    locators = ProductLocators()

    def __init__(self, page: TracedPage) -> None:
        super().__init__(page)
        self._page.wait_for_selector(self.locators.name)

    def product_name(self) -> str:
        return self._page.text_content(self.locators.name).strip()

    def product_price(self) -> str:
        return self._page.text_content(self.locators.price).strip()

    def product_description(self) -> str:
        return self._page.text_content(self.locators.description).strip()

    def add_to_cart(self) -> None:
        """Site shows a browser alert on success, so we handle that here."""
        dialog_handled = []

        def handle_dialog(dialog):
            dialog_handled.append(dialog.message)
            dialog.accept()

        self._page.on("dialog", handle_dialog)
        self._page.click(self.locators.add_to_cart_btn)
        self._page.wait_for_timeout(1500)
        self._page.remove_listener("dialog", handle_dialog)
