import re

from playwright.sync_api import Page, expect


class BasePage:
    """Parent of every page object. Holds what all pages share."""

    def __init__(self, page: Page):
        self.page = page

    def open(self, path: str = "/"):
        # "/" is joined to --base-url from pytest.ini
        self.page.goto(path)

    def expect_url_contains(self, text: str):
        expect(self.page).to_have_url(re.compile(text))
