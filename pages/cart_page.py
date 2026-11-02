from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.items = page.locator("[data-test='inventory-item']")
        self.item_names = page.locator("[data-test='inventory-item-name']")
        self.checkout_button = page.locator("[data-test='checkout']")

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def remove(self, product_name: str):
        slug = product_name.lower().replace(" ", "-")
        self.page.locator(f"[data-test='remove-{slug}']").click()

    def checkout(self):
        self.checkout_button.click()
