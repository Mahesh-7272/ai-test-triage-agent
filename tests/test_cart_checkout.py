import pytest
from playwright.sync_api import expect

from utils.test_data import CHECKOUT_INFO

BACKPACK = "sauce-labs-backpack"


def test_add_item_updates_cart_badge(standard_user_session):
    standard_user_session.add_to_cart(BACKPACK)
    expect(standard_user_session.cart_badge).to_have_text("1")


def test_added_item_appears_in_cart(standard_user_session, cart_page):
    standard_user_session.add_to_cart(BACKPACK)
    standard_user_session.open_cart()
    assert cart_page.names() == ["Sauce Labs Backpack"]


@pytest.mark.smoke
def test_complete_purchase(standard_user_session, cart_page, checkout_page):
    standard_user_session.add_to_cart(BACKPACK)
    standard_user_session.open_cart()
    cart_page.checkout()
    checkout_page.fill_info(**CHECKOUT_INFO)
    checkout_page.finish()
    expect(checkout_page.complete_header).to_have_text("Thank you for your order!")


def test_checkout_requires_first_name(standard_user_session, cart_page, checkout_page):
    standard_user_session.add_to_cart(BACKPACK)
    standard_user_session.open_cart()
    cart_page.checkout()
    checkout_page.fill_info("", "User", "12345")
    expect(checkout_page.error_message).to_contain_text("First Name is required")
