"""Home page — product grid and category filtering."""

from support.traced import TracedPage
from pages.base_page import BasePage
from pages.locators import HomeLocators, ProductLocators


class HomePage(BasePage):

    locators = HomeLocators()

    def __init__(self, page: TracedPage) -> None:
        super().__init__(page)

    def product_names(self) -> list[str]:
        cards = self._page.query_selector_all(self.locators.product_link)
        return [card.text_content().strip() for card in cards]

    def product_count(self) -> int:
        return len(self._page.query_selector_all(self.locators.product_card))

    def select_category(self, category: str) -> None:
        selector = {
            "phones": self.locators.cat_phones,
            "laptops": self.locators.cat_laptops,
            "monitors": self.locators.cat_monitors,
        }[category.lower()]

        # demoblaze repopulates the grid via AJAX after category click;
        # we clear it manually so wait_for_selector catches the fresh cards
        self._page.click(selector)
        self._page.evaluate(
            f"document.querySelector('{self.locators.product_grid}').innerHTML = ''"
        )
        self._page.wait_for_selector(self.locators.product_card)

    def click_product(self, name: str) -> None:
        self._page.click(f"a.hrefch:has-text('{name}')")
        self._page.wait_for_selector(ProductLocators.name)
