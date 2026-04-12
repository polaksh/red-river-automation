"""All CSS selectors for demoblaze.com in one place. Edit here, not in page objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavLocators:
    cart_btn: str = "#cartur"
    login_btn: str = "#login2"
    signup_btn: str = "#signin2"
    logout_btn: str = "#logout2"
    welcome_user: str = "#nameofuser"
    contact_btn: str = "a.nav-link[data-target='#exampleModal']"


@dataclass(frozen=True)
class BaseLocators:
    product_card: str = "#tbodyid .card"
    page_wrapper: str = "#page-wrapper"


@dataclass(frozen=True)
class HomeLocators:
    product_grid: str = "#tbodyid"
    product_card: str = "#tbodyid .col-lg-4"
    product_link: str = ".hrefch"

    # #itemc is duplicated in the DOM, so we target onclick instead
    cat_phones: str = "a[onclick=\"byCat('phone')\"]"
    cat_laptops: str = "a[onclick=\"byCat('notebook')\"]"
    cat_monitors: str = "a[onclick=\"byCat('monitor')\"]"


@dataclass(frozen=True)
class ProductLocators:
    name: str = "#tbodyid h2.name"
    price: str = "#tbodyid h3.price-container"
    description: str = "#more-information p"
    add_to_cart_btn: str = "a[onclick^='addToCart']"


@dataclass(frozen=True)
class CartLocators:
    cart_table: str = "#tbodyid"
    cart_row: str = "#tbodyid tr.success"
    total_price: str = "#totalp"
    place_order_btn: str = "button[data-target='#orderModal']"

    col_title: str = "td:nth-child(2)"
    col_price: str = "td:nth-child(3)"
    col_delete: str = "td:nth-child(4) a"


@dataclass(frozen=True)
class SignupModalLocators:
    open_btn: str = "#signin2"
    modal: str = "#signInModal"
    username: str = "#sign-username"
    password: str = "#sign-password"
    submit_btn: str = "#signInModal .btn-primary"


@dataclass(frozen=True)
class LoginModalLocators:
    open_btn: str = "#login2"
    modal: str = "#logInModal"
    username: str = "#loginusername"
    password: str = "#loginpassword"
    submit_btn: str = "#logInModal .btn-primary"
    welcome_user: str = "#nameofuser"
    logout_btn: str = "#logout2"


@dataclass(frozen=True)
class ContactModalLocators:
    open_btn: str = "a.nav-link[data-target='#exampleModal']"
    modal: str = "#exampleModal"
    email: str = "#recipient-email"
    name: str = "#recipient-name"
    message: str = "#message-text"
    submit_btn: str = "#exampleModal .btn-primary"


@dataclass(frozen=True)
class PlaceOrderModalLocators:
    open_btn: str = "button[data-target='#orderModal']"
    modal: str = "#orderModal"
    name: str = "#name"
    country: str = "#country"
    city: str = "#city"
    card: str = "#card"
    month: str = "#month"
    year: str = "#year"
    submit_btn: str = "#orderModal .btn-primary"

    confirm_dialog: str = ".sweet-alert"
    confirm_title: str = ".sweet-alert h2"
    confirm_body: str = ".sweet-alert p"
    confirm_ok: str = ".sweet-alert .confirm"
