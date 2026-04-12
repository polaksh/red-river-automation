"""Cart page — items table and checkout."""

from support.traced import TracedPage
from pages.base_page import BasePage
from pages.locators import CartLocators


class CartPage(BasePage):

    locators = CartLocators()

    def __init__(self, page: TracedPage) -> None:
        super().__init__(page)

    def wait_for_cart_loaded(self) -> None:
        self._page.wait_for_selector(self.locators.cart_row)

    def item_names(self) -> list[str]:
        rows = self._page.query_selector_all(self.locators.cart_row)
        return [row.query_selector(self.locators.col_title).text_content().strip()
                for row in rows]

    def item_prices(self) -> list[str]:
        rows = self._page.query_selector_all(self.locators.cart_row)
        return [row.query_selector(self.locators.col_price).text_content().strip()
                for row in rows]

    def total_price(self) -> str:
        return self._page.text_content(self.locators.total_price).strip()

    def item_count(self) -> int:
        return len(self._page.query_selector_all(self.locators.cart_row))
