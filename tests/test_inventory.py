from playwright.sync_api import expect


def test_six_products_are_listed(standard_user_session):
    expect(standard_user_session.items).to_have_count(6)


def test_sort_price_low_to_high(standard_user_session):
    standard_user_session.sort_by("lohi")
    prices = standard_user_session.prices()
    assert prices == sorted(prices)


def test_sort_name_z_to_a(standard_user_session):
    standard_user_session.sort_by("za")
    names = standard_user_session.names()
    assert names == sorted(names, reverse=True)
