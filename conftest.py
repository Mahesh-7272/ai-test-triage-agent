"""Shared fixtures. Pytest loads this file automatically."""
import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.test_data import PASSWORD, USERS


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """A LoginPage with the login screen already open."""
    login = LoginPage(page)
    login.open()
    return login


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    return InventoryPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)


@pytest.fixture
def standard_user_session(login_page: LoginPage, inventory_page: InventoryPage) -> InventoryPage:
    """Logged in as standard_user. Use it when a test does not care about logging in."""
    login_page.login(USERS["standard"], PASSWORD)
    return inventory_page


@pytest.fixture
def problem_user_session(login_page: LoginPage, inventory_page: InventoryPage) -> InventoryPage:
    """Logged in as problem_user, whose site has real bugs."""
    login_page.login(USERS["problem"], PASSWORD)
    return inventory_page
