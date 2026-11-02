import pytest
from playwright.sync_api import expect

from utils.test_data import PASSWORD, USERS


@pytest.mark.smoke
def test_valid_login(login_page, inventory_page):
    login_page.login(USERS["standard"], PASSWORD)
    login_page.expect_url_contains("inventory")
    expect(inventory_page.title).to_have_text("Products")


def test_locked_out_user_sees_error(login_page):
    login_page.login(USERS["locked"], PASSWORD)
    expect(login_page.error_message).to_contain_text("locked out")


def test_wrong_password_sees_error(login_page):
    login_page.login(USERS["standard"], "wrong_password")
    expect(login_page.error_message).to_contain_text("do not match")


def test_empty_username_sees_error(login_page):
    login_page.login("", PASSWORD)
    expect(login_page.error_message).to_contain_text("Username is required")
