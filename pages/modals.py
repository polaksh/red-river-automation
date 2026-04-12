"""Modal page objects: signup, login, contact, place order."""

from support.traced import TracedPage
from pages.locators import (
    SignupModalLocators,
    LoginModalLocators,
    ContactModalLocators,
    PlaceOrderModalLocators,
)


class SignupModal:

    locators = SignupModalLocators()

    def __init__(self, page: TracedPage) -> None:
        self._page = page

    def open(self) -> None:
        self._page.click(self.locators.open_btn)
        self._page.wait_for_selector(self.locators.modal, state="visible")

    def fill(self, username: str, password: str) -> None:
        self._page.fill(self.locators.username, username)
        self._page.fill(self.locators.password, password)

    def submit(self) -> None:
        self._page.click(self.locators.submit_btn)


class LoginModal:

    locators = LoginModalLocators()

    def __init__(self, page: TracedPage) -> None:
        self._page = page

    def open(self) -> None:
        self._page.click(self.locators.open_btn)
        self._page.wait_for_selector(self.locators.modal, state="visible")

    def fill(self, username: str, password: str) -> None:
        self._page.fill(self.locators.username, username)
        self._page.fill(self.locators.password, password)

    def submit(self) -> None:
        self._page.click(self.locators.submit_btn)

    def wait_for_logged_in(self) -> str:
        self._page.wait_for_selector(self.locators.welcome_user, state="visible")
        return self._page.text_content(self.locators.welcome_user)

    def is_logout_visible(self) -> bool:
        return self._page.is_visible(self.locators.logout_btn)

    def logout(self) -> None:
        self._page.click(self.locators.logout_btn)
        self._page.wait_for_selector(self.locators.open_btn, state="visible")


class ContactModal:

    locators = ContactModalLocators()

    def __init__(self, page: TracedPage) -> None:
        self._page = page

    def open(self) -> None:
        self._page.click(self.locators.open_btn)
        self._page.wait_for_selector(self.locators.modal, state="visible")

    def fill(self, email: str, name: str, message: str) -> None:
        self._page.fill(self.locators.email, email)
        self._page.fill(self.locators.name, name)
        self._page.fill(self.locators.message, message)

    def submit(self) -> None:
        self._page.click(self.locators.submit_btn)


class PlaceOrderModal:

    locators = PlaceOrderModalLocators()

    def __init__(self, page: TracedPage) -> None:
        self._page = page

    def open(self) -> None:
        self._page.click(self.locators.open_btn)
        self._page.wait_for_selector(self.locators.modal, state="visible")

    def fill(self, name: str, country: str, city: str,
             card: str, month: str, year: str) -> None:
        self._page.fill(self.locators.name, name)
        self._page.fill(self.locators.country, country)
        self._page.fill(self.locators.city, city)
        self._page.fill(self.locators.card, card)
        self._page.fill(self.locators.month, month)
        self._page.fill(self.locators.year, year)

    def submit(self) -> None:
        self._page.click(self.locators.submit_btn)
        self._page.wait_for_selector(self.locators.confirm_dialog, state="visible")

    def confirmation_title(self) -> str:
        return self._page.text_content(self.locators.confirm_title)

    def confirmation_body(self) -> str:
        return self._page.text_content(self.locators.confirm_body)

    def dismiss_confirmation(self) -> None:
        self._page.click(self.locators.confirm_ok)
