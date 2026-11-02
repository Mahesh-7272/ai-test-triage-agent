from playwright.sync_api import Page

from pages.base_page import BasePage


class InventoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.locator("[data-test='title']")
        self.items = page.locator("[data-test='inventory-item']")
        self.item_names = page.locator("[data-test='inventory-item-name']")
        self.item_prices = page.locator("[data-test='inventory-item-price']")
        self.sort_dropdown = page.locator("[data-test='product-sort-container']")
        self.cart_badge = page.locator("[data-test='shopping-cart-badge']")
        self.cart_link = page.locator("[data-test='shopping-cart-link']")

    def sort_by(self, option_value: str):
        """option_value: 'az', 'za', 'lohi' or 'hilo'."""
        self.sort_dropdown.select_option(option_value)

    def add_to_cart(self, product_name: str):
        # Button ids look like: add-to-cart-sauce-labs-backpack
        slug = product_name.lower().replace(" ", "-")
        self.page.locator(f"[data-test='add-to-cart-{slug}']").click()

    def prices(self) -> list[float]:
        texts = self.item_prices.all_inner_texts()
        return [float(t.replace("$", "")) for t in texts]

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def open_cart(self):
        self.cart_link.click()
