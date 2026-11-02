"""Tests that FAIL on purpose.

problem_user has real bugs on saucedemo. These tests assert the correct
behaviour, so they fail and give the AI failure analyzer real input.

Skip them with:  pytest -m "not demo_failure"
"""
import pytest

from utils.test_data import CHECKOUT_INFO

pytestmark = pytest.mark.demo_failure


def test_problem_user_sort_price_low_to_high(problem_user_session):
    problem_user_session.sort_by("lohi")
    prices = problem_user_session.prices()
    assert prices == sorted(prices), "Prices are not sorted low to high"


def test_problem_user_can_enter_last_name(problem_user_session, cart_page, checkout_page):
    problem_user_session.add_to_cart("sauce-labs-backpack")
    problem_user_session.open_cart()
    cart_page.checkout()
    checkout_page.first_name.fill(CHECKOUT_INFO["first_name"])
    checkout_page.last_name.fill(CHECKOUT_INFO["last_name"])
    assert checkout_page.last_name.input_value() == CHECKOUT_INFO["last_name"]


def test_wrong_expected_title(standard_user_session):
    # Wrong on purpose: the real title is "Products"
    assert standard_user_session.title.inner_text() == "Product List"
